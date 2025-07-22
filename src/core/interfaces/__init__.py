"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

from .loadcell_service import LoadCellService
from .power_service import PowerService
from .test_repository import TestRepository

__all__ = [
    'LoadCellService',
    'PowerService', 
    'TestRepository'
]