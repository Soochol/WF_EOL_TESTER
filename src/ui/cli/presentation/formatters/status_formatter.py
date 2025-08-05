"""Status Display Formatter for CLI Rich UI Components

Specialized formatter class focused on status display formatting including
status panels and hardware status displays. This module provides methods for
creating consistent status representations with intelligent color coding and
icon selection.

This formatter handles both simple status strings and complex status dictionaries
with appropriate visual indicators for different status types and conditions.
"""

from typing import Any, Dict, Optional, Union

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from domain.enums.test_status import TestStatus
from .base_formatter import BaseFormatter


class StatusFormatter(BaseFormatter):
    """Specialized formatter for status displays and hardware status panels.

    This class extends BaseFormatter to provide specialized methods for creating
    status panels, hardware status displays, and status-related formatting.
    It handles both simple status strings and complex status dictionaries with
    intelligent color coding and icon selection.

    Key Features:
    - Intelligent status color and icon mapping
    - Hardware component status displays
    - Support for both simple and complex status formats
    - Consistent visual styling for all status types
    """

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
            color = self.colors.get_color(self.colors.STATUS_COLORS[status])
            status_text = status.value.upper().replace("_", " ")
            if not icon:
                icon = self._get_status_icon(status)
        else:
            color = self.colors.get_color("info")
            status_text = str(status)
            if not icon:
                icon = self.icons.get_icon("info")

        # Create status content
        content = Text()
        content.append(f"{icon} ")
        content.append(f"{title}: ")
        content.append(status_text, style=color)

        # Add details if provided
        if details:
            content.append("\n\n")
            for key, value in details.items():
                content.append(f"{self.icons.get_icon('bullet')} {key}: ")
                content.append(f"{value}\n", style=self.colors.get_color("text"))

        return Panel(
            content,
            border_style=color,
            padding=self.layout.DEFAULT_PANEL_PADDING,
        )

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
                status_line = self._format_complex_hardware_status(component, status)
            else:
                status_line = self._format_simple_hardware_status(component, status)

            content.append(status_line)

        return Panel(
            Group(*content),
            title=f"{self.icons.get_icon('hardware')} {title}",
            title_align="left",
            border_style=self.colors.get_color("secondary"),
            padding=self.layout.DEFAULT_PANEL_PADDING,
        )

    def _format_complex_hardware_status(self, component: str, status: Dict[str, Any]) -> Text:
        """Format complex hardware status from dictionary data.

        Args:
            component: Hardware component name
            status: Dictionary containing detailed status information

        Returns:
            Formatted Text object with status information and details
        """
        is_connected = status.get("connected", False)
        status_text = "CONNECTED" if is_connected else "DISCONNECTED"
        color = self.colors.get_color("success") if is_connected else self.colors.get_color("error")
        icon = self.icons.get_icon("check") if is_connected else self.icons.get_icon("cross")

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
            status_line.append("\n" + "\n".join(details), style=self.colors.get_color("muted"))

        return status_line

    def _format_simple_hardware_status(self, component: str, status: Any) -> Text:
        """Format simple hardware status from string or basic value.

        Args:
            component: Hardware component name
            status: Simple status value (string, boolean, etc.)

        Returns:
            Formatted Text object with status information
        """
        is_ok = str(status).lower() in ["ok", "connected", "ready", "true"]
        color = self.colors.get_color("success") if is_ok else self.colors.get_color("error")
        icon = self.icons.get_icon("check") if is_ok else self.icons.get_icon("cross")

        status_line = Text()
        status_line.append(f"{icon} ", style=f"bold {color}")
        status_line.append(f"{component}: ", style="bold")
        status_line.append(str(status), style=f"bold {color}")

        return status_line

    # Convenience method for console output
    def print_status(
        self,
        title: str,
        status: Union[str, TestStatus],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Print a status panel to the console.

        Args:
            title: Panel title
            status: Status value
            details: Optional additional details
        """
        panel = self.create_status_panel(title, status, details)
        self.console.print(panel)

    def print_hardware_status(
        self,
        hardware_status: Dict[str, Any],
        title: str = "Hardware Status",
    ) -> None:
        """Print a hardware status display to the console.

        Args:
            hardware_status: Dictionary containing hardware component status information
            title: Display title for the hardware status panel
        """
        panel = self.create_hardware_status_display(hardware_status, title)
        self.console.print(panel)
