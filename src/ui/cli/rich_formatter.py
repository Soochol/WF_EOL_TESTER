"""Rich UI Formatter Module - Refactored with Specialized Formatters

Refactored Rich UI formatter class for the EOL Tester CLI application that uses
composition with specialized formatter classes. This module serves as a facade
that delegates to specialized formatters while maintaining the same public API
for backward compatibility.

This approach provides better separation of concerns, improved maintainability,
and focused responsibilities while preserving all existing functionality.
"""

from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.layout import Layout
from rich.progress import Progress
from rich.status import Status
from rich.table import Table

from domain.enums.test_status import TestStatus
from domain.value_objects.eol_test_result import EOLTestResult

from .interfaces.formatter_interface import IFormatter
from .presentation.formatters import (
    BaseFormatter,
    LayoutFormatter,
    ProgressFormatter,
    StatusFormatter,
    TableFormatter,
)


class RichFormatter(IFormatter):
    """Comprehensive Rich UI formatter using specialized formatter composition.

    This class serves as a facade that delegates to specialized formatter classes
    while maintaining the same public API as the original RichFormatter. It uses
    composition to organize formatting responsibilities into focused classes:

    - StatusFormatter: Status panels and hardware displays
    - TableFormatter: Test results tables and statistics tables
    - ProgressFormatter: Progress bars and spinners
    - LayoutFormatter: Multi-component layouts and arrangements
    - BaseFormatter: Common utilities and theme integration

    Key Features:
    - Maintains full backward compatibility with existing API
    - Improved separation of concerns through specialized formatters
    - Better maintainability with focused responsibilities
    - Consistent styling and theme integration across all formatters
    - Professional appearance and comprehensive functionality
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the Rich formatter with specialized formatter composition.

        Args:
            console: Optional Rich Console instance. If None, creates a new one
                    with default settings optimized for the EOL Tester application.
        """
        # Initialize console - shared across all formatters with Windows-compatible settings
        self._console = console or Console(
            force_terminal=True, 
            legacy_windows=True,  # Enable legacy Windows compatibility
            color_system="auto",  # Auto-detect color support
            width=95,  # Match panel width for consistency
            safe_box=True,  # Use ASCII box drawing for better compatibility
        )

        # Initialize specialized formatters with shared console
        self._status_formatter = StatusFormatter(self._console)
        self._table_formatter = TableFormatter(self._console)
        self._progress_formatter = ProgressFormatter(self._console)
        self._layout_formatter = LayoutFormatter(self._console)
        self._base_formatter = BaseFormatter(self._console)

        # Expose theme components for backward compatibility
        self.colors = self._base_formatter.colors
        self.icons = self._base_formatter.icons
        self.layout = self._base_formatter.layout

    @property
    def console(self) -> Console:
        """Get the Rich console instance.

        Returns:
            Rich Console instance for output operations
        """
        return self._console

    # Header and message methods (delegated to BaseFormatter)
    def create_header_banner(
        self,
        title: str,
        subtitle: Optional[str] = None,
        width: Optional[int] = None,
    ):
        """Create a professional header banner with consistent styling.

        Delegates to BaseFormatter for consistent header creation.
        """
        return self._base_formatter.create_header_banner(title, subtitle, width)

    def create_message_panel(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
        width: Optional[int] = None,
    ):
        """Create a formatted message panel with appropriate styling.

        Delegates to BaseFormatter for consistent message panel creation.
        """
        return self._base_formatter.create_message_panel(message, message_type, title, width)

    # Status methods (delegated to StatusFormatter)
    def create_status_panel(
        self,
        title: str,
        status: Union[str, TestStatus],
        details: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
    ):
        """Create a status panel with intelligent color coding and icons.

        Delegates to StatusFormatter for specialized status handling.
        """
        return self._status_formatter.create_status_panel(title, status, details, icon)

    def create_hardware_status_display(
        self,
        hardware_status: Dict[str, Any],
        title: str = "Hardware Status",
    ):
        """Create a hardware status display with intelligent color coding.

        Delegates to StatusFormatter for specialized hardware status formatting.
        """
        return self._status_formatter.create_hardware_status_display(hardware_status, title)

    # Table methods (delegated to TableFormatter)
    def create_test_results_table(
        self,
        results: List[Union[EOLTestResult, Dict[str, Any]]],
        title: str = "Test Results",
        show_details: bool = True,
        dut_info: Optional[Dict[str, str]] = None,
    ) -> Table:
        """Create a rich table for displaying test results with flexible formatting.

        Delegates to TableFormatter for specialized table creation and formatting.
        """
        return self._table_formatter.create_test_results_table(results, title, show_details, dut_info)

    # Progress methods (delegated to ProgressFormatter)
    def create_progress_display(
        self, description: str, show_spinner: bool = True
    ) -> Union[Progress, Status]:
        """Create a progress display for long-running operations.

        Delegates to ProgressFormatter for specialized progress handling.
        """
        return self._progress_formatter.create_progress_display(description, show_spinner)

    # Layout methods (delegated to LayoutFormatter)
    def create_statistics_display(
        self,
        statistics: Dict[str, Any],
        title: str = "Test Statistics",
    ):
        """Create a comprehensive statistics display panel.

        Delegates to LayoutFormatter for specialized statistics layout.
        """
        return self._layout_formatter.create_statistics_display(statistics, title)

    def create_layout(
        self,
        components: Dict[str, Any],
        layout_type: str = "vertical",
    ) -> Layout:
        """Create a rich layout with multiple components using strategy pattern.

        Delegates to LayoutFormatter for specialized layout creation.
        """
        return self._layout_formatter.create_layout(components, layout_type)

    # Convenience methods for console output
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a header banner to the console."""
        self._base_formatter.print_header(title, subtitle)

    def print_status(
        self,
        title: str,
        status: Union[str, TestStatus],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Print a status panel to the console."""
        self._status_formatter.print_status(title, status, details)

    def print_message(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
    ) -> None:
        """Print a formatted message to the console."""
        self._base_formatter.print_message(message, message_type, title)

    def print_table(self, table: Table) -> None:
        """Print a table to the console."""
        self._table_formatter.print_table(table)

    def print_menu(self, menu_options: Dict[str, str]) -> None:
        """Print menu options to the console.

        Args:
            menu_options: Dictionary of option number to description
        """
        self._console.print("\n📋 Menu Options:", style="bold cyan")
        for key, description in menu_options.items():
            self._console.print(f"  {key}. {description}")
        self._console.print()

    def print_title(self, title: str) -> None:
        """Print a formatted title to the console.

        Args:
            title: Title text to display
        """
        self._console.print(f"\n{title}", style="bold magenta")
        self._console.print("=" * len(title), style="magenta")

    # Additional methods that might be used by existing code
    def _truncate_string(self, text: str, max_length: Optional[int] = None) -> str:
        """Truncate string to specified length with ellipsis.

        Delegates to BaseFormatter for consistent text handling.
        """
        return self._base_formatter._truncate_text(  # pylint: disable=protected-access
            text, max_length
        )

    def _get_status_icon(self, status: TestStatus) -> str:
        """Get appropriate icon for test status.

        Delegates to BaseFormatter for consistent icon handling.
        """
        return self._base_formatter._get_status_icon(status)  # pylint: disable=protected-access

    # Backward compatibility aliases
    def _truncate_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Alias for _truncate_string for backward compatibility."""
        return self._truncate_string(text, max_length)

    def _create_model_stats_table(self, model_stats: Dict[str, Dict[str, Any]]) -> Table:
        """Create a table for model statistics.

        Delegates to TableFormatter for specialized table creation.
        """
        return self._table_formatter.create_statistics_table_by_model(model_stats)
