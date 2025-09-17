"""
Domain Entities Package

Contains the core business entities that represent the main concepts in the EOL testing domain.
"""

# Local application imports
from domain.entities.dut import DUT
from domain.entities.eol_test import EOLTest
from domain.entities.test_result import TestResult


__all__ = ["EOLTest", "TestResult", "DUT"]
