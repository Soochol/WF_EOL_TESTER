"""
Side Menu Widget for WF EOL Tester GUI

Navigation menu with industrial styling and accessibility features.
"""

from typing import Any, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import QSize, Qt, Signal, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ui.gui.services.gui_state_manager import GUIStateManager


class MenuButton(QPushButton):
    """Custom menu button with enhanced styling and accessibility"""

    def __init__(
        self, text: str, panel_id: str, description: str = "", parent: Optional[QWidget] = None
    ):
        """
        Initialize menu button

        Args:
            text: Button display text
            panel_id: ID of associated panel
            description: Accessibility description
            parent: Parent widget
        """
        super().__init__(text, parent)

        self.panel_id = panel_id
        self.is_active = False

        # Setup button properties
        self.setCheckable(True)
        self.setMinimumHeight(60)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Accessibility
        self.setAccessibleName(f"{text} Navigation Button")
        if description:
            self.setAccessibleDescription(description)

        # Set font
        button_font = QFont("Arial", 11, QFont.Weight.DemiBold)
        self.setFont(button_font)

        # Apply initial styling
        self.update_style()

    def set_active(self, active: bool) -> None:
        """
        Set button active state

        Args:
            active: Whether button is active
        """
        if active != self.is_active:
            self.is_active = active
            self.setChecked(active)
            self.update_style()

    def update_style(self) -> None:
        """Update button styling based on state"""
        if self.is_active:
            # Active state - highlighted
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: 2px solid #2980B9;
                    border-left: 4px solid #2980B9;
                    text-align: left;
                    padding-left: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5DADE2;
                }
            """
            )
        else:
            # Inactive state
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    border: 2px solid #BDC3C7;
                    border-left: 4px solid transparent;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #D5DBDB;
                    border-left: 4px solid #3498DB;
                }
                QPushButton:focus {
                    border: 2px solid #3498DB;
                    outline: none;
                }
            """
            )


class ExpandableMenuButton(MenuButton):
    """Expandable menu button for parent categories with expand/collapse functionality"""
    
    # Signal emitted when expand state changes
    expanded_changed = Signal(bool)
    
    def __init__(
        self, text: str, panel_id: str, description: str = "", parent: Optional[QWidget] = None
    ):
        """
        Initialize expandable menu button
        
        Args:
            text: Button display text
            panel_id: ID of associated panel
            description: Accessibility description
            parent: Parent widget
        """
        super().__init__(text, panel_id, description, parent)
        
        self.is_expanded = False
        self.original_text = text
        
        # Update text to show collapse indicator
        self.setText(f"▶ {self.original_text}")
    
    def toggle_expanded(self) -> None:
        """Toggle expanded state"""
        self.set_expanded(not self.is_expanded)
    
    def set_expanded(self, expanded: bool) -> None:
        """
        Set expanded state
        
        Args:
            expanded: Whether to expand the menu
        """
        if expanded != self.is_expanded:
            self.is_expanded = expanded
            
            # Update text and icon
            if expanded:
                self.setText(f"▼ {self.original_text}")
            else:
                self.setText(f"▶ {self.original_text}")
            
            self.expanded_changed.emit(expanded)
    
    def mousePressEvent(self, event):
        """Override mouse press to handle expand/collapse"""
        # Toggle expansion instead of normal button behavior
        self.toggle_expanded()
        # Don't call super() to avoid normal button click behavior


class SubMenuButton(MenuButton):
    """Sub-menu button for child items with indented styling"""
    
    def __init__(
        self, text: str, panel_id: str, description: str = "", parent: Optional[QWidget] = None
    ):
        """
        Initialize sub-menu button
        
        Args:
            text: Button display text
            panel_id: ID of associated panel
            description: Accessibility description
            parent: Parent widget
        """
        super().__init__(text, panel_id, description, parent)
        
        # Override height for sub-menu buttons
        self.setMinimumHeight(45)
        
        # Apply sub-menu specific styling
        self.update_sub_menu_style()
    
    def update_sub_menu_style(self) -> None:
        """Update styling specific to sub-menu buttons"""
        if self.is_active:
            # Active sub-menu state
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #2ECC71;
                    color: white;
                    border: 2px solid #27AE60;
                    border-left: 4px solid #27AE60;
                    text-align: left;
                    padding-left: 40px;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #58D68D;
                }
            """
            )
        else:
            # Inactive sub-menu state
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #F8F9FA;
                    color: #495057;
                    border: 1px solid #DEE2E6;
                    border-left: 4px solid transparent;
                    text-align: left;
                    padding-left: 40px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                    border-left: 4px solid #2ECC71;
                }
                QPushButton:focus {
                    border: 2px solid #2ECC71;
                    outline: none;
                }
            """
            )
    
    def update_style(self) -> None:
        """Override parent update_style to use sub-menu styling"""
        self.update_sub_menu_style()


