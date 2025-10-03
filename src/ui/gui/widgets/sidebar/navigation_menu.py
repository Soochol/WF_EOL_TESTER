"""
Navigation Menu Widget

Sidebar navigation menu with main application pages.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Local application imports
# Local imports
from ui.gui.utils.icon_manager import get_emoji
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider


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
        self.hardware_submenu_visible = False  # Track hardware submenu visibility
        self.hardware_submenu_buttons = []  # Store hardware submenu buttons
        self.is_collapsed = False  # Track collapse state
        self.expanded_width = 220  # Increased from 200px
        self.collapsed_width = 70  # Icon-only mode
        self.all_buttons = []  # Store all buttons for collapse/expand
        self.category_headers = []  # Store category headers
        self.section_dividers = []  # Store section dividers
        self.setup_ui()
        # Set size policy to preferred size to allow stretcher to work effectively
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Navigation menu will size to its content, allowing stretcher to control layout

        # Ensure we don't get compressed horizontally
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)

    def setup_ui(self) -> None:
        """Setup the navigation menu UI with category sections"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 10, 0, 0)

        # Navigation buttons
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.setExclusive(True)

        # NAVIGATION Section
        header = self._create_category_header("NAVIGATION")
        layout.addWidget(header)
        self.category_headers.append(header)

        navigation_items = [
            ("dashboard", "dashboard", "Dashboard"),
            ("test_control", "test_control", "Test Control"),
            ("results", "results", "Results"),
        ]
        for page_id, icon_name, label in navigation_items:
            btn = self.create_nav_button(page_id, icon_name, label)
            layout.addWidget(btn)
            self.nav_buttons.addButton(btn)
            self.all_buttons.append(btn)

        # ANALYTICS Section
        divider = self._create_section_divider()
        layout.addWidget(divider)
        self.section_dividers.append(divider)

        header = self._create_category_header("ANALYTICS")
        layout.addWidget(header)
        self.category_headers.append(header)

        # Statistics button (now directly navigates to Overview with 3 tabs)
        stats_btn = self.create_nav_button("statistics_overview", "statistics", "Statistics")
        stats_btn.setEnabled(False)  # Disable statistics button
        stats_btn.setToolTip("Statistics feature coming soon")
        layout.addWidget(stats_btn)
        self.nav_buttons.addButton(stats_btn)
        self.all_buttons.append(stats_btn)

        # SYSTEM Section
        divider = self._create_section_divider()
        layout.addWidget(divider)
        self.section_dividers.append(divider)

        header = self._create_category_header("SYSTEM")
        layout.addWidget(header)
        self.category_headers.append(header)

        # Hardware parent button (toggles submenu)
        self.hardware_button = self.create_nav_button("hardware", "chip", "Hardware")
        self.hardware_button.clicked.connect(self._on_hardware_clicked)
        layout.addWidget(self.hardware_button)
        self.nav_buttons.addButton(self.hardware_button)
        self.all_buttons.append(self.hardware_button)

        # Hardware submenu - Robot
        self.robot_button = self.create_submenu_button("robot", "motor", "Robot")
        layout.addWidget(self.robot_button)
        self.nav_buttons.addButton(self.robot_button)
        self.all_buttons.append(self.robot_button)
        self.hardware_submenu_buttons.append(self.robot_button)
        self.robot_button.setVisible(False)  # Hidden by default

        # Hardware submenu - MCU
        self.mcu_button = self.create_submenu_button("mcu", "cpu", "MCU")
        layout.addWidget(self.mcu_button)
        self.nav_buttons.addButton(self.mcu_button)
        self.all_buttons.append(self.mcu_button)
        self.hardware_submenu_buttons.append(self.mcu_button)
        self.mcu_button.setVisible(False)  # Hidden by default

        # Hardware submenu - Power Supply
        self.power_supply_button = self.create_submenu_button("power_supply", "battery", "Power Supply")
        layout.addWidget(self.power_supply_button)
        self.nav_buttons.addButton(self.power_supply_button)
        self.all_buttons.append(self.power_supply_button)
        self.hardware_submenu_buttons.append(self.power_supply_button)
        self.power_supply_button.setVisible(False)  # Hidden by default

        # Hardware submenu - Digital Output
        self.digital_output_button = self.create_submenu_button("digital_output", "toggle_on", "Digital Output")
        layout.addWidget(self.digital_output_button)
        self.nav_buttons.addButton(self.digital_output_button)
        self.all_buttons.append(self.digital_output_button)
        self.hardware_submenu_buttons.append(self.digital_output_button)
        self.digital_output_button.setVisible(False)  # Hidden by default

        # Hardware submenu - Digital Input
        self.digital_input_button = self.create_submenu_button("digital_input", "toggle_off", "Digital Input")
        layout.addWidget(self.digital_input_button)
        self.nav_buttons.addButton(self.digital_input_button)
        self.all_buttons.append(self.digital_input_button)
        self.hardware_submenu_buttons.append(self.digital_input_button)
        self.digital_input_button.setVisible(False)  # Hidden by default

        # Hardware submenu - Loadcell
        self.loadcell_button = self.create_submenu_button("loadcell", "activity", "Loadcell")
        layout.addWidget(self.loadcell_button)
        self.nav_buttons.addButton(self.loadcell_button)
        self.all_buttons.append(self.loadcell_button)
        self.hardware_submenu_buttons.append(self.loadcell_button)
        self.loadcell_button.setVisible(False)  # Hidden by default

        # Other system items
        system_items = [
            ("settings", "settings", "Settings"),
            ("about", "status_info", "About"),
        ]
        for page_id, icon_name, label in system_items:
            btn = self.create_nav_button(page_id, icon_name, label)
            layout.addWidget(btn)
            self.nav_buttons.addButton(btn)
            self.all_buttons.append(btn)

        # Set default selection
        self.nav_buttons.buttons()[0].setChecked(True)

        # Connect signals
        self.nav_buttons.buttonClicked.connect(self._on_button_clicked)

        # Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event) -> None:
        """Handle keyboard navigation"""
        key: int = event.key()

        # Ctrl+Number shortcuts for direct page navigation
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            shortcuts: dict[int, int] = {
                Qt.Key.Key_1: 0,  # Dashboard
                Qt.Key.Key_2: 1,  # Test Control
                Qt.Key.Key_3: 2,  # Results
                Qt.Key.Key_4: 3,  # Statistics
                Qt.Key.Key_5: 4,  # Hardware
                Qt.Key.Key_6: 5,  # Settings
                Qt.Key.Key_7: 6,  # About
            }
            if key in shortcuts:
                buttons = self.nav_buttons.buttons()
                btn_index: int = shortcuts[key]
                if 0 <= btn_index < len(buttons):
                    buttons[btn_index].animateClick()
                return

        # Arrow key navigation
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            buttons = self.nav_buttons.buttons()
            current_idx = -1
            for i, btn in enumerate(buttons):
                if btn.isChecked():
                    current_idx = i
                    break

            if key == Qt.Key.Key_Up and current_idx > 0:
                buttons[current_idx - 1].animateClick()
            elif key == Qt.Key.Key_Down and current_idx < len(buttons) - 1:
                buttons[current_idx + 1].animateClick()
            return

        super().keyPressEvent(event)

    def _create_category_header(self, text: str) -> QWidget:
        """Create a category header label"""
        header = QLabel(text)
        header.setStyleSheet(
            """
            QLabel {
                color: #666666;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 12px 16px 8px 16px;
                background-color: transparent;
            }
        """
        )
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return header

    def _create_section_divider(self) -> QWidget:
        """Create a subtle section divider"""
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            """
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                margin: 16px 12px;
            }
        """
        )
        return divider

    def create_nav_button(self, page_id: str, icon_name: str, label: str) -> QPushButton:
        """Create a navigation button with SVG icon and text"""
        # Get SVG icon provider
        svg_provider = get_svg_icon_provider()

        # Get multi-state SVG icon (normal, hover, active)
        icon = svg_provider.get_multi_state_icon(icon_name, size=24)

        # Create button with text
        btn = QPushButton(f"  {label}")  # Extra space for icon
        btn.setObjectName(f"nav_btn_{page_id}")
        btn.setCheckable(True)
        btn.setProperty("page_id", page_id)
        btn.setProperty("label", label)  # Store original label

        # Set icon if available
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
        else:
            # Fallback to emoji if SVG not found
            emoji = get_emoji(icon_name)
            if emoji:
                btn.setText(f"{emoji} {label}")
                btn.setProperty("emoji", emoji)

        # Style the button - fixed height to allow stretcher to work
        btn.setMinimumHeight(55)  # Compact size for half-height navigation
        btn.setMaximumHeight(55)  # Fix button height to prevent expansion
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Set font (increased size for better readability)
        font = QFont()
        font.setPointSize(15)
        font.setWeight(QFont.Weight.Medium)
        btn.setFont(font)

        # Set alignment
        btn.setStyleSheet(self._get_button_style())

        return btn

    def create_submenu_button(self, page_id: str, icon_name: str, label: str) -> QPushButton:
        """Create an indented submenu button with SVG icon"""
        # Get SVG icon provider
        svg_provider = get_svg_icon_provider()

        # Get multi-state SVG icon (smaller size for submenu)
        icon = svg_provider.get_multi_state_icon(icon_name, size=20)

        # Create button with text
        btn = QPushButton(f"  {label}")  # Extra space for icon
        btn.setObjectName(f"nav_btn_{page_id}")
        btn.setCheckable(True)
        btn.setProperty("page_id", page_id)
        btn.setProperty("label", label)  # Store original label
        btn.setProperty("icon_name", icon_name)  # Store icon name

        # Set icon if available
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))

        # Smaller height for submenu buttons
        btn.setMinimumHeight(45)
        btn.setMaximumHeight(45)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Smaller font for submenu
        font = QFont()
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Normal)
        btn.setFont(font)

        # Submenu-specific style
        btn.setStyleSheet(self._get_submenu_button_style())

        return btn

    def _get_button_style(self) -> str:
        """Get button stylesheet with modern Material Design 3 styling"""
        return """
        QPushButton {
            text-align: left;
            padding-left: 15px;
            padding-right: 10px;
            padding-top: 8px;
            padding-bottom: 8px;
            margin: 4px 8px;
            border: none;
            border-left: 4px solid transparent;
            border-radius: 12px;
            background-color: transparent;
            color: #cccccc;
            min-height: 52px;
            max-height: 52px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            border-left: 4px solid rgba(99, 179, 237, 0.5);
        }
        QPushButton:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(33, 150, 243, 0.15),
                stop:1 rgba(33, 150, 243, 0.05));
            color: #63b3ed;
            border-left: 4px solid #2196F3;
            font-weight: 600;
        }
        QPushButton:pressed {
            background-color: rgba(33, 150, 243, 0.25);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #2196F3;
            border-left: 4px solid #2196F3;
        }
        """

    def _get_submenu_button_style(self) -> str:
        """Get submenu button stylesheet with modern styling (darker, indented)"""
        return """
        QPushButton {
            text-align: left;
            padding-left: 35px;
            padding-right: 10px;
            padding-top: 6px;
            padding-bottom: 6px;
            margin: 2px 8px 2px 16px;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 10px;
            background-color: transparent;
            color: #999999;
            min-height: 42px;
            max-height: 42px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.06);
            color: #cccccc;
            border-left: 3px solid rgba(99, 179, 237, 0.4);
        }
        QPushButton:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(33, 150, 243, 0.12),
                stop:1 rgba(33, 150, 243, 0.03));
            color: #63b3ed;
            border-left: 3px solid #2196F3;
            font-weight: 500;
        }
        QPushButton:pressed {
            background-color: rgba(33, 150, 243, 0.2);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #2196F3;
            border-left: 3px solid #2196F3;
        }
        """

    def _get_collapsed_submenu_style(self) -> str:
        """Get collapsed submenu button stylesheet (centered, no indent)"""
        return """
        QPushButton {
            text-align: center;
            padding-left: 15px;
            padding-right: 10px;
            padding-top: 8px;
            padding-bottom: 8px;
            margin: 4px 8px;
            border: none;
            border-left: 4px solid transparent;
            border-radius: 12px;
            background-color: transparent;
            color: #cccccc;
            min-height: 52px;
            max-height: 52px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            border-left: 4px solid rgba(99, 179, 237, 0.5);
        }
        QPushButton:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(33, 150, 243, 0.15),
                stop:1 rgba(33, 150, 243, 0.05));
            color: #63b3ed;
            border-left: 4px solid #2196F3;
            font-weight: 600;
        }
        QPushButton:pressed {
            background-color: rgba(33, 150, 243, 0.25);
        }
        QPushButton:focus {
            outline: none;
            border: 2px solid #2196F3;
            border-left: 4px solid #2196F3;
        }
        """

    def _on_hardware_clicked(self) -> None:
        """Toggle hardware submenu visibility"""
        self.hardware_submenu_visible = not self.hardware_submenu_visible
        for btn in self.hardware_submenu_buttons:
            btn.setVisible(self.hardware_submenu_visible)

    def _on_button_clicked(self, button: QPushButton) -> None:
        """Handle navigation button click"""
        page_id = button.property("page_id")

        # Hardware button only toggles submenu, doesn't navigate
        if page_id == "hardware":
            return

        # Normal page navigation
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

    def collapse(self) -> None:
        """Collapse menu to icon-only mode"""
        self.is_collapsed = True

        # Hide category headers and dividers
        for header in self.category_headers:
            header.setVisible(False)
        for divider in self.section_dividers:
            divider.setVisible(False)

        # Update all buttons to icon-only mode
        for btn in self.all_buttons:
            label = btn.property("label")
            if label:
                btn.setText("")  # Remove text, keep only icon
                btn.setToolTip(label)  # Show label as tooltip

        # Update submenu buttons (icon-only mode with centered alignment)
        for btn in self.statistics_submenu_buttons:
            label = btn.property("label")
            if label:
                btn.setText("")  # Remove text, keep only icon
                btn.setToolTip(label)  # Show label as tooltip
                # Update icon size to match main buttons
                btn.setIconSize(QSize(24, 24))
                # Apply collapsed submenu style (centered, no indent)
                btn.setStyleSheet(self._get_collapsed_submenu_style())

        for btn in self.hardware_submenu_buttons:
            label = btn.property("label")
            if label:
                btn.setText("")  # Remove text, keep only icon
                btn.setToolTip(label)  # Show label as tooltip
                # Update icon size to match main buttons
                btn.setIconSize(QSize(24, 24))
                # Apply collapsed submenu style (centered, no indent)
                btn.setStyleSheet(self._get_collapsed_submenu_style())

        # Adjust width
        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(self.collapsed_width)

    def expand(self) -> None:
        """Expand menu to show icon + text mode"""
        self.is_collapsed = False

        # Show category headers and dividers
        for header in self.category_headers:
            header.setVisible(True)
        for divider in self.section_dividers:
            divider.setVisible(True)

        # Update all buttons to show text
        for btn in self.all_buttons:
            label = btn.property("label")
            emoji = btn.property("emoji")
            if label:
                if emoji:
                    btn.setText(f"{emoji} {label}")
                else:
                    btn.setText(f"  {label}")  # Extra space for icon
                btn.setToolTip("")  # Clear tooltip

        # Update submenu buttons (show text mode with original style)
        for btn in self.statistics_submenu_buttons:
            label = btn.property("label")
            if label:
                btn.setText(f"  {label}")  # Extra space for icon
                btn.setToolTip("")  # Clear tooltip
                # Restore original icon size
                btn.setIconSize(QSize(20, 20))
                # Restore original submenu style
                btn.setStyleSheet(self._get_submenu_button_style())

        for btn in self.hardware_submenu_buttons:
            label = btn.property("label")
            if label:
                btn.setText(f"  {label}")  # Extra space for icon
                btn.setToolTip("")  # Clear tooltip
                # Restore original icon size
                btn.setIconSize(QSize(20, 20))
                # Restore original submenu style
                btn.setStyleSheet(self._get_submenu_button_style())

        # Adjust width
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)

    def toggle_collapse(self) -> None:
        """Toggle between collapsed and expanded state"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
