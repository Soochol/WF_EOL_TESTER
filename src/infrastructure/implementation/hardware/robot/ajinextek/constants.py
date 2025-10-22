"""
Constants for AJINEXTEK AXL Library.

These constants are defined based on the AXL library header files.
"""

# Standard library imports
import sys
from pathlib import Path
import platform


# Library paths - handle both development and PyInstaller environments
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
    AXL_LIBRARY_DIR = BASE_DIR / "driver" / "AXL"
    IS_PYINSTALLER = True
else:
    # Running in development
    BASE_DIR = Path(__file__).parent.parent.parent.parent.parent.parent.parent
    AXL_LIBRARY_DIR = BASE_DIR / "src" / "driver" / "ajinextek" / "AXL(Library)" / "Library"
    IS_PYINSTALLER = False


# Select DLL based on system architecture with enhanced path verification
def get_dll_path() -> Path:
    """Get appropriate DLL path based on system architecture with verification."""
    # Determine architecture
    is_64bit = platform.machine().endswith("64") or platform.architecture()[0] == "64bit"

    # PyInstaller environment: DLL is directly in AXL_LIBRARY_DIR
    if IS_PYINSTALLER:
        dll_path = AXL_LIBRARY_DIR / "AXL.dll"
        if dll_path.exists():
            print(f"[OK] Using PyInstaller bundled AXL DLL: {dll_path}")
            return dll_path
        else:
            print(f"[ERROR] PyInstaller bundled AXL DLL not found at: {dll_path}")
            print(f"  Library directory: {AXL_LIBRARY_DIR}")
            return dll_path

    # Development environment: DLL is in architecture-specific subdirectory
    # Select appropriate DLL path
    if is_64bit:
        dll_path = AXL_LIBRARY_DIR / "64Bit" / "AXL.dll"
        fallback_path = AXL_LIBRARY_DIR / "32Bit" / "AXL.dll"
        arch_type = "64-bit"
        fallback_arch = "32-bit"
    else:
        dll_path = AXL_LIBRARY_DIR / "32Bit" / "AXL.dll"
        fallback_path = AXL_LIBRARY_DIR / "64Bit" / "AXL.dll"
        arch_type = "32-bit"
        fallback_arch = "64-bit"

    # Verify primary path
    if dll_path.exists():
        print(f"[OK] Using {arch_type} AXL DLL: {dll_path}")
        return dll_path

    # Try fallback path if primary doesn't exist
    if fallback_path.exists():
        print(
            f"[WARNING] {arch_type} DLL not found, using {fallback_arch} fallback: {fallback_path}"
        )
        print("  Warning: Architecture mismatch may cause loading issues")
        return fallback_path

    # Neither path exists - return primary for error reporting
    print(f"[ERROR] No AXL DLL found in either {arch_type} or {fallback_arch} directories")
    print(f"  Primary path: {dll_path}")
    print(f"  Fallback path: {fallback_path}")
    print(f"  Library directory: {AXL_LIBRARY_DIR}")

    return dll_path


# Get the appropriate DLL path
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


# DLL Path Verification Functions
def verify_dll_installation() -> dict:
    """Verify AXL DLL installation and provide diagnostic information."""
    info = {
        "library_dir_exists": AXL_LIBRARY_DIR.exists(),
        "dll_path": str(DLL_PATH),
        "dll_exists": DLL_PATH.exists(),
        "architecture": platform.machine(),
        "python_arch": platform.architecture()[0],
        "available_dlls": [],
        "missing_components": [],
    }

    if AXL_LIBRARY_DIR.exists():
        # Check for available DLLs
        for bit_dir in ["32Bit", "64Bit"]:
            dll_file = AXL_LIBRARY_DIR / bit_dir / "AXL.dll"
            if dll_file.exists():
                info["available_dlls"].append(
                    {
                        "path": str(dll_file),
                        "architecture": bit_dir,
                        "size": dll_file.stat().st_size,
                    }
                )
            else:
                info["missing_components"].append(f"{bit_dir}/AXL.dll")

        # Check for other important files
        lib_files = ["AXL.lib", "EzBasicAxl.dll", "EzBasicAxl.lib"]
        for bit_dir in ["32Bit", "64Bit"]:
            for lib_file in lib_files:
                lib_path = AXL_LIBRARY_DIR / bit_dir / lib_file
                if not lib_path.exists():
                    info["missing_components"].append(f"{bit_dir}/{lib_file}")
    else:
        info["missing_components"].append("Entire AJINEXTEK library directory")

    return info


def print_dll_diagnostic_info():
    """Print detailed diagnostic information about DLL installation."""
    info = verify_dll_installation()

    print("\n=== AJINEXTEK AXL DLL Diagnostic Information ===")
    print(f'System Architecture: {info["architecture"]}')
    print(f'Python Architecture: {info["python_arch"]}')
    print(f"Library Directory: {AXL_LIBRARY_DIR}")
    print(f'Library Directory Exists: {"✓" if info["library_dir_exists"] else "❌"}')
    print(f'Selected DLL Path: {info["dll_path"]}')
    print(f'Selected DLL Exists: {"✓" if info["dll_exists"] else "❌"}')

    if info["available_dlls"]:
        print("\nAvailable DLLs:")
        for dll in info["available_dlls"]:
            print(f'  ✓ {dll["architecture"]}: {dll["path"]} ({dll["size"]:,} bytes)')

    if info["missing_components"]:
        print("\nMissing Components:")
        for component in info["missing_components"]:
            print(f"  ❌ {component}")

    print("\n" + "=" * 50)
