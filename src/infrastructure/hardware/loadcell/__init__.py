"""
LoadCell Hardware Module

This module contains loadcell hardware implementations and services.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.loadcell.bs205 import BS205LoadCellService
except ImportError:
    BS205LoadCellService = None

try:
    from infrastructure.hardware.loadcell.mock import MockLoadCellService
except ImportError:
    MockLoadCellService = None

__all__ = []

if BS205LoadCellService:
    __all__.append('BS205LoadCellService')
    
if MockLoadCellService:
    __all__.append('MockLoadCellService')