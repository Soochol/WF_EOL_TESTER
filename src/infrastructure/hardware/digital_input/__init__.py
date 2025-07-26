"""
Digital Input Hardware Module

This module contains digital input hardware services organized by device type.
Provides digital I/O control for EOL testing systems.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.digital_input.ajinextek import AjinextekInputAdapter
except ImportError:
    AjinextekInputAdapter = None

try:
    from infrastructure.hardware.digital_input.mock import MockInputAdapter
except ImportError:
    MockInputAdapter = None

__all__ = []

if AjinextekInputAdapter:
    __all__.append('AjinextekInputAdapter')
    
if MockInputAdapter:
    __all__.append('MockInputAdapter')