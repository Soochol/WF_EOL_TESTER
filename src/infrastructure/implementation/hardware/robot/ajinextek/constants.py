"""
Constants for AJINEXTEK AXL Library

These constants are defined based on the AXL library header files.
"""

import platform
from pathlib import Path

# Library paths
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
AXL_LIBRARY_DIR = BASE_DIR / "driver" / "ajinextek" / "AXL(Library)" / "Library"

# Select DLL based on system architecture
if platform.machine().endswith("64"):
    DLL_PATH = AXL_LIBRARY_DIR / "64Bit" / "AXL.dll"
else:
    DLL_PATH = AXL_LIBRARY_DIR / "32Bit" / "AXL.dll"


# Servo control
SERVO_OFF = 0
SERVO_ON = 1

# Motion status
MOTION_STATUS_IDLE = 0
MOTION_STATUS_MOVING = 1
MOTION_STATUS_ERROR = -1

# Coordinate modes
POS_ABS = 0  # Absolute position
POS_REL = 1  # Relative position

# Stop modes
STOP_DECEL = 0  # Stop with deceleration
STOP_IMMEDIATE = 1  # Immediate stop

# Direction
DIR_CCW = 0  # Counter-clockwise
DIR_CW = 1  # Clockwise

# Motion profile modes
MOTION_PROFILE_TRAP = 0  # Trapezoidal
MOTION_PROFILE_SCURVE = 1  # S-curve

# Home search directions
HOME_DIR_CCW = 0  # CCW direction
HOME_DIR_CW = 1  # CW direction

# Home search modes
HOME_MODE_0 = 0x00  # Home sensor only
HOME_MODE_1 = 0x01  # Home sensor + Index
HOME_MODE_2 = 0x02  # Home sensor + Limit
HOME_MODE_3 = 0x03  # Home sensor + Limit + Index

# Limit sensor levels
LIMIT_LEVEL_LOW = 0  # Active low
LIMIT_LEVEL_HIGH = 1  # Active high

# Homing result status codes (AXT_MOTION_HOME_RESULT_DEF)
HOME_SUCCESS = 0x01  # Homing completed successfully
HOME_SEARCHING = 0x02  # Homing in progress
HOME_ERR_GNT_RANGE = 0x10  # Gantry offset out of range
HOME_ERR_USER_BREAK = 0x11  # User stopped homing
HOME_ERR_VELOCITY = 0x12  # Invalid velocity setting
HOME_ERR_AMP_FAULT = 0x13  # Servo amplifier alarm
HOME_ERR_NEG_LIMIT = 0x14  # Negative limit sensor detected
HOME_ERR_POS_LIMIT = 0x15  # Positive limit sensor detected
HOME_ERR_NOT_DETECT = 0x16  # Home sensor not detected
HOME_ERR_UNKNOWN = 0xFF  # Unknown axis number

# Limit sensor stop modes
LIMIT_STOP_DECEL = 0  # Stop with deceleration when limit triggered
LIMIT_STOP_IMMEDIATE = 1  # Immediate stop when limit triggered

# Pulse output methods
PULSE_OUT_METHOD_ONEPULSE = 0x00  # 1 pulse method
PULSE_OUT_METHOD_TWOPULSE = 0x01  # 2 pulse method (CW/CCW)
PULSE_OUT_METHOD_PHASE = 0x02  # Phase method (A/B phase)

# Max values
MAX_AXIS_COUNT = 128
MAX_MODULE_COUNT = 16
MAX_BOARD_COUNT = 8
