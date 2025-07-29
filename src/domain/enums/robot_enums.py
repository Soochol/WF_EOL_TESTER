"""
Robot Related Enumerations

Robot motion and status related enums for position control and status tracking.
"""

from enum import Enum


class MotionStatus(Enum):
    """모션 상태"""

    IDLE = "idle"
    MOVING = "moving"
    ERROR = "error"
    COMPLETED = "completed"
    HOMING = "homing"
    STOPPED = "stopped"
    EMERGENCY_STOP = "emergency_stop"
