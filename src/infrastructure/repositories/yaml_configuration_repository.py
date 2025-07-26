"""
YAML Configuration Repository

Concrete implementation of ConfigurationRepository using YAML files.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
from loguru import logger

from application.interfaces.configuration_repository import ConfigurationRepository
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.exceptions.configuration_exceptions import (
    ConfigurationException, InvalidConfigurationException, 
    MissingConfigurationException, ConfigurationConflictException,
    ConfigurationSecurityException, ConfigurationFormatException
)


class YamlConfigurationRepository(ConfigurationRepository):
    """
    YAML-based implementation of ConfigurationRepository
    
    Repository for managing test configuration data stored as YAML files in the filesystem.
    Provides CRUD operations for configuration profiles with validation and backup support.
    """
    
    def __init__(self, config_path: str = "config/test_profiles"):
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
        
        # Create backup directory
        self._backup_path = self._config_path / "backups"
        self._backup_path.mkdir(exist_ok=True)
        
        logger.info(f"YAML Configuration Service initialized with path: {self._config_path}")
    
    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """
        Load a configuration profile from YAML file
        
        Args:
            profile_name: Name of the configuration profile to load
            
        Returns:
            TestConfiguration object containing the loaded configuration
            
        Raises:
            MissingConfigurationException: If profile file does not exist
            ConfigurationFormatException: If YAML file is malformed
            InvalidConfigurationException: If configuration values are invalid
        """
        # Check cache first
        if profile_name in self._cache:
            logger.debug(f"Returning cached configuration for profile '{profile_name}'")
            return self._cache[profile_name]
        
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file),
                details={"available_profiles": await self.list_available_profiles()}
            )
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                raise ConfigurationFormatException(
                    parameter_name="profile_content",
                    invalid_format="empty_file",
                    expected_format="YAML configuration data",
                    config_source=str(profile_file)
                )
            
            # Flatten nested YAML structure for TestConfiguration
            flattened_data = self._flatten_yaml_data(yaml_data)
            
            # Create configuration object
            config = TestConfiguration(**flattened_data)
            
            # Cache the configuration
            self._cache[profile_name] = config
            
            logger.info(f"Successfully loaded configuration profile '{profile_name}'")
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationFormatException(
                parameter_name="yaml_syntax",
                invalid_format=str(e),
                expected_format="Valid YAML syntax",
                config_source=str(profile_file)
            )
        except TypeError as e:
            raise InvalidConfigurationException(
                parameter_name="configuration_structure",
                invalid_value=str(e),
                validation_rule="TestConfiguration parameter requirements",
                config_source=str(profile_file)
            )
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load configuration profile '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
    async def load_hardware_config(self, profile_name: str) -> HardwareConfiguration:
        """
        Load hardware configuration from YAML file
        
        Args:
            profile_name: Name of the configuration profile to load
            
        Returns:
            HardwareConfiguration object containing the loaded hardware settings
            
        Raises:
            MissingConfigurationException: If profile file does not exist
            ConfigurationFormatException: If YAML file is malformed
            InvalidConfigurationException: If hardware configuration values are invalid
        """
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file),
                details={"available_profiles": await self.list_available_profiles()}
            )
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                raise ConfigurationFormatException(
                    parameter_name="profile_content",
                    invalid_format="empty_file",
                    expected_format="YAML configuration data",
                    config_source=str(profile_file)
                )
            
            # Extract hardware_config section
            if 'hardware_config' not in yaml_data:
                # Return default hardware configuration if section not found
                logger.warning(f"No hardware_config section found in {profile_name}, using defaults")
                return HardwareConfiguration()
            
            hardware_data = yaml_data['hardware_config']
            
            # Create hardware configuration object
            hardware_config = HardwareConfiguration.from_dict(hardware_data)
            
            logger.info(f"Successfully loaded hardware configuration from profile '{profile_name}'")
            return hardware_config
            
        except yaml.YAMLError as e:
            raise ConfigurationFormatException(
                parameter_name="yaml_syntax",
                invalid_format=str(e),
                expected_format="Valid YAML syntax",
                config_source=str(profile_file)
            )
        except Exception as e:
            raise ConfigurationException(
                f"Failed to load hardware configuration from profile '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
    def _flatten_yaml_data(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested YAML structure to match TestConfiguration parameters
        
        Args:
            yaml_data: Nested YAML data dictionary
            
        Returns:
            Flattened dictionary suitable for TestConfiguration
        """
        flattened = {}
        
        # Hardware section
        if 'hardware' in yaml_data:
            hardware = yaml_data['hardware']
            flattened.update({
                'voltage': hardware.get('voltage', 18.0),
                'current': hardware.get('current', 20.0),
                'upper_temperature': hardware.get('upper_temperature', 80.0),
                'fan_speed': hardware.get('fan_speed', 10),
                'max_stroke': hardware.get('max_stroke', 240.0),
                'initial_position': hardware.get('initial_position', 10.0)
            })
        
        # Test parameters section
        if 'test_parameters' in yaml_data:
            test_params = yaml_data['test_parameters']
            flattened.update({
                'temperature_list': test_params.get('temperature_list', [25.0, 30.0, 35.0, 40.0, 45.0, 50.0]),
                'stroke_positions': test_params.get('stroke_positions', [10.0, 60.0, 100.0, 140.0, 180.0, 220.0, 240.0]),
                'standby_position': test_params.get('standby_position', 10.0)
            })
        
        # Timing section
        if 'timing' in yaml_data:
            timing = yaml_data['timing']
            flattened.update({
                'stabilization_delay': timing.get('stabilization_delay', 0.5),
                'temperature_stabilization': timing.get('temperature_stabilization', 1.0),
                'power_stabilization': timing.get('power_stabilization', 0.5),
                'loadcell_zero_delay': timing.get('loadcell_zero_delay', 0.1)
            })
        
        # Tolerances section
        if 'tolerances' in yaml_data:
            tolerances = yaml_data['tolerances']
            flattened.update({
                'measurement_tolerance': tolerances.get('measurement_tolerance', 0.001),
                'force_precision': tolerances.get('force_precision', 2),
                'temperature_precision': tolerances.get('temperature_precision', 1)
            })
        
        # Execution section
        if 'execution' in yaml_data:
            execution = yaml_data['execution']
            flattened.update({
                'retry_attempts': execution.get('retry_attempts', 3),
                'timeout_seconds': execution.get('timeout_seconds', 300.0)
            })
        
        # Safety section
        if 'safety' in yaml_data:
            safety = yaml_data['safety']
            flattened.update({
                'max_temperature': safety.get('max_temperature', 100.0),
                'max_force': safety.get('max_force', 1000.0),
                'max_voltage': safety.get('max_voltage', 30.0),
                'max_current': safety.get('max_current', 50.0)
            })
        
        # Pass criteria section
        if 'pass_criteria' in yaml_data:
            pass_criteria = yaml_data['pass_criteria']
            
            # Convert spec_points from list format to tuple format
            spec_points = pass_criteria.get('spec_points', [])
            if spec_points:
                # Convert each spec point from list to tuple
                spec_points_tuples = [tuple(point) if isinstance(point, list) else point for point in spec_points]
            else:
                spec_points_tuples = []
            
            # Create pass_criteria dictionary for PassCriteria.from_dict()
            pass_criteria_dict = {
                'force_limit_min': pass_criteria.get('force_limit_min', 0.0),
                'force_limit_max': pass_criteria.get('force_limit_max', 100.0),
                'temperature_limit_min': pass_criteria.get('temperature_limit_min', -10.0),
                'temperature_limit_max': pass_criteria.get('temperature_limit_max', 80.0),
                'spec_points': spec_points_tuples,
                'measurement_tolerance': pass_criteria.get('measurement_tolerance', 0.001),
                'force_precision': pass_criteria.get('force_precision', 2),
                'temperature_precision': pass_criteria.get('temperature_precision', 1),
                'position_tolerance': pass_criteria.get('position_tolerance', 0.5),
                'max_test_duration': pass_criteria.get('max_test_duration', 300.0),
                'min_stabilization_time': pass_criteria.get('min_stabilization_time', 0.5)
            }
            
            flattened['pass_criteria'] = pass_criteria_dict
        
        # Handle direct top-level parameters (backward compatibility)
        for key, value in yaml_data.items():
            if key not in ['hardware', 'test_parameters', 'timing', 'tolerances', 'execution', 'safety', 'pass_criteria', 'hardware_config']:
                flattened[key] = value
        
        return flattened
    
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
                    validation_rule="; ".join(errors) if errors else "Configuration validation failed",
                    config_source="validate_configuration"
                )
        except Exception as e:
            if isinstance(e, InvalidConfigurationException):
                raise
            logger.error(f"Configuration validation failed: {e}")
            raise InvalidConfigurationException(
                parameter_name="test_configuration",
                invalid_value="TestConfiguration object",
                validation_rule=str(e),
                config_source="validate_configuration"
            )
    
    
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
        try:
            # Validate override values don't conflict with safety constraints
            self._validate_override_safety(base, override)
            
            # Create merged configuration
            merged_config = base.with_overrides(**override)
            
            # Validate merged configuration (will raise exception if invalid)
            await self.validate_configuration(merged_config)
            
            logger.debug(f"Successfully merged configuration with overrides: {list(override.keys())}")
            return merged_config
            
        except Exception as e:
            if isinstance(e, (InvalidConfigurationException, ConfigurationConflictException)):
                raise
            raise ConfigurationException(
                f"Failed to merge configurations: {str(e)}",
                config_source="merge_operation"
            )
    
    def _validate_override_safety(self, base: TestConfiguration, override: Dict[str, Any]) -> None:
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
        if 'voltage' in override and override['voltage'] > base.max_voltage:
            safety_conflicts['voltage'] = f"Override voltage {override['voltage']} exceeds safety limit {base.max_voltage}"
        
        # Check current safety
        if 'current' in override and override['current'] > base.max_current:
            safety_conflicts['current'] = f"Override current {override['current']} exceeds safety limit {base.max_current}"
        
        # Check temperature safety
        if 'upper_temperature' in override and override['upper_temperature'] > base.max_temperature:
            safety_conflicts['upper_temperature'] = f"Override temperature {override['upper_temperature']} exceeds safety limit {base.max_temperature}"
        
        if safety_conflicts:
            raise ConfigurationConflictException(
                conflicting_parameters=safety_conflicts,
                conflict_description="Override values violate safety constraints",
                config_source="runtime_override"
            )
    
    async def list_available_profiles(self) -> List[str]:
        """
        List all available configuration profiles
        
        Returns:
            List of profile names that can be loaded
        """
        try:
            yaml_files = list(self._config_path.glob("*.yaml"))
            profiles = [f.stem for f in yaml_files if f.is_file()]
            
            # Filter out backup files
            profiles = [p for p in profiles if not p.startswith('backup_')]
            
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
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file)
            )
        
        try:
            # Get file stats
            stat = profile_file.stat()
            
            # Load configuration to get computed info
            config = await self.load_profile(profile_name)
            
            return {
                'profile_name': profile_name,
                'file_path': str(profile_file),
                'file_size_bytes': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'measurement_points': config.get_total_measurement_points(),
                'estimated_duration_seconds': config.estimate_test_duration_seconds(),
                'temperature_count': config.get_temperature_count(),
                'position_count': config.get_position_count(),
                'is_valid': True  # If we get here, validation passed
            }
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to get profile info for '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
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
        
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        try:
            # Convert configuration to structured YAML format
            yaml_data = self._config_to_yaml_structure(config)
            
            # Add metadata
            yaml_data['metadata'] = {
                'profile_name': profile_name,
                'created_by': 'YamlConfigurationRepository',
                'created_time': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Write to file
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False, indent=2)
            
            # Update cache
            self._cache[profile_name] = config
            
            logger.info(f"Successfully saved configuration profile '{profile_name}'")
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to save profile '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
    def _config_to_yaml_structure(self, config: TestConfiguration) -> Dict[str, Any]:
        """
        Convert TestConfiguration to structured YAML format
        
        Args:
            config: TestConfiguration to convert
            
        Returns:
            Dictionary in structured YAML format
        """
        return {
            'hardware': {
                'voltage': config.voltage,
                'current': config.current,
                'upper_temperature': config.upper_temperature,
                'fan_speed': config.fan_speed,
                'max_stroke': config.max_stroke,
                'initial_position': config.initial_position
            },
            'test_parameters': {
                'temperature_list': config.temperature_list,
                'stroke_positions': config.stroke_positions,
                'standby_position': config.standby_position
            },
            'timing': {
                'stabilization_delay': config.stabilization_delay,
                'temperature_stabilization': config.temperature_stabilization,
                'power_stabilization': config.power_stabilization,
                'loadcell_zero_delay': config.loadcell_zero_delay
            },
            'tolerances': {
                'measurement_tolerance': config.measurement_tolerance,
                'force_precision': config.force_precision,
                'temperature_precision': config.temperature_precision
            },
            'execution': {
                'retry_attempts': config.retry_attempts,
                'timeout_seconds': config.timeout_seconds
            },
            'safety': {
                'max_temperature': config.max_temperature,
                'max_force': config.max_force,
                'max_voltage': config.max_voltage,
                'max_current': config.max_current
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
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file)
            )
        
        # Check if profile is protected (default profiles)
        if profile_name in ['default', 'factory', 'safety']:
            raise ConfigurationSecurityException(
                security_violation=f"Cannot delete protected profile '{profile_name}'",
                affected_parameters=[profile_name],
                risk_level="medium",
                config_source=str(profile_file)
            )
        
        try:
            # Create backup before deletion
            await self.backup_profile(profile_name, f"before_delete_{profile_name}")
            
            # Delete file
            profile_file.unlink()
            
            # Remove from cache
            if profile_name in self._cache:
                del self._cache[profile_name]
            
            logger.info(f"Successfully deleted configuration profile '{profile_name}'")
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to delete profile '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
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
    
    async def backup_profile(self, profile_name: str, backup_name: str = None) -> str:
        """
        Create a backup of a configuration profile
        
        Args:
            profile_name: Name of the profile to backup
            backup_name: Optional name for backup (auto-generated if not provided)
            
        Returns:
            Name of the created backup
        """
        profile_file = self._config_path / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[profile_name],
                config_source=str(profile_file)
            )
        
        # Generate backup name if not provided
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{profile_name}_{timestamp}"
        
        backup_file = self._backup_path / f"{backup_name}.yaml"
        
        try:
            shutil.copy2(profile_file, backup_file)
            logger.info(f"Created backup '{backup_name}' for profile '{profile_name}'")
            return backup_name
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to create backup for profile '{profile_name}': {str(e)}",
                config_source=str(profile_file)
            )
    
    async def restore_profile(self, backup_name: str, target_profile_name: str) -> None:
        """
        Restore a configuration profile from backup
        
        Args:
            backup_name: Name of the backup to restore from
            target_profile_name: Name of the profile to restore to
        """
        backup_file = self._backup_path / f"{backup_name}.yaml"
        
        if not backup_file.exists():
            raise MissingConfigurationException(
                missing_parameters=[backup_name],
                config_source=str(backup_file)
            )
        
        target_file = self._config_path / f"{target_profile_name}.yaml"
        
        try:
            shutil.copy2(backup_file, target_file)
            
            # Clear cache for target profile
            if target_profile_name in self._cache:
                del self._cache[target_profile_name]
            
            logger.info(f"Restored profile '{target_profile_name}' from backup '{backup_name}'")
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to restore profile '{target_profile_name}' from backup '{backup_name}': {str(e)}",
                config_source=str(backup_file)
            )
    
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
        """
        config1 = await self.load_profile(profile1_name)
        config2 = await self.load_profile(profile2_name)
        
        config1_dict = config1.to_dict()
        config2_dict = config2.to_dict()
        
        differences = {}
        all_keys = set(config1_dict.keys()) | set(config2_dict.keys())
        
        for key in all_keys:
            val1 = config1_dict.get(key)
            val2 = config2_dict.get(key)
            
            if val1 != val2:
                differences[key] = {
                    'profile1': val1,
                    'profile2': val2,
                    'type': 'modified' if key in config1_dict and key in config2_dict else 
                           'only_in_profile1' if key in config1_dict else 'only_in_profile2'
                }
        
        return {
            'profile1_name': profile1_name,
            'profile2_name': profile2_name,
            'differences': differences,
            'identical': len(differences) == 0
        }
    
    async def get_default_configuration(self) -> TestConfiguration:
        """
        Get the default configuration
        
        Returns:
            TestConfiguration with default values
        """
        try:
            return await self.load_profile('default')
        except MissingConfigurationException:
            # Return built-in default if no default profile exists
            logger.info("No default profile found, returning built-in default configuration")
            return TestConfiguration()
    
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
        """
        config = await self.load_profile(profile_name)
        
        compatibility = {
            'profile_name': profile_name,
            'compatible': True,
            'issues': [],
            'warnings': []
        }
        
        # Check if configuration is valid
        try:
            await self.validate_configuration(config)
        except InvalidConfigurationException as e:
            compatibility['compatible'] = False
            compatibility['issues'].append(str(e))
        
        # Add system-specific compatibility checks here
        # For now, just basic validation
        
        return compatibility