"""
MCU Hardware Module

This module contains MCU (Microcontroller Unit) hardware implementations and services.
Handles temperature control, test modes, and fan management.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.mcu.lma import LMAMCUService
except ImportError:
    LMAMCUService = None

try:
    from infrastructure.hardware.mcu.mock import MockMCUService
except ImportError:
    MockMCUService = None

__all__ = []

if LMAMCUService:
    __all__.append('LMAMCUService')
    
if MockMCUService:
    __all__.append('MockMCUService')