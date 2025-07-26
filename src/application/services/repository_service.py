"""
Repository Service

Service layer that manages all repository operations and data persistence.
Uses Exception First principles for error handling.
"""

from typing import List, Dict, Any
from loguru import logger

from application.interfaces.test_repository import TestRepository
from application.interfaces.configuration_repository import ConfigurationRepository
from application.interfaces.profile_preference_repository import ProfilePreferenceRepository
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.exceptions import (
    RepositoryError,
    ConfigurationNotFoundError,
    RepositoryAccessError
)


class RepositoryService:
    """
    Service for managing repository operations
    
    This service centralizes all repository-related operations and provides
    a unified interface for data persistence across the application.
    """
    
    def __init__(
        self,
        test_repository: TestRepository,
        configuration_repository: ConfigurationRepository,
        profile_preference_repository: ProfilePreferenceRepository = None
    ):
        self._test_repository = test_repository
        self._configuration_repository = configuration_repository
        
        # ProfilePreferenceRepository - create default if not provided
        if profile_preference_repository:
            self._profile_preference_repository = profile_preference_repository
        else:
            # Create with default JSON repository if not provided
            from infrastructure.repositories.json_profile_preference_repository import JsonProfilePreferenceRepository
            self._profile_preference_repository = JsonProfilePreferenceRepository()
    
    @property
    def test_repository(self) -> TestRepository:
        """Get the test repository"""
        return self._test_repository
    
    @property
    def configuration_repository(self) -> ConfigurationRepository:
        """Get the configuration repository"""
        return self._configuration_repository
    
    @property
    def profile_preference_repository(self) -> ProfilePreferenceRepository:
        """Get the profile preference repository"""
        return self._profile_preference_repository
    
    async def load_configurations(
        self, 
        profile_name: str
    ) -> tuple[TestConfiguration, HardwareConfiguration]:
        """
        Load both test and hardware configurations from repository
        
        Args:
            profile_name: Name of the configuration profile to load
            
        Returns:
            Tuple of (TestConfiguration, HardwareConfiguration)
            
        Raises:
            ConfigurationNotFoundError: If profile doesn't exist
            RepositoryAccessError: If loading fails
        """
        logger.debug(f"Loading configurations from profile: '{profile_name}'")
        
        try:
            test_config = await self._configuration_repository.load_profile(profile_name)
            hardware_config = await self._configuration_repository.load_hardware_config(profile_name)
            
            logger.debug(f"Configurations loaded successfully from '{profile_name}.yaml'")
            return test_config, hardware_config
            
        except FileNotFoundError:
            available_profiles = await self.list_available_profiles()
            raise ConfigurationNotFoundError(profile_name, available_profiles)
        except Exception as e:
            logger.error(f"Failed to load configurations from profile '{profile_name}': {e}")
            raise RepositoryAccessError(
                operation="load_configurations",
                reason=str(e),
                file_path=f"{profile_name}.yaml"
            )
    
    async def list_available_profiles(self) -> List[str]:
        """
        Get list of available configuration profiles
        
        Returns:
            List of available profile names
        """
        return await self._configuration_repository.list_available_profiles()
    
    async def save_test_result(self, test_data: Dict[str, Any]) -> None:
        """
        Save test result to repository
        
        Args:
            test_data: Test result data to save
            
        Raises:
            RepositoryAccessError: If saving fails
        """
        try:
            await self._test_repository.save_test_result(test_data)
            logger.debug("Test result saved successfully")
        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
            raise RepositoryAccessError(
                operation="save_test_result",
                reason=str(e)
            )
    
    async def get_active_profile_name(self) -> str:
        """
        Get the profile name that should be used, following business priority rules
        
        Priority:
        1. Last used profile (if available)
        2. Default fallback
        
        Returns:
            Profile name to use for configuration loading
        """
        fallback_profile = 'default'
        
        try:
            # 1st priority: Last used profile from repository
            last_used = await self._profile_preference_repository.load_last_used_profile()
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
            await self._profile_preference_repository.save_last_used_profile(profile_name)
            
            # Update usage history  
            await self._profile_preference_repository.update_usage_history(profile_name)
            
            logger.debug(f"Marked profile as used: '{profile_name}'")
            
        except Exception as e:
            # Don't let preference saving break the main workflow
            logger.warning(f"Failed to mark profile '{profile_name}' as used: {e}")
    
    async def get_profile_usage_info(self) -> Dict[str, Any]:
        """
        Get comprehensive profile usage information
        
        Returns:
            Dictionary with current profile, usage history, and available profiles
        """
        try:
            current_profile = await self.get_active_profile_name()
            last_used = await self._profile_preference_repository.load_last_used_profile()
            history = await self._profile_preference_repository.get_usage_history()
            available_profiles = await self._configuration_repository.list_available_profiles()
            
            return {
                "current_profile": current_profile,
                "last_used_profile": last_used,  
                "usage_history": history,
                "available_profiles": available_profiles,
                "history_count": len(history),
                "unique_profiles_used": len(set(history)) if history else 0,
                "repository_available": await self._profile_preference_repository.is_available()
            }
            
        except Exception as e:
            logger.warning(f"Failed to get profile usage info: {e}")
            return {
                "current_profile": "default",
                "error": str(e)
            }
    
    async def clear_profile_preferences(self) -> None:
        """
        Clear profile preferences (reset to environment/default behavior)
        
        Raises:
            RepositoryAccessError: If clearing preferences fails
        """
        try:
            await self._profile_preference_repository.clear_preferences()
            logger.info("All profile preferences cleared - will use environment variable or default")
        except Exception as e:
            logger.error(f"Failed to clear profile preferences: {e}")
            raise RepositoryAccessError(
                operation="clear_profile_preferences",
                reason=str(e)
            )
    
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
        dangerous_chars = ['/', '\\', '..', '<', '>', '|', '*', '?', '"']
        if any(char in profile_name for char in dangerous_chars):
            return False
            
        return True
    
    def get_all_repositories(self) -> dict:
        """Get all repositories as a dictionary (for debugging/testing)"""
        return {
            'test_repository': self._test_repository,
            'configuration_repository': self._configuration_repository,
            'profile_preference_repository': self._profile_preference_repository
        }