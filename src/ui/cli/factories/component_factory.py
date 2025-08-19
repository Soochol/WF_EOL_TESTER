"""Component Factory System

Factory patterns for creating configured components with dependency resolution
and injection, instance lifecycle management, and interface-based component
creation. Supports configuration-driven component creation and assembly.

Key Features:
- Factory for creating configured components
- Dependency resolution and injection
- Instance lifecycle management
- Interface-based component creation
- Configuration-driven assembly
"""

from typing import Any, Optional, Type, TypeVar
from loguru import logger

from infrastructure.containers.application_container import ApplicationContainer
from ..config.component_config import ComponentConfig, ConfigurationMode

# Type variable for generic factory methods
T = TypeVar("T")


class ComponentFactory:
    """Factory for creating configured components with dependency injection.

    Provides centralized component creation with dependency resolution,
    lifecycle management, and configuration-driven assembly. Uses the
    dependency injection container to manage component dependencies.
    """

    def __init__(
        self,
        container: ApplicationContainer,
        config: ComponentConfig,
    ):
        """Initialize component factory.

        Args:
            container: Dependency injection container
            config: Component configuration for service bindings
        """
        self._container = container
        self._config = config
        self._is_configured = False

    def configure_services(self) -> None:
        """Configure services in the dependency container.

        Registers all configured services with the container based on
        the current configuration mode and service bindings.
        """
        if self._is_configured:
            logger.debug("Services already configured, skipping")
            return

        logger.info(f"Configuring services for mode: {self._config.mode.value}")

        # Register all configured services
        configurations = self._config.get_all_configurations()

        for interface_type, config in configurations.items():
            implementation = config.get("implementation")
            factory = config.get("factory")
            lifetime = config.get("lifetime")

            if implementation or factory:
                # Ensure lifetime has a default value
                service_lifetime = lifetime if lifetime is not None else self._config.get_lifetime(interface_type)

                self._container.register(
                    interface_type=interface_type,
                    implementation_type=implementation,
                    factory=factory,
                    lifetime=service_lifetime,
                )
                logger.debug(
                    f"Registered {interface_type.__name__} -> "
                    f"{implementation.__name__ if implementation else 'factory'} "
                    f"({service_lifetime.value})"
                )

        self._is_configured = True
        logger.info("Service configuration completed")

    def create(self, service_type: Type[T]) -> T:
        """Create a service instance with dependency injection.

        Args:
            service_type: The service type to create

        Returns:
            Service instance with dependencies injected

        Raises:
            ValueError: If service is not configured or creation fails
        """
        if not self._is_configured:
            self.configure_services()

        try:
            instance = self._container.resolve(service_type)
            logger.debug(f"Created {service_type.__name__} instance")
            return instance
        except Exception as e:
            logger.error(f"Failed to create {service_type.__name__}: {e}")
            raise ValueError(f"Failed to create {service_type.__name__}: {e}")

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a specific instance in the container.

        Args:
            service_type: The service type to register
            instance: The instance to register
        """
        self._container.register_instance(service_type, instance)
        logger.debug(f"Registered instance for {service_type.__name__}")

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered.

        Args:
            service_type: The service type to check

        Returns:
            True if the service is registered, False otherwise
        """
        return self._container.is_registered(service_type)

    @property
    def container(self) -> ApplicationContainer:
        """Get the dependency injection container.

        Returns:
            The dependency injection container
        """
        return self._container

    @property
    def config(self) -> ComponentConfig:
        """Get the component configuration.

        Returns:
            The component configuration
        """
        return self._config


