"""
Core Interfaces

Core interfaces for the EOL Tester application.
"""

from application.interfaces.loadcell import LoadCellService
from application.interfaces.power import PowerService
from application.interfaces.robot import RobotService
from application.interfaces.mcu import MCUService
from application.interfaces.digital_input import DigitalInputService
from application.interfaces.configuration_repository import ConfigurationRepository
from application.interfaces.test_repository import TestRepository
from application.interfaces.profile_preference_repository import ProfilePreferenceRepository

__all__ = [
    'LoadCellService',
    'PowerService',
    'RobotService',
    'MCUService',
    'DigitalInputService',
    'ConfigurationRepository',
    'TestRepository',
    'ProfilePreferenceRepository'
]