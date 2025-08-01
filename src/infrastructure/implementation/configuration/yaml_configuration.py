"""
YAML Configuration

Concrete implementation of ConfigurationRepository using YAML files.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger

from application.interfaces.configuration.configuration import (
    Configuration,
)
from domain.exceptions.configuration_exceptions import (
    ConfigurationConflictException,
    ConfigurationException,
    ConfigurationFormatException,
    ConfigurationSecurityException,
    InvalidConfigurationException,
    MissingConfigurationException,
)
from domain.value_objects.hardware_configuration import (
    HardwareConfiguration,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
)


class YamlConfiguration(Configuration):
    """
    YAML-based implementation of ConfigurationRepository

    Repository for managing test configuration data stored as YAML files in the filesystem.
    Provides CRUD operations for configuration profiles with validation and backup support.
    """

    # Configuration constants
    DEFAULT_CONFIG_PATH = "configuration/test_profiles"
    HARDWARE_CONFIG_PATH = "configuration"
    HARDWARE_CONFIG_FILENAME = "hardware.yaml"
    YAML_FILE_EXTENSION = ".yaml"
    CONFIGURATION_VERSION = "1.0"
    YAML_INDENT_SIZE = 2
    FILE_ENCODING = "utf-8"

    # Protected profiles that cannot be deleted
    PROTECTED_PROFILES = ["default", "factory", "safety"]

    def __init__(
        self,
        config_path: str = DEFAULT_CONFIG_PATH,
    ):
        """
        Initialize YAML configuration service

        Args:
            config_path: Path to directory containing YAML configuration files
        """
        self._config_path = Path(config_path)
        self._cache: Dict[str, TestConfiguration] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

        # Ensure configuration directory exists
        self._config_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"YAML Configuration Service initialized with path: {self._config_path}")

    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """
        Load a configuration profile from YAML file.
        If file does not exist, creates it with default test configuration.

        Args:
            profile_name: Name of the configuration profile to load

        Returns:
            TestConfiguration object containing the loaded configuration

        Raises:
            ConfigurationFormatException: If YAML file is malformed
            InvalidConfigurationException: If configuration values are invalid
            ConfigurationException: If file operations fail
        """
        # Check cache first
        if profile_name in self._cache:
            logger.debug(f"Returning cached configuration for profile '{profile_name}'")
            return self._cache[profile_name]

        profile_file = self._config_path / f"{profile_name}{self.YAML_FILE_EXTENSION}"

        # If file doesn't exist, create it with default test configuration
        if not profile_file.exists():
            logger.info(
                f"Profile file '{profile_name}.yaml' not found, creating with default test configuration"
            )
            await self._create_default_profile(profile_name)

        try:
            with open(profile_file, "r", encoding=self.FILE_ENCODING) as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)

            if yaml_data is None:
                raise ConfigurationFormatException(
                    parameter_name="profile_content",
                    invalid_format="empty_file",
                    expected_format="YAML configuration data",
                    config_source=str(profile_file),
                )

            # Create configuration object from structured YAML data
            config = TestConfiguration.from_structured_dict(yaml_data)

            # Cache the configuration
            self._cache[profile_name] = config

            logger.info(f"Successfully loaded configuration profile '{profile_name}'")
            return config

        except yaml.YAMLError as e:
            raise ConfigurationFormatException(
                parameter_name="yaml_syntax",
                invalid_format=str(e),
                expected_format="Valid YAML syntax",
                config_source=str(profile_file),
            ) from e
        except TypeError as e:
            raise InvalidConfigurationException(
                parameter_name="configuration_structure",
                invalid_value=str(e),
                validation_rule="TestConfiguration parameter requirements",
                config_source=str(profile_file),
            ) from e
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load configuration profile '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e

    async def load_hardware_config(
        self,
    ) -> HardwareConfiguration:
        """
        Load hardware configuration from fixed hardware.yaml file.
        If file does not exist, creates it with default hardware configuration.

        Returns:
            HardwareConfiguration object containing the loaded hardware settings

        Raises:
            ConfigurationFormatException: If YAML file is malformed
            InvalidConfigurationException: If hardware configuration values are invalid
            ConfigurationException: If file operations fail
        """
        hardware_file = Path(self.HARDWARE_CONFIG_PATH) / self.HARDWARE_CONFIG_FILENAME

        # If file doesn't exist, create it with default hardware configuration
        if not hardware_file.exists():
            logger.info(
                "Hardware file 'configuration/hardware.yaml' not found, creating with default hardware configuration"
            )
            await self._create_default_hardware_profile()

        try:
            with open(hardware_file, "r", encoding=self.FILE_ENCODING) as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)

            if yaml_data is None:
                raise ConfigurationFormatException(
                    parameter_name="hardware_content",
                    invalid_format="empty_file",
                    expected_format="YAML configuration data",
                    config_source=str(hardware_file),
                )

            # Extract hardware_config section
            if "hardware_config" not in yaml_data:
                # Return default hardware configuration if section not found
                logger.warning("No hardware_config section found in hardware.yaml, using defaults")
                return HardwareConfiguration()

            hardware_data = yaml_data["hardware_config"]

            # Create hardware configuration object
            hardware_config = HardwareConfiguration.from_dict(hardware_data)

            logger.info("Successfully loaded hardware configuration from hardware.yaml")
            return hardware_config

        except yaml.YAMLError as e:
            raise ConfigurationFormatException(
                parameter_name="yaml_syntax",
                invalid_format=str(e),
                expected_format="Valid YAML syntax",
                config_source=str(hardware_file),
            ) from e
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load hardware configuration from hardware.yaml: {str(e)}",
                config_source=str(hardware_file),
            ) from e

    async def validate_configuration(self, config: TestConfiguration) -> None:
        """
        Validate a configuration object against business rules

        Args:
            config: TestConfiguration to validate

        Raises:
            InvalidConfigurationException: If configuration is invalid
        """
        try:
            if not config.is_valid():
                # Get detailed validation errors
                errors = []
                try:
                    config.__post_init__()  # This will raise validation exceptions
                except Exception as e:
                    errors.append(str(e))

                raise InvalidConfigurationException(
                    parameter_name="test_configuration",
                    invalid_value="TestConfiguration object",
                    validation_rule=(
                        "; ".join(errors) if errors else "Configuration validation failed"
                    ),
                    config_source="validate_configuration",
                )
        except Exception as e:
            if isinstance(e, InvalidConfigurationException):
                raise
            logger.error(f"Configuration validation failed: {e}")
            raise InvalidConfigurationException(
                parameter_name="test_configuration",
                invalid_value="TestConfiguration object",
                validation_rule=str(e),
                config_source="validate_configuration",
            ) from e

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
        try:
            # Validate override values don't conflict with safety constraints
            self._validate_override_safety(base, override)

            # Create merged configuration
            merged_config = base.with_overrides(**override)

            # Validate merged configuration (will raise exception if invalid)
            await self.validate_configuration(merged_config)

            logger.debug(
                f"Successfully merged configuration with overrides: {list(override.keys())}"
            )
            return merged_config

        except Exception as e:
            if isinstance(
                e,
                (
                    InvalidConfigurationException,
                    ConfigurationConflictException,
                ),
            ):
                raise
            raise ConfigurationException(
                f"Failed to merge configurations: {str(e)}",
                config_source="merge_operation",
            ) from e

    def _validate_override_safety(
        self,
        base: TestConfiguration,
        override: Dict[str, Any],
    ) -> None:
        """
        Validate that override values don't violate safety constraints

        Args:
            base: Base configuration
            override: Override values to validate

        Raises:
            ConfigurationConflictException: If override values violate safety
        """
        safety_conflicts = {}

        # Check voltage safety
        if "voltage" in override and override["voltage"] > base.max_voltage:
            safety_conflicts["voltage"] = (
                f"Override voltage {override['voltage']} exceeds safety limit {base.max_voltage}"
            )

        # Check current safety
        if "current" in override and override["current"] > base.max_current:
            safety_conflicts["current"] = (
                f"Override current {override['current']} exceeds safety limit {base.max_current}"
            )

        # Temperature safety check removed - max_temperature no longer in TestConfiguration

        if safety_conflicts:
            raise ConfigurationConflictException(
                conflicting_parameters=safety_conflicts,
                conflict_description="Override values violate safety constraints",
                config_source="runtime_override",
            )

    async def list_available_profiles(self) -> List[str]:
        """
        List all available configuration profiles

        Returns:
            List of profile names that can be loaded
        """
        try:
            yaml_files = list(self._config_path.glob(f"*{self.YAML_FILE_EXTENSION}"))
            profiles = [f.stem for f in yaml_files if f.is_file()]

            # Filter out backup files
            profiles = [p for p in profiles if not p.startswith("backup_")]

            logger.debug(f"Found {len(profiles)} configuration profiles")
            return sorted(profiles)

        except Exception as e:
            logger.warning(f"Failed to list available profiles: {e}")
            return []

    async def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Get metadata information about a configuration profile

        Args:
            profile_name: Name of the configuration profile

        Returns:
            Dictionary containing profile metadata

        Raises:
            MissingConfigurationException: If profile does not exist
        """
        profile_file = self._config_path / f"{profile_name}{self.YAML_FILE_EXTENSION}"

        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file),
            )

        try:
            # Get file stats
            file_stats = profile_file.stat()

            # Load configuration to get computed info
            config = await self.load_profile(profile_name)

            return {
                "profile_name": profile_name,
                "file_path": str(profile_file),
                "file_size_bytes": file_stats.st_size,
                "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "measurement_points": config.get_total_measurement_points(),
                "estimated_duration_seconds": config.estimate_test_duration_seconds(),
                "temperature_count": config.get_temperature_count(),
                "position_count": config.get_position_count(),
                "is_valid": True,  # If we get here, validation passed
            }

        except Exception as e:
            raise ConfigurationException(
                f"Failed to get profile info for '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e

    async def save_profile(self, profile_name: str, config: TestConfiguration) -> None:
        """
        Save a configuration as a named profile

        Args:
            profile_name: Name for the new profile
            config: TestConfiguration to save

        Raises:
            InvalidConfigurationException: If configuration is invalid
        """
        # Validate configuration first (will raise exception if invalid)
        await self.validate_configuration(config)

        profile_file = self._config_path / f"{profile_name}{self.YAML_FILE_EXTENSION}"

        try:
            # Convert configuration to structured YAML format
            yaml_data = self._config_to_yaml_structure(config)

            # Add metadata
            yaml_data["metadata"] = {
                "profile_name": profile_name,
                "created_by": "YamlConfiguration",
                "created_time": datetime.now().isoformat(),
                "version": self.CONFIGURATION_VERSION,
            }

            # Write to file
            with open(profile_file, "w", encoding=self.FILE_ENCODING) as yaml_file:
                yaml.dump(
                    yaml_data,
                    yaml_file,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=self.YAML_INDENT_SIZE,
                )

            # Update cache
            self._cache[profile_name] = config

            logger.info(f"Successfully saved configuration profile '{profile_name}'")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to save profile '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e

    def _config_to_yaml_structure(self, config: TestConfiguration) -> Dict[str, Any]:
        """
        Convert TestConfiguration to structured YAML format

        Args:
            config: TestConfiguration to convert

        Returns:
            Dictionary in structured YAML format
        """
        return {
            "hardware": {
                "voltage": config.voltage,
                "current": config.current,
                "upper_temperature": config.upper_temperature,
                "fan_speed": config.fan_speed,
                "max_stroke": config.max_stroke,
                "initial_position": config.initial_position,
            },
            "test_parameters": {
                "temperature_list": config.temperature_list,
                "stroke_positions": config.stroke_positions,
            },
            "timing": {
                "stabilization_delay": config.stabilization_delay,
                "temperature_stabilization": config.temperature_stabilization,
                "power_stabilization": config.power_stabilization,
                "loadcell_zero_delay": config.loadcell_zero_delay,
            },
            "tolerances": {
                "measurement_tolerance": config.measurement_tolerance,
                "force_precision": config.force_precision,
                "temperature_precision": config.temperature_precision,
            },
            "execution": {
                "retry_attempts": config.retry_attempts,
                "timeout_seconds": config.timeout_seconds,
            },
            "safety": {
                "max_voltage": config.max_voltage,
                "max_current": config.max_current,
            },
        }

    def _hardware_config_to_yaml_structure(
        self, hardware_config: HardwareConfiguration
    ) -> Dict[str, Any]:
        """
        Convert HardwareConfiguration to structured YAML format

        Args:
            hardware_config: HardwareConfiguration to convert

        Returns:
            Dictionary in structured YAML format for hardware_config section
        """
        return {
            "hardware_config": {
                "robot": {
                    "model": hardware_config.robot.model,
                    "irq_no": hardware_config.robot.irq_no,
                },
                "loadcell": {
                    "model": hardware_config.loadcell.model,
                    "port": hardware_config.loadcell.port,
                    "baudrate": hardware_config.loadcell.baudrate,
                    "timeout": hardware_config.loadcell.timeout,
                    "bytesize": hardware_config.loadcell.bytesize,
                    "stopbits": hardware_config.loadcell.stopbits,
                    "parity": hardware_config.loadcell.parity,
                    "indicator_id": hardware_config.loadcell.indicator_id,
                },
                "mcu": {
                    "model": hardware_config.mcu.model,
                    "port": hardware_config.mcu.port,
                    "baudrate": hardware_config.mcu.baudrate,
                    "timeout": hardware_config.mcu.timeout,
                    "bytesize": hardware_config.mcu.bytesize,
                    "stopbits": hardware_config.mcu.stopbits,
                    "parity": hardware_config.mcu.parity,
                },
                "power": {
                    "model": hardware_config.power.model,
                    "host": hardware_config.power.host,
                    "port": hardware_config.power.port,
                    "timeout": hardware_config.power.timeout,
                    "channel": hardware_config.power.channel,
                },
                "digital_input": {
                    "model": hardware_config.digital_input.model,
                    "board_no": hardware_config.digital_input.board_no,
                    "input_count": hardware_config.digital_input.input_count,
                    "debounce_time": hardware_config.digital_input.debounce_time,
                },
            }
        }

    async def delete_profile(self, profile_name: str) -> None:
        """
        Delete a configuration profile

        Args:
            profile_name: Name of the profile to delete

        Raises:
            MissingConfigurationException: If profile does not exist
            ConfigurationSecurityException: If profile is protected
        """
        profile_file = self._config_path / f"{profile_name}{self.YAML_FILE_EXTENSION}"

        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file),
            )

        # Check if profile is protected (default profiles)
        if profile_name in self.PROTECTED_PROFILES:
            raise ConfigurationSecurityException(
                security_violation=f"Cannot delete protected profile '{profile_name}'",
                affected_parameters=[profile_name],
                risk_level="medium",
                config_source=str(profile_file),
            )

        try:
            # Delete file
            profile_file.unlink()

            # Remove from cache
            if profile_name in self._cache:
                del self._cache[profile_name]

            logger.info(f"Successfully deleted configuration profile '{profile_name}'")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to delete profile '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e

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
        """
        # Load template configuration
        template_config = await self.load_profile(template_name)

        # Apply customizations if provided
        if customizations:
            new_config = await self.merge_configurations(template_config, customizations)
        else:
            new_config = template_config

        # Save as new profile
        await self.save_profile(new_profile_name, new_config)

        logger.info(f"Created profile '{new_profile_name}' from template '{template_name}'")
        return new_config

    async def get_default_configuration(
        self,
    ) -> TestConfiguration:
        """
        Get the default configuration

        Returns:
            TestConfiguration with default values
        """
        try:
            return await self.load_profile("default")
        except MissingConfigurationException:
            # Return built-in default if no default profile exists
            logger.info("No default profile found, returning built-in default configuration")
            return TestConfiguration()

    async def validate_profile_compatibility(
        self,
        profile_name: str,
        system_version: Optional[str] = None,
    ) -> Dict[str, Union[str, bool, List[str]]]:
        """
        Validate if a profile is compatible with current system

        Args:
            profile_name: Name of profile to check
            system_version: Optional system version to check against

        Returns:
            Dictionary with compatibility information and any issues
        """
        config = await self.load_profile(profile_name)

        compatibility: Dict[str, Union[str, bool, List[str]]] = {
            "profile_name": profile_name,
            "compatible": True,
            "issues": [],
            "warnings": [],
        }

        # Check if configuration is valid
        try:
            await self.validate_configuration(config)
        except InvalidConfigurationException as e:
            compatibility["compatible"] = False
            issues_list = compatibility["issues"]
            if isinstance(issues_list, list):
                issues_list.append(str(e))

        # Add system-specific compatibility checks here
        # For now, just basic validation

        return compatibility

    async def _create_default_hardware_profile(
        self,
    ) -> None:
        """
        Create default hardware.yaml file with default hardware configuration

        Raises:
            ConfigurationException: If file creation fails
        """
        hardware_file = Path(self.HARDWARE_CONFIG_PATH) / self.HARDWARE_CONFIG_FILENAME

        # Ensure configuration directory exists
        hardware_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Create default hardware configuration
            default_hardware_config = HardwareConfiguration()

            # Convert to YAML structure
            yaml_data = self._hardware_config_to_yaml_structure(default_hardware_config)

            # Add metadata
            yaml_data["metadata"] = {
                "description": "Auto-generated hardware configuration",
                "version": self.CONFIGURATION_VERSION,
                "created_by": "YamlConfiguration (auto-generated)",
                "created_time": datetime.now().isoformat(),
            }

            # Write to file
            with open(hardware_file, "w", encoding=self.FILE_ENCODING) as yaml_file:
                yaml.dump(
                    yaml_data,
                    yaml_file,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=self.YAML_INDENT_SIZE,
                )

            logger.info("Successfully created default hardware.yaml")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to create default hardware.yaml: {str(e)}",
                config_source=str(hardware_file),
            ) from e

    async def _create_default_profile(self, profile_name: str) -> None:
        """
        Create a new profile with default test configuration

        Args:
            profile_name: Name for the new profile

        Raises:
            ConfigurationException: If file creation fails
        """
        profile_file = self._config_path / f"{profile_name}{self.YAML_FILE_EXTENSION}"

        try:
            # Create default test configuration
            default_test_config = TestConfiguration()

            # Convert to YAML structure
            yaml_data = self._config_to_yaml_structure(default_test_config)

            # Add metadata
            yaml_data["metadata"] = {
                "profile_name": profile_name,
                "description": f"Auto-generated test configuration profile for {profile_name}",
                "version": self.CONFIGURATION_VERSION,
                "created_by": "YamlConfiguration (auto-generated)",
                "created_time": datetime.now().isoformat(),
            }

            # Write to file
            with open(profile_file, "w", encoding=self.FILE_ENCODING) as yaml_file:
                yaml.dump(
                    yaml_data,
                    yaml_file,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=self.YAML_INDENT_SIZE,
                )

            logger.info(f"Successfully created default test profile '{profile_name}'")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to create default test profile '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e
