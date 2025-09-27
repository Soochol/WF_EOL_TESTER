"""
Configuration Container (Layer 1)

Centralized configuration management for the application.
Handles YAML configuration loading, validation, and hot-reload capability.
This layer is independent and can be reloaded without affecting connections or services.
"""

# Third-party imports
from dependency_injector import containers, providers
from loguru import logger

# Local application imports
from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from domain.value_objects.application_config import ApplicationConfig
from infrastructure.implementation.configuration.yaml_configuration import YamlConfiguration
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)


class ConfigurationContainer(containers.DeclarativeContainer):
    """
    Layer 1: Configuration Management Container

    Responsibilities:
    - YAML configuration loading and management
    - Configuration validation
    - Configuration service provisioning
    - Hot-reload of configuration data

    This container is stateless and can be safely reloaded without side effects.
    """

    # ============================================================================
    # CORE CONFIGURATION PROVIDERS
    # ============================================================================

    # Main configuration provider - dynamically loaded from YAML
    config = providers.Configuration()

    # Default application configuration fallback
    _default_config = ApplicationConfig()

    # ============================================================================
    # CONFIGURATION INFRASTRUCTURE
    # ============================================================================

    # YAML configuration implementation
    yaml_configuration = providers.Singleton(YamlConfiguration)

    # Configuration service with all path dependencies
    configuration_service = providers.Singleton(
        ConfigurationService,
        configuration=yaml_configuration,
        application_config_path=_default_config.services.config_application_path,
        hardware_config_path=_default_config.services.config_hardware_path,
        profile_preference_path=_default_config.services.config_profile_preference_path,
        test_profiles_dir=_default_config.services.config_test_profiles_dir,
        heating_cooling_config_path=_default_config.services.config_heating_cooling_path,
    )

    # Configuration validator
    configuration_validator = providers.Singleton(ConfigurationValidator)

    # ============================================================================
    # CONFIGURATION MANAGEMENT METHODS
    # ============================================================================

    @classmethod
    def create(cls) -> "ConfigurationContainer":
        """
        Create configuration container with loaded YAML data.

        Returns:
            Configured ConfigurationContainer instance
        """
        container = cls()

        try:
            # Load configuration from YAML files
            config_loader = YamlContainerConfigurationLoader()
            config_data = config_loader.load_all_configurations()
            container.config.from_dict(config_data)
            logger.info("🔧 ConfigurationContainer created successfully")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using fallback configuration")
            cls._apply_fallback_config(container)

        return container

    @classmethod
    def _apply_fallback_config(cls, container: "ConfigurationContainer") -> None:
        """Apply fallback configuration to container."""
        # Use default configurations separately
        app_config = ApplicationConfig()
        from domain.value_objects.hardware_config import HardwareConfig
        hardware_config = HardwareConfig()

        # Apply configurations separately
        container.config.from_dict(app_config.to_dict())
        container.config.from_dict({"hardware": hardware_config.to_dict()})

        logger.info("🔧 Fallback configuration applied to ConfigurationContainer")

    def reload_configuration(self) -> bool:
        """
        Reload configuration from YAML files.

        This is a hot-reload operation that only affects configuration data.
        No connections or services are disrupted.

        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            logger.info("🔄 Reloading configuration data...")

            # Load fresh configuration from YAML files
            config_loader = YamlContainerConfigurationLoader()
            config_data = config_loader.load_all_configurations()

            # Update the configuration provider with new data
            self.config.from_dict(config_data)

            logger.info("✅ Configuration reloaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Configuration reload failed: {e}")
            return False

    def get_hardware_config(self) -> dict:
        """Get hardware configuration data."""
        try:
            return self.config.hardware()
        except Exception as e:
            logger.error(f"Failed to get hardware config: {e}")
            return {}

    def get_application_config(self) -> dict:
        """Get application configuration data."""
        try:
            return self.config()
        except Exception as e:
            logger.error(f"Failed to get application config: {e}")
            return {}

    @classmethod
    def ensure_config_exists(cls) -> None:
        """
        Ensure configuration files exist, create from defaults if missing.
        """
        try:
            config_loader = YamlContainerConfigurationLoader()
            config_loader.ensure_configurations_exist()
            logger.info("🔧 Configuration files ensured successfully")
        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")