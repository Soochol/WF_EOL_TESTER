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
        self.setup_ui()
        # Set size policy to preferred size to allow stretcher to work effectively
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Navigation menu will size to its content, allowing stretcher to control layout

        # Ensure we don't get compressed horizontally and limit navigation height
        self.setMinimumWidth(200)  # Match sidebar width
        self.setMaximumWidth(200)  # Match sidebar width
        self.setMaximumHeight(385)  # Limit navigation menu to half height

    def setup_ui(self) -> None:
        """Setup the navigation menu UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)  # No spacing between buttons
        layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins to prevent overlap
        # Remove size constraint to allow dynamic sizing

        # Navigation buttons
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.setExclusive(True)

        # Menu items with icon names and labels
        menu_items = [
            ("dashboard", "dashboard", "Dashboard"),
            ("test_control", "test_control", "Test Control"),
            ("results", "results", "Results"),
            ("hardware", "hardware", "Hardware"),
            ("about", "status_info", "About"),
        ]

        for page_id, icon_name, label in menu_items:
            btn = self.create_nav_button(page_id, icon_name, label)
            layout.addWidget(btn)
            self.nav_buttons.addButton(btn)

        # Add stretcher to push navigation buttons up and settings button down
        stretcher = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(stretcher)

        # Add settings button at the bottom
        self.settings_btn = self.create_settings_button()
        layout.addWidget(self.settings_btn)

        # Set default selection
        self.nav_buttons.buttons()[0].setChecked(True)

        # Connect signals
        self.nav_buttons.buttonClicked.connect(self._on_button_clicked)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

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

    def create_settings_button(self) -> QPushButton:
        """Create a settings button with same styling as navigation buttons"""
        # Try to get icon from icon manager
        icon = get_icon("settings", IconSize.MEDIUM)

        # Create button with text
        btn = QPushButton("Settings")
        btn.setObjectName("settings_btn")
        btn.setCheckable(False)  # Settings button is not checkable like nav buttons

        # Set icon if available, otherwise use emoji fallback
        if not icon.isNull():
            btn.setIcon(icon)
        else:
            # Use emoji fallback in button text
            emoji = get_emoji("settings")
            if emoji:
                btn.setText(f"{emoji} Settings")
            else:
                btn.setText("⚙️ Settings")

        # Style the button same as navigation buttons
        btn.setMinimumHeight(55)  # Same minimum height as nav buttons
        btn.setMaximumHeight(55)  # Fix button height to prevent expansion
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Set font
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Medium)
        btn.setFont(font)

        # Set alignment - use similar style but without checkable states
        btn.setStyleSheet(self._get_settings_button_style())

        return btn

    def _get_settings_button_style(self) -> str:
        """Get settings button stylesheet (similar to nav buttons but no checked state)"""
        return """
        QPushButton {
            text-align: center;
            padding: 0px;
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
        QPushButton:pressed {
            background-color: #106ebe;
        }
        QPushButton:focus {
            outline: none;
            border: 1px solid #404040;
        }
        """

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
        QPushButton {
            text-align: center;
            padding: 0px;
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
