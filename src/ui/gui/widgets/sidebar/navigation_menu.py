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
    QSpacerItem,
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
    settings_clicked = Signal()  # Emits when settings button is clicked

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_page = "dashboard"
        self.statistics_submenu_visible = False  # Track submenu visibility
        self.statistics_submenu_buttons = []  # Store submenu buttons
        self.setup_ui()
        # Set size policy to preferred size to allow stretcher to work effectively
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Navigation menu will size to its content, allowing stretcher to control layout

        # Ensure we don't get compressed horizontally
        self.setMinimumWidth(200)  # Match sidebar width
        self.setMaximumWidth(200)  # Match sidebar width
        # Removed height limit to accommodate submenu

    def setup_ui(self) -> None:
        """Setup the navigation menu UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)  # No spacing between buttons
        layout.setContentsMargins(0, 15, 0, 0)  # 15px top margin to move buttons down
        # Remove size constraint to allow dynamic sizing

        # Navigation buttons
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.setExclusive(True)

        # Menu items with icon names and labels
        menu_items = [
            ("dashboard", "dashboard", "Dashboard"),
            ("test_control", "test_control", "Test Control"),
            ("results", "results", "Results"),
            ("statistics", "statistics", "Statistics"),
            ("hardware", "hardware", "Hardware"),
            ("settings", "settings", "Settings"),
            ("about", "status_info", "About"),
        ]

        for page_id, icon_name, label in menu_items:
            btn = self.create_nav_button(page_id, icon_name, label)
            layout.addWidget(btn)
            self.nav_buttons.addButton(btn)

            # Add statistics submenu buttons after statistics button
            if page_id == "statistics":
                self.create_statistics_submenu(layout)

        # Set default selection
        self.nav_buttons.buttons()[0].setChecked(True)

        # Connect signals
        self.nav_buttons.buttonClicked.connect(self._on_button_clicked)

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

        # Style the button - fixed height to allow stretcher to work
        btn.setMinimumHeight(55)  # Compact size for half-height navigation
        btn.setMaximumHeight(55)  # Fix button height to prevent expansion
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Set font
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Medium)
        btn.setFont(font)

        # Set alignment
        btn.setStyleSheet(self._get_button_style())

        return btn

    def create_statistics_submenu(self, layout: QVBoxLayout) -> None:
        """Create statistics submenu buttons"""
        submenu_items = [
            ("statistics_overview", "📊", "Overview"),
            ("statistics_2d", "📉", "2D Charts"),
            ("statistics_3d", "🎲", "3D Viz"),
            ("statistics_4d", "🌐", "4D Analysis"),
            ("statistics_performance", "⚡", "Performance"),
            ("statistics_export", "💾", "Export"),
        ]

        for page_id, emoji, label in submenu_items:
            btn = self.create_submenu_button(page_id, emoji, label)
            btn.setVisible(False)  # Initially hidden
            layout.addWidget(btn)
            self.statistics_submenu_buttons.append(btn)
            self.nav_buttons.addButton(btn)

    def create_submenu_button(self, page_id: str, emoji: str, label: str) -> QPushButton:
        """Create an indented submenu button"""
        btn = QPushButton(f"  {emoji} {label}")  # Two spaces for indentation
        btn.setObjectName(f"nav_btn_{page_id}")
        btn.setCheckable(True)
        btn.setProperty("page_id", page_id)

        # Smaller height for submenu buttons
        btn.setMinimumHeight(45)
        btn.setMaximumHeight(45)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Smaller font
        font = QFont()
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Normal)
        btn.setFont(font)

        # Submenu-specific style
        btn.setStyleSheet(self._get_submenu_button_style())

        return btn

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
        QPushButton {
            text-align: left;
            padding-left: 15px;
            padding-right: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
            margin: 0px;
            border: 1px solid #404040;
            border-radius: 4px;
            background-color: #2d2d2d;
            color: #cccccc;
            min-height: 55px;
            max-height: 55px;
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
        QPushButton:focus {
            outline: none;
            border: 1px solid #404040;
        }
        """

    def _get_submenu_button_style(self) -> str:
        """Get submenu button stylesheet (darker, indented)"""
        return """
        QPushButton {
            text-align: left;
            padding-left: 30px;
            padding-right: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
            margin: 0px;
            border: 1px solid #353535;
            border-radius: 4px;
            background-color: #252525;
            color: #aaaaaa;
            min-height: 45px;
            max-height: 45px;
        }
        QPushButton:hover {
            background-color: #353535;
            color: #ffffff;
        }
        QPushButton:checked {
            background-color: #005a9e;
            color: #ffffff;
            border-color: #004578;
        }
        QPushButton:pressed {
            background-color: #004578;
        }
        QPushButton:focus {
            outline: none;
            border: 1px solid #353535;
        }
        """

    def _on_button_clicked(self, button: QPushButton) -> None:
        """Handle navigation button click"""
        page_id = button.property("page_id")

        # Special handling for Statistics button - toggle submenu
        if page_id == "statistics":
            self.toggle_statistics_submenu()
            return  # Don't emit page_changed signal

        # Normal page navigation
        if page_id and page_id != self.current_page:
            self.current_page = page_id
            self.page_changed.emit(page_id)

    def toggle_statistics_submenu(self) -> None:
        """Toggle statistics submenu visibility"""
        self.statistics_submenu_visible = not self.statistics_submenu_visible
        for btn in self.statistics_submenu_buttons:
            btn.setVisible(self.statistics_submenu_visible)

    def set_statistics_submenu_visible(self, visible: bool) -> None:
        """Programmatically show/hide statistics submenu"""
        self.statistics_submenu_visible = visible
        for btn in self.statistics_submenu_buttons:
            btn.setVisible(visible)

    def set_current_page(self, page_id: str) -> None:
        """Set the current page programmatically"""
        for button in self.nav_buttons.buttons():
            if button.property("page_id") == page_id:
                button.setChecked(True)
                self.current_page = page_id
                break
