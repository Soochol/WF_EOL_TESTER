"""
JSON Configuration

Concrete implementation of Configuration interface using JSON files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast, Dict, List, Optional

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


class JsonConfiguration(Configuration):
    """
    JSON-based implementation of Configuration interface

    Repository for managing test configuration data stored as JSON files in the filesystem.
    Provides CRUD operations for configuration profiles with validation and backup support.
    """

    # Configuration constants
    DEFAULT_CONFIG_PATH = "config/test_profiles"
    HARDWARE_CONFIG_PATH = "configuration"
    HARDWARE_CONFIG_FILENAME = "hardware.json"
    JSON_FILE_EXTENSION = ".json"
    CONFIGURATION_VERSION = "1.0"
    JSON_INDENT_SIZE = 2
    FILE_ENCODING = "utf-8"

    # Protected profiles that cannot be deleted
    PROTECTED_PROFILES = ["default", "factory", "safety"]

    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        """
        Initialize JSON configuration service

        Args:
            config_path: Path to directory containing JSON configuration files
        """
        self._config_path = Path(config_path)
        self._cache: Dict[str, TestConfiguration] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}

        # Ensure configuration directory exists
        self._config_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"JSON Configuration Service initialized with path: {self._config_path}")

    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """
        Load a configuration profile from JSON file

        Args:
            profile_name: Name of the configuration profile to load

        Returns:
            TestConfiguration object containing the loaded configuration

        Raises:
            MissingConfigurationException: If profile file does not exist
            ConfigurationFormatException: If JSON file is malformed
            InvalidConfigurationException: If configuration values are invalid
        """
        # Check cache first
        if self._is_profile_cached(profile_name):
            return self._get_cached_profile(profile_name)

        profile_file = self._get_profile_file_path(profile_name)
        await self._validate_profile_exists(profile_file, profile_name)

        json_data = await self._load_json_from_file(profile_file)
        config = self._create_configuration_from_json(json_data)

        self._cache_configuration(profile_name, config)

        logger.info(f"Successfully loaded configuration profile '{profile_name}'")
        return config

    async def load_hardware_config(
        self,
    ) -> HardwareConfiguration:
        """
        Load hardware configuration from fixed hardware.json file.
        If file does not exist, creates it with default hardware configuration.

        Returns:
            HardwareConfiguration object containing the loaded hardware settings

        Raises:
            ConfigurationFormatException: If JSON file is malformed
            InvalidConfigurationException: If hardware configuration values are invalid
            ConfigurationException: If file operations fail
        """
        hardware_file = self._get_hardware_file_path()

        # Ensure hardware file exists
        await self._ensure_hardware_file_exists(hardware_file)

        json_data = await self._load_json_from_file(hardware_file)
        hardware_config = self._create_hardware_configuration_from_json(json_data, hardware_file)

        logger.info(
            f"Successfully loaded hardware configuration from {self.HARDWARE_CONFIG_FILENAME}"
        )
        return hardware_config

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

    # Helper methods for load_profile
    def _is_profile_cached(self, profile_name: str) -> bool:
        """Check if profile is already cached."""
        if profile_name in self._cache:
            logger.debug(f"Returning cached configuration for profile '{profile_name}'")
            return True
        return False

    def _get_cached_profile(self, profile_name: str) -> TestConfiguration:
        """Get cached profile configuration."""
        return self._cache[profile_name]

    def _get_profile_file_path(self, profile_name: str) -> Path:
        """Get file path for a profile."""
        return self._config_path / f"{profile_name}{self.JSON_FILE_EXTENSION}"

    async def _validate_profile_exists(self, profile_file: Path, profile_name: str) -> None:
        """Validate that profile file exists."""
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file),
                details={"available_profiles": await self.list_available_profiles()},
            )

    async def _load_json_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse JSON data from file."""
        try:
            with open(file_path, "r", encoding=self.FILE_ENCODING) as f:
                json_data = json.load(f)

            if json_data is None:
                raise ConfigurationFormatException(
                    parameter_name="file_content",
                    invalid_format="empty_file",
                    expected_format="JSON configuration data",
                    config_source=str(file_path),
                )

            return json_data

        except json.JSONDecodeError as e:
            raise ConfigurationFormatException(
                parameter_name="json_syntax",
                invalid_format=str(e),
                expected_format="Valid JSON syntax",
                config_source=str(file_path),
            ) from e

    def _create_configuration_from_json(self, json_data: Dict[str, Any]) -> TestConfiguration:
        """Create TestConfiguration object from JSON data."""
        try:
            return TestConfiguration.from_structured_dict(json_data)
        except TypeError as e:
            raise InvalidConfigurationException(
                parameter_name="configuration_structure",
                invalid_value=str(e),
                validation_rule="TestConfiguration parameter requirements",
                config_source="json_data",
            ) from e

    def _cache_configuration(self, profile_name: str, config: TestConfiguration) -> None:
        """Cache the configuration for future use."""
        self._cache[profile_name] = config

    # Helper methods for load_hardware_config
    def _get_hardware_file_path(self) -> Path:
        """Get hardware configuration file path."""
        return Path(self.HARDWARE_CONFIG_PATH) / self.HARDWARE_CONFIG_FILENAME

    async def _ensure_hardware_file_exists(self, hardware_file: Path) -> None:
        """Ensure hardware configuration file exists, create if missing."""
        if not hardware_file.exists():
            logger.info(
                f"Hardware file '{self.HARDWARE_CONFIG_PATH}/{self.HARDWARE_CONFIG_FILENAME}' not found, creating with default hardware configuration"
            )
            await self._create_default_hardware_profile()

    def _create_hardware_configuration_from_json(
        self, json_data: Dict[str, Any], hardware_file: Path
    ) -> HardwareConfiguration:
        """Create HardwareConfiguration object from JSON data."""
        # Extract hardware_config section
        if "hardware_config" not in json_data:
            # Return default hardware configuration if section not found
            logger.warning(
                f"No hardware_config section found in {self.HARDWARE_CONFIG_FILENAME}, using defaults"
            )
            return HardwareConfiguration()

        hardware_data = json_data["hardware_config"]
        return HardwareConfiguration.from_dict(hardware_data)

    # Helper methods for get_profile_info
    def _get_file_statistics(self, file_path: Path) -> Dict[str, Any]:
        """Get file statistics for profile info."""
        file_stats = file_path.stat()
        return {
            "file_size_bytes": file_stats.st_size,
            "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
        }

    def _analyze_configuration(self, config: TestConfiguration) -> Dict[str, Any]:
        """Analyze configuration to extract metadata."""
        return {
            "measurement_points": config.get_total_measurement_points(),
            "estimated_duration_seconds": config.estimate_test_duration_seconds(),
            "temperature_count": config.get_temperature_count(),
            "position_count": config.get_position_count(),
            "is_valid": True,  # If we get here, validation passed
        }

    def _build_profile_info_response(
        self,
        profile_name: str,
        profile_file: Path,
        file_stats: Dict[str, Any],
        config_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build complete profile info response."""
        return {
            "profile_name": profile_name,
            "file_path": str(profile_file),
            **file_stats,
            **config_analysis,
        }

    # Helper methods for save_profile
    def _prepare_profile_json_structure(
        self, profile_name: str, config: TestConfiguration
    ) -> Dict[str, Any]:
        """Prepare JSON structure for saving profile."""
        json_data = self._config_to_json_structure(config)

        # Add metadata
        json_data["metadata"] = {
            "profile_name": profile_name,
            "created_by": "JsonConfiguration",
            "created_time": datetime.now().isoformat(),
            "version": self.CONFIGURATION_VERSION,
        }

        return json_data

    async def _write_json_to_file(self, file_path: Path, json_data: Dict[str, Any]) -> None:
        """Write JSON data to file."""
        with open(file_path, "w", encoding=self.FILE_ENCODING) as f:
            json.dump(
                json_data,
                f,
                indent=self.JSON_INDENT_SIZE,
                ensure_ascii=False,
            )

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
            json_files = list(self._config_path.glob(f"*{self.JSON_FILE_EXTENSION}"))
            profiles = [f.stem for f in json_files if f.is_file()]

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
        profile_file = self._get_profile_file_path(profile_name)
        await self._validate_profile_exists(profile_file, profile_name)

        try:
            file_stats = self._get_file_statistics(profile_file)
            config = await self.load_profile(profile_name)
            config_analysis = self._analyze_configuration(config)

            return self._build_profile_info_response(
                profile_name, profile_file, file_stats, config_analysis
            )

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

        profile_file = self._get_profile_file_path(profile_name)

        try:
            json_structure = self._prepare_profile_json_structure(profile_name, config)
            await self._write_json_to_file(profile_file, json_structure)
            self._cache_configuration(profile_name, config)

            logger.info(f"Successfully saved configuration profile '{profile_name}'")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to save profile '{profile_name}': {str(e)}",
                config_source=str(profile_file),
            ) from e

    def _config_to_json_structure(self, config: TestConfiguration) -> Dict[str, Any]:
        """
        Convert TestConfiguration to structured JSON format

        Args:
            config: TestConfiguration to convert

        Returns:
            Dictionary in structured JSON format
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

    async def delete_profile(self, profile_name: str) -> None:
        """
        Delete a configuration profile

        Args:
            profile_name: Name of the profile to delete

        Raises:
            MissingConfigurationException: If profile does not exist
            ConfigurationSecurityException: If profile is protected
        """
        profile_file = self._config_path / f"{profile_name}{self.JSON_FILE_EXTENSION}"

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
    ) -> Dict[str, Any]:
        """
        Validate if a profile is compatible with current system

        Args:
            profile_name: Name of profile to check
            system_version: Optional system version to check against

        Returns:
            Dictionary with compatibility information and any issues
        """
        config = await self.load_profile(profile_name)

        compatibility = {
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
            cast(List[str], compatibility["issues"]).append(str(e))

        # Add system-specific compatibility checks here
        # For now, just basic validation

        return compatibility

    async def _create_default_hardware_profile(
        self,
    ) -> None:
        """
        Create default hardware.json file with default hardware configuration

        Raises:
            ConfigurationException: If file creation fails
        """
        hardware_file = Path(self.HARDWARE_CONFIG_PATH) / self.HARDWARE_CONFIG_FILENAME

        # Ensure configuration directory exists
        hardware_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Create default hardware configuration
            default_hardware_config = HardwareConfiguration()

            # Convert to JSON structure
            json_data = self._hardware_config_to_json_structure(default_hardware_config)

            # Add metadata
            json_data["metadata"] = {
                "description": "Auto-generated hardware configuration",
                "version": self.CONFIGURATION_VERSION,
                "created_by": "JsonConfiguration (auto-generated)",
                "created_time": datetime.now().isoformat(),
            }

            # Write to file
            with open(hardware_file, "w", encoding=self.FILE_ENCODING) as f:
                json.dump(
                    json_data,
                    f,
                    indent=self.JSON_INDENT_SIZE,
                    ensure_ascii=False,
                )

            logger.info(f"Successfully created default {self.HARDWARE_CONFIG_FILENAME}")

        except Exception as e:
            raise ConfigurationException(
                f"Failed to create default {self.HARDWARE_CONFIG_FILENAME}: {str(e)}",
                config_source=str(hardware_file),
            ) from e

    def _hardware_config_to_json_structure(
        self, hardware_config: HardwareConfiguration
    ) -> Dict[str, Any]:
        """
        Convert HardwareConfiguration to structured JSON format

        Args:
            hardware_config: HardwareConfiguration to convert

        Returns:
            Dictionary in structured JSON format for hardware_config section
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
                    "indicator_id": hardware_config.loadcell.indicator_id,
                },
                "mcu": {
                    "model": hardware_config.mcu.model,
                    "port": hardware_config.mcu.port,
                    "baudrate": hardware_config.mcu.baudrate,
                    "timeout": hardware_config.mcu.timeout,
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
