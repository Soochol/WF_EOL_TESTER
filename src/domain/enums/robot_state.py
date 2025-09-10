"""Robot state enumeration for tracking robot position and movement status."""

# Standard library imports
from enum import Enum


class RobotState(Enum):
    """Enumeration of possible robot states for position tracking."""

    UNKNOWN = "unknown"
    """Robot state is unknown (typically at system startup)."""

    HOME = "home"
    """Robot is at the home position (calibrated origin)."""

    INITIAL_POSITION = "initial_position"
    """Robot is at the test initial/standby position."""

    MEASUREMENT_POSITION = "measurement_position"
    """Robot is at a measurement position for force testing."""

    MAX_STROKE = "max_stroke"
    """Robot is at the maximum stroke position."""

    MOVING = "moving"
    """Robot is currently moving between positions."""


__all__ = ["RobotState"]
