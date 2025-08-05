"""Base Formatter for CLI Rich UI Components

Provides core formatting interface and common utilities used by all specialized
formatters. This module defines the foundational patterns and dependencies that
all formatter classes require for consistent styling and behavior.

This class encapsulates common theme integration, basic panel creation, and
utility methods that form the foundation for all specialized formatter classes.
"""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.domain.enums.test_status import TestStatus
from ..themes import ColorScheme, IconSet, LayoutConstants


class BaseFormatter:
    """Abstract base formatter providing common functionality for all specialized formatters.

    This class serves as the foundation for all formatter classes, providing:
    - Theme integration (colors, icons, layout constants)
    - Common utility methods for text handling and formatting
    - Base panel and message creation methods
    - Consistent interface for all specialized formatters

    Specialized formatters inherit from this class to ensure consistent
    behavior and styling across the entire CLI application.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize base formatter with theme components.

        Args:
            console: Optional Rich Console instance. If None, creates a new one
                    with default settings optimized for the EOL Tester application.
        """
        self.console = console or Console(
            force_terminal=True, legacy_windows=False, color_system="truecolor"
        )

        # Initialize theme components via dependency injection
        self.colors = ColorScheme()
        self.icons = IconSet()
        self.layout = LayoutConstants()

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
            "success": self.colors.get_color("success"),
            "error": self.colors.get_color("error"),
            "warning": self.colors.get_color("warning"),
            "info": self.colors.get_color("info"),
        }

        icon_map = {
            "success": self.icons.get_icon("success"),
            "error": self.icons.get_icon("error"),
            "warning": self.icons.get_icon("warning"),
            "info": self.icons.get_icon("info"),
        }

        color = color_map.get(message_type, self.colors.get_color("info"))
        icon = icon_map.get(message_type, self.icons.get_icon("info"))

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
            padding=self.layout.DEFAULT_PANEL_PADDING,
            width=width,
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
        content = Text(title, style=f"bold {self.colors.get_color('text')}")
        content.justify = "center"

        if subtitle:
            content.append("\n")
            subtitle_text = Text(subtitle, style=self.colors.get_color("muted"))
            subtitle_text.justify = "center"
            content.append(subtitle_text)

        return Panel(
            content,
            style=self.colors.get_color("primary"),
            border_style=self.colors.get_color("border"),
            width=width,
            padding=self.layout.HEADER_PANEL_PADDING,
        )

    def _truncate_text(
        self, text: str, max_length: Optional[int] = None
    ) -> str:
        """Utility to consistently truncate text with proper null handling.

        Provides safe text truncation with graceful handling of None values
        and consistent formatting across all formatter displays.

        Args:
            text: Text to truncate (handles None and empty values gracefully)
            max_length: Maximum display length before truncation with ellipsis
                       (uses layout default if None)

        Returns:
            Safely truncated text string with consistent N/A handling
        """
        if not text:  # Handle None, empty string, or falsy values
            return "N/A"

        if max_length is None:
            max_length = self.layout.DEFAULT_TRUNCATE_LENGTH

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
            TestStatus.NOT_STARTED: self.icons.get_icon("info"),
            TestStatus.PREPARING: self.icons.get_icon("settings"),
            TestStatus.RUNNING: self.icons.get_icon("running"),
            TestStatus.COMPLETED: self.icons.get_icon("success"),
            TestStatus.FAILED: self.icons.get_icon("error"),
            TestStatus.CANCELLED: self.icons.get_icon("warning"),
            TestStatus.ERROR: self.icons.get_icon("error"),
        }
        return status_to_icon_mapping.get(status, self.icons.get_icon("info"))

    def _format_current_timestamp(self) -> str:
        """Format current timestamp for display with consistent formatting.

        Returns:
            Formatted timestamp string using standard display format
        """
        from datetime import datetime
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
            from datetime import datetime
            # Handle ISO format with timezone (convert Z to +00:00 for Python compatibility)
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            # Return N/A for any parsing errors to maintain table consistency
            return "N/A"

    # Convenience methods for console output
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a header banner to the console.

        Args:
            title: Main title text
            subtitle: Optional subtitle text
        """
        header = self.create_header_banner(title, subtitle)
        self.console.print(header)

    def print_message(
        self,
        message: str,
        message_type: str = "info",
        title: Optional[str] = None,
    ) -> None:
        """Print a formatted message to the console.

        Args:
            message: Message text
            message_type: Type of message
            title: Optional title
        """
        panel = self.create_message_panel(message, message_type, title)
        self.console.print(panel)
