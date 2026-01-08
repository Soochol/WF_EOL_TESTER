"""
Domain module for standalone EOL Tester sequence.
Contains value objects, exceptions, and enums.
"""

from .exceptions import ValidationException, HardwareException
from .value_objects import (
    TestConfiguration,
    HardwareConfig,
    DUTCommandInfo,
    TestMeasurements,
    CycleResult,
    PassCriteria,
)
from .enums import RobotState

__all__ = [
    "ValidationException",
    "HardwareException",
    "TestConfiguration",
    "HardwareConfig",
    "DUTCommandInfo",
    "TestMeasurements",
    "CycleResult",
    "PassCriteria",
    "RobotState",
]
