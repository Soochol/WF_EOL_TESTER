"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

from application.interfaces.loadcell_service import LoadCellService
from application.interfaces.power_service import PowerService
from application.interfaces.robot_service import RobotService
from application.interfaces.test_repository import TestRepository

__all__ = [
    'LoadCellService',
    'PowerService',
    'RobotService', 
    'TestRepository'
]