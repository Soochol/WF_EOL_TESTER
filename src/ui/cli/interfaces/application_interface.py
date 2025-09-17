"""CLI Application Interface

Defines the contract for main CLI application with composition-based architecture.
Orchestrates specialized components to provide comprehensive EOL testing
functionality with professional user interface and robust error handling.

This interface enables dependency injection and flexible implementation
substitution for different application strategies.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

# Third-party imports
from rich.console import Console

# Local folder imports
from .validation_interface import IInputValidator


# TYPE_CHECKING imports to avoid circular dependencies
if TYPE_CHECKING:
    # Local folder imports
    from ..rich_formatter import RichFormatter
    from ..usecase_manager import UseCaseManager


class ICLIApplication(ABC):
    """Abstract interface for main CLI application.

    Defines the contract for coordinating specialized components to provide
    comprehensive EOL testing functionality with professional user interface
    and robust error handling. Implementations should use composition-based
    architecture and dependency injection.

    Key Responsibilities:
    - Composition-based architecture with specialized components
    - Dependency injection for flexible configuration
    - Professional Rich UI integration
    - Comprehensive error handling and logging
    - Hardware integration with fallback handling
    """

    @abstractmethod
    async def run_interactive(self) -> None:
        """Run the interactive CLI application.

        Delegates to the session manager for comprehensive session handling.
        Should provide complete application lifecycle management with proper
        error handling and resource cleanup.

        Raises:
            Exception: Various exceptions may be raised during application execution
        """
        ...

    # Legacy compatibility properties
    @property
    @abstractmethod
    def _running(self) -> bool:
        """Legacy compatibility property for running state.

        Returns:
            True if session is running, False otherwise
        """
        ...

    @_running.setter
    @abstractmethod
    def _running(self, value: bool) -> None:
        """Legacy compatibility setter for running state.

        Args:
            value: New running state value
        """
        ...

    # Component access methods for external integration
    @abstractmethod
    def get_console(self) -> Console:
        """Get console instance for external components.

        Returns:
            Rich console instance
        """
        ...

    @abstractmethod
    def get_formatter(self) -> "RichFormatter":
        """Get formatter instance for external components.

        Returns:
            Rich formatter instance
        """
        ...

    @abstractmethod
    def get_validator(self) -> IInputValidator:
        """Get validator instance for external components.

        Returns:
            Input validator instance implementing IInputValidator
        """
        ...

    @abstractmethod
    def get_hardware_manager(self) -> Optional[Any]:
        """Get hardware manager instance for external components.

        Returns:
            Hardware manager instance if available, None otherwise
        """
        ...

    @abstractmethod
    def get_usecase_manager(self) -> "UseCaseManager":
        """Get usecase manager instance for external components.

        Returns:
            UseCase manager instance
        """
        ...
