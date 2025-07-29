"""
Domain Entities Package

Contains the core business entities that represent the main concepts in the EOL testing domain.
"""

from domain.entities.eol_test import EOLTest
from domain.entities.test_result import TestResult
from domain.entities.dut import DUT

__all__ = [
    'EOLTest',
    'TestResult',
    'DUT'
]
