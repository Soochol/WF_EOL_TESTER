"""
MCU Hardware Module

This module contains MCU (Microcontroller Unit) hardware implementations and services.
Handles temperature control, test modes, and fan management.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.mcu.lma import LMAMCUAdapter
except ImportError:
    LMAMCUAdapter = None

try:
    from infrastructure.hardware.mcu.mock import MockMCUAdapter
except ImportError:
    MockMCUAdapter = None

__all__ = []

if LMAMCUAdapter:
    __all__.append('LMAMCUAdapter')
    
if MockMCUAdapter:
    __all__.append('MockMCUAdapter')