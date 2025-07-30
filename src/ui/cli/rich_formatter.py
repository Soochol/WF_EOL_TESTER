"""
Rich UI Formatter Module

Comprehensive Rich UI formatter class for the EOL Tester CLI application.
Provides centralized styling and formatting for beautiful terminal output with
consistent visual design and professional appearance.

This module encapsulates all Rich UI formatting logic, making it easy to maintain
consistent styling across the entire CLI application while providing flexibility
for different display contexts and user interface scenarios.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.status import Status
from rich.table import Table
from rich.text import Text

from domain.enums.test_status import TestStatus
from domain.value_objects.eol_test_result import EOLTestResult


# UI Constants for consistent formatting and maintainability
class UIConstants:
    """UI formatting constants that eliminate magic numbers and ensure consistent display.

    These constants define standard dimensions, timing, and layout parameters
    used throughout the Rich UI system to maintain visual consistency and
    improve code maintainability.
    """

    # Text truncation lengths for consistent display widths
    DEFAULT_TRUNCATE_LENGTH = 10  # Standard truncation for short fields
    EXTENDED_TRUNCATE_LENGTH = 15  # Extended truncation for medium fields
    MAX_TEXT_DISPLAY_LENGTH = 50  # Maximum before forced truncation

    # Table column widths for optimal readability
    STATUS_COLUMN_WIDTH = 10  # Status indicator column
    TEST_ID_COLUMN_WIDTH = 12  # Test identifier column
    DUT_ID_COLUMN_WIDTH = 15  # Device under test ID column
    MODEL_COLUMN_WIDTH = 12  # Model number column
    DURATION_COLUMN_WIDTH = 10  # Test duration column
    MEASUREMENTS_COLUMN_WIDTH = 12  # Measurement count column
    TIMESTAMP_COLUMN_WIDTH = 16  # Timestamp display column

    # Panel padding for consistent spacing
    DEFAULT_PANEL_PADDING = (1, 2)  # Standard panel padding (vertical, horizontal)
    HEADER_PANEL_PADDING = (1, 2)  # Header panel padding

    # Grid layout constraints for organized display
    MAX_GRID_COMPONENTS = 4  # Maximum components in grid layout
    GRID_TOP_COMPONENTS = 2  # Components in top row of grid

    # Animation and timing for smooth user experience
    DEFAULT_REFRESH_RATE = 4  # Updates per second for live displays
    PROGRESS_UPDATE_DELAY = 0.1  # Seconds between progress updates


class RichFormatter:
    """Comprehensive Rich UI formatter for EOL Tester CLI application.

    This class serves as the central hub for all Rich UI formatting operations,
    providing methods to create beautiful, consistent terminal output. It encapsulates
    styling decisions, color schemes, and layout patterns to ensure a professional
    appearance throughout the CLI application.

    Key Features:
    - Centralized color scheme and styling management
    - Consistent table formatting with customizable details
    - Professional status displays with appropriate icons
    - Flexible layout system with multiple arrangement options
    - Comprehensive progress indication for long operations
    """

    # Professional color scheme optimized for readability and accessibility
    COLORS = {
        "primary": "#2E86C1",  # Professional blue - main accent color
        "secondary": "#48C9B0",  # Teal - secondary operations and highlights
        "success": "#58D68D",  # Green - successful operations and confirmations
        "warning": "#F7DC6F",  # Yellow - warnings and cautions
        "error": "#EC7063",  # Red - errors and failures
        "info": "#85C1E9",  # Light blue - informational content
        "accent": "#BB8FCE",  # Purple - special emphasis and decorative elements
        "text": "#F8F9FA",  # Light text - primary readable content
        "muted": "#AEB6BF",  # Muted text - secondary information and labels
        "background": "#34495E",  # Dark background - container backgrounds
        "border": "#5D6D7E",  # Border color - panel and table borders
    }

    # Status color mapping for intuitive visual feedback
    STATUS_COLORS = {
        TestStatus.NOT_STARTED: "muted",  # Inactive/waiting states
        TestStatus.PREPARING: "info",  # Preparation and setup phases
        TestStatus.RUNNING: "primary",  # Active execution states
        TestStatus.COMPLETED: "success",  # Successful completion
        TestStatus.FAILED: "error",  # Test failures
        TestStatus.CANCELLED: "warning",  # User-cancelled operations
        TestStatus.ERROR: "error",  # System errors and exceptions
    }

    # Unicode icons for enhanced visual communication
    ICONS = {
        "success": "✅",  # Successful operations and confirmations
        "error": "❌",  # Errors and failures
        "warning": "⚠️",  # Warnings and cautions
        "info": "ℹ️",  # Informational content
        "running": "🔄",  # Active processes and operations
        "hardware": "🔧",  # Hardware-related displays
        "test": "🧪",  # Test operations and results
        "report": "📊",  # Reports and statistics
        "settings": "⚙️",  # Configuration and settings
        "clock": "⏱️",  # Time-related information
        "check": "✓",  # Simple check marks
        "cross": "✗",  # Simple failure indicators
        "arrow_right": "➤",  # Navigation and flow indicators
        "bullet": "•",  # List items and bullet points
    }

    def __init__(self, console: Optional[Console] = None):
        """Initialize the Rich formatter with console configuration.

        Args:
            console: Optional Rich Console instance. If None, creates a new one
                    with default settings optimized for the EOL Tester application.
        """
        self.console = console or Console(
            force_terminal=True,
            legacy_windows=False,
            color_system="truecolor"
        )

    def create_header_banner(
        self,
        title: str,
        subtitle: Optional[str] = None,
        width: Optional[int] = None,
    ) -> Panel:
        """Create a professional header banner with consistent styling.

        Generates an attractive header panel suitable for application titles,
        section headers, and major operation announcements. The header uses
        centered text alignment and professional color scheme.

        Args:
            title: Main title text to display prominently
            subtitle: Optional subtitle text displayed below the main title
            width: Optional width override for the panel (auto-sized if None)

        Returns:
            Rich Panel containing the formatted header with appropriate styling
        """
        content = Text(title, style=f"bold {self.COLORS['text']}")
        content.justify = "center"

        if subtitle:
            content.append("\n")
            subtitle_text = Text(subtitle, style=self.COLORS["muted"])
            subtitle_text.justify = "center"
            content.append(subtitle_text)

        return Panel(
            content,
            style=self.COLORS["primary"],
            border_style=self.COLORS["border"],
            width=width,
            padding=UIConstants.HEADER_PANEL_PADDING,
        )

    def create_status_panel(
        self,
        title: str,
        status: Union[str, TestStatus],
        details: Optional[Dict[str, Any]] = None,
        icon: Optional[str] = None,
    ) -> Panel:
        """Create a status panel with intelligent color coding and icons.

        Generates a status display panel that automatically applies appropriate
        colors and icons based on the status value. Supports both string statuses
        and TestStatus enum values for maximum flexibility.

        Args:
            title: Panel title describing what status is being shown
            status: Status value (string or TestStatus enum) determining color/icon
            details: Optional dictionary of additional details to display below status
            icon: Optional icon override to replace automatic icon selection

        Returns:
            Rich Panel with formatted status information and appropriate visual styling
        """
        # Determine status color and icon
        if isinstance(status, TestStatus):
            color = self.COLORS[self.STATUS_COLORS[status]]
            status_text = status.value.upper().replace("_", " ")
            if not icon:
                icon = self._get_status_icon(status)
        else:
            color = self.COLORS["info"]
            status_text = str(status)
            if not icon:
                icon = self.ICONS["info"]

        # Create status content
        content = Text()
        content.append(f"{icon} ")
        content.append(f"{title}: ")
        content.append(status_text, style=color)

        # Add details if provided
        if details:
            content.append("\n\n")
            for key, value in details.items():
                content.append(f"{self.ICONS['bullet']} {key}: ")
                content.append(f"{value}\n", style=self.COLORS["text"])

        return Panel(
            content,
            border_style=color,
            padding=UIConstants.DEFAULT_PANEL_PADDING,
        )

    def create_test_results_table(
        self,
        test_results: List[Union[EOLTestResult, Dict[str, Any]]],
        title: str = "Test Results",
        show_details: bool = True,
    ) -> Table:
        """Create a rich table for displaying test results with flexible formatting.

        Generates a professionally formatted table that can handle both EOLTestResult
        objects and dictionary-based test results. The table automatically adjusts
        its columns based on the show_details parameter for optimal display.

        Args:
            test_results: List of test results to display (mixed types supported)
            title: Table title displayed at the top of the table
            show_details: Whether to include detailed columns (model, duration, measurements)

        Returns:
            Rich Table with formatted test results and appropriate column styling
        """
        table = self._create_base_table(title, show_details)

        # Add rows
        for result in test_results:
            if isinstance(result, EOLTestResult):
                row_data = self._format_eol_result_row(result, show_details)
            else:  # Dict format from repository
                row_data = self._format_dict_result_row(result, show_details)

            table.add_row(*row_data)

        return table

    def create_hardware_status_display(
        self,
        hardware_status: Dict[str, Any],
        title: str = "Hardware Status",
    ) -> Panel:
        """Create a hardware status display with intelligent color coding.

        Generates a comprehensive hardware status panel that displays the current
        state of all hardware components with appropriate visual indicators.
        Supports both simple status strings and detailed status dictionaries.

        Args:
            hardware_status: Dictionary containing hardware component status information
            title: Display title for the hardware status panel

        Returns:
            Rich Panel with formatted hardware status and color-coded indicators
        """
        content = []

        for component, status in hardware_status.items():
            # Determine status color and icon
            if isinstance(status, dict):
                is_connected = status.get("connected", False)
                status_text = "CONNECTED" if is_connected else "DISCONNECTED"
                color = self.COLORS["success"] if is_connected else self.COLORS["error"]
                icon = self.ICONS["check"] if is_connected else self.ICONS["cross"]

                # Add additional status details
                details = []
                for key, value in status.items():
                    if key != "connected":
                        details.append(f"  {key}: {value}")

                status_line = Text()
                status_line.append(f"{icon} ", style=f"bold {color}")
                status_line.append(f"{component}: ", style="bold")
                status_line.append(status_text, style=f"bold {color}")

                if details:
                    status_line.append("\n" + "\n".join(details), style=self.COLORS["muted"])

            else:
                # Simple status
                is_ok = str(status).lower() in ["ok", "connected", "ready", "true"]
                color = self.COLORS["success"] if is_ok else self.COLORS["error"]
                icon = self.ICONS["check"] if is_ok else self.ICONS["cross"]

                status_line = Text()
                status_line.append(f"{icon} ", style=f"bold {color}")
                status_line.append(f"{component}: ", style="bold")
                status_line.append(str(status), style=f"bold {color}")

            content.append(status_line)

        return Panel(
            Group(*content),
            title=f"{self.ICONS['hardware']} {title}",
            title_align="left",
            border_style=self.COLORS["secondary"],
            padding=UIConstants.DEFAULT_PANEL_PADDING,
        )

    def create_progress_display(
        self,
        task_name: str,
        total_steps: Optional[int] = None,
        current_step: Optional[int] = None,
        show_spinner: bool = True,
    ) -> Union[Progress, Status]:
        """Create a progress display for long-running operations.

        Generates an appropriate progress indicator based on whether the total
        number of steps is known. Creates a progress bar for deterministic
        operations or a spinner for indeterminate operations.

        Args:
            task_name: Descriptive name of the task being performed
            total_steps: Total number of steps (enables progress bar if provided)
            current_step: Current step number for initial progress position
            show_spinner: Whether to show a spinner animation in progress displays

        Returns:
            Rich Progress bar for deterministic operations or Status spinner
            for indeterminate operations
        """
        if total_steps is not None:
            # Create progress bar
            progress = Progress(
                (
                    SpinnerColumn()
                    if show_spinner
                    else TextColumn("[progress.description]{task.description}")
                ),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(
                    style=self.COLORS["primary"],
                    complete_style=self.COLORS["success"],
                ),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
            )

            task_id = progress.add_task(task_name, total=total_steps)
            if current_step is not None:
                progress.update(task_id, completed=current_step)

            return progress

        # Create spinner status with improved visibility and terminal compatibility
        # Try different spinners for better compatibility across terminals
        spinner_options = ["dots2", "dots", "line", "arc", "arrow3"]
        selected_spinner = "dots2"
        
        # Use simpler spinner for Windows/basic terminals
        try:
            import os
            if os.name == 'nt':  # Windows
                selected_spinner = "line"
        except:
            selected_spinner = "dots"
            
        return Status(
            f"{self.ICONS['running']} {task_name}",
            console=self.console,
            spinner=selected_spinner,
            spinner_style=self.COLORS["primary"],
            speed=1.0,  # Normal spinner speed
        )

    def create_message_panel(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
        width: Optional[int] = None,
    ) -> Panel:
        """Create a formatted message panel with appropriate styling.

        Generates a message panel with color coding and icons based on the
        message type. Supports different message categories with consistent
        visual styling for effective user communication.

        Args:
            message: Message text content to display
            message_type: Message category (success, error, warning, info)
            title: Optional panel title (defaults to message_type if None)
            width: Optional panel width constraint

        Returns:
            Rich Panel with formatted message and appropriate visual styling
        """
        color_map = {
            "success": self.COLORS["success"],
            "error": self.COLORS["error"],
            "warning": self.COLORS["warning"],
            "info": self.COLORS["info"],
        }

        icon_map = {
            "success": self.ICONS["success"],
            "error": self.ICONS["error"],
            "warning": self.ICONS["warning"],
            "info": self.ICONS["info"],
        }

        color = color_map.get(message_type, self.COLORS["info"])
        icon = icon_map.get(message_type, self.ICONS["info"])

        # Create content with proper Rich markup parsing
        icon_text = Text()
        icon_text.append(f"{icon} ", style=f"bold {color}")
        
        # Parse Rich markup in the message
        message_text = Text.from_markup(message)
        
        # Combine icon and message
        content = Text()
        content.append_text(icon_text)
        content.append_text(message_text)

        panel_title = title or message_type.upper()

        return Panel(
            content,
            title=panel_title,
            title_align="left",
            border_style=color,
            padding=UIConstants.DEFAULT_PANEL_PADDING,
            width=width,
        )

    def create_statistics_display(
        self,
        statistics: Dict[str, Any],
        title: str = "Test Statistics",
    ) -> Panel:
        """Create a comprehensive statistics display panel.

        Generates a formatted statistics panel that can display overall statistics,
        recent performance data, and model-specific breakdowns. Automatically
        formats different types of statistical data with appropriate styling.

        Args:
            statistics: Dictionary containing statistics data with keys like
                       'overall', 'recent', 'by_model' for organized display
            title: Display title for the statistics panel

        Returns:
            Rich Panel with formatted statistics and organized sections
        """
        content = []

        # Overall statistics
        if "overall" in statistics:
            overall = statistics["overall"]
            content.append(self._create_stats_section("Overall Statistics", overall))

        # Recent statistics
        if "recent" in statistics:
            recent = statistics["recent"]
            content.append(self._create_stats_section("Recent (7 days)", recent))

        # By model statistics
        if "by_model" in statistics:
            by_model = statistics["by_model"]
            model_stats_table = self._create_model_stats_table(by_model)
            content.append(Group(model_stats_table))

        return Panel(
            Group(*content),
            title=f"{self.ICONS['report']} {title}",
            title_align="left",
            border_style=self.COLORS["accent"],
            padding=UIConstants.DEFAULT_PANEL_PADDING,
        )

    def create_layout(
        self,
        components: Dict[str, Any],
        layout_type: str = "vertical",
    ) -> Layout:
        """Create a rich layout with multiple components using strategy pattern.

        Provides a flexible layout system that can arrange multiple Rich components
        in different patterns. Uses the strategy pattern to delegate layout creation
        to specialized methods based on the requested layout type.

        Args:
            components: Dictionary mapping component names to Rich objects for display
            layout_type: Layout arrangement type ("vertical", "horizontal", "grid")

        Returns:
            Rich Layout with components organized according to the specified type

        Raises:
            ValueError: If layout_type is not supported by the available strategies
        """
        if not components:
            return Layout()

        layout_strategies = {
            "vertical": self._create_vertical_layout,
            "horizontal": self._create_horizontal_layout,
            "grid": self._create_grid_layout,
        }

        strategy = layout_strategies.get(layout_type)
        if not strategy:
            raise ValueError(f"Unsupported layout type: {layout_type}")

        return strategy(components)

    def _create_vertical_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a vertical layout with components stacked top to bottom.

        Args:
            components: Dictionary of components to arrange vertically

        Returns:
            Layout with components arranged in a vertical stack
        """
        layout = Layout()
        component_layouts = [Layout(comp, name=name) for name, comp in components.items()]
        layout.split_column(*component_layouts)
        return layout

    def _create_horizontal_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a horizontal layout with components arranged left to right.

        Args:
            components: Dictionary of components to arrange horizontally

        Returns:
            Layout with components arranged in a horizontal row
        """
        layout = Layout()
        component_layouts = [Layout(comp, name=name) for name, comp in components.items()]
        layout.split_row(*component_layouts)
        return layout

    def _create_grid_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a 2x2 grid layout for up to 4 components with automatic fallback.

        Args:
            components: Dictionary of components to arrange in grid formation

        Returns:
            Layout with components arranged in a 2x2 grid, or vertical layout
            if more than 4 components are provided
        """
        if len(components) > UIConstants.MAX_GRID_COMPONENTS:
            # Graceful fallback to vertical layout for excessive components
            return self._create_vertical_layout(components)

        layout = Layout()
        components_list = list(components.items())

        # Create main grid structure with top and bottom sections
        layout.split_column(
            Layout(name="top"),
            Layout(name="bottom"),
        )

        # Populate top row with first set of components
        self._populate_grid_row(layout["top"], components_list[: UIConstants.GRID_TOP_COMPONENTS])

        # Populate bottom row with remaining components if available
        bottom_components = components_list[UIConstants.GRID_TOP_COMPONENTS :]
        if bottom_components:
            self._populate_grid_row(layout["bottom"], bottom_components)

        return layout

    def _populate_grid_row(self, row_layout: Layout, components: List[Tuple[str, Any]]) -> None:
        """Populate a grid row with the provided components using optimal arrangement.

        Args:
            row_layout: Layout object representing the row to populate
            components: List of (name, component) tuples to place in the row
        """
        if len(components) == 1:
            # Single component takes full row width
            name, comp = components[0]
            row_layout.update(Layout(comp, name=name))
        elif len(components) == 2:
            # Two components split row equally
            row_layout.split_row(
                Layout(components[0][1], name=components[0][0]),
                Layout(components[1][1], name=components[1][0]),
            )

    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """
        Print a header banner to the console.

        Args:
            title: Main title text
            subtitle: Optional subtitle text
        """
        header = self.create_header_banner(title, subtitle)
        self.console.print(header)

    def print_status(
        self,
        title: str,
        status: Union[str, TestStatus],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Print a status panel to the console.

        Args:
            title: Panel title
            status: Status value
            details: Optional additional details
        """
        panel = self.create_status_panel(title, status, details)
        self.console.print(panel)

    def print_message(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
    ) -> None:
        """
        Print a formatted message to the console.

        Args:
            message: Message text
            message_type: Type of message
            title: Optional title
        """
        panel = self.create_message_panel(message, message_type, title)
        self.console.print(panel)

    def print_table(self, table: Table) -> None:
        """
        Print a table to the console.

        Args:
            table: Rich Table to print
        """
        self.console.print(table)

    def _truncate_string(
        self, text: str, max_length: int = UIConstants.DEFAULT_TRUNCATE_LENGTH
    ) -> str:
        """Truncate string to specified length with ellipsis for improved readability.

        Provides consistent text truncation across the UI to maintain uniform
        column widths and prevent layout disruption from overly long text.

        Args:
            text: String to truncate (handles None gracefully)
            max_length: Maximum length before truncation (uses UIConstants default)

        Returns:
            Truncated string with ellipsis if needed, ensuring consistent display widths
        """
        if not text:  # Handle None or empty strings gracefully
            return "N/A"

        text_str = str(text)
        if len(text_str) > max_length:
            return f"{text_str[:max_length]}..."
        return text_str

    def _get_status_icon(self, status: TestStatus) -> str:
        """Get appropriate icon for test status with intelligent mapping.

        Args:
            status: TestStatus enum value to map to an appropriate icon

        Returns:
            Unicode icon string representing the status visually
        """
        status_to_icon_mapping = {
            TestStatus.NOT_STARTED: self.ICONS["info"],
            TestStatus.PREPARING: self.ICONS["settings"],
            TestStatus.RUNNING: self.ICONS["running"],
            TestStatus.COMPLETED: self.ICONS["success"],
            TestStatus.FAILED: self.ICONS["error"],
            TestStatus.CANCELLED: self.ICONS["warning"],
            TestStatus.ERROR: self.ICONS["error"],
        }
        return status_to_icon_mapping.get(status, self.ICONS["info"])

    def _get_result_status_icon(self, result: EOLTestResult) -> str:
        """Get appropriate icon for test result based on execution outcome.

        Args:
            result: EOLTestResult object containing test execution details

        Returns:
            Unicode icon string representing the test result visually
        """
        if result.is_passed:
            return self.ICONS["check"]
        if result.is_failed_execution:
            return self.ICONS["error"]
        return self.ICONS["cross"]

    def _get_result_status_color(self, result: EOLTestResult) -> str:
        """Get appropriate color for test result based on execution outcome.

        Args:
            result: EOLTestResult object containing test execution details

        Returns:
            Color string from the professional color scheme
        """
        if result.is_passed:
            return self.COLORS["success"]
        if result.is_failed_execution:
            return self.COLORS["error"]
        return self.COLORS["error"]

    def _create_stats_section(self, title: str, stats: Dict[str, Any]) -> Group:
        """Create a formatted statistics section with consistent styling.

        Args:
            title: Section title to display prominently
            stats: Dictionary of statistic names and values

        Returns:
            Rich Group containing the formatted statistics section
        """
        content = []

        # Create formatted section title
        title_text = Text(f"\n{title}", style=f"bold {self.COLORS['secondary']}")
        content.append(title_text)

        # Format each statistic with appropriate styling
        for key, value in stats.items():
            stat_text = Text()
            stat_text.append(f"  {self.ICONS['bullet']} ", style=self.COLORS["muted"])
            stat_text.append(f"{key.replace('_', ' ').title()}: ", style="bold")

            # Apply special formatting for percentage rates
            if isinstance(value, float) and "rate" in key.lower():
                stat_text.append(f"{value:.1f}%", style=self.COLORS["accent"])
            else:
                stat_text.append(str(value), style=self.COLORS["text"])

            content.append(stat_text)

        return Group(*content)

    def _create_base_table(self, title: str, show_details: bool) -> Table:
        """Create base table structure with consistent column definitions.

        Establishes the foundation table structure with professional styling
        and configurable column sets based on the detail level requested.

        Args:
            title: Table title for display at the top of the table
            show_details: Whether to include detailed columns for comprehensive display

        Returns:
            Configured Rich Table with appropriate columns and professional styling
        """
        table = Table(
            title=title,
            title_style=f"bold {self.COLORS['primary']}",
            border_style=self.COLORS["border"],
            header_style=f"bold {self.COLORS['secondary']}",
            show_lines=True,
        )

        # Always include core columns for essential information
        self._add_core_table_columns(table)

        # Add detailed columns for comprehensive views
        if show_details:
            self._add_detail_table_columns(table)

        # Timestamp column always appears last for chronological context
        table.add_column(
            "Timestamp", style=self.COLORS["muted"], width=UIConstants.TIMESTAMP_COLUMN_WIDTH
        )
        return table

    def _add_core_table_columns(self, table: Table) -> None:
        """Add core table columns that are always present in test result displays.

        Args:
            table: Rich Table object to add columns to
        """
        table.add_column(
            "Status", justify="center", style="bold", width=UIConstants.STATUS_COLUMN_WIDTH
        )
        table.add_column(
            "Test ID", style=self.COLORS["text"], width=UIConstants.TEST_ID_COLUMN_WIDTH
        )
        table.add_column("DUT ID", style=self.COLORS["text"], width=UIConstants.DUT_ID_COLUMN_WIDTH)

    def _add_detail_table_columns(self, table: Table) -> None:
        """Add detailed table columns for comprehensive test result display.

        Args:
            table: Rich Table object to add detailed columns to
        """
        table.add_column("Model", style=self.COLORS["muted"], width=UIConstants.MODEL_COLUMN_WIDTH)
        table.add_column(
            "Duration",
            justify="right",
            style=self.COLORS["info"],
            width=UIConstants.DURATION_COLUMN_WIDTH,
        )
        table.add_column(
            "Measurements",
            justify="center",
            style=self.COLORS["accent"],
            width=UIConstants.MEASUREMENTS_COLUMN_WIDTH,
        )

    def _truncate_text(
        self, text: str, max_length: int = UIConstants.DEFAULT_TRUNCATE_LENGTH
    ) -> str:
        """Utility to consistently truncate text with proper null handling.

        Provides safe text truncation with graceful handling of None values
        and consistent formatting across all table displays.

        Args:
            text: Text to truncate (handles None and empty values gracefully)
            max_length: Maximum display length before truncation with ellipsis

        Returns:
            Safely truncated text string with consistent N/A handling
        """
        if not text:  # Handle None, empty string, or falsy values
            return "N/A"

        text_str = str(text)
        if len(text_str) > max_length:
            return f"{text_str[:max_length]}..."
        return text_str

    def _format_eol_result_row(self, result: EOLTestResult, show_details: bool) -> List[Any]:
        """Format EOLTestResult into table row data with consistent styling.

        Transforms an EOLTestResult object into properly formatted table row data
        with appropriate icons, colors, and text formatting for display.

        Args:
            result: EOL test result object containing test execution data
            show_details: Whether to include detailed columns in the row

        Returns:
            List of formatted row data elements ready for table display
        """
        # Determine appropriate status styling based on test outcome
        status_icon = self._get_result_status_icon(result)
        status_color = self._get_result_status_color(result)

        # Build core row data with essential information
        row_data = self._build_core_row_data(
            status_icon=status_icon,
            status_color=status_color,
            test_id=str(result.test_id),
            dut_id="N/A",  # Not directly available in EOLTestResult
        )

        # Add detailed columns if comprehensive view is requested
        if show_details:
            detail_data = self._build_eol_detail_data(result)
            row_data.extend(detail_data)

        # Add timestamp (current time since EOLTestResult doesn't store creation time)
        timestamp = self._format_current_timestamp()
        row_data.append(timestamp)

        return row_data

    def _format_dict_result_row(self, result: Dict[str, Any], show_details: bool) -> List[Any]:
        """Format dictionary result into table row data with consistent styling.

        Transforms a dictionary-based test result into properly formatted table
        row data with appropriate icons, colors, and text formatting for display.

        Args:
            result: Dictionary containing test result data from repository
            show_details: Whether to include detailed columns in the row

        Returns:
            List of formatted row data elements ready for table display
        """
        # Determine status styling based on test outcome
        is_passed = result.get("passed", False)
        status_icon = self.ICONS["check"] if is_passed else self.ICONS["cross"]
        status_color = self.COLORS["success"] if is_passed else self.COLORS["error"]

        # Extract DUT information from nested dictionary
        dut_info = result.get("dut", {})

        # Build core row data with essential information
        row_data = self._build_core_row_data(
            status_icon=status_icon,
            status_color=status_color,
            test_id=result.get("test_id", "N/A"),
            dut_id=str(dut_info.get("dut_id", "N/A")),
        )

        # Add detailed columns if comprehensive view is requested
        if show_details:
            detail_data = self._build_dict_detail_data(result, dut_info)
            row_data.extend(detail_data)

        # Format and add timestamp with safe parsing
        timestamp = self._format_result_timestamp(result.get("created_at", ""))
        row_data.append(timestamp)

        return row_data

    def _create_model_stats_table(self, model_stats: Dict[str, Dict[str, Any]]) -> Table:
        """Create a table for model statistics."""
        table = Table(
            title="Statistics by Model",
            title_style=f"bold {self.COLORS['secondary']}",
            border_style=self.COLORS["border"],
            header_style=f"bold {self.COLORS['secondary']}",
            show_lines=True,
        )

        table.add_column("Model", style=self.COLORS["text"])
        table.add_column("Total Tests", justify="center", style=self.COLORS["info"])
        table.add_column("Passed", justify="center", style=self.COLORS["success"])
        table.add_column("Pass Rate", justify="center", style=self.COLORS["accent"])

        for model, stats in model_stats.items():
            pass_rate = stats.get("pass_rate", 0)
            pass_rate_color = (
                self.COLORS["success"]
                if pass_rate >= 90
                else (self.COLORS["warning"] if pass_rate >= 70 else self.COLORS["error"])
            )

            table.add_row(
                model,
                str(stats.get("total", 0)),
                str(stats.get("passed", 0)),
                Text(f"{pass_rate:.1f}%", style=f"bold {pass_rate_color}"),
            )

        return table

    def _build_core_row_data(
        self, status_icon: str, status_color: str, test_id: str, dut_id: str
    ) -> List[Any]:
        """Build core row data common to both result formats.

        Args:
            status_icon: Unicode icon representing the test status
            status_color: Color string for status styling
            test_id: Test identifier string
            dut_id: Device under test identifier string

        Returns:
            List of formatted core data elements
        """
        return [
            Text(status_icon, style=f"bold {status_color}"),
            self._truncate_text(test_id),
            self._truncate_text(dut_id),
        ]

    def _build_eol_detail_data(self, result: EOLTestResult) -> List[str]:
        """Build detail data specific to EOLTestResult objects.

        Args:
            result: EOLTestResult object containing test execution data

        Returns:
            List of formatted detail data elements
        """
        return [
            "N/A",  # Model not directly available in EOLTestResult
            result.format_duration(),
            str(result.measurement_count),
        ]

    def _build_dict_detail_data(
        self, result: Dict[str, Any], dut_info: Dict[str, Any]
    ) -> List[str]:
        """Build detail data specific to dictionary result objects.

        Args:
            result: Dictionary containing test result data
            dut_info: Dictionary containing DUT information

        Returns:
            List of formatted detail data elements
        """
        return [
            str(dut_info.get("model_number", "N/A")),
            str(result.get("duration", "N/A")),
            str(len(result.get("measurement_ids", []))),
        ]

    def _format_current_timestamp(self) -> str:
        """Format current timestamp for display with consistent formatting.

        Returns:
            Formatted timestamp string using standard display format
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _format_result_timestamp(self, created_at: str) -> str:
        """Format result timestamp with proper error handling and timezone support.

        Safely parses ISO format timestamps with timezone information and
        converts them to a consistent display format.

        Args:
            created_at: ISO format timestamp string with optional timezone

        Returns:
            Formatted timestamp string or "N/A" if parsing fails
        """
        if not created_at:
            return "N/A"

        try:
            # Handle ISO format with timezone (convert Z to +00:00 for Python compatibility)
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            # Return N/A for any parsing errors to maintain table consistency
            return "N/A"
