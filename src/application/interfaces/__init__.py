"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.configuration.configuration import Configuration
from application.interfaces.configuration.profile_preference import ProfilePreference
from application.interfaces.repository.test_result_repository import TestResultRepository

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