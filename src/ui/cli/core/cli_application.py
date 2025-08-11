"""
CLI Application Core Module

Main CLI application class with focused responsibility and composition-based
architecture. Orchestrates specialized components to provide comprehensive
EOL testing functionality.

Key Features:
- Composition-based architecture with specialized components
- Dependency injection for flexible configuration
- Professional Rich UI integration
- Comprehensive error handling and logging
- Hardware integration with fallback handling
"""

# Standard library imports
from typing import TYPE_CHECKING, Any, Optional

# Third-party imports
from loguru import logger
from rich.console import Console

# Local imports - Application layer
from application.use_cases.eol_force_test import EOLForceTestUseCase

# Local imports - UI modules
from ..config_reader import CLIConfigReader
from ..enhanced_cli_integration import (
    create_enhanced_cli_integrator,
    create_enhanced_menu_system,
)
from ..execution.test_executor import TestExecutor
from ..hardware_controller import HardwareControlManager
from ..menu.menu_system import MenuSystem
from ..rich_formatter import RichFormatter
from ..session.session_manager import SessionManager
from ..usecase_manager import UseCaseManager
from ..validation.input_validator import InputValidator
from ..interfaces.application_interface import ICLIApplication
from ..interfaces.validation_interface import IInputValidator

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from application.services.hardware_service_facade import HardwareServiceFacade


class CLIApplication(ICLIApplication):
    """Main CLI application with composition-based architecture.

    Coordinates specialized components to provide comprehensive EOL testing
    functionality with professional user interface and robust error handling.
    """

    def __init__(
        self,
        use_case: EOLForceTestUseCase,
        hardware_facade: Optional["HardwareServiceFacade"] = None,
        configuration_service: Optional[Any] = None,
    ):
        """Initialize the CLI application with dependency injection.

        Args:
            use_case: EOL test execution use case
            hardware_facade: Hardware service facade for individual hardware control
            configuration_service: Configuration service for loading DUT defaults
        """
        # Store dependencies
        self._use_case = use_case
        self._hardware_facade = hardware_facade
        self._configuration_service = configuration_service

        # Initialize core components
        self._console = Console(
            force_terminal=True,
            legacy_windows=False,
            color_system="truecolor"
        )
        self._formatter = RichFormatter(self._console)
        self._validator = InputValidator()

        # Initialize enhanced input system
        self._input_integrator = create_enhanced_cli_integrator(
            self._console, self._formatter, self._configuration_service
        )
        self._enhanced_menu = create_enhanced_menu_system(self._input_integrator)

        # Initialize specialized components
        self._session_manager = SessionManager(self._console, self._formatter)
        self._menu_system = MenuSystem(
            self._console,
            self._formatter,
            self._enhanced_menu
        )
        self._test_executor = TestExecutor(
            self._console,
            self._formatter,
            self._use_case,
            self._input_integrator
        )
        self._usecase_manager = UseCaseManager(
            self._console,
            self._configuration_service
        )

        # Setup component relationships
        self._session_manager.set_menu_system(self._menu_system)
        self._menu_system.set_session_manager(self._session_manager)
        self._menu_system.set_test_executor(self._test_executor)
        self._menu_system.set_usecase_manager(self._usecase_manager)

        # Initialize hardware control manager if hardware facade is provided
        self._hardware_manager: Optional[Any] = None
        self._config_reader: Optional[CLIConfigReader] = None

        if self._hardware_facade:
            self._hardware_manager = HardwareControlManager(
                self._hardware_facade,
                self._console,
                self._configuration_service
            )
            self._menu_system.set_hardware_manager(self._hardware_manager)

            # Initialize configuration reader for CLI commands
            self._config_reader = CLIConfigReader()

    async def run_interactive(self) -> None:
        """Run the interactive CLI application.

        Delegates to the session manager for comprehensive session handling.
        """
        logger.info("Starting CLI Application")

        try:
            await self._session_manager.run_interactive()
        except Exception as e:
            logger.error(f"CLI Application error: {e}")
            self._formatter.print_message(
                f"Application error: {str(e)}",
                message_type="error",
                title="System Error"
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
        if not value:
            self._session_manager.stop_session()

    # Legacy compatibility methods for external access
    def get_console(self) -> Console:
        """Get console instance for external components.

        Returns:
            Rich console instance
        """
        return self._console

    def get_formatter(self) -> RichFormatter:
        """Get formatter instance for external components.

        Returns:
            Rich formatter instance
        """
        return self._formatter

    def get_validator(self) -> IInputValidator:
        """Get validator instance for external components.

        Returns:
            Input validator instance
        """
        return self._validator

    def get_hardware_manager(self) -> Optional[Any]:
        """Get hardware manager instance for external components.

        Returns:
            Hardware manager instance if available, None otherwise
        """
        return self._hardware_manager

    def get_usecase_manager(self) -> UseCaseManager:
        """Get usecase manager instance for external components.

        Returns:
            UseCase manager instance
        """
        return self._usecase_manager
