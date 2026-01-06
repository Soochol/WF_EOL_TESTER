"""
Ajinextek AXL Driver

Windows-only driver for Ajinextek motion control hardware.
Provides access to Robot and Digital I/O functionality through the AXL library.
"""

from .constants import (
    SERVO_OFF,
    SERVO_ON,
    POS_ABS,
    POS_REL,
    HOME_SUCCESS,
    HOME_SEARCHING,
    STOP_DECEL,
    STOP_IMMEDIATE,
    DIR_CCW,
    DIR_CW,
)
from .error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
    is_success,
    is_motion_error,
    is_dio_error,
)
from .exceptions import (
    AXLError,
    AXLMotionError,
    AXLDIOError,
    AXLConnectionError,
    AXLPlatformError,
)
from .axl_wrapper import AXLWrapper

__all__ = [
    # Wrapper
    "AXLWrapper",
    # Constants
    "SERVO_OFF",
    "SERVO_ON",
    "POS_ABS",
    "POS_REL",
    "HOME_SUCCESS",
    "HOME_SEARCHING",
    "STOP_DECEL",
    "STOP_IMMEDIATE",
    "DIR_CCW",
    "DIR_CW",
    # Error codes
    "AXT_RT_SUCCESS",
    "get_error_message",
    "is_success",
    "is_motion_error",
    "is_dio_error",
    # Exceptions
    "AXLError",
    "AXLMotionError",
    "AXLDIOError",
    "AXLConnectionError",
    "AXLPlatformError",
]
