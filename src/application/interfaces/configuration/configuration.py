"""
Configuration Interface

Abstract interface for configuration management in the application layer.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.value_objects.hardware_configuration import (
    HardwareConfiguration,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
)


class Configuration(ABC):
    """
    Abstract interface for configuration data persistence

    This repository interface defines the contract for loading, saving, and managing
    test configuration data from various storage sources (YAML, JSON, database, etc.).
    Follows the Repository pattern to abstract away storage implementation details.
    """

    @abstractmethod
    async def load_profile(
        self, profile_name: str
    ) -> TestConfiguration:
        """
        Load a configuration profile by name

        Args:
            profile_name: Name of the configuration profile to load

        Returns:
            TestConfiguration object containing the loaded configuration

        Raises:
            ConfigurationException: If profile cannot be loaded or is invalid
            MissingConfigurationException: If profile does not exist
            InvalidConfigurationException: If profile contains invalid values
        """
        ...

    @abstractmethod
    async def load_hardware_config(
        self,
    ) -> HardwareConfiguration:
        """
        Load hardware configuration from fixed hardware.yaml file

        Returns:
            HardwareConfiguration object containing the loaded hardware settings

        Raises:
            ConfigurationException: If hardware config cannot be loaded or is invalid
            InvalidConfigurationException: If hardware config contains invalid values
        """
        ...

    @abstractmethod
    async def validate_configuration(
        self, config: TestConfiguration
    ) -> None:
        """
        Validate a configuration object against business rules

        Args:
            config: TestConfiguration to validate

        Raises:
            ConfigurationValidationError: If configuration contains validation errors
            InvalidConfigurationException: If configuration contains invalid values
        """
        ...

    @abstractmethod
    async def merge_configurations(
        self,
        base: TestConfiguration,
        override: Dict[str, Any],
    ) -> TestConfiguration:
        """
        Merge base configuration with runtime overrides

        Args:
            base: Base TestConfiguration object
            override: Dictionary of values to override in base configuration

        Returns:
            New TestConfiguration with merged values

        Raises:
            InvalidConfigurationException: If merged configuration is invalid
            ConfigurationConflictException: If override values conflict with base
        """
        ...

    @abstractmethod
    async def list_available_profiles(self) -> List[str]:
        """
        List all available configuration profiles

        Returns:
            List of profile names that can be loaded
        """
        ...

    @abstractmethod
    async def get_profile_info(
        self, profile_name: str
    ) -> Dict[str, Any]:
        """
        Get metadata information about a configuration profile

        Args:
            profile_name: Name of the configuration profile

        Returns:
            Dictionary containing profile metadata (description, version, etc.)

        Raises:
            MissingConfigurationException: If profile does not exist
        """
        ...

    @abstractmethod
    async def save_profile(
        self, profile_name: str, config: TestConfiguration
    ) -> None:
        """
        Save a configuration as a named profile

        Args:
            profile_name: Name for the new profile
            config: TestConfiguration to save

        Raises:
            InvalidConfigurationException: If configuration is invalid
            ConfigurationException: If profile cannot be saved
        """
        ...

    @abstractmethod
    async def delete_profile(
        self, profile_name: str
    ) -> None:
        """
        Delete a configuration profile

        Args:
            profile_name: Name of the profile to delete

        Raises:
            MissingConfigurationException: If profile does not exist
            ConfigurationSecurityException: If profile cannot be deleted (e.g., protected)
        """
        ...

    @abstractmethod
    async def create_profile_from_template(
        self,
        template_name: str,
        new_profile_name: str,
        customizations: Optional[Dict[str, Any]] = None,
    ) -> TestConfiguration:
        """
        Create a new profile based on an existing template

        Args:
            template_name: Name of the template profile to use as base
            new_profile_name: Name for the new profile
            customizations: Optional customizations to apply to template

        Returns:
            TestConfiguration object for the new profile

        Raises:
            MissingConfigurationException: If template does not exist
            InvalidConfigurationException: If customizations create invalid config
        """
        ...

    @abstractmethod
    async def get_default_configuration(
        self,
    ) -> TestConfiguration:
        """
        Get the default configuration

        Returns:
            TestConfiguration with default values
        """
        ...

    @abstractmethod
    async def validate_profile_compatibility(
        self,
        profile_name: str,
        system_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate if a profile is compatible with current system

        Args:
            profile_name: Name of profile to check
            system_version: Optional system version to check against

        Returns:
            Dictionary with compatibility information and any issues

        Raises:
            MissingConfigurationException: If profile does not exist
        """
