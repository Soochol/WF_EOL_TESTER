"""
Standalone enums for EOL Tester sequence.
"""

from enum import Enum, auto


class RobotState(Enum):
    """Robot position/movement state."""
    UNKNOWN = auto()
    HOME = auto()
    INITIAL_POSITION = auto()
    MOVING = auto()
    MAX_STROKE = auto()
    MEASUREMENT_POSITION = auto()


class TestMode(Enum):
    """MCU test mode."""
    MODE_0 = 0
    MODE_1 = 1
    MODE_2 = 2
