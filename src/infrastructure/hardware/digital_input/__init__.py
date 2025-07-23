"""
Digital Input Hardware Module

This module contains digital input hardware services organized by device type.
Provides digital I/O control for EOL testing systems.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.digital_input.ajinextek import AjinextekInputService
except ImportError:
    AjinextekInputService = None

try:
    from infrastructure.hardware.digital_input.mock import MockInputService
except ImportError:
    MockInputService = None

__all__ = []

if AjinextekInputService:
    __all__.append('AjinextekInputService')
    
if MockInputService:
    __all__.append('MockInputService')