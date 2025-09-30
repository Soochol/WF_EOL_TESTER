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
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from .navigation_menu import NavigationMenu


class SidebarWidget(QWidget):
    """
    Main sidebar widget for the application.

    Contains navigation menu and system information display.
    """

    page_changed = Signal(str)  # Forwards navigation signals
    settings_clicked = Signal()  # Forwards settings button clicks

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)  # No margin - alignment handled by content_layout

        # Navigation menu
        self.navigation_menu = NavigationMenu()
        self.navigation_menu.page_changed.connect(self.page_changed.emit)
        self.navigation_menu.settings_clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.navigation_menu)

        # Add stretcher to push navigation menu to top
        stretcher = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(stretcher)


        # Apply sidebar styling
        self.setStyleSheet(self._get_sidebar_style())
        # Set explicit fixed size to prevent content overlap
        self.setFixedWidth(200)  # Restore original width
        self.setMinimumWidth(200)  # Enforce minimum width
        self.setMaximumWidth(200)  # Enforce maximum width

        # Set size policy: fixed width, expanding height (full height, content controlled internally)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


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

    def set_statistics_submenu_visible(self, visible: bool) -> None:
        """Show or hide the statistics submenu"""
        self.navigation_menu.set_statistics_submenu_visible(visible)

