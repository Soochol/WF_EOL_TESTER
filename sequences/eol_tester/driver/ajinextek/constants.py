"""
Constants for AJINEXTEK AXL Library.

These constants are defined based on the AXL library header files.
"""

import platform
import sys
from pathlib import Path

# Library paths - handle both development and PyInstaller environments
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running in PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
    AXL_LIBRARY_DIR = BASE_DIR / "driver" / "AXL"
    IS_PYINSTALLER = True
else:
    # Running in development - look for DLL in standalone package
    BASE_DIR = Path(__file__).parent
    AXL_LIBRARY_DIR = BASE_DIR / "lib"
    IS_PYINSTALLER = False


def get_dll_path() -> Path:
    """Get appropriate DLL path based on system architecture."""
    is_64bit = platform.machine().endswith("64") or platform.architecture()[0] == "64bit"

    if IS_PYINSTALLER:
        dll_path = AXL_LIBRARY_DIR / "AXL.dll"
        return dll_path

    # Development/standalone: check architecture subdirectories
    if is_64bit:
        dll_path = AXL_LIBRARY_DIR / "64Bit" / "AXL.dll"
        if not dll_path.exists():
            dll_path = AXL_LIBRARY_DIR / "AXL.dll"  # Fallback to root
    else:
        dll_path = AXL_LIBRARY_DIR / "32Bit" / "AXL.dll"
        if not dll_path.exists():
            dll_path = AXL_LIBRARY_DIR / "AXL.dll"  # Fallback to root

    return dll_path


DLL_PATH = get_dll_path()

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

# Home search results
HOME_SUCCESS = 0x01
HOME_SEARCHING = 0x02
HOME_ERR_GNT_RANGE = 0x10
HOME_ERR_USER_BREAK = 0x11
HOME_ERR_VELOCITY = 0x12
HOME_ERR_AMP_FAULT = 0x13
HOME_ERR_NEG_LIMIT = 0x14
HOME_ERR_POS_LIMIT = 0x15
HOME_ERR_NOT_DETECT = 0x16
HOME_ERR_UNKNOWN = 0xFF

# Max values
MAX_AXIS_COUNT = 128
MAX_MODULE_COUNT = 16
MAX_BOARD_COUNT = 8

# Digital I/O
LEVEL_LOW = 0
LEVEL_HIGH = 1
