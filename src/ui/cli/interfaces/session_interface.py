"""Session Management Interface

Defines the contract for session lifecycle management including startup,
shutdown, main execution loop, and state management for CLI applications.

This interface enables dependency injection and flexible implementation
substitution for different session management strategies.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# TYPE_CHECKING imports to avoid circular dependencies
if TYPE_CHECKING:
    from .menu_interface import IMenuSystem


class ISessionManager(ABC):
    """Abstract interface for session lifecycle management.

    Defines the contract for managing CLI session state, startup/shutdown
    procedures, and the main interactive loop. Implementations should provide
    comprehensive error handling and graceful resource management.

    Key Responsibilities:
    - Session state management and lifecycle control
    - Graceful startup and shutdown procedures
    - Interactive session main loop with error handling
    - Resource cleanup and state persistence
    - Integration with menu system for navigation
    """

    @abstractmethod
    def set_menu_system(self, menu_system: "IMenuSystem") -> None:
        """Set the menu system for session navigation.

        Args:
            menu_system: Menu system instance implementing IMenuSystem
        """
        ...

    @abstractmethod
    async def run_interactive(self) -> None:
        """Run the interactive CLI session with comprehensive error handling.

        Main session loop that handles startup, user interaction, and shutdown
        with proper exception handling and user feedback. Should manage the
        complete session lifecycle from initialization to cleanup.

        Raises:
            Exception: Various exceptions may be raised during session execution
        """
        ...

    @abstractmethod
    def stop_session(self) -> None:
        """Stop the current session.

        Sets the running flag to False to terminate the main loop.
        Should trigger graceful shutdown procedures.
        """
        ...

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Check if session is currently running.

        Returns:
            True if session is active, False otherwise
        """
        ...