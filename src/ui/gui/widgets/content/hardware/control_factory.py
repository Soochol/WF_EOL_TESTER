"""
Hardware Control Factory

Factory pattern implementation for creating hardware control widgets.
"""

# Standard library imports
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtWidgets import QWidget

# Local imports
from .hardware_control import HardwareControlWidget


class HardwareControlFactory:
    """Factory for creating standardized hardware control widgets."""
    
    # Hardware control configurations
    HARDWARE_CONFIGS = {
        "loadcell": {
            "display_name": "Loadcell",
            "buttons": [
                {"name": "connect", "text": "Connect"},
                {"name": "disconnect", "text": "Disconnect"},
                {"name": "calibrate", "text": "Calibrate"},
            ]
        },
        "mcu": {
            "display_name": "MCU",
            "buttons": [
                {"name": "connect", "text": "Connect"},
                {"name": "disconnect", "text": "Disconnect"},
                {"name": "reset", "text": "Reset"},
            ]
        },
        "power_supply": {
            "display_name": "Power Supply",
            "buttons": [
                {"name": "connect", "text": "Connect"},
                {"name": "disconnect", "text": "Disconnect"},
                {"name": "test", "text": "Test Output"},
            ]
        },
        "robot": {
            "display_name": "Robot",
            "buttons": [
                {"name": "connect", "text": "Connect"},
                {"name": "disconnect", "text": "Disconnect"},
                {"name": "home", "text": "Home"},
            ]
        },
        "digital_io": {
            "display_name": "Digital I/O",
            "buttons": [
                {"name": "connect", "text": "Connect"},
                {"name": "disconnect", "text": "Disconnect"},
                {"name": "test", "text": "Test Channels"},
            ]
        },
    }
    
    @classmethod
    def create_control_widget(
        cls,
        hardware_type: str,
        parent: Optional[QWidget] = None
    ) -> HardwareControlWidget:
        """Create a hardware control widget for the specified type.
        
        Args:
            hardware_type: Type of hardware (e.g., 'loadcell', 'mcu', etc.)
            parent: Parent widget
            
        Returns:
            Configured hardware control widget
            
        Raises:
            ValueError: If hardware_type is not supported
        """
        if hardware_type not in cls.HARDWARE_CONFIGS:
            raise ValueError(
                f"Unsupported hardware type: {hardware_type}. "
                f"Supported types: {list(cls.HARDWARE_CONFIGS.keys())}"
            )
        
        config = cls.HARDWARE_CONFIGS[hardware_type]
        return HardwareControlWidget(
            device_name=config["display_name"],
            buttons_config=config["buttons"],
            parent=parent
        )
    
    @classmethod
    def create_all_controls(
        cls,
        parent: Optional[QWidget] = None
    ) -> Dict[str, HardwareControlWidget]:
        """Create all standard hardware control widgets.
        
        Args:
            parent: Parent widget
            
        Returns:
            Dictionary mapping hardware types to their control widgets
        """
        controls = {}
        for hardware_type in cls.HARDWARE_CONFIGS:
            controls[hardware_type] = cls.create_control_widget(hardware_type, parent)
        return controls
    
    @classmethod
    def get_supported_hardware_types(cls) -> List[str]:
        """Get list of supported hardware types.
        
        Returns:
            List of supported hardware type strings
        """
        return list(cls.HARDWARE_CONFIGS.keys())
    
    @classmethod
    def add_hardware_config(
        cls,
        hardware_type: str,
        display_name: str,
        buttons: List[Dict[str, str]]
    ) -> None:
        """Add a new hardware configuration.
        
        Args:
            hardware_type: Unique identifier for the hardware type
            display_name: Human-readable name for display
            buttons: List of button configurations
        """
        cls.HARDWARE_CONFIGS[hardware_type] = {
            "display_name": display_name,
            "buttons": buttons
        }
