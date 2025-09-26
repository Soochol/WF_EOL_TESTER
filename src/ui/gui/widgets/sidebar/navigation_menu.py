"""
Navigation Menu Widget

Sidebar navigation menu with main application pages.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Local application imports
# Local imports
from ui.gui.utils.icon_manager import get_emoji, get_icon, IconSize


class NavigationMenu(QWidget):
    """
    Navigation menu widget for the sidebar.

    Provides navigation buttons for different application pages.
    """

    page_changed = Signal(str)  # Emits page name when selection changes

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_page = "dashboard"
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the navigation menu UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 10, 5, 10)

        # Navigation buttons
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.setExclusive(True)

        # Menu items with icon names and labels
        menu_items = [
            ("dashboard", "dashboard", "Dashboard"),
            ("test_control", "test_control", "Test Control"),
            ("results", "results", "Results"),
            ("hardware", "hardware", "Hardware"),
            ("settings", "settings", "Settings"),
            ("about", "status_info", "About"),
        ]

        for page_id, icon_name, label in menu_items:
            btn = self.create_nav_button(page_id, icon_name, label)
            layout.addWidget(btn)
            self.nav_buttons.addButton(btn)

        # Set default selection
        self.nav_buttons.buttons()[0].setChecked(True)

        # Connect signals
        self.nav_buttons.buttonClicked.connect(self._on_button_clicked)

        # Add stretch to push buttons to top
        layout.addStretch()

    def create_nav_button(self, page_id: str, icon_name: str, label: str) -> QPushButton:
        """Create a navigation button with icon and text"""
        # Try to get icon from icon manager
        icon = get_icon(icon_name, IconSize.MEDIUM)

        # Create button with text
        btn = QPushButton(label)
        btn.setObjectName(f"nav_btn_{page_id}")
        btn.setCheckable(True)
        btn.setProperty("page_id", page_id)

        # Set icon if available, otherwise use emoji fallback
        if not icon.isNull():
            btn.setIcon(icon)
        else:
            # Use emoji fallback in button text
            emoji = get_emoji(icon_name)
            if emoji:
                btn.setText(f"{emoji} {label}")

        # Style the button
        btn.setMinimumHeight(52)
        btn.setMaximumHeight(59)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Set font
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Medium)
        btn.setFont(font)

        # Set alignment
        btn.setStyleSheet(self._get_button_style())

        return btn

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
        QPushButton {
            text-align: left;
            padding: 10px 12px;
            border: 1px solid #404040;
            border-radius: 4px;
            background-color: #2d2d2d;
            color: #cccccc;
            min-height: 52px;
            max-height: 59px;
        }
        QPushButton:hover {
            background-color: #404040;
            color: #ffffff;
        }
        QPushButton:checked {
            background-color: #0078d4;
            color: #ffffff;
            border-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #106ebe;
        }
        """

    def _on_button_clicked(self, button: QPushButton) -> None:
        """Handle navigation button click"""
        page_id = button.property("page_id")
        if page_id and page_id != self.current_page:
            self.current_page = page_id
            self.page_changed.emit(page_id)

    def set_current_page(self, page_id: str) -> None:
        """Set the current page programmatically"""
        for button in self.nav_buttons.buttons():
            if button.property("page_id") == page_id:
                button.setChecked(True)
                self.current_page = page_id
                break
