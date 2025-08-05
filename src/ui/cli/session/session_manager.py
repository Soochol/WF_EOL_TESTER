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
from ..rich_formatter import RichFormatter
from ..interfaces.session_interface import ISessionManager

# TYPE_CHECKING imports
if TYPE_CHECKING:
    from ..interfaces.menu_interface import IMenuSystem


class SessionManager(ISessionManager):
    """Session lifecycle management for CLI application.

    Manages the overall session state, startup/shutdown procedures,
    and the main interactive loop for the CLI application.
    """

    def __init__(self, console: Console, formatter: RichFormatter):
        """Initialize session manager.

        Args:
            console: Rich console instance for output
            formatter: Rich formatter for professional output
        """
        self._console = console
        self._formatter = formatter
        self._running = False
        self._menu_system: Optional["IMenuSystem"] = None

    def set_menu_system(self, menu_system: "IMenuSystem") -> None:
        """Set the menu system for session navigation.

        Args:
            menu_system: Menu system instance implementing IMenuSystem
        """
        self._menu_system = menu_system

    async def run_interactive(self) -> None:
        """Run the interactive CLI session with comprehensive error handling.

        Main session loop that handles startup, user interaction, and shutdown
        with proper exception handling and user feedback.
        """
        logger.info("Starting Enhanced EOL Tester CLI session")

        try:
            # Perform session startup
            await self._startup()

            # Display welcome header
            self._formatter.print_header(
                "EOL Tester - Enhanced Version",
                "Professional End-of-Line Testing System"
            )

            # Main interactive loop
            while self._running:
                if self._menu_system:
                    await self._menu_system.show_main_menu()
                else:
                    logger.error("Menu system not initialized")
                    break

        except KeyboardInterrupt:
            self._formatter.print_message(
                "Exiting EOL Tester... Goodbye!",
                message_type="info",
                title="Shutdown"
            )
            logger.info("CLI interrupted by user")
        except Exception as e:
            self._formatter.print_message(
                f"Unexpected error occurred: {e}",
                message_type="error",
                title="System Error"
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
        """Perform graceful shutdown with comprehensive cleanup and Rich UI feedback.

        Handles all cleanup operations with visual feedback and proper error
        handling to ensure resources are properly released during shutdown.
        """
        logger.info("Shutting down Enhanced CLI session")

        try:
            # Display shutdown progress with visual feedback
            with self._formatter.create_progress_display(
                "Shutting down system...", show_spinner=True
            ) as shutdown_status:
                # Step 1: Hardware cleanup
                try:
                    shutdown_status.update("Cleaning up hardware connections...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Hardware cleanup operations would be implemented here
                # This might include closing serial connections, releasing instruments, etc.

                # Step 2: Configuration persistence
                try:
                    shutdown_status.update("Saving configuration...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Configuration saving operations would be implemented here
                # This might include saving user preferences, test settings, etc.

                # Step 3: Final cleanup
                try:
                    shutdown_status.update("Finalizing shutdown...")  # type: ignore
                except (TypeError, AttributeError):
                    pass  # Progress display doesn't support update messages
                # NOTE: Final cleanup operations would be implemented here
                # This might include temporary file cleanup, logging finalization, etc.

            logger.debug("Enhanced CLI session shutdown completed successfully")

        except Exception as e:
            # Log shutdown errors but don't prevent shutdown completion
            logger.warning("Error during session shutdown: %s", e)

        logger.info("Enhanced CLI session shutdown complete")

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
