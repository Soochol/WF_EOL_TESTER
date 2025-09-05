"""
Session Management Module

Session lifecycle management including startup, shutdown, main execution loop,
and state management for the CLI application.

Key Features:
- Session state management and lifecycle control
- Graceful startup and shutdown procedures
- Interactive session main loop with error handling
- Resource cleanup and state persistence
- Visual feedback during session operations
"""

# Standard library imports
from typing import TYPE_CHECKING, Optional

# Third-party imports
from loguru import logger
from rich.console import Console

# Local imports
from ..interfaces.session_interface import ISessionManager
from ..rich_formatter import RichFormatter

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from ..menu.menu_system import MenuSystem


class SessionManager(ISessionManager):
    """Session lifecycle management for CLI application.

    Manages the overall session state, startup/shutdown procedures,
    and the main interactive loop for the CLI application.
    """

    def __init__(self, console: Console, formatter: RichFormatter, emergency_stop_service=None):
        """Initialize session manager.

        Args:
            console: Rich console instance for output
            formatter: Rich formatter for professional output
            emergency_stop_service: Emergency stop service for hardware safety shutdown
        """
        self._console = console
        self._formatter = formatter
        self._running = False
        self._menu_system: Optional["MenuSystem"] = None
        self._emergency_stop_service = emergency_stop_service

        # Debug log to confirm emergency_stop_service injection
        logger.info(
            f"SessionManager initialized with emergency_stop_service: {emergency_stop_service is not None}"
        )
        if emergency_stop_service:
            logger.info(f"Emergency stop service type: {type(emergency_stop_service).__name__}")

    def set_menu_system(self, menu_system: "MenuSystem") -> None:
        """Set the menu system for session navigation.

        Args:
            menu_system: Menu system instance
        """
        self._menu_system = menu_system

    async def run_interactive(self) -> None:
        """Run the interactive CLI session with comprehensive error handling.

        Main session loop that handles startup, user interaction, and shutdown
        with proper exception handling and user feedback.
        """
        logger.info("Starting Enhanced EOL Tester CLI session")
        logger.debug(f"Emergency stop service: {self._emergency_stop_service}")

        try:
            # Perform session startup
            await self._startup()

            # Display welcome header
            self._formatter.print_header(
                "EOL Tester - Enhanced Version", "Professional End-of-Line Testing System"
            )

            # Main interactive loop
            while self._running:
                if self._menu_system:
                    try:
                        await self._menu_system.show_main_menu()
                    except KeyboardInterrupt:
                        logger.info(
                            "KeyboardInterrupt caught in main loop - re-raising to outer handler"
                        )
                        # Re-raise to trigger outer exception handler which handles emergency stop
                        raise
                else:
                    logger.error("Menu system not initialized")
                    break

        except KeyboardInterrupt:
            logger.info("SessionManager: KeyboardInterrupt caught!")
            # Emergency stop is only needed when UseCase is running
            # BaseUseCase handles it if active, otherwise just exit cleanly

            self._formatter.print_message(
                "Exiting EOL Tester... Goodbye!", message_type="info", title="Shutdown"
            )
            logger.info("CLI interrupted by user")
        except Exception as e:
            self._formatter.print_message(
                f"Unexpected error occurred: {e}", message_type="error", title="System Error"
            )
            logger.error(f"CLI session error: {e}")
        finally:
            self._running = False
            await self._shutdown()

    async def _startup(self) -> None:
        """Perform session startup procedures.

        Initialize session state and prepare for interactive operation.
        """
        logger.debug("Performing session startup")
        self._running = True

        # Additional startup procedures can be added here
        # such as configuration loading, hardware initialization, etc.

    async def _shutdown(self) -> None:
        """Perform graceful session shutdown.

        Handles session-level cleanup with proper error handling.
        Hardware cleanup is handled at the use case level.
        """
        logger.info("Shutting down CLI session")

        try:
            self._console.print("[blue]Shutting down session...[/blue]")

            # Session-level cleanup only
            logger.debug("Performing session cleanup...")
            # NOTE: Session-specific cleanup can be added here
            # such as saving session state, cleaning temporary UI state, etc.

            logger.debug("CLI session shutdown completed successfully")

        except Exception as e:
            # Log shutdown errors but don't prevent shutdown completion
            logger.warning(f"Error during session shutdown: {e}")

        logger.info("CLI session shutdown complete")

    def stop_session(self) -> None:
        """Stop the current session.

        Sets the running flag to False to terminate the main loop.
        """
        self._running = False
        logger.debug("Session stop requested")

    @property
    def is_running(self) -> bool:
        """Check if session is currently running.

        Returns:
            True if session is active, False otherwise
        """
        return self._running
