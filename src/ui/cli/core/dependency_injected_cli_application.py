"""Dependency Injected CLI Application

CLI Application implementation that uses dependency injection for all components.
This replaces the original CLIApplication with proper dependency injection
patterns while maintaining the same interface.

Key Features:
- Full dependency injection for all components
- Interface-based design
- Configuration-driven component creation
- Flexible component substitution
- Testability and maintainability
"""

# Standard library imports
from typing import TYPE_CHECKING, Any, Optional

# Third-party imports
from loguru import logger
from rich.console import Console

# Local imports - Application layer
from application.use_cases.eol_force_test import EOLForceTestUseCase

# Local imports - UI interfaces
from ..interfaces.application_interface import ICLIApplication
from ..interfaces.execution_interface import ITestExecutor
from ..interfaces.formatter_interface import IFormatter
from ..interfaces.menu_interface import IMenuSystem
from ..interfaces.session_interface import ISessionManager
from ..interfaces.validation_interface import IInputValidator
from ..usecase_manager import UseCaseManager

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from application.services.hardware_service_facade import HardwareServiceFacade


class DependencyInjectedCLIApplication(ICLIApplication):
    """CLI Application with full dependency injection.

    Implements the CLI application using dependency injection for all components.
    All dependencies are injected through the constructor, enabling flexible
    component substitution and improved testability.
    """

    def __init__(
        self,
        session_manager: ISessionManager,
        menu_system: IMenuSystem,
        test_executor: ITestExecutor,
        validator: IInputValidator,
        formatter: IFormatter,
        console: Console,
        use_case: EOLForceTestUseCase,
        hardware_facade: Optional["HardwareServiceFacade"] = None,
        configuration_service: Optional[Any] = None,
        usecase_manager: Optional[UseCaseManager] = None,
        hardware_manager: Optional[Any] = None,
    ):
        """Initialize CLI application with injected dependencies.

        Args:
            session_manager: Session lifecycle manager
            menu_system: Menu display and navigation system
            test_executor: Test execution coordinator
            validator: Input validation utility
            formatter: UI formatting utility
            console: Rich console for output
            use_case: EOL test execution use case
            hardware_facade: Optional hardware service facade
            configuration_service: Optional configuration service
            usecase_manager: Optional usecase manager
            hardware_manager: Optional hardware manager
        """
        # Store injected dependencies
        self._session_manager = session_manager
        self._menu_system = menu_system
        self._test_executor = test_executor
        self._validator = validator
        self._formatter = formatter
        self._console = console
        self._use_case = use_case
        self._hardware_facade = hardware_facade
        self._configuration_service = configuration_service
        self._usecase_manager = usecase_manager
        self._hardware_manager = hardware_manager

        # Initialize configuration reader if hardware facade is provided
        self._config_reader: Optional[Any] = None
        if self._hardware_facade:
            from ..config_reader import CLIConfigReader

            self._config_reader = CLIConfigReader()

        # Setup component relationships
        self._setup_component_relationships()

        logger.info("Dependency injected CLI application initialized")

    def _setup_component_relationships(self) -> None:
        """Setup relationships between injected components."""
        # Setup bidirectional relationships
        self._session_manager.set_menu_system(self._menu_system)
        self._menu_system.set_session_manager(self._session_manager)
        self._menu_system.set_test_executor(self._test_executor)

        # Setup optional components
        if self._usecase_manager:
            self._menu_system.set_usecase_manager(self._usecase_manager)

        if self._hardware_manager:
            self._menu_system.set_hardware_manager(self._hardware_manager)

        logger.debug("Component relationships configured")

    async def run_interactive(self) -> None:
        """Run the interactive CLI application.

        Delegates to the session manager for comprehensive session handling.
        """
        logger.info("Starting dependency injected CLI application")

        try:
            await self._session_manager.run_interactive()
        except Exception as e:
            logger.error(f"CLI Application error: {e}")
            self._formatter.print_message(
                f"Application error: {str(e)}", message_type="error", title="System Error"
            )
        finally:
            logger.info("CLI Application shutdown complete")

    # Legacy compatibility properties
    @property
    def _running(self) -> bool:
        """Legacy compatibility property for running state.

        Returns:
            True if session is running, False otherwise
        """
        return self._session_manager.is_running

    @_running.setter
    def _running(self, value: bool) -> None:
        """Legacy compatibility setter for running state.

        Args:
            value: New running state value
        """
        if value:
            # Note: Cannot directly set running=True through interface
            # Session must be started via run_interactive() method
            pass  # Running state is managed internally by session manager
        else:
            self._session_manager.stop_session()

    # Component access methods for external integration
    def get_console(self) -> Console:
        """Get console instance for external components.

        Returns:
            Rich console instance
        """
        return self._console

    def get_formatter(self) -> IFormatter:
        """Get formatter instance for external components.

        Returns:
            Formatter instance implementing IFormatter
        """
        return self._formatter

    def get_validator(self) -> IInputValidator:
        """Get validator instance for external components.

        Returns:
            Input validator instance implementing IInputValidator
        """
        return self._validator

    def get_hardware_manager(self) -> Optional[Any]:
        """Get hardware manager instance for external components.

        Returns:
            Hardware manager instance if available, None otherwise
        """
        return self._hardware_manager

    def get_usecase_manager(self) -> Optional[UseCaseManager]:
        """Get usecase manager instance for external components.

        Returns:
            UseCase manager instance if available, None otherwise
        """
        return self._usecase_manager
