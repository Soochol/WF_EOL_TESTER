"""
Configuration Interface

Abstract interface for configuration management in the application layer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.hardware_configuration import HardwareConfiguration


class Configuration(ABC):
    """
    Abstract interface for configuration data persistence

    This repository interface defines the contract for loading, saving, and managing
    test configuration data from various storage sources (YAML, JSON, database, etc.).
    Follows the Repository pattern to abstract away storage implementation details.
    """

    @abstractmethod
    async def load_profile(self, profile_name: str) -> TestConfiguration:
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
        pass

    @abstractmethod
    async def load_hardware_config(self, profile_name: str) -> HardwareConfiguration:
        """
        Load hardware configuration from a profile

        Args:
            profile_name: Name of the configuration profile to load hardware config from

        Returns:
            HardwareConfiguration object containing the loaded hardware settings

        Raises:
            ConfigurationException: If hardware config cannot be loaded or is invalid
            MissingConfigurationException: If profile does not exist
            InvalidConfigurationException: If hardware config contains invalid values
        """
        pass

    @abstractmethod
    async def validate_configuration(self, config: TestConfiguration) -> None:
        """
        Validate a configuration object against business rules

        Args:
            config: TestConfiguration to validate

        Raises:
            ConfigurationValidationError: If configuration contains validation errors
            InvalidConfigurationException: If configuration contains invalid values
        """
        pass

    @abstractmethod
    async def merge_configurations(
        self,
        base: TestConfiguration,
        override: Dict[str, Any]
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
        pass

    @abstractmethod
    async def list_available_profiles(self) -> List[str]:
        """
        List all available configuration profiles

        Returns:
            List of profile names that can be loaded
        """
        pass

    @abstractmethod
    async def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Get metadata information about a configuration profile

        Args:
            profile_name: Name of the configuration profile

        Returns:
            Dictionary containing profile metadata (description, version, etc.)

        Raises:
            MissingConfigurationException: If profile does not exist
        """
        pass

    @abstractmethod
    async def save_profile(self, profile_name: str, config: TestConfiguration) -> None:
        """
        Save a configuration as a named profile

        Args:
            profile_name: Name for the new profile
            config: TestConfiguration to save

        Raises:
            InvalidConfigurationException: If configuration is invalid
            ConfigurationException: If profile cannot be saved
        """
        pass

    @abstractmethod
    async def delete_profile(self, profile_name: str) -> None:
        """
        Delete a configuration profile

        Args:
            profile_name: Name of the profile to delete

        Raises:
            MissingConfigurationException: If profile does not exist
            ConfigurationSecurityException: If profile cannot be deleted (e.g., protected)
        """
        pass

    @abstractmethod
    async def create_profile_from_template(
        self,
        template_name: str,
        new_profile_name: str,
        customizations: Dict[str, Any] = None
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
        pass

    @abstractmethod
    async def backup_profile(self, profile_name: str, backup_name: str = None) -> str:
        """
        Create a backup of a configuration profile

        Args:
            profile_name: Name of the profile to backup
            backup_name: Optional name for backup (auto-generated if not provided)

        Returns:
            Name of the created backup

        Raises:
            MissingConfigurationException: If profile does not exist
            ConfigurationException: If backup cannot be created
        """
        pass

    @abstractmethod
    async def restore_profile(self, backup_name: str, target_profile_name: str) -> None:
        """
        Restore a configuration profile from backup

        Args:
            backup_name: Name of the backup to restore from
            target_profile_name: Name of the profile to restore to

        Raises:
            MissingConfigurationException: If backup does not exist
            ConfigurationException: If restore operation fails
        """
        pass

    @abstractmethod
    async def compare_profiles(
        self,
        profile1_name: str,
        profile2_name: str
    ) -> Dict[str, Any]:
        """
        Compare two configuration profiles and return differences

        Args:
            profile1_name: Name of first profile
            profile2_name: Name of second profile

        Returns:
            Dictionary containing differences between profiles

        Raises:
            MissingConfigurationException: If either profile does not exist
        """
        pass

    @abstractmethod
    async def get_default_configuration(self) -> TestConfiguration:
        """
        Get the default configuration

        Returns:
            TestConfiguration with default values
        """
        pass

    @abstractmethod
    async def validate_profile_compatibility(
        self,
        profile_name: str,
        system_version: str = None
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
        pass
