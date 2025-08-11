"""Formatter Interface

Defines the contract for UI formatting with Rich UI components and consistent
styling. Extends existing formatter interfaces to ensure consistent formatting
contract and UI display methods across all components.

This interface enables dependency injection and flexible implementation
substitution for different formatting strategies.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# TYPE_CHECKING imports to avoid circular dependencies
if TYPE_CHECKING:
    from domain.value_objects.eol_test_result import EOLTestResult


class IFormatter(ABC):
    """Abstract interface for UI formatting with Rich components.

    Defines the contract for consistent formatting and display methods
    across all CLI components. Implementations should provide professional
    Rich UI formatting with comprehensive styling and visual feedback.

    Key Responsibilities:
    - Consistent formatting contract across components
    - Professional Rich UI integration
    - Visual feedback and progress indication
    - Table and panel creation with consistent styling
    - Message formatting with appropriate visual cues
    """

    @property
    @abstractmethod
    def console(self) -> Console:
        """Get the Rich console instance.

        Returns:
            Rich Console instance for output operations
        """
        ...

    @abstractmethod
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a professional header banner.

        Args:
            title: Main header title
            subtitle: Optional subtitle text
        """
        ...

    @abstractmethod
    def print_message(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
    ) -> None:
        """Print a formatted message panel.

        Args:
            message: Message content to display
            message_type: Type of message (info, success, warning, error)
            title: Optional panel title
        """
        ...

    @abstractmethod
    def print_status(
        self,
        title: str,
        status: str,
        details: Optional[Dict[str, str]] = None,
    ) -> None:
        """Print a status panel with details.

        Args:
            title: Status title
            status: Current status value
            details: Optional dictionary of additional details
        """
        ...

    @abstractmethod
    def create_message_panel(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
    ) -> Panel:
        """Create a formatted message panel.

        Args:
            message: Message content
            message_type: Type of message for styling
            title: Optional panel title

        Returns:
            Rich Panel with formatted message
        """
        ...

    @abstractmethod
    def create_test_results_table(
        self,
        results: List["EOLTestResult"],
        title: str = "Test Results",
        show_details: bool = False,
    ) -> Table:
        """Create a formatted test results table.

        Args:
            results: List of test results to display
            title: Table title
            show_details: Whether to show detailed information

        Returns:
            Rich Table with formatted test results
        """
        ...

    @abstractmethod
    def print_table(self, table: Table) -> None:
        """Print a Rich table to the console.

        Args:
            table: Rich Table instance to display
        """
        ...

    @abstractmethod
    def create_progress_display(
        self, description: str, show_spinner: bool = True
    ) -> Any:
        """Create a progress display context manager.

        Args:
            description: Progress description text
            show_spinner: Whether to show a spinner animation

        Returns:
            Context manager for progress display
        """
        ...