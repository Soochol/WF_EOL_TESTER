"""
Core Use Cases

Business use cases for the EOL Tester application.
Organized by domain areas for better maintainability.
"""

# EOL Force Test
from application.use_cases.eol_force_test.main_executor import (
    EOLForceTestUseCase,
    EOLForceTestCommand,
)
from domain.value_objects.eol_test_result import EOLTestResult

# Heating/Cooling Time Test
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestUseCase,
    HeatingCoolingTimeTestCommand,
    HeatingCoolingTimeTestResult,
)

# Robot Operations
from application.use_cases.robot_operations import (
    RobotHomeUseCase,
    RobotHomeCommand,
    RobotHomeResult,
)

# System Tests
from application.use_cases.system_tests import (
    SimpleMCUTestUseCase,
    SimpleMCUTestCommand,
    SimpleMCUTestResult,
)

__all__ = [
    # EOL Force Test
    "EOLForceTestUseCase", 
    "EOLForceTestCommand", 
    "EOLTestResult",
    
    # Heating/Cooling Time Test
    "HeatingCoolingTimeTestUseCase",
    "HeatingCoolingTimeTestCommand", 
    "HeatingCoolingTimeTestResult",
    
    # Robot Operations
    "RobotHomeUseCase",
    "RobotHomeCommand",
    "RobotHomeResult",
    
    # System Tests
    "SimpleMCUTestUseCase",
    "SimpleMCUTestCommand",
    "SimpleMCUTestResult",
]
