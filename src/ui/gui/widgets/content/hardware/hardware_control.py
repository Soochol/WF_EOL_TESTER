"""
Hardware Control Widget

Reusable widget for individual hardware device controls.
"""

# Standard library imports
from typing import Dict, List, Optional, Callable

# Third-party imports
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)

# Local imports
from .styles import HardwareStyles


class HardwareControlWidget(QWidget):
    """Reusable hardware control widget with configurable buttons."""

    def __init__(
        self,
        device_name: str,
        buttons_config: List[Dict[str, str]],
        parent: Optional[QWidget] = None,
    ):
        """Initialize hardware control widget.
        
        Args:
            device_name: Display name of the hardware device
            buttons_config: List of button configurations with 'name' and 'text' keys
            parent: Parent widget
        """
        super().__init__(parent)
        self.device_name = device_name
        self.buttons_config = buttons_config
        self.buttons: Dict[str, QPushButton] = {}
        self.button_callbacks: Dict[str, Callable] = {}
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self) -> None:
        """Setup the control widget UI."""
        layout = QGridLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Device label
        label = QLabel(f"{self.device_name}:")
        layout.addWidget(label, 0, 0)
        
        # Create buttons based on configuration
        for i, button_config in enumerate(self.buttons_config):
            button_name = button_config["name"]
            button_text = button_config["text"]
            
            button = QPushButton(button_text)
            button.setObjectName(f"{self.device_name.lower()}_{button_name}_btn")
            
            # Store button reference
            self.buttons[button_name] = button
            
            # Add to layout (starting from column 1)
            layout.addWidget(button, 0, i + 1)
    
    def apply_styles(self) -> None:
        """Apply styles to the widget."""
        self.setStyleSheet(HardwareStyles.get_button_stylesheet())
        
        # Apply label styling
        for child in self.findChildren(QLabel):
            child.setStyleSheet("color: #cccccc; font-size: 14px; font-weight: bold;")
    
    def connect_button(self, button_name: str, callback: Callable) -> None:
        """Connect a button to a callback function.
        
        Args:
            button_name: Name of the button (as defined in buttons_config)
            callback: Function to call when button is clicked
        """
        if button_name in self.buttons:
            self.buttons[button_name].clicked.connect(callback)
            self.button_callbacks[button_name] = callback
        else:
            raise ValueError(f"Button '{button_name}' not found in widget")
    
    def set_button_enabled(self, button_name: str, enabled: bool) -> None:
        """Enable or disable a specific button.
        
        Args:
            button_name: Name of the button to modify
            enabled: Whether the button should be enabled
        """
        if button_name in self.buttons:
            self.buttons[button_name].setEnabled(enabled)
        else:
            raise ValueError(f"Button '{button_name}' not found in widget")
    
    def get_button(self, button_name: str) -> Optional[QPushButton]:
        """Get a button by name.
        
        Args:
            button_name: Name of the button to retrieve
            
        Returns:
            The button widget or None if not found
        """
        return self.buttons.get(button_name)
    
    def set_all_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable all buttons in the widget.
        
        Args:
            enabled: Whether all buttons should be enabled
        """
        for button in self.buttons.values():
            button.setEnabled(enabled)
