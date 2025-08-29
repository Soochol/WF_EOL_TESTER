"""
Configuration Service

Service layer that manages configuration and profile preference operations.
Uses Exception First principles for error handling.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from application.interfaces.configuration.configuration import Configuration
from domain.exceptions import (
    ConfigurationNotFoundError,
    RepositoryAccessError,
)
from domain.value_objects.application_config import ApplicationConfig
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.test_configuration import (
    TestConfiguration,
)
from domain.value_objects.heating_cooling_configuration import HeatingCoolingConfiguration


class ConfigPaths:
    """Configuration file paths constants"""

    # Default configuration file paths
    DEFAULT_APPLICATION_CONFIG = "configuration/application.yaml"
    DEFAULT_HARDWARE_CONFIG = "configuration/hardware_config.yaml"

    # Default paths for repositories
    DEFAULT_PROFILE_PREFERENCE_PATH = "configuration/profile_preferences.json"
    DEFAULT_TEST_PROFILES_DIR = "configuration/test_profiles"
    DEFAULT_HEATING_COOLING_CONFIG = "configuration/heating_cooling_time_test.yaml"


class ConfigurationService:
    """
    Service for managing configuration and profile preference operations

    This service handles configuration loading, profile management, and user preferences.
    It coordinates between ConfigurationRepository and ProfilePreferenceRepository.
    """

    # ============================================================================
    # INITIALIZATION & PROPERTIES
    # ============================================================================

    def __init__(
        self,
        configuration: Optional[Configuration] = None,
    ):
        self._configuration = configuration
        self.application_config_path = ConfigPaths.DEFAULT_APPLICATION_CONFIG
        self.hardware_config_path = ConfigPaths.DEFAULT_HARDWARE_CONFIG

    @property
    def configuration(self) -> Optional[Configuration]:
        """Get the configuration"""
        return self._configuration

    # ============================================================================
    # CORE CONFIGURATION LOADING
    # ============================================================================

    async def load_test_config(self, profile_name: str) -> TestConfiguration:
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
        if not self._configuration:
            raise RepositoryAccessError(
                operation="load_test_config",
                reason="Configuration repository not available",
            )

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
                operation="load_test_config",
                reason=str(e),
                file_path=f"{profile_name}.yaml",
            ) from e

    async def load_hardware_config(self) -> HardwareConfig:
        """
        Load hardware configuration

        Returns:
            HardwareConfig object containing the loaded hardware settings

        Raises:
            RepositoryAccessError: If hardware configuration loading fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="load_hardware_config",
                reason="Configuration repository not available",
            )

        try:
            return await self._configuration.load_hardware_config()
        except Exception as e:
            logger.error(f"Failed to load hardware configuration: {e}")
            raise RepositoryAccessError(
                operation="load_hardware_config",
                reason=str(e),
                file_path="hardware_config.yaml",
            ) from e

    async def load_application_config(
        self, app_config_path: Optional[str] = None
    ) -> ApplicationConfig:
        """
        Load application configuration from file

        Args:
            app_config_path: Path to application configuration file

        Returns:
            ApplicationConfig object

        Raises:
            RepositoryAccessError: If loading fails
        """
        try:
            if app_config_path is None:
                app_config_path = ConfigPaths.DEFAULT_APPLICATION_CONFIG
            app_config_file = Path(app_config_path)

            if not app_config_file.exists():
                logger.warning(f"Application config not found: {app_config_path}")
                return ApplicationConfig()  # Return default

            with open(app_config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            return ApplicationConfig.from_dict(config_data)

        except Exception as e:
            logger.error(f"Failed to load application config from {app_config_path}: {e}")
            raise RepositoryAccessError(
                operation="load_application_config",
                reason=str(e),
                file_path=app_config_path,
            ) from e

    async def load_heating_cooling_config(
        self, config_path: Optional[str] = None
    ) -> HeatingCoolingConfiguration:
        """
        Load heating/cooling configuration from YAML file or create with defaults

        Args:
            config_path: Path to heating/cooling configuration file

        Returns:
            HeatingCoolingConfiguration object

        Raises:
            RepositoryAccessError: If loading fails after file creation attempt
        """
        try:
            if config_path is None:
                config_path = ConfigPaths.DEFAULT_HEATING_COOLING_CONFIG
            config_file = Path(config_path)

            # If file doesn't exist, create it with defaults
            if not config_file.exists():
                logger.info(f"Heating/cooling config not found: {config_path}")
                logger.info("Creating default heating/cooling configuration file...")
                
                # Create directory if it doesn't exist
                config_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create default configuration and write to file
                default_config = HeatingCoolingConfiguration()
                await self._create_default_heating_cooling_config_file(config_file, default_config)
                
                logger.info(f"Created default configuration file: {config_path}")
                return default_config

            # Load existing file
            logger.info(f"Loading heating/cooling configuration from {config_path}")
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            # Extract configuration parameters, using defaults for missing values
            config = HeatingCoolingConfiguration(
                repeat_count=yaml_data.get('repeat_count', 1),
                heating_wait_time=yaml_data.get('heating_wait_time', 2.0),
                cooling_wait_time=yaml_data.get('cooling_wait_time', 2.0),
                stabilization_wait_time=yaml_data.get('stabilization_wait_time', 1.0),
                power_monitoring_interval=yaml_data.get('power_monitoring_interval', 0.5),
                power_monitoring_enabled=yaml_data.get('power_monitoring_enabled', True),
                activation_temperature=yaml_data.get('activation_temperature', 52.0),
                standby_temperature=yaml_data.get('standby_temperature', 38.0),
                voltage=yaml_data.get('voltage', 38.0),
                current=yaml_data.get('current', 25.0),
                fan_speed=yaml_data.get('fan_speed', 10),
                upper_temperature=yaml_data.get('upper_temperature', 80.0),
                poweron_stabilization=yaml_data.get('poweron_stabilization', 0.5),
                mcu_boot_complete_stabilization=yaml_data.get('mcu_boot_complete_stabilization', 2.0),
                mcu_command_stabilization=yaml_data.get('mcu_command_stabilization', 0.1),
                mcu_temperature_stabilization=yaml_data.get('mcu_temperature_stabilization', 0.1),
                calculate_statistics=yaml_data.get('calculate_statistics', True),
                show_detailed_results=yaml_data.get('show_detailed_results', True)
            )
            
            logger.info("Heating/cooling configuration loaded successfully")
            return config

        except Exception as e:
            logger.error(f"Failed to load heating/cooling config from {config_path}: {e}")
            raise RepositoryAccessError(
                operation="load_heating_cooling_config",
                reason=str(e),
                file_path=config_path,
            ) from e

    async def _create_default_heating_cooling_config_file(
        self, config_file: Path, default_config: HeatingCoolingConfiguration
    ) -> None:
        """Create default heating/cooling configuration YAML file"""
        from datetime import datetime
        
        yaml_content = f"""# Heating/Cooling Time Test Configuration
# Configuration parameters for heating/cooling time test including
# wait times, power monitoring settings, and test execution parameters.

# ========================================================================
# TEST EXECUTION PARAMETERS
# ========================================================================
repeat_count: {default_config.repeat_count}  # Number of heating/cooling cycles to perform

# ========================================================================
# WAIT TIME PARAMETERS (in seconds)
# ========================================================================
heating_wait_time: {default_config.heating_wait_time}  # Wait time after heating completes
cooling_wait_time: {default_config.cooling_wait_time}  # Wait time after cooling completes  
stabilization_wait_time: {default_config.stabilization_wait_time}  # Wait time for temperature stabilization

# ========================================================================
# POWER MONITORING PARAMETERS
# ========================================================================
power_monitoring_interval: {default_config.power_monitoring_interval}  # Power measurement interval (seconds)
power_monitoring_enabled: {str(default_config.power_monitoring_enabled).lower()}  # Enable/disable power monitoring

# ========================================================================
# TEMPERATURE PARAMETERS (°C)
# ========================================================================
activation_temperature: {default_config.activation_temperature}  # Temperature activation threshold
standby_temperature: {default_config.standby_temperature}     # Standby temperature setting

# ========================================================================
# POWER SUPPLY PARAMETERS
# ========================================================================
voltage: {default_config.voltage}  # Operating voltage (V)
current: {default_config.current}  # Operating current (A)

# ========================================================================
# MCU PARAMETERS
# ========================================================================
fan_speed: {default_config.fan_speed}           # Fan speed level (1-10)
upper_temperature: {default_config.upper_temperature} # Maximum temperature limit (°C)

# ========================================================================
# STABILIZATION TIME PARAMETERS (in seconds)
# ========================================================================
poweron_stabilization: {default_config.poweron_stabilization}  # Power-on stabilization time
mcu_boot_complete_stabilization: {default_config.mcu_boot_complete_stabilization}  # MCU boot complete stabilization time
mcu_command_stabilization: {default_config.mcu_command_stabilization}  # MCU command stabilization time
mcu_temperature_stabilization: {default_config.mcu_temperature_stabilization}  # MCU temperature stabilization time

# ========================================================================
# STATISTICS PARAMETERS
# ========================================================================
calculate_statistics: {str(default_config.calculate_statistics).lower()}    # Calculate power consumption statistics
show_detailed_results: {str(default_config.show_detailed_results).lower()}   # Show detailed cycle-by-cycle results

# ========================================================================
# METADATA
# ========================================================================
metadata:
  created_at: '{datetime.now().isoformat()}'
  created_by: 'ConfigurationService (auto-generated)'
  version: '1.0.0'
  description: 'Heating/Cooling Time Test configuration with power monitoring'
  notes: |
    This configuration file contains parameters for heating/cooling time tests.
    
    Key parameters:
    - Wait times control delays between heating/cooling phases
    - Power monitoring tracks energy consumption during test cycles
    - Temperature parameters define test operating ranges
    - Statistics options control data analysis and display
    
    Modify these values to customize test behavior according to your
    hardware specifications and testing requirements.
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

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
        if not self._configuration:
            raise RepositoryAccessError(
                operation="load_dut_defaults",
                reason="Configuration repository not available",
            )

        try:
            # Delegate to Configuration repository for file operations
            return await self._configuration.load_dut_defaults(profile_name)

        except Exception as e:
            logger.error(f"Unexpected error loading DUT defaults: {e}")
            raise RepositoryAccessError(
                operation="load_dut_defaults", reason=f"Failed to load DUT defaults: {str(e)}"
            ) from e

    # ============================================================================
    # CORE CONFIGURATION SAVING
    # ============================================================================

    async def save_test_profile(self, profile_name: str, config_data: Dict[str, Any]) -> None:
        """
        Save test profile configuration

        Args:
            profile_name: Name of the profile to save
            config_data: Configuration data dictionary

        Raises:
            RepositoryAccessError: If save operation fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="save_test_profile",
                reason="Configuration repository not available",
            )

        try:
            # Convert dict to TestConfiguration object
            test_config = TestConfiguration.from_structured_dict(config_data)

            # Save using the configuration repository
            await self._configuration.save_profile(profile_name, test_config)

            logger.info(f"Successfully saved test profile: {profile_name}")

        except Exception as e:
            logger.error(f"Failed to save test profile {profile_name}: {e}")
            raise RepositoryAccessError(
                operation="save_test_profile",
                reason=str(e),
                file_path=f"{profile_name}.yaml",
            ) from e

    async def save_hardware_config(self, hardware_config_data: Dict[str, Any]) -> None:
        """
        Save hardware configuration to hardware_config.yaml

        Args:
            hardware_config_data: Hardware configuration data dictionary

        Raises:
            RepositoryAccessError: If save operation fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="save_hardware_config",
                reason="Configuration repository not available",
            )

        try:
            # Convert dict to HardwareConfig object
            hardware_config = HardwareConfig.from_dict(hardware_config_data)

            # Save using the configuration repository
            await self._configuration.save_hardware_config(hardware_config)

            logger.info("Successfully saved hardware configuration to hardware_config.yaml")

        except Exception as e:
            logger.error(f"Failed to save hardware configuration: {e}")
            raise RepositoryAccessError(
                operation="save_hardware_config",
                reason=str(e),
                file_path="hardware_config.yaml",
            ) from e

    async def save_dut_defaults_configuration(self, dut_defaults_data: Dict[str, Any]) -> None:
        """
        Save DUT defaults configuration

        Args:
            dut_defaults_data: DUT defaults data dictionary

        Raises:
            RepositoryAccessError: If save operation fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="save_dut_defaults_configuration",
                reason="Configuration repository not available",
            )

        try:
            # Extract profile name if present
            profile_name = dut_defaults_data.get("active_profile", "default")

            # Save using the configuration repository
            await self._configuration.save_dut_defaults(dut_defaults_data, profile_name)

            logger.info("Successfully saved DUT defaults configuration")

        except Exception as e:
            logger.error(f"Failed to save DUT defaults configuration: {e}")
            raise RepositoryAccessError(
                operation="save_dut_defaults",
                reason=str(e),
                file_path="dut_defaults.yaml",
            ) from e

    # ============================================================================
    # PROFILE MANAGEMENT
    # ============================================================================

    async def list_available_profiles(self) -> List[str]:
        """
        Get list of available configuration profiles

        Returns:
            List of available profile names
        """
        if not self._configuration:
            return []
        return await self._configuration.list_available_profiles()

    async def get_active_profile_name(self) -> str:
        """
        Get the profile name that should be used, following business priority rules

        Priority:
        1. Last used profile (if available and exists)
        2. Active profile from profile.yaml (if exists)
        3. Default fallback

        Returns:
            Profile name to use for configuration loading
        """
        fallback_profile = "default"

        if not self._configuration:
            logger.warning("Configuration repository not available, using fallback")
            return fallback_profile

        try:
            # Ensure profile system is initialized
            await self._ensure_profile_system_initialized()

            # 1st priority: Last used profile from repository
            last_used = await self._configuration.load_last_used_profile()
            if last_used and self._is_valid_profile_name(last_used):
                # Verify the profile actually exists before using it
                available_profiles = await self.list_available_profiles()
                if last_used in available_profiles:
                    logger.debug(f"Using last used profile: '{last_used}'")
                    return last_used
                else:
                    logger.warning(
                        f"Last used profile '{last_used}' no longer exists, falling back"
                    )

            # 2nd priority: Default fallback (which should exist after initialization)
            logger.debug(f"Using fallback profile: '{fallback_profile}'")
            return fallback_profile

        except Exception as e:
            logger.warning(f"Error determining active profile, using fallback: {e}")
            return fallback_profile

    async def get_profile_info(self) -> Dict[str, Any]:
        """
        Get basic profile information without usage history

        Returns:
            Dictionary with current profile and available profiles
        """
        try:
            current_profile = await self.get_active_profile_name()
            available_profiles = await self.list_available_profiles() if self._configuration else []

            return {
                "current_profile": current_profile,
                "available_profiles": available_profiles,
                "repository_available": self._configuration is not None,
            }

        except Exception as e:
            logger.warning(f"Failed to get profile info: {e}")
            return {
                "current_profile": "default",
                "available_profiles": [],
                "repository_available": False,
                "error": str(e),
            }

    async def clear_profile_preferences(self) -> None:
        """
        Clear profile preferences (reset to environment/default behavior)

        Raises:
            RepositoryAccessError: If clearing preferences fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="clear_profile_preferences",
                reason="Configuration repository not available",
            )

        try:
            await self._configuration.clear_preferences()
            logger.info(
                "All profile preferences cleared - will use environment variable or default"
            )
        except Exception as e:
            logger.error(f"Failed to clear profile preferences: {e}")
            raise RepositoryAccessError(
                operation="clear_profile_preferences",
                reason=str(e),
            ) from e

    async def set_active_profile(self, profile_name: str) -> None:
        """
        Set the active profile for the system

        Args:
            profile_name: Name of the profile to activate

        Raises:
            ConfigurationNotFoundError: If profile doesn't exist
            RepositoryAccessError: If setting active profile fails
        """
        if not self._configuration:
            raise RepositoryAccessError(
                operation="set_active_profile",
                reason="Configuration repository not available",
            )

        # Validate profile name
        if not self._is_valid_profile_name(profile_name):
            raise RepositoryAccessError(
                operation="set_active_profile",
                reason=f"Invalid profile name: {profile_name}",
            )

        try:
            # Ensure profile system is initialized
            await self._ensure_profile_system_initialized()

            # Check if profile exists
            available_profiles = await self.list_available_profiles()
            if profile_name not in available_profiles:
                raise ConfigurationNotFoundError(profile_name, available_profiles)

            # Save as last used profile
            await self._configuration.save_last_used_profile(profile_name)

            logger.info(f"Active profile set to: {profile_name}")

        except ConfigurationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to set active profile to '{profile_name}': {e}")
            raise RepositoryAccessError(
                operation="set_active_profile",
                reason=str(e),
            ) from e

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    async def _ensure_profile_system_initialized(self) -> None:
        """
        Ensure the profile system is properly initialized

        This method ensures that:
        1. Profile configuration files exist
        2. Default profile exists in test_profiles/
        3. Profile system is ready for use
        """
        try:
            # Check if default profile exists, if not this will create it
            default_profile = "default"
            available_profiles = await self.list_available_profiles()

            if default_profile not in available_profiles:
                logger.info(f"Default profile '{default_profile}' not found, creating it...")
                # Loading a non-existent profile will auto-create it via YamlConfiguration
                await self.load_test_config(default_profile)
                logger.info(f"Default profile '{default_profile}' created successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize profile system: {e}")

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