class SideMenuWidget(QWidget):
    """
    Side menu widget for navigation

    Provides navigation buttons for different application panels
    with industrial styling and clear visual hierarchy.
    """

    # Signals
    panel_requested = Signal(str)  # panel_id
    exit_requested = Signal()

    def __init__(self, state_manager: GUIStateManager, parent: Optional[QWidget] = None):
        """
        Initialize side menu widget

        Args:
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        self.state_manager = state_manager

        # Menu configuration with hierarchical structure
        self.menu_items = [
            {
                "id": "dashboard",
                "text": "Dashboard",
                "description": "View system overview and status",
                "type": "normal",
                "default": True,
            },
            {
                "id": "use_cases",
                "text": "Use Cases",
                "description": "Available test use cases",
                "type": "expandable",
                "children": [
                    {
                        "id": "eol_test",
                        "text": "EOL Force Test",
                        "description": "Execute end-of-line force testing",
                        "type": "sub",
                    },
                    {
                        "id": "mcu_test",
                        "text": "Simple MCU Test",
                        "description": "Perform basic MCU communication test",
                        "type": "sub",
                    },
                    {
                        "id": "heating_cooling_test",
                        "text": "Heating Cooling Time Test",
                        "description": "Execute heating and cooling time testing",
                        "type": "sub",
                    },
                ]
            },
            {
                "id": "hardware",
                "text": "Hardware Control",
                "description": "Manual hardware control and monitoring",
                "type": "normal",
            },
        ]

        # Button tracking
        self.menu_buttons: Dict[str, MenuButton] = {}
        self.sub_menu_buttons: Dict[str, SubMenuButton] = {}
        self.expandable_buttons: Dict[str, ExpandableMenuButton] = {}
        self.button_group = QButtonGroup()
        self.active_panel: Optional[str] = None
        self.expanded_menus: set = set()  # Track which expandable menus are open

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()

        logger.debug("Side menu widget initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setFixedWidth(250)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Create menu buttons based on type
        for item in self.menu_items:
            if item.get("type") == "expandable":
                # Create expandable button
                button = ExpandableMenuButton(
                    text=item["text"],
                    panel_id=item["id"],
                    description=item.get("description", ""),
                    parent=self,
                )
                self.expandable_buttons[item["id"]] = button
                self.menu_buttons[item["id"]] = button
                
                # Connect expand/collapse signal
                button.expanded_changed.connect(
                    lambda expanded, menu_id=item["id"]: self.on_menu_expanded(menu_id, expanded)
                )
                
                # Create sub-menu buttons (initially hidden)
                for child_item in item.get("children", []):
                    sub_button = SubMenuButton(
                        text=child_item["text"],
                        panel_id=child_item["id"],
                        description=child_item.get("description", ""),
                        parent=self,
                    )
                    self.sub_menu_buttons[child_item["id"]] = sub_button
                    self.menu_buttons[child_item["id"]] = sub_button
                    self.button_group.addButton(sub_button)
                    
                    # Initially hide sub-menu buttons
                    sub_button.setVisible(False)
                    
                    # Set default active button
                    if child_item.get("default", False):
                        self.active_panel = child_item["id"]
                        sub_button.set_active(True)
                        
            else:
                # Create normal button
                button = MenuButton(
                    text=item["text"],
                    panel_id=item["id"],
                    description=item.get("description", ""),
                    parent=self,
                )
                self.menu_buttons[item["id"]] = button
                self.button_group.addButton(button)

                # Set default active button
                if item.get("default", False):
                    self.active_panel = item["id"]
                    button.set_active(True)

        # Create exit button (separate styling)
        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumHeight(50)
        self.exit_button.setAccessibleName("Exit Application")
        self.exit_button.setAccessibleDescription("Close the WF EOL Tester application")

        # Exit button styling
        self.exit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: 2px solid #C0392B;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #CD212A;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
            QPushButton:focus {
                outline: 3px solid #F39C12;
                outline-offset: 2px;
            }
        """
        )

        # Create header label
        self.header_label = QLabel("NAVIGATION")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont("Arial", 10, QFont.Weight.Bold)
        self.header_label.setFont(header_font)
        self.header_label.setStyleSheet(
            """
            QLabel {
                color: #2C3E50;
                background-color: #BDC3C7;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 8px;
            }
        """
        )

    def setup_layout(self) -> None:
        """Setup widget layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 16, 8, 16)
        main_layout.setSpacing(4)

        # Add header
        main_layout.addWidget(self.header_label)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #BDC3C7;")
        main_layout.addWidget(separator)

        # Add menu buttons (hierarchical layout)
        for item in self.menu_items:
            button = self.menu_buttons.get(item["id"])
            if button:
                main_layout.addWidget(button)
                
                # Add sub-menu buttons if this is an expandable menu
                if item.get("type") == "expandable":
                    for child_item in item.get("children", []):
                        sub_button = self.sub_menu_buttons.get(child_item["id"])
                        if sub_button:
                            main_layout.addWidget(sub_button)

        # Add flexible space
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(spacer)

        # Add separator before exit
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("color: #BDC3C7;")
        main_layout.addWidget(separator2)

        # Add exit button
        main_layout.addWidget(self.exit_button)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Normal menu button signals (excluding expandable buttons)
        for panel_id, button in self.menu_buttons.items():
            if panel_id not in self.expandable_buttons:
                button.clicked.connect(lambda checked=False, pid=panel_id: self.on_menu_clicked(pid))

        # Exit button signal
        self.exit_button.clicked.connect(self.exit_requested.emit)

        # State manager signals
        if self.state_manager:
            self.state_manager.panel_changed.connect(self.on_panel_changed)
    
    def on_menu_expanded(self, menu_id: str, expanded: bool) -> None:
        """
        Handle expandable menu expand/collapse
        
        Args:
            menu_id: ID of the expandable menu
            expanded: Whether the menu is expanded
        """
        if expanded:
            # Collapse other expandable menus (single expand behavior)
            for other_id, other_button in self.expandable_buttons.items():
                if other_id != menu_id and other_button.is_expanded:
                    other_button.set_expanded(False)
                    self.hide_sub_menu(other_id)
            
            # Show this menu's sub-items
            self.show_sub_menu(menu_id)
            self.expanded_menus.add(menu_id)
        else:
            # Hide sub-items
            self.hide_sub_menu(menu_id)
            self.expanded_menus.discard(menu_id)
        
        logger.debug(f"Menu {'expanded' if expanded else 'collapsed'}: {menu_id}")
    
    def show_sub_menu(self, menu_id: str) -> None:
        """
        Show sub-menu items for an expandable menu
        
        Args:
            menu_id: ID of the expandable menu
        """
        # Find the menu item configuration
        for item in self.menu_items:
            if item["id"] == menu_id and item.get("type") == "expandable":
                for child_item in item.get("children", []):
                    sub_button = self.sub_menu_buttons.get(child_item["id"])
                    if sub_button:
                        sub_button.setVisible(True)
                break
    
    def hide_sub_menu(self, menu_id: str) -> None:
        """
        Hide sub-menu items for an expandable menu
        
        Args:
            menu_id: ID of the expandable menu
        """
        # Find the menu item configuration
        for item in self.menu_items:
            if item["id"] == menu_id and item.get("type") == "expandable":
                for child_item in item.get("children", []):
                    sub_button = self.sub_menu_buttons.get(child_item["id"])
                    if sub_button:
                        sub_button.setVisible(False)
                        # If this sub-menu item was active, deactivate it
                        if child_item["id"] == self.active_panel:
                            sub_button.set_active(False)
                break

    def on_menu_clicked(self, panel_id: str) -> None:
        """
        Handle menu button click

        Args:
            panel_id: ID of clicked panel
        """
        if panel_id != self.active_panel:
            # If clicking a sub-menu item, ensure its parent is expanded
            self.ensure_parent_expanded(panel_id)
            
            # Collapse other expandable menus when switching to a different section
            if panel_id not in self.sub_menu_buttons:
                for expandable_id in list(self.expanded_menus):
                    expandable_button = self.expandable_buttons.get(expandable_id)
                    if expandable_button:
                        expandable_button.set_expanded(False)
                        self.hide_sub_menu(expandable_id)
            
            self.set_active_panel(panel_id)
            self.panel_requested.emit(panel_id)
            logger.debug(f"Menu clicked: {panel_id}")
    
    def ensure_parent_expanded(self, panel_id: str) -> None:
        """
        Ensure the parent expandable menu is expanded for a sub-menu item
        
        Args:
            panel_id: ID of the panel (could be a sub-menu item)
        """
        # Check if this is a sub-menu item and find its parent
        for item in self.menu_items:
            if item.get("type") == "expandable":
                for child_item in item.get("children", []):
                    if child_item["id"] == panel_id:
                        # This is a sub-menu item, ensure parent is expanded
                        parent_button = self.expandable_buttons.get(item["id"])
                        if parent_button and not parent_button.is_expanded:
                            parent_button.set_expanded(True)
                        return

    def on_panel_changed(self, panel_id: str) -> None:
        """
        Handle panel change from state manager

        Args:
            panel_id: New active panel ID
        """
        self.set_active_panel(panel_id)

    def set_active_panel(self, panel_id: str) -> None:
        """
        Set active panel and update button states

        Args:
            panel_id: ID of panel to activate
        """
        if panel_id in self.menu_buttons:
            # Deactivate current button
            if self.active_panel and self.active_panel in self.menu_buttons:
                self.menu_buttons[self.active_panel].set_active(False)

            # Activate new button
            self.menu_buttons[panel_id].set_active(True)
            self.active_panel = panel_id

            logger.debug(f"Active panel set to: {panel_id}")

    def get_active_panel(self) -> Optional[str]:
        """
        Get currently active panel ID

        Returns:
            Active panel ID or None
        """
        return self.active_panel

    def enable_panel(self, panel_id: str, enabled: bool = True) -> None:
        """
        Enable or disable a panel button

        Args:
            panel_id: Panel ID to enable/disable
            enabled: Whether to enable the panel
        """
        if panel_id in self.menu_buttons:
            self.menu_buttons[panel_id].setEnabled(enabled)

            if not enabled and panel_id == self.active_panel:
                # Switch to dashboard if current panel is disabled
                self.set_active_panel("dashboard")
                self.panel_requested.emit("dashboard")

    def update_button_text(self, panel_id: str, text: str) -> None:
        """
        Update button display text

        Args:
            panel_id: Panel ID to update
            text: New button text
        """
        if panel_id in self.menu_buttons:
            self.menu_buttons[panel_id].setText(text)

    def add_badge(self, panel_id: str, badge_text: str) -> None:
        """
        Add badge text to button (e.g., notification count)

        Args:
            panel_id: Panel ID to add badge to
            badge_text: Badge text
        """
        if panel_id in self.menu_buttons:
            button = self.menu_buttons[panel_id]
            original_text = button.text().split(" (")[0]  # Remove existing badge
            button.setText(f"{original_text} ({badge_text})")

    def remove_badge(self, panel_id: str) -> None:
        """
        Remove badge from button

        Args:
            panel_id: Panel ID to remove badge from
        """
        if panel_id in self.menu_buttons:
            button = self.menu_buttons[panel_id]
            original_text = button.text().split(" (")[0]
            button.setText(original_text)

    def get_menu_item_info(self, panel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get menu item information

        Args:
            panel_id: Panel ID to get info for

        Returns:
            Menu item information dict or None
        """
        for item in self.menu_items:
            if item["id"] == panel_id:
                return item
        return None

    def set_exit_button_enabled(self, enabled: bool) -> None:
        """
        Enable or disable exit button

        Args:
            enabled: Whether to enable exit button
        """
        self.exit_button.setEnabled(enabled)

    def highlight_panel(self, panel_id: str, highlight: bool = True) -> None:
        """
        Highlight a panel button (e.g., for notifications)

        Args:
            panel_id: Panel ID to highlight
            highlight: Whether to highlight
        """
        if panel_id in self.menu_buttons:
            button = self.menu_buttons[panel_id]

            if highlight:
                # Add highlight styling
                current_style = button.styleSheet()
                highlight_style = current_style.replace(
                    "border-left: 4px solid transparent;", "border-left: 4px solid #F39C12;"
                )
                button.setStyleSheet(highlight_style)
            else:
                # Remove highlight - trigger style update
                button.update_style()
