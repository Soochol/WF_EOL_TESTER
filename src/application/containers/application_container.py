"""
Application Container

Main dependency injection container orchestrator for the WF EOL Tester application.
Combines all specialized sub-containers and provides a unified interface.
"""

from dependency_injector import containers, providers
from loguru import logger

# Sub-container imports
from application.containers.configuration_container import ConfigurationContainer
from application.containers.persistence_container import PersistenceContainer
from application.containers.core_services_container import CoreServicesContainer
from application.containers.hardware_container import HardwareContainer
from application.containers.use_case_container import UseCaseContainer

# Domain Layer Imports (for fallback config)
from domain.value_objects.application_config import ApplicationConfig
from domain.value_objects.hardware_config import HardwareConfig

# Infrastructure Layer Imports (for configuration loading)
from infrastructure.implementation.configuration.yaml_container_configuration import (
    YamlContainerConfigurationLoader,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Main application container orchestrator for dependency injection.

    Combines specialized sub-containers and provides a unified interface for:
    - Configuration services (via ConfigurationContainer)
    - Hardware services (via HardwareContainer)
    - Repository services (via PersistenceContainer)
    - Core services (via CoreServicesContainer)
    - Use cases and business logic (via UseCaseContainer)
    """

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    config = providers.Configuration()

    # ============================================================================
    # SUB-CONTAINERS
    # ============================================================================

    # Configuration container
    configuration = providers.Container(
        ConfigurationContainer,
        config=config,
    )

    # Persistence container
    persistence = providers.Container(
        PersistenceContainer,
        config=config,
    )

    # Core services container
    core_services = providers.Container(CoreServicesContainer)

    # Hardware container
    hardware = providers.Container(
        HardwareContainer,
        config=config,
    )

    # Use cases container
    use_cases = providers.Container(
        UseCaseContainer,
        hardware_service_facade=hardware.hardware_service_facade,
        configuration_service=configuration.configuration_service,
        configuration_validator=configuration.configuration_validator,
        test_result_evaluator=core_services.test_result_evaluator,
        repository_service=persistence.repository_service,
        exception_handler=core_services.exception_handler,
    )

    # ============================================================================
    # UNIFIED INTERFACE (Backward Compatibility)
    # ============================================================================

    # Configuration services
    configuration_service = providers.Delegate(configuration.configuration_service)
    configuration_validator = providers.Delegate(configuration.configuration_validator)

    # Repository services
    repository_service = providers.Delegate(persistence.repository_service)

    # Core services
    exception_handler = providers.Delegate(core_services.exception_handler)
    test_result_evaluator = providers.Delegate(core_services.test_result_evaluator)

    # Hardware services
    hardware_service_facade = providers.Delegate(hardware.hardware_service_facade)

    # Use cases
    eol_force_test_use_case = providers.Delegate(use_cases.eol_force_test_use_case)
    robot_home_use_case = providers.Delegate(use_cases.robot_home_use_case)
    heating_cooling_time_test_use_case = providers.Delegate(use_cases.heating_cooling_time_test_use_case)
    simple_mcu_test_use_case = providers.Delegate(use_cases.simple_mcu_test_use_case)

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
