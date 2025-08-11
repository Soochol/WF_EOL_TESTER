"""
Execute EOL Test Use Case

Comprehensive use case for executing End-of-Line tests with full Exception First architecture.
This module implements robust error handling, hardware coordination, and test evaluation
following Exception First principles throughout the entire test execution workflow.

Key Features:
- Exception First error handling at all levels
- Comprehensive hardware service coordination
- Automated configuration management and validation
- Proper resource cleanup and error reporting
- Test result evaluation with detailed failure analysis

REFACTORED: This module now uses focused components for better maintainability
while preserving identical functionality and execution order.
"""

# Import EOLTestResult from its actual location for backward compatibility
from domain.value_objects.eol_test_result import EOLTestResult

# Import all components to maintain backward compatibility
from .eol_force_test.constants import TestExecutionConstants
from .eol_force_test.main_executor import EOLForceTestCommand, EOLForceTestUseCase

# Re-export for backward compatibility
__all__ = [
    "EOLForceTestUseCase",
    "EOLForceTestCommand", 
    "TestExecutionConstants",
    "EOLTestResult",
]
