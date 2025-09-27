"""
Application Container (Unified)

Single comprehensive dependency injection container that combines all application dependencies.
Manages configuration, infrastructure, core services, hardware, persistence, and use cases.
"""

# Third-party imports
from dependency_injector import containers, providers
from loguru import logger

# Local application imports
# Configuration and Infrastructure
from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator

# Core Services
from application.services.core.exception_handler import ExceptionHandler
from application.services.core.repository_service import RepositoryService

# Hardware
from application.services.hardware_facade import HardwareServiceFacade

# Industrial Services
from application.services.industrial.industrial_system_manager import (
    IndustrialSystemManager,
)

# Monitoring Services
from application.services.monitoring.emergency_stop_service import EmergencyStopService
from application.services.test.test_result_evaluator import TestResultEvaluator

# Use Cases
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestUseCase,
)
from application.use_cases.robot_operations import RobotHomeUseCase
from application.use_cases.system_tests import SimpleMCUTestUseCase

# Domain Configuration
from domain.value_objects.application_config import ApplicationConfig
from infrastructure.factories.hardware_factory import HardwareFactory
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)

# Persistence
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Unified application container for dependency injection.

    Manages all application dependencies in a single container:
    - Configuration loading and management
    - Infrastructure components (YAML, repositories, hardware factory)
    - Core business services (exception handling, test evaluation)
    - Hardware services and facade
    - Data persistence services
    - Application use cases
    """

    # Configuration provider
    config = providers.Configuration()

    # Default application configuration
    _default_config = ApplicationConfig()

    # ============================================================================
    # CONFIGURATION INFRASTRUCTURE
    # ============================================================================

    yaml_configuration = providers.Singleton(YamlConfiguration)

    configuration_service = providers.Singleton(
        ConfigurationService,
        configuration=yaml_configuration,
        application_config_path=_default_config.services.config_application_path,
        hardware_config_path=_default_config.services.config_hardware_path,
        profile_preference_path=_default_config.services.config_profile_preference_path,
        test_profiles_dir=_default_config.services.config_test_profiles_dir,
        heating_cooling_config_path=_default_config.services.config_heating_cooling_path,
    )

    configuration_validator = providers.Singleton(ConfigurationValidator)

    # ============================================================================
    # HARDWARE INFRASTRUCTURE
    # ============================================================================

    hardware_factory = providers.Container(HardwareFactory, config=config.hardware)

    # GUI State Manager (optional, set by GUI application)
    gui_state_manager = providers.Object(None)

    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware_factory.robot_service,
        mcu_service=hardware_factory.mcu_service,
        loadcell_service=hardware_factory.loadcell_service,
        power_service=hardware_factory.power_service,
        digital_io_service=hardware_factory.digital_io_service,
        gui_state_manager=gui_state_manager,
    )

    # ============================================================================
    # PERSISTENCE INFRASTRUCTURE
    # ============================================================================

    json_result_repository = providers.Singleton(
        JsonResultRepository,
        data_dir=_default_config.services.repository_results_path,
        auto_save=_default_config.services.repository_auto_save,
    )

    # ============================================================================
    # CORE SERVICES
    # ============================================================================

    exception_handler = providers.Singleton(ExceptionHandler)

    test_result_evaluator = providers.Singleton(TestResultEvaluator)

    repository_service = providers.Singleton(
        RepositoryService,
        test_repository=json_result_repository,
        raw_data_dir=_default_config.services.repository_raw_data_path,
        summary_dir=_default_config.services.repository_summary_path,
        summary_filename=_default_config.services.repository_summary_filename,
    )

    # ============================================================================
    # MONITORING SERVICES
    # ============================================================================

    emergency_stop_service = providers.Factory(
        EmergencyStopService,
        hardware_facade=hardware_service_facade,
        configuration_service=configuration_service,
    )

    # ============================================================================
    # INDUSTRIAL SERVICES
    # ============================================================================

    industrial_system_manager = providers.Singleton(
        IndustrialSystemManager,
        hardware_service_facade=hardware_service_facade,
        configuration_service=configuration_service,
        gui_alert_callback=None,  # Will be set by GUI if available
    )

    # ============================================================================
    # USE CASES
    # ============================================================================

    # Complex Use Case (with full dependency set)
    eol_force_test_use_case = providers.Factory(
        EOLForceTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        configuration_validator=configuration_validator,
        test_result_evaluator=test_result_evaluator,
        repository_service=repository_service,
        exception_handler=exception_handler,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    # Standard Use Cases (with industrial system integration)
    robot_home_use_case = providers.Factory(
        RobotHomeUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        industrial_system_manager=industrial_system_manager,
    )

    heating_cooling_time_test_use_case = providers.Factory(
        HeatingCoolingTimeTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    simple_mcu_test_use_case = providers.Factory(
        SimpleMCUTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    # ============================================================================
    # CONFIGURATION MANAGEMENT METHODS
    # ============================================================================

    @classmethod
    def create(cls) -> "ApplicationContainer":
        """
        Create container with configuration loaded via ConfigurationService.

        Returns:
            Configured ApplicationContainer instance
        """
        container = cls()

        try:
            # Create configuration loader for container initialization
            config_loader = YamlContainerConfigurationLoader()

            # Load all configurations via configuration loader
            config_data = config_loader.load_all_configurations()
            container.config.from_dict(config_data)
            logger.info("Container created successfully with loaded configuration")

        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            logger.info("Using fallback configuration")
            cls._apply_fallback_config(container)

        # Bind reload_configuration method to the container instance
        container.reload_configuration = lambda: cls._instance_reload_configuration(container)
        logger.debug("🔗 Bound reload_configuration method to container instance")

        return container

    @classmethod
    def create_with_paths(cls, **kwargs) -> "ApplicationContainer":
        """
        Create container with configuration paths (legacy method for compatibility).

        Note: Paths are now managed internally via value objects.
        All path arguments are ignored.

        Returns:
            Configured ApplicationContainer instance
        """
        # Path arguments are silently ignored as they're managed internally
        return cls.create()

    @classmethod
    def ensure_config_exists(cls, **kwargs) -> None:
        """
        Ensure configuration files exist, create from defaults if missing.

        Note: Path arguments are ignored. Uses default paths from ConfigPaths.
        """
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")

        try:
            config_loader = YamlContainerConfigurationLoader()
            config_loader.ensure_configurations_exist()
            logger.info("Configuration files ensured successfully")
        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")

    @classmethod
    def _apply_fallback_config(cls, container: "ApplicationContainer") -> None:
        """Apply fallback configuration to container."""
        # Use default configurations separately
        app_config = ApplicationConfig()
        # Local application imports
        from domain.value_objects.hardware_config import HardwareConfig

        hardware_config = HardwareConfig()

        # Apply configurations separately
        container.config.from_dict(app_config.to_dict())
        container.config.from_dict({"hardware": hardware_config.to_dict()})

        logger.info("In-memory default configuration applied successfully")

    @classmethod
    def _instance_reload_configuration(cls, container_instance: "ApplicationContainer") -> bool:
        """
        Instance-specific reload configuration method.
        This method is bound to container instances to enable hot-reload functionality.

        Args:
            container_instance: The container instance to reload configuration for

        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            logger.info("🔄 Starting instance configuration reload...")

            # Load fresh configuration from YAML files
            config_loader = YamlContainerConfigurationLoader()
            config_data = config_loader.load_all_configurations()

            # Update the configuration provider with new data
            container_instance.config.from_dict(config_data)
            logger.info("✅ Configuration data reloaded from YAML files")

            # Synchronize HardwareFactory configuration
            cls._synchronize_hardware_factory_config(container_instance)

            # Reset hardware-related Singletons to force recreation with new config
            cls._reset_hardware_singletons_instance(container_instance)

            logger.info("🔄 Instance configuration reload completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Instance configuration reload failed: {e}")
            return False

    @classmethod
    def _synchronize_hardware_factory_config(
        cls, container_instance: "ApplicationContainer"
    ) -> None:
        """
        Synchronize HardwareFactory configuration with main container configuration.
        """
        try:
            # Get hardware configuration from main container
            hardware_config = container_instance.config.hardware()

            # Update HardwareFactory config to match
            container_instance.hardware_factory.config.from_dict(hardware_config)
            logger.info("🔄 HardwareFactory configuration synchronized")

            # Reset HardwareFactory providers to pick up new config
            hardware_factory_providers = [
                "robot_service",
                "power_service",
                "mcu_service",
                "loadcell_service",
                "digital_io_service",
            ]

            for provider_name in hardware_factory_providers:
                try:
                    provider = getattr(container_instance.hardware_factory, provider_name)
                    if hasattr(provider, "reset"):
                        provider.reset()
                        logger.info(f"🔄 Reset HardwareFactory.{provider_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset HardwareFactory.{provider_name}: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to synchronize HardwareFactory config: {e}")

    @classmethod
    def _reset_hardware_singletons_instance(
        cls, container_instance: "ApplicationContainer"
    ) -> None:
        """
        Reset hardware-related Singletons for a specific container instance.
        """
        singletons_to_reset = [
            ("hardware_service_facade", container_instance.hardware_service_facade),
            ("industrial_system_manager", container_instance.industrial_system_manager),
        ]

        for name, singleton_provider in singletons_to_reset:
            try:
                if hasattr(singleton_provider, "reset"):
                    singleton_provider.reset()
                    logger.info(f"🔄 Reset {name} Singleton")
                else:
                    logger.warning(f"⚠️ {name} does not have reset() method")
            except Exception as e:
                logger.error(f"❌ Failed to reset {name}: {e}")

        # Reset emergency_stop_service if it's a Factory that creates instances dependent on hardware
        try:
            if hasattr(container_instance.emergency_stop_service, "reset"):
                container_instance.emergency_stop_service.reset()
                logger.info("🔄 Reset emergency_stop_service provider")
        except Exception as e:
            logger.debug(f"Emergency stop service reset skipped: {e}")

        logger.info("✅ Hardware Singletons reset completed")

    def reload_configuration(self) -> bool:
        """
        Reload configuration from YAML files and refresh hardware services.

        This method enables hot-reload of configuration changes made through the Settings UI.
        It reloads YAML files and resets hardware-related Singletons to apply new configurations.

        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            logger.info("🔄 Starting configuration reload...")

            # Load fresh configuration from YAML files
            config_loader = YamlContainerConfigurationLoader()
            config_data = config_loader.load_all_configurations()

            # Update the configuration provider with new data
            self.config.from_dict(config_data)
            logger.info("✅ Configuration data reloaded from YAML files")

            # Reset hardware-related Singletons to force recreation with new config
            self._reset_hardware_singletons()

            logger.info("🔄 Configuration reload completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Configuration reload failed: {e}")
            return False

    def _reset_hardware_singletons(self) -> None:
        """
        Reset hardware-related Singletons to force recreation with updated configuration.
        """
        singletons_to_reset = [
            ("hardware_service_facade", self.hardware_service_facade),
            ("industrial_system_manager", self.industrial_system_manager),
        ]

        for name, singleton_provider in singletons_to_reset:
            try:
                if hasattr(singleton_provider, "reset"):
                    singleton_provider.reset()
                    logger.info(f"🔄 Reset {name} Singleton")
                else:
                    logger.warning(f"⚠️ {name} does not have reset() method")
            except Exception as e:
                logger.error(f"❌ Failed to reset {name}: {e}")

        # Reset emergency_stop_service if it's a Factory that creates instances dependent on hardware
        try:
            if hasattr(self.emergency_stop_service, "reset"):
                self.emergency_stop_service.reset()
                logger.info("🔄 Reset emergency_stop_service provider")
        except Exception as e:
            logger.debug(f"Emergency stop service reset skipped: {e}")

        logger.info("✅ Hardware Singletons reset completed")
        try:
            if hasattr(self.emergency_stop_service, "reset"):
                self.emergency_stop_service.reset()
                logger.info("🔄 Reset emergency_stop_service provider")
        except Exception as e:
            logger.debug(f"Emergency stop service reset skipped: {e}")

        logger.info("✅ Hardware Singletons reset completed")
