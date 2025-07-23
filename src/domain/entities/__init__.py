"""
Domain Entities Package

Contains the core business entities that represent the main concepts in the EOL testing domain.
"""

from domain.entities.eol_test import EOLTest
from domain.entities.measurement import Measurement  
from domain.entities.test_result import TestResult
from domain.entities.hardware_device import HardwareDevice
from domain.entities.dut import DUT

__all__ = [
    'EOLTest',
    'Measurement', 
    'TestResult',
    'HardwareDevice',
    'DUT'
]