"""
Configuration Service

Service layer that manages configuration and profile preference operations.
Uses Exception First principles for error handling.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from application.interfaces.configuration.configuration import (
    Configuration,
)
from application.interfaces.configuration.profile_preference import (
    ProfilePreference,
)
from domain.exceptions import (
    ConfigurationNotFoundError,
    RepositoryAccessError,
)
from domain.value_objects.hardware_configuration import (
    HardwareConfiguration,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
)


class ConfigurationService:
    """
    Service for managing configuration and profile preference operations

    This service handles configuration loading, profile management, and user preferences.
    It coordinates between ConfigurationRepository and ProfilePreferenceRepository.
    """

    def __init__(
        self,
        configuration: Configuration,
        profile_preference: Optional[ProfilePreference] = None,
    ):
        self._configuration = configuration
        self._profile_preference = profile_preference

    @property
    def configuration(self) -> Configuration:
        """Get the configuration"""
        return self._configuration

    @property
    def profile_preference(
        self,
    ) -> Optional[ProfilePreference]:
        """Get the profile preference"""
        return self._profile_preference

    async def load_configuration(self, profile_name: str) -> TestConfiguration:
        """
        Load test configuration from repository

        Args:
            profile_name: Name of the configuration profile to load

        Returns:
            TestConfiguration

        Raises:
            ConfigurationNotFoundError: If profile doesn't exist
            RepositoryAccessError: If loading fails
        """
        logger.debug(f"Loading configuration from profile: '{profile_name}'")

        try:
            test_config = await self._configuration.load_profile(profile_name)

            logger.debug(f"Configuration loaded successfully from '{profile_name}.yaml'")
            return test_config

        except FileNotFoundError as e:
            available_profiles = await self.list_available_profiles()
            raise ConfigurationNotFoundError(profile_name, available_profiles) from e
        except Exception as e:
            logger.error(f"Failed to load configurations from profile '{profile_name}': {e}")
            raise RepositoryAccessError(
                operation="load_configuration",
                reason=str(e),
                file_path=f"{profile_name}.yaml",
            ) from e

    async def load_hardware_config(self) -> HardwareConfiguration:
        """
        Load hardware configuration

        Returns:
            HardwareConfiguration object containing the loaded hardware settings

        Raises:
            RepositoryAccessError: If hardware configuration loading fails
        """
        try:
            return await self._configuration.load_hardware_config()
        except Exception as e:
            logger.error(f"Failed to load hardware configuration: {e}")
            raise RepositoryAccessError(
                operation="load_hardware_config",
                reason=str(e),
                file_path="hardware_configuration.yaml",
            ) from e

    async def list_available_profiles(self) -> List[str]:
        """
        Get list of available configuration profiles

        Returns:
            List of available profile names
        """
        return await self._configuration.list_available_profiles()

    async def get_active_profile_name(self) -> str:
        """
        Get the profile name that should be used, following business priority rules

        Priority:
        1. Last used profile (if available)
        2. Default fallback

        Returns:
            Profile name to use for configuration loading
        """
        fallback_profile = "default"

        try:
            # 1st priority: Last used profile from repository
            last_used = (
                await self._profile_preference.load_last_used_profile()
                if self._profile_preference
                else None
            )
            if last_used and self._is_valid_profile_name(last_used):
                logger.debug(f"Using last used profile: '{last_used}'")
                return last_used

            # 2nd priority: Default fallback
            logger.debug(f"Using fallback profile: '{fallback_profile}'")
            return fallback_profile

        except Exception as e:
            logger.warning(f"Error determining active profile, using fallback: {e}")
            return fallback_profile

    async def mark_profile_as_used(self, profile_name: str) -> None:
        """
        Mark a profile as used, updating last used and history

        Args:
            profile_name: Name of the profile that was used
        """
        if not profile_name or not self._is_valid_profile_name(profile_name):
            logger.warning(f"Invalid profile name for usage tracking: '{profile_name}'")
            return

        try:
            # Update last used profile
            if self._profile_preference:
                await self._profile_preference.save_last_used_profile(profile_name)

                # Update usage history
                await self._profile_preference.update_usage_history(profile_name)

            logger.debug(f"Marked profile as used: '{profile_name}'")

        except Exception as e:
            # Don't let preference saving break the main workflow
            logger.warning(f"Failed to mark profile '{profile_name}' as used: {e}")

    async def get_profile_usage_info(
        self,
    ) -> Dict[str, Any]:
        """
        Get comprehensive profile usage information

        Returns:
            Dictionary with current profile, usage history, and available profiles
        """
        try:
            current_profile = await self.get_active_profile_name()
            last_used = (
                await self._profile_preference.load_last_used_profile()
                if self._profile_preference
                else None
            )
            history = (
                await self._profile_preference.get_usage_history()
                if self._profile_preference
                else []
            )
            available_profiles = await self._configuration.list_available_profiles()

            return {
                "current_profile": current_profile,
                "last_used_profile": last_used,
                "usage_history": history,
                "available_profiles": available_profiles,
                "history_count": len(history),
                "unique_profiles_used": len(set(history)) if history else 0,
                "repository_available": (
                    await self._profile_preference.is_available()
                    if self._profile_preference
                    else False
                ),
            }

        except Exception as e:
            logger.warning(f"Failed to get profile usage info: {e}")
            return {
                "current_profile": "default",
                "error": str(e),
            }

    async def clear_profile_preferences(self) -> None:
        """
        Clear profile preferences (reset to environment/default behavior)

        Raises:
            RepositoryAccessError: If clearing preferences fails
        """
        try:
            if self._profile_preference:
                await self._profile_preference.clear_preferences()
            logger.info(
                "All profile preferences cleared - will use environment variable or default"
            )
        except Exception as e:
            logger.error(f"Failed to clear profile preferences: {e}")
            raise RepositoryAccessError(
                operation="clear_profile_preferences",
                reason=str(e),
            ) from e

    def _is_valid_profile_name(self, profile_name: str) -> bool:
        """
        Validate profile name using basic business rules

        Args:
            profile_name: Profile name to validate

        Returns:
            True if profile name appears valid
        """
        if not profile_name or not isinstance(profile_name, str):
            return False

        # Basic validation - profile names should be reasonable
        if len(profile_name) > 100 or len(profile_name.strip()) == 0:
            return False

        # No path traversal or dangerous characters
        dangerous_chars = [
            "/",
            "\\",
            "..",
            "<",
            ">",
            "|",
            "*",
            "?",
            '"',
        ]
        if any(char in profile_name for char in dangerous_chars):
            return False

        return True

    async def load_dut_defaults(self, profile_name: Optional[str] = None) -> Dict[str, str]:
        """
        Load DUT default values from configuration file

        Args:
            profile_name: Specific profile to load, defaults to active profile from config

        Returns:
            Dictionary containing DUT default values

        Raises:
            ConfigurationNotFoundError: If DUT defaults file is not found
            RepositoryAccessError: If DUT defaults cannot be loaded
        """
        try:
            # Delegate to Configuration repository for file operations
            return await self._configuration.load_dut_defaults(profile_name)

        except Exception as e:
            logger.error(f"Unexpected error loading DUT defaults: {e}")
            raise RepositoryAccessError(
                operation="load_dut_defaults", reason=f"Failed to load DUT defaults: {str(e)}"
            ) from e
