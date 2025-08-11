"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

from src.application.interfaces.hardware.loadcell import LoadCellService
from src.application.interfaces.hardware.power import PowerService
from src.application.interfaces.hardware.robot import RobotService
from src.application.interfaces.hardware.mcu import MCUService
from src.application.interfaces.hardware.digital_io import DigitalIOService
from src.application.interfaces.configuration.configuration import Configuration
from src.application.interfaces.configuration.profile_preference import ProfilePreference
from src.application.interfaces.repository.test_result_repository import TestResultRepository

__all__ = [
    "LoadCellService",
    "PowerService", 
    "RobotService",
    "MCUService",
    "DigitalIOService",
    "Configuration",
    "ProfilePreference",
    "TestResultRepository",
]
