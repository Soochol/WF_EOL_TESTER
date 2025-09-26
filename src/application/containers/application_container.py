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

# Monitoring Services
from application.services.monitoring.emergency_stop_service import EmergencyStopService
from application.services.test.test_result_evaluator import TestResultEvaluator

# Industrial Services
from application.services.industrial.industrial_system_manager import IndustrialSystemManager

# Use Cases
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.heating_cooling_time_test import HeatingCoolingTimeTestUseCase
from application.use_cases.robot_operations import RobotHomeUseCase
from application.use_cases.system_tests import SimpleMCUTestUseCase

# Domain Configuration
from domain.value_objects.application_config import ApplicationConfig
from infrastructure.factories.hardware_factory import HardwareFactory
from infrastructure.implementation.configuration.yaml_configuration import YamlConfiguration
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)

# Persistence
from infrastructure.implementation.repositories.json_result_repository import JsonResultRepository


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

    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware_factory.robot_service,
        mcu_service=hardware_factory.mcu_service,
        loadcell_service=hardware_factory.loadcell_service,
        power_service=hardware_factory.power_service,
        digital_io_service=hardware_factory.digital_io_service,
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
