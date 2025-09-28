"""
Service Container (Layer 3)

Manages business services, use cases, and application logic.
This layer contains hot-swappable providers that don't manage connections directly
but depend on the ConnectionContainer for hardware access.
"""

# Third-party imports
from dependency_injector import containers, providers
from loguru import logger

# Local application imports
from application.containers.configuration_container import ConfigurationContainer
from application.containers.connection_container import ConnectionContainer

# Core Services
from application.services.core.exception_handler import ExceptionHandler
from application.services.core.repository_service import RepositoryService

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

# Persistence
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)


class ServiceContainer(containers.DeclarativeContainer):
    """
    Layer 3: Service Management Container

    Responsibilities:
    - Business services and application logic
    - Use cases and workflows
    - Data persistence services
    - Non-hardware infrastructure components

    This container contains hot-swappable services that can be reloaded
    independently of hardware connections.
    """

    # ============================================================================
    # CONFIGURATION (will be set dynamically)
    # ============================================================================

    # Configuration data (will be injected dynamically)
    config = providers.Configuration()

    # Container references (will be wired dynamically)
    config_container = providers.Dependency()
    connection_container = providers.Dependency()

    # ============================================================================
    # PERSISTENCE INFRASTRUCTURE
    # ============================================================================

    json_result_repository = providers.Singleton(
        JsonResultRepository,
        # These paths come from configuration
        data_dir=config.services.repository_results_path,
        auto_save=config.services.repository_auto_save,
    )

    # ============================================================================
    # CORE SERVICES
    # ============================================================================

    exception_handler = providers.Singleton(ExceptionHandler)

    test_result_evaluator = providers.Singleton(TestResultEvaluator)

    repository_service = providers.Singleton(
        RepositoryService,
        test_repository=json_result_repository,
        raw_data_dir=config.services.repository_raw_data_path,
        summary_dir=config.services.repository_summary_path,
        summary_filename=config.services.repository_summary_filename,
    )

    # ============================================================================
    # MONITORING SERVICES
    # ============================================================================

    emergency_stop_service = providers.Factory(
        EmergencyStopService,
        hardware_facade=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
    )

    # ============================================================================
    # INDUSTRIAL SERVICES
    # ============================================================================

    industrial_system_manager = providers.Singleton(
        IndustrialSystemManager,
        hardware_service_facade=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
        gui_alert_callback=None,  # Will be set by GUI if available
    )

    # ============================================================================
    # USE CASES
    # ============================================================================

    # Complex Use Case (with full dependency set)
    eol_force_test_use_case = providers.Factory(
        EOLForceTestUseCase,
        hardware_services=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
        configuration_validator=config_container.configuration_validator,
        test_result_evaluator=test_result_evaluator,
        repository_service=repository_service,
        exception_handler=exception_handler,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    # Standard Use Cases (with industrial system integration)
    robot_home_use_case = providers.Factory(
        RobotHomeUseCase,
        hardware_services=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
        industrial_system_manager=industrial_system_manager,
    )

    heating_cooling_time_test_use_case = providers.Factory(
        HeatingCoolingTimeTestUseCase,
        hardware_services=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    simple_mcu_test_use_case = providers.Factory(
        SimpleMCUTestUseCase,
        hardware_services=connection_container.hardware_service_facade,
        configuration_service=config_container.configuration_service,
        emergency_stop_service=emergency_stop_service,
        industrial_system_manager=industrial_system_manager,
    )

    # ============================================================================
    # SERVICE MANAGEMENT METHODS
    # ============================================================================

    def reload_services(self) -> bool:
        """
        Reload business services and use cases.

        This is a hot-reload operation that resets service providers
        while preserving hardware connections.

        Returns:
            bool: True if reload was successful
        """
        try:
            logger.info("🔄 Reloading business services...")

            # Reset singleton services to force recreation with updated config
            services_to_reset = [
                "test_result_evaluator",
                "repository_service",
                "industrial_system_manager",
                "json_result_repository",
            ]

            for service_name in services_to_reset:
                try:
                    service_provider = getattr(self, service_name)
                    if hasattr(service_provider, "reset"):
                        service_provider.reset()
                        logger.info(f"🔄 Reset {service_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset {service_name}: {e}")

            # Reset factory providers for use cases
            use_case_factories = [
                "eol_force_test_use_case",
                "robot_home_use_case",
                "heating_cooling_time_test_use_case",
                "simple_mcu_test_use_case",
                "emergency_stop_service",
            ]

            for use_case_name in use_case_factories:
                try:
                    use_case_provider = getattr(self, use_case_name)
                    if hasattr(use_case_provider, "reset"):
                        use_case_provider.reset()
                        logger.info(f"🔄 Reset {use_case_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to reset {use_case_name}: {e}")

            logger.info("✅ Business services reloaded successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Service reload failed: {e}")
            return False

    def sync_configuration(
        self, config_container: ConfigurationContainer, connection_container: ConnectionContainer
    ) -> bool:
        """
        Synchronize service configuration with updated containers.

        Args:
            config_container: Updated configuration container
            connection_container: Updated connection container

        Returns:
            bool: True if sync was successful
        """
        try:
            logger.info("🔄 Synchronizing ServiceContainer dependencies...")

            # Update container dependencies
            self.config_container.override(config_container)
            self.connection_container.override(connection_container)

            logger.info("✅ ServiceContainer dependencies synchronized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to synchronize ServiceContainer dependencies: {e}")
            return False

    def set_gui_alert_callback(self, callback) -> None:
        """Set GUI alert callback for industrial system manager."""
        try:
            # Get the current industrial system manager instance
            if hasattr(self.industrial_system_manager, "_provided"):
                # If already created, update the callback directly
                ism_instance = self.industrial_system_manager()
                # Update the private callback attribute directly
                ism_instance._gui_alert_callback = callback
                logger.info("🔄 Updated GUI alert callback for existing ISM instance")

            # For future instances, we need to update the provider
            # This is more complex with dependency-injector, so we'll handle it
            # by resetting the singleton if a callback is set
            if callback is not None:
                logger.info("🔄 GUI alert callback set for ServiceContainer")

        except Exception as e:
            logger.error(f"Failed to set GUI alert callback: {e}")

    @classmethod
    def create(
        cls, config_container: ConfigurationContainer, connection_container: ConnectionContainer
    ) -> "ServiceContainer":
        """
        Create service container with configuration and connection dependencies.

        Args:
            config_container: Configuration container to use
            connection_container: Connection container to use

        Returns:
            Configured ServiceContainer instance
        """
        container = cls()

        # Inject container dependencies
        container.config_container.override(config_container)
        container.connection_container.override(connection_container)

        logger.info("🏭 ServiceContainer created successfully")
        return container
