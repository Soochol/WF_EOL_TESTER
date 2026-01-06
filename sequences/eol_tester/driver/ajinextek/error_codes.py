"""
AJINEXTEK AXL Library Error Codes

This module contains all error codes and descriptions from the AXL library.
"""

# Success
AXT_RT_SUCCESS = 0x0000

# Library Errors (1000-1099)
AXT_RT_OPEN_ERROR = 1001
AXT_RT_OPEN_ALREADY = 1002
AXT_RT_NOT_INITIAL = 1052
AXT_RT_NOT_OPEN = 1053
AXT_RT_NOT_SUPPORT_VERSION = 1054
AXT_RT_BAD_PARAMETER = 1070

# Hardware Validation Errors (1100-1159)
AXT_RT_INVALID_HARDWARE = 1100
AXT_RT_INVALID_BOARD_NO = 1101
AXT_RT_INVALID_MODULE_POS = 1102
AXT_RT_INVALID_LEVEL = 1103
AXT_RT_INVALID_VARIABLE = 1104
AXT_RT_INVALID_MODULE_NO = 1105
AXT_RT_INVALID_NO = 1106

# Motion Module Errors (4000-4999)
AXT_RT_MOTION_OPEN_ERROR = 4001
AXT_RT_MOTION_NOT_MODULE = 4051
AXT_RT_MOTION_INVALID_AXIS_NO = 4101
AXT_RT_MOTION_INVALID_METHOD = 4102
AXT_RT_MOTION_INVALID_VELOCITY = 4113
AXT_RT_MOTION_ERROR_IN_MOTION = 4152
AXT_RT_MOTION_HOME_SEARCHING = 4201
AXT_RT_PROTECTED_DURING_SERVOON = 4260

# DIO Module Errors (3000-3199)
AXT_RT_DIO_OPEN_ERROR = 3001
AXT_RT_DIO_NOT_MODULE = 3051
AXT_RT_DIO_INVALID_MODULE_NO = 3101
AXT_RT_DIO_INVALID_OFFSET_NO = 3102
AXT_RT_DIO_INVALID_VALUE = 3105

ERROR_MESSAGES = {
    AXT_RT_SUCCESS: "Function executed successfully",
    AXT_RT_OPEN_ERROR: "Library is not open",
    AXT_RT_OPEN_ALREADY: "Library is already open and in use",
    AXT_RT_NOT_INITIAL: "Serial module is not initialized",
    AXT_RT_NOT_OPEN: "Library initialization failed",
    AXT_RT_NOT_SUPPORT_VERSION: "Unsupported hardware",
    AXT_RT_BAD_PARAMETER: "Invalid parameter provided by user",
    AXT_RT_INVALID_HARDWARE: "Invalid board",
    AXT_RT_INVALID_BOARD_NO: "Invalid board number",
    AXT_RT_INVALID_MODULE_POS: "Invalid module position",
    AXT_RT_INVALID_LEVEL: "Invalid level",
    AXT_RT_INVALID_VARIABLE: "Invalid variable",
    AXT_RT_INVALID_MODULE_NO: "Invalid module number",
    AXT_RT_INVALID_NO: "Invalid number",
    AXT_RT_DIO_OPEN_ERROR: "DIO module open failed",
    AXT_RT_DIO_NOT_MODULE: "DIO module not found",
    AXT_RT_DIO_INVALID_MODULE_NO: "Invalid DIO module number",
    AXT_RT_DIO_INVALID_OFFSET_NO: "Invalid DIO offset number",
    AXT_RT_DIO_INVALID_VALUE: "Invalid value setting",
    AXT_RT_MOTION_OPEN_ERROR: "Motion library open failed",
    AXT_RT_MOTION_NOT_MODULE: "No motion module installed in system",
    AXT_RT_MOTION_INVALID_AXIS_NO: "Axis does not exist",
    AXT_RT_MOTION_INVALID_METHOD: "Invalid axis drive configuration",
    AXT_RT_MOTION_INVALID_VELOCITY: "Motion velocity set to 0",
    AXT_RT_MOTION_ERROR_IN_MOTION: "Cannot execute while axis is in motion",
    AXT_RT_MOTION_HOME_SEARCHING: "Cannot use while home search is in progress",
    AXT_RT_PROTECTED_DURING_SERVOON: "Cannot use while servo is ON",
}


def get_error_message(error_code: int) -> str:
    """Get error message for given error code."""
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")


def is_success(error_code: int) -> bool:
    """Check if error code indicates success."""
    return error_code == AXT_RT_SUCCESS


def is_motion_error(error_code: int) -> bool:
    """Check if error code is motion related."""
    return 4000 <= error_code < 5000


def is_dio_error(error_code: int) -> bool:
    """Check if error code is DIO related."""
    return 3000 <= error_code < 3200
