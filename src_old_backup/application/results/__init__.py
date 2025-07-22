"""
Application Results Package

Contains result objects that represent output data from use cases.
Results are immutable data structures that carry the outcome and 
relevant information from use case execution.
"""

from .eol_test_result import EOLTestResult
from .hardware_control_result import HardwareControlResult
from .report_generation_result import ReportGenerationResult

__all__ = [
    'EOLTestResult',
    'HardwareControlResult',
    'ReportGenerationResult'
]