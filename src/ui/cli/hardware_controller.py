"""
Hardware Control Manager - Legacy Compatibility Module

This module has been refactored into a modular controller structure.
Imports from the new controllers package for backward compatibility.

New structure:
- controllers/base/hardware_controller.py - Abstract base class
- controllers/hardware/ - Specialized hardware controllers
- controllers/orchestration/ - Hardware management orchestration

For new development, import directly from the controllers package.
"""

# Legacy compatibility imports - use controllers package for new development
from .controllers import (
    HardwareController,
    HardwareControlManager,
    LoadCellController,
    MCUController,
    PowerController,
    RobotController,
)
from .controllers.base.hardware_controller import simple_interactive_menu

# Re-export for backward compatibility
__all__ = [
    "HardwareController",
    "RobotController",
    "MCUController",
    "LoadCellController",
    "PowerController",
    "HardwareControlManager",
    "simple_interactive_menu",
]