class CLIComponentFactory(ComponentFactory):
    """Specialized factory for CLI components.

    Extends ComponentFactory with CLI-specific creation methods and
    convenience functions for common CLI component assembly patterns.
    Provides pre-configured creation methods for CLI application components.
    """

    def __init__(self, mode: ConfigurationMode = ConfigurationMode.PRODUCTION):
        """Initialize CLI component factory.

        Args:
            mode: Configuration mode for component creation
        """
        container = ApplicationContainer()
        config = ComponentConfig(mode)
        super().__init__(container, config)

        logger.info(f"Initialized CLI component factory in {mode.value} mode")

    def create_cli_application(
        self,
        use_case: Any,
        hardware_facade: Optional[Any] = None,
        configuration_service: Optional[Any] = None,
    ) -> Any:
        """Create a CLI application with dependencies.

        Args:
            use_case: EOL test execution use case
            hardware_facade: Optional hardware service facade
            configuration_service: Optional configuration service

        Returns:
            CLI application instance with dependencies injected
        """
        from ..core.dependency_injected_cli_application import DependencyInjectedCLIApplication
        from ..usecase_manager import UseCaseManager
        from ..hardware_controller import HardwareControlManager
        from rich.console import Console

        # Create core components directly with proper dependencies
        console = Console(force_terminal=True, legacy_windows=False, color_system="truecolor")

        # Create formatter
        from ..rich_formatter import RichFormatter
        formatter = RichFormatter(console)

        # Create validator
        from ..validation.input_validator import InputValidator
        validator = InputValidator()

        # Create enhanced CLI integrator
        from ..enhanced_cli_integration import create_enhanced_cli_integrator, create_enhanced_menu_system
        enhanced_integrator = create_enhanced_cli_integrator(console, formatter, configuration_service)
        enhanced_menu = create_enhanced_menu_system(enhanced_integrator)

        # Create components with proper dependencies
        from ..session.session_manager import SessionManager
        from ..menu.menu_system import MenuSystem
        from ..execution.test_executor import TestExecutor

        session_manager = SessionManager(console, formatter)
        menu_system = MenuSystem(console, formatter, enhanced_menu)
        test_executor = TestExecutor(console, formatter, use_case, enhanced_integrator)

        # Create optional components
        usecase_manager = None
        if configuration_service:
            usecase_manager = UseCaseManager(console, configuration_service)

        hardware_manager = None
        if hardware_facade:
            hardware_manager = HardwareControlManager(
                hardware_facade, console, configuration_service
            )

        # Create dependency injected CLI application
        application = DependencyInjectedCLIApplication(
            session_manager=session_manager,
            menu_system=menu_system,
            test_executor=test_executor,
            validator=validator,
            formatter=formatter,
            console=console,
            use_case=use_case,
            hardware_facade=hardware_facade,
            configuration_service=configuration_service,
            usecase_manager=usecase_manager,
            hardware_manager=hardware_manager,
        )

        return application

    def create_session_manager(self) -> Any:
        """Create a session manager with dependencies.

        Returns:
            Session manager instance
        """
        from ..interfaces import ISessionManager
        return self.create(ISessionManager)

    def create_menu_system(self) -> Any:
        """Create a menu system with dependencies.

        Returns:
            Menu system instance
        """
        from ..interfaces import IMenuSystem
        return self.create(IMenuSystem)

    def create_test_executor(self) -> Any:
        """Create a test executor with dependencies.

        Returns:
            Test executor instance
        """
        from ..interfaces import ITestExecutor
        return self.create(ITestExecutor)

    def create_input_validator(self) -> Any:
        """Create an input validator with dependencies.

        Returns:
            Input validator instance
        """
        from ..interfaces import IInputValidator
        return self.create(IInputValidator)

    def create_formatter(self) -> Any:
        """Create a formatter with dependencies.

        Returns:
            Formatter instance
        """
        from ..interfaces import IFormatter
        return self.create(IFormatter)

    @classmethod
    def create_production_factory(cls) -> "CLIComponentFactory":
        """Create a factory configured for production mode.

        Returns:
            CLI component factory in production mode
        """
        return cls(ConfigurationMode.PRODUCTION)

    @classmethod
    def create_development_factory(cls) -> "CLIComponentFactory":
        """Create a factory configured for development mode.

        Returns:
            CLI component factory in development mode
        """
        return cls(ConfigurationMode.DEVELOPMENT)

    @classmethod
    def create_testing_factory(cls) -> "CLIComponentFactory":
        """Create a factory configured for testing mode.

        Returns:
            CLI component factory in testing mode
        """
        return cls(ConfigurationMode.TESTING)

    @classmethod
    def create_mock_factory(cls) -> "CLIComponentFactory":
        """Create a factory configured for mock mode.

        Returns:
            CLI component factory in mock mode
        """
        return cls(ConfigurationMode.MOCK)