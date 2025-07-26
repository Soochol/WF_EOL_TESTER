"""
Power Supply Hardware Module

This module contains power supply hardware implementations and services.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.power.oda import OdaPowerAdapter
except ImportError:
    OdaPowerAdapter = None

try:
    from infrastructure.hardware.power.mock import MockPowerAdapter
except ImportError:
    MockPowerAdapter = None

__all__ = []

if OdaPowerAdapter:
    __all__.append('OdaPowerAdapter')
    
if MockPowerAdapter:
    __all__.append('MockPowerAdapter')