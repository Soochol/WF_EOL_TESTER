"""
Adapter Interfaces

Abstract interfaces that define the contract between service implementations
and hardware-specific adapters.
"""

from .loadcell_adapter import LoadCellAdapter
from .power_adapter import PowerAdapter
from .robot_adapter import RobotAdapter

__all__ = [
    'LoadCellAdapter',
    'PowerAdapter',
    'RobotAdapter'
]