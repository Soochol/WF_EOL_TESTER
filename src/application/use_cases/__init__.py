"""
Core Use Cases

Business use cases for the EOL Tester application.
Organized by domain areas for better maintainability.
"""

# Local application imports
# EOL Force Test
from application.use_cases.eol_force_test.main_use_case import (
    EOLForceTestInput,
    EOLForceTestUseCase,
    EOLTestResult,
)

# Heating/Cooling Time Test
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestInput,
    HeatingCoolingTimeTestResult,
    HeatingCoolingTimeTestUseCase,
)

# Robot Operations
from application.use_cases.robot_operations import (
    RobotHomeInput,
    RobotHomeResult,
    RobotHomeUseCase,
)

# System Tests
from application.use_cases.system_tests import (
    SimpleMCUTestInput,
    SimpleMCUTestResult,
    SimpleMCUTestUseCase,
)


__all__ = [
    # EOL Force Test
    "EOLForceTestUseCase",
    "EOLForceTestInput",
    "EOLTestResult",
    # Heating/Cooling Time Test
    "HeatingCoolingTimeTestUseCase",
    "HeatingCoolingTimeTestInput",
    "HeatingCoolingTimeTestResult",
    # Robot Operations
    "RobotHomeUseCase",
    "RobotHomeInput",
    "RobotHomeResult",
    # System Tests
    "SimpleMCUTestUseCase",
    "SimpleMCUTestInput",
    "SimpleMCUTestResult",
]
