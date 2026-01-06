"""
AJINEXTEK Robot Service

Hardware implementation for AJINEXTEK robot controllers using AXL library.
"""

try:
    # Local application imports
    from infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
        AjinextekRobot,
    )
    from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import AXLWrapper
    from infrastructure.implementation.hardware.robot.ajinextek.constants import (
        DLL_PATH,
        SERVO_OFF,
        SERVO_ON,
        MOTION_STATUS_IDLE,
        MOTION_STATUS_MOVING,
        MOTION_STATUS_ERROR,
        POS_ABS,
        POS_REL,
        STOP_DECEL,
        STOP_IMMEDIATE,
        DIR_CCW,
        DIR_CW,
        HOME_SUCCESS,
        HOME_SEARCHING,
        MAX_AXIS_COUNT,
    )
    from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
        AXT_RT_SUCCESS,
        AXT_RT_MOTION_INVALID_AXIS_NO,
        get_error_message,
        is_success,
        is_motion_error,
    )

    _AJINEXTEK_AVAILABLE = True
except ImportError as e:
    # Standard library imports
    import warnings

    warnings.warn(f"AJINEXTEK robot service not available: {e}")
    _AJINEXTEK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.extend(["AjinextekRobot", "AXLWrapper"])
