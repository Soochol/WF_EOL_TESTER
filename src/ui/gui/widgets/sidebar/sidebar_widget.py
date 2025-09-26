"""
Sidebar Widget

Main sidebar widget containing navigation menu and system information.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from .navigation_menu import NavigationMenu
from .system_info import SystemInfo


class SidebarWidget(QWidget):
    """
    Main sidebar widget for the application.

    Contains navigation menu and system information display.
    """

    page_changed = Signal(str)  # Forwards navigation signals

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation menu
        self.navigation_menu = NavigationMenu()
        self.navigation_menu.page_changed.connect(self.page_changed.emit)
        layout.addWidget(self.navigation_menu)

        # Separator
        separator = self.create_separator()
        layout.addWidget(separator)

        # System info
        self.system_info = SystemInfo()
        layout.addWidget(self.system_info)

        # Apply sidebar styling
        self.setStyleSheet(self._get_sidebar_style())
        self.setFixedWidth(234)

    def create_separator(self) -> QFrame:
        """Create a separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #404040; margin: 5px 10px;")
        separator.setFixedHeight(1)
        return separator

    def _get_sidebar_style(self) -> str:
        """Get sidebar stylesheet"""
        return """
        SidebarWidget {
            background-color: #2d2d2d;
            border-right: 1px solid #404040;
        }
        """

    def set_current_page(self, page_id: str) -> None:
        """Set the current page"""
        self.navigation_menu.set_current_page(page_id)

    def update_system_status(self, status: str) -> None:
        """Update system status in system info"""
        self.system_info.update_system_status(status)

    def update_connection_status(self, connected: int, total: int) -> None:
        """Update connection status in system info"""
        self.system_info.update_connection_status(connected, total)

    def update_temperature(self, temperature: float) -> None:
        """Update temperature in system info"""
        self.system_info.update_temperature(temperature)
