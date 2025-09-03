"""
Application Container

Main dependency injection container for the WF EOL Tester application.
Manages all application services, use cases, and hardware dependencies.
"""

from dependency_injector import containers, providers
from loguru import logger

# Application Layer Imports - Updated for new domain structure
from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from application.services.core.exception_handler import ExceptionHandler
from application.services.core.repository_service import RepositoryService
from application.services.hardware_facade import HardwareServiceFacade
from application.services.test.test_result_evaluator import TestResultEvaluator
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestUseCase,
)
from application.use_cases.robot_operations import RobotHomeUseCase
from application.use_cases.system_tests import SimpleMCUTestUseCase
from domain.value_objects.application_config import ApplicationConfig

# Domain Layer Imports
from domain.value_objects.hardware_config import HardwareConfig

# Infrastructure Layer Imports
from infrastructure.factories.hardware_factory import HardwareFactory
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Main application container for dependency injection.

    Provides centralized configuration and dependency management for:
    - Configuration services
    - Hardware services
    - Repository services
    - Use cases and business logic
    """

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    config = providers.Configuration()

    # ============================================================================
    # HARDWARE LAYER
    # ============================================================================

    hardware = providers.Container(HardwareFactory, config=config.hardware)

    # ============================================================================
    # INFRASTRUCTURE & CORE SERVICES
    # ============================================================================

    # Configuration Infrastructure
    yaml_configuration = providers.Singleton(YamlConfiguration)

    # Repository Infrastructure
    json_result_repository = providers.Singleton(
        JsonResultRepository,
        data_dir=config.services.repository.results_path,
        auto_save=config.services.repository.auto_save,
    )

    # Configuration Services
    configuration_service = providers.Singleton(
        ConfigurationService,
        configuration=yaml_configuration,
    )

    configuration_validator = providers.Singleton(ConfigurationValidator)

    # Business Services
    repository_service = providers.Singleton(
        RepositoryService, test_repository=json_result_repository
    )

    exception_handler = providers.Singleton(ExceptionHandler)
    test_result_evaluator = providers.Singleton(TestResultEvaluator)

    # Hardware Service Facade
    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware.robot_service,
        mcu_service=hardware.mcu_service,
        loadcell_service=hardware.loadcell_service,
        power_service=hardware.power_service,
        digital_io_service=hardware.digital_io_service,
    )

    # ============================================================================
    # USE CASES
    # ============================================================================

    # Complex Use Case (with full dependency set)
    eol_force_test_use_case: providers.Factory[EOLForceTestUseCase] = providers.Factory(
        EOLForceTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        configuration_validator=configuration_validator,
        test_result_evaluator=test_result_evaluator,
        repository_service=repository_service,
        exception_handler=exception_handler,
    )

    # Standard Use Cases (with minimal dependencies)
    robot_home_use_case: providers.Factory[RobotHomeUseCase] = providers.Factory(
        RobotHomeUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
    )

    heating_cooling_time_test_use_case: providers.Factory[HeatingCoolingTimeTestUseCase] = (
        providers.Factory(
            HeatingCoolingTimeTestUseCase,
            hardware_services=hardware_service_facade,
            configuration_service=configuration_service,
        )
    )

    simple_mcu_test_use_case: providers.Factory[SimpleMCUTestUseCase] = providers.Factory(
        SimpleMCUTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
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

        Note: Paths are now fixed in ConfigPaths and cannot be customized.
        All path arguments are ignored.

        Returns:
            Configured ApplicationContainer instance
        """
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")
        return cls.create()

    @classmethod
    def ensure_config_exists(cls, **kwargs) -> None:
        """
        Ensure configuration files exist, create from defaults if missing.

        Note: Path arguments are ignored. Uses default paths from ConfigPaths.
        """
        if kwargs:
            logger.warning(f"Path arguments are ignored: {list(kwargs.keys())}")

        config_loader = YamlContainerConfigurationLoader()
        config_loader.ensure_configurations_exist()

    @classmethod
    def _apply_fallback_config(cls, container: "ApplicationContainer") -> None:
        """Apply fallback configuration to container."""
        # Use default configurations separately
        app_config = ApplicationConfig()
        hardware_config = HardwareConfig()

        # Apply configurations separately
        container.config.from_dict(app_config.to_dict())
        container.config.from_dict({"hardware": hardware_config.to_dict()})

        logger.info("In-memory default configuration applied successfully")

    # Legacy support method - delegates to create_with_paths
    @classmethod
    def load_config_safely(
        cls,
        application_config_path: str = "configuration/application.yaml",
        hardware_config_path: str = "configuration/hardware_config.yaml",
    ) -> "ApplicationContainer":
        """
        Legacy method - Create container and load configuration safely with fallback.

        Deprecated: Use create() or create_with_paths() instead.

        Args:
            application_config_path: Path to application configuration file
            hardware_config_path: Path to hardware configuration file

        Returns:
            Configured ApplicationContainer instance
        """
        logger.warning(
            "load_config_safely() is deprecated. Use create() or create_with_paths() instead."
        )
        return cls.create_with_paths(
            application_config_path=application_config_path,
            hardware_config_path=hardware_config_path,
        )
