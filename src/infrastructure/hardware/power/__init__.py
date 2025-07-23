"""
Power Supply Hardware Module

This module contains power supply hardware implementations and services.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.power.oda import OdaPowerService
except ImportError:
    OdaPowerService = None

try:
    from infrastructure.hardware.power.mock import MockPowerService
except ImportError:
    MockPowerService = None

__all__ = []

if OdaPowerService:
    __all__.append('OdaPowerService')
    
if MockPowerService:
    __all__.append('MockPowerService')