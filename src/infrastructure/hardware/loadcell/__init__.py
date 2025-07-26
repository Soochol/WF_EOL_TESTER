"""
LoadCell Hardware Module

This module contains loadcell hardware implementations and services.
"""

# Import device-specific implementations
try:
    from infrastructure.hardware.loadcell.bs205 import BS205LoadCellAdapter
except ImportError:
    BS205LoadCellAdapter = None

try:
    from infrastructure.hardware.loadcell.mock import MockLoadCellAdapter
except ImportError:
    MockLoadCellAdapter = None

__all__ = []

if BS205LoadCellAdapter:
    __all__.append('BS205LoadCellAdapter')
    
if MockLoadCellAdapter:
    __all__.append('MockLoadCellAdapter')