"""
Python wrapper for AJINEXTEK AXL Library.

This module provides ctypes bindings for the AXL motion control library.
Standalone version for EOL Tester package.
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

import ctypes
import platform
from ctypes import POINTER, c_char_p, c_double, c_long, c_ulong
from pathlib import Path
from typing import Any, List, Optional, Tuple

from .constants import DLL_PATH
from .error_codes import AXT_RT_SUCCESS, get_error_message
from .exceptions import AXLError, AXLMotionError, AXLPlatformError


# Platform-specific handling
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    from ctypes import wintypes

    try:
        from ctypes import WinDLL  # type: ignore[attr-defined]
    except ImportError:

        class WinDLL:  # type: ignore[no-redef]
            """Fallback WinDLL class."""

            def __init__(self, path: str) -> None:
                pass

    # Function type for callbacks
    try:
        from ctypes import WINFUNCTYPE  # type: ignore[attr-defined]

        FuncType = WINFUNCTYPE
    except ImportError:
        from ctypes import CFUNCTYPE

        FuncType = CFUNCTYPE
else:
    # Mock classes for non-Windows systems
    class wintypes:  # type: ignore[no-redef]
        """Mock wintypes for non-Windows."""

        DWORD = c_ulong
        HWND = c_long
        HANDLE = c_long

    class WinDLL:  # type: ignore[no-redef]
        """Mock WinDLL class for non-Windows systems."""

        def __init__(self, path: str) -> None:
            pass

    from ctypes import CFUNCTYPE

    FuncType = CFUNCTYPE


# Digital I/O Constants
LEVEL_LOW = 0
LEVEL_HIGH = 1
UP_EDGE = 1
DOWN_EDGE = 0
BOTH_EDGE = 2


class AXLWrapper:
    """Wrapper class for AXL library functions."""

    _instance: Optional["AXLWrapper"] = None
    _initialized: bool = False

    def __new__(cls) -> "AXLWrapper":
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize AXL wrapper instance."""
        if AXLWrapper._initialized:
            return

        self.dll: Optional[Any] = None
        self.is_windows = IS_WINDOWS
        self.board_count: int = 0
        self.version: str = "Unknown"
        self._connection_count: int = 0

        if not self.is_windows:
            import os

            if os.getenv("AXL_MOCK_MODE", "").lower() == "true":
                print("Warning: Running in AXL mock mode (no actual hardware control)")
                self.dll = None
                self.board_count = 1
                self.version = "Mock AXL v1.0.0"
                AXLWrapper._initialized = True
                return
            else:
                raise AXLPlatformError(
                    "AXL Motion library is only supported on Windows platform. "
                    "For development/testing on other platforms, use MockRobot instead."
                )

        self._load_library()
        self._setup_functions()
        AXLWrapper._initialized = True

    def _load_library(self) -> None:
        """Load the AXL DLL."""
        dll_path = Path(DLL_PATH)

        if not dll_path.exists():
            raise FileNotFoundError(f"AXL DLL not found at {DLL_PATH}")

        try:
            self.dll = WinDLL(str(DLL_PATH))
        except OSError as e:
            raise RuntimeError(f"Failed to load AXL DLL: {e}") from e

    def _setup_functions(self) -> None:
        """Set up function signatures for ctypes."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        # === Library Functions ===
        try:
            self.dll.AxlOpen.argtypes = [c_long]
            self.dll.AxlOpen.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxlClose.argtypes = []
            self.dll.AxlClose.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxlIsOpened.argtypes = []
            self.dll.AxlIsOpened.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxlGetBoardCount.argtypes = [POINTER(c_long)]
            self.dll.AxlGetBoardCount.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxlGetLibVersion.argtypes = [c_char_p]
            self.dll.AxlGetLibVersion.restype = c_long
        except AttributeError:
            pass

        # === Motion Functions ===
        try:
            self.dll.AxmInfoGetAxisCount.argtypes = [POINTER(c_long)]
            self.dll.AxmInfoGetAxisCount.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMotSetPulseOutMethod.argtypes = [c_long, c_long]
            self.dll.AxmMotSetPulseOutMethod.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMotSetMoveUnitPerPulse.argtypes = [c_long, c_double, c_long]
            self.dll.AxmMotSetMoveUnitPerPulse.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmSignalServoOn.argtypes = [c_long, c_long]
            self.dll.AxmSignalServoOn.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmSignalIsServoOn.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmSignalIsServoOn.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmStatusSetCmdPos.argtypes = [c_long, c_double]
            self.dll.AxmStatusSetCmdPos.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmStatusGetCmdPos.argtypes = [c_long, POINTER(c_double)]
            self.dll.AxmStatusGetCmdPos.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmStatusSetActPos.argtypes = [c_long, c_double]
            self.dll.AxmStatusSetActPos.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmStatusGetActPos.argtypes = [c_long, POINTER(c_double)]
            self.dll.AxmStatusGetActPos.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMoveStartPos.argtypes = [
                c_long,
                c_double,
                c_double,
                c_double,
                c_double,
            ]
            self.dll.AxmMoveStartPos.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMoveStop.argtypes = [c_long, c_double]
            self.dll.AxmMoveStop.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMoveEStop.argtypes = [c_long]
            self.dll.AxmMoveEStop.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMoveSStop.argtypes = [c_long]
            self.dll.AxmMoveSStop.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmStatusReadInMotion.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmStatusReadInMotion.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmHomeSetMethod.argtypes = [
                c_long,
                c_long,
                c_long,
                c_long,
                c_double,
            ]
            self.dll.AxmHomeSetMethod.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmHomeSetVel.argtypes = [
                c_long,
                c_double,
                c_double,
                c_double,
                c_double,
            ]
            self.dll.AxmHomeSetVel.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmHomeSetStart.argtypes = [c_long]
            self.dll.AxmHomeSetStart.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmHomeGetResult.argtypes = [c_long, POINTER(c_ulong)]
            self.dll.AxmHomeGetResult.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmHomeGetRate.argtypes = [c_long, POINTER(c_ulong), POINTER(c_ulong)]
            self.dll.AxmHomeGetRate.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmSignalReadServoAlarm.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmSignalReadServoAlarm.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmSignalServoAlarmReset.argtypes = [c_long, c_long]
            self.dll.AxmSignalServoAlarmReset.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmSignalReadLimit.argtypes = [c_long, POINTER(c_long), POINTER(c_long)]
            self.dll.AxmSignalReadLimit.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMotSetAbsRelMode.argtypes = [c_long, c_long]
            self.dll.AxmMotSetAbsRelMode.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMotGetAbsRelMode.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmMotGetAbsRelMode.restype = c_long
        except AttributeError:
            pass

        try:
            self.dll.AxmMoveVel.argtypes = [c_long, c_double, c_double, c_double]
            self.dll.AxmMoveVel.restype = c_long
        except AttributeError:
            pass

        # === Digital I/O Functions ===
        self._setup_dio_functions()

    def _setup_dio_functions(self) -> None:
        """Set up DIO function signatures."""
        if self.dll is None:
            return

        try:
            self.dll.AxdInfoIsDIOModule.argtypes = [POINTER(wintypes.DWORD)]
            self.dll.AxdInfoIsDIOModule.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdInfoGetModuleCount.argtypes = [POINTER(c_long)]
            self.dll.AxdInfoGetModuleCount.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdInfoGetModuleNo.argtypes = [c_long, c_long, POINTER(c_long)]
            self.dll.AxdInfoGetModuleNo.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdInfoGetInputCount.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxdInfoGetInputCount.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdInfoGetOutputCount.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxdInfoGetOutputCount.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdiReadInportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportBit.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdiReadInportByte.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportByte.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdiReadInportWord.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportWord.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdiReadInportDword.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportDword.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoWriteOutportBit.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportBit.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoWriteOutportByte.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportByte.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoWriteOutportWord.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportWord.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoWriteOutportDword.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportDword.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoReadOutportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportBit.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoReadOutportByte.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportByte.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoReadOutportWord.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportWord.restype = wintypes.DWORD
        except AttributeError:
            pass

        try:
            self.dll.AxdoReadOutportDword.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportDword.restype = wintypes.DWORD
        except AttributeError:
            pass

    # === Library Functions ===
    def open(self, irq_no: int = 7) -> int:  # noqa: A003
        """Initialize and open the AXL library."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlOpen(irq_no)  # type: ignore[no-any-return]

    def close(self) -> int:
        """Close the AXL library."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlClose()  # type: ignore[no-any-return]

    def is_opened(self) -> bool:
        """Check if library is opened."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlIsOpened() == 1  # type: ignore[no-any-return]

    def get_board_count(self) -> int:
        """Get the number of boards."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxlGetBoardCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return count.value

    def get_lib_version(self) -> str:
        """Get library version."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        version = ctypes.create_string_buffer(32)
        result = self.dll.AxlGetLibVersion(version)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return version.value.decode("ascii")

    # === Motion Functions ===
    def get_axis_count(self) -> int:
        """Get total number of axes."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxmInfoGetAxisCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return count.value

    def servo_on(self, axis_no: int, on_off: int = 1) -> int:
        """Turn servo on/off."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoOn(axis_no, on_off)  # type: ignore[no-any-return]

    def servo_off(self, axis_no: int) -> int:
        """Turn servo off."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoOn(axis_no, 0)  # type: ignore[no-any-return]

    def is_servo_on(self, axis_no: int) -> bool:
        """Check if servo is on."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = c_long()
        result = self.dll.AxmSignalIsServoOn(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return status.value == 1

    def set_cmd_pos(self, axis_no: int, position: float) -> int:
        """Set command position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmStatusSetCmdPos(axis_no, position)  # type: ignore[no-any-return]

    def get_cmd_pos(self, axis_no: int) -> float:
        """Get command position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        position = c_double()
        result = self.dll.AxmStatusGetCmdPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return position.value

    def set_act_pos(self, axis_no: int, position: float) -> int:
        """Set actual position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmStatusSetActPos(axis_no, position)  # type: ignore[no-any-return]

    def get_act_pos(self, axis_no: int) -> float:
        """Get actual position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        position = c_double()
        result = self.dll.AxmStatusGetActPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return position.value

    def move_start_pos(
        self,
        axis_no: int,
        position: float,
        velocity: float,
        accel: float,
        decel: float,
    ) -> int:
        """Start position move."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMoveStartPos(  # type: ignore[no-any-return]
            axis_no, position, velocity, accel, decel
        )

    def move_stop(self, axis_no: int, decel: float) -> int:
        """Stop motion."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMoveStop(axis_no, decel)  # type: ignore[no-any-return]

    def move_emergency_stop(self, axis_no: int) -> int:
        """Emergency stop."""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS
        return self.dll.AxmMoveEStop(axis_no)  # type: ignore[no-any-return]

    def move_smooth_stop(self, axis_no: int) -> int:
        """Smooth stop with deceleration."""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS
        return self.dll.AxmMoveSStop(axis_no)  # type: ignore[no-any-return]

    def read_in_motion(self, axis_no: int) -> bool:
        """Check if axis is in motion."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = c_long()
        result = self.dll.AxmStatusReadInMotion(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return status.value == 1

    def home_set_method(
        self,
        axis_no: int,
        home_dir: int,
        signal_level: int,
        mode: int,
        offset: float,
    ) -> int:
        """Set homing method."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmHomeSetMethod(  # type: ignore[no-any-return]
            axis_no, home_dir, signal_level, mode, offset
        )

    def home_set_vel(
        self,
        axis_no: int,
        vel_first: float,
        vel_second: float,
        accel: float,
        decel: float,
    ) -> int:
        """Set homing velocities."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmHomeSetVel(  # type: ignore[no-any-return]
            axis_no, vel_first, vel_second, accel, decel
        )

    def home_set_start(self, axis_no: int) -> int:
        """Start homing."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmHomeSetStart(axis_no)  # type: ignore[no-any-return]

    def home_get_result(self, axis_no: int) -> int:
        """Get homing result status."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        home_result = c_ulong()
        result = self.dll.AxmHomeGetResult(axis_no, ctypes.byref(home_result))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return home_result.value

    def home_get_rate(self, axis_no: int) -> Tuple[int, int]:
        """Get homing progress rate."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        home_main_step = c_ulong()
        home_step = c_ulong()
        result = self.dll.AxmHomeGetRate(
            axis_no, ctypes.byref(home_main_step), ctypes.byref(home_step)
        )
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return (home_main_step.value, home_step.value)

    def read_servo_alarm(self, axis_no: int) -> bool:
        """Read servo alarm status."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        alarm_status = c_long()
        result = self.dll.AxmSignalReadServoAlarm(axis_no, ctypes.byref(alarm_status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return alarm_status.value == 1

    def servo_alarm_reset(self, axis_no: int, on_off: int = 1) -> int:
        """Reset servo alarm status."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoAlarmReset(axis_no, on_off)  # type: ignore[no-any-return]

    def read_limit_status(self, axis_no: int) -> Tuple[bool, bool]:
        """Read positive and negative limit sensor status."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        pos_limit = c_long()
        neg_limit = c_long()
        result = self.dll.AxmSignalReadLimit(
            axis_no, ctypes.byref(pos_limit), ctypes.byref(neg_limit)
        )
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return (pos_limit.value == 1, neg_limit.value == 1)

    def set_abs_rel_mode(self, axis_no: int, mode: int) -> int:
        """Set absolute/relative coordinate mode."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetAbsRelMode(axis_no, mode)  # type: ignore[no-any-return]

    def get_abs_rel_mode(self, axis_no: int) -> int:
        """Get current coordinate mode."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        mode = c_long()
        result = self.dll.AxmMotGetAbsRelMode(axis_no, ctypes.byref(mode))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result)
        return mode.value

    def move_start_vel(self, axis_no: int, velocity: float, accel: float, decel: float) -> int:
        """Start velocity (jog) motion."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        if not hasattr(self.dll, "AxmMoveVel"):
            return 0

        return self.dll.AxmMoveVel(axis_no, velocity, accel, decel)  # type: ignore[no-any-return]

    # === Digital I/O Functions ===
    def is_dio_module(self) -> bool:
        """Check if DIO modules exist."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = wintypes.DWORD()
        result = self.dll.AxdInfoIsDIOModule(ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return bool(status.value)

    def get_dio_module_count(self) -> int:
        """Get total number of DIO modules."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetModuleCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return count.value

    def get_dio_module_no(self, board_no: int, module_pos: int) -> int:
        """Get module number from board number and position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        module_no = c_long()
        result = self.dll.AxdInfoGetModuleNo(board_no, module_pos, ctypes.byref(module_no))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return module_no.value

    def get_input_count(self, module_no: int) -> int:
        """Get input channel count for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetInputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return count.value

    def get_output_count(self, module_no: int) -> int:
        """Get output channel count for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetOutputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return count.value

    def read_input_bit(self, module_no: int, offset: int) -> bool:
        """Read single input bit."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportBit(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return bool(value.value)

    def read_input_byte(self, module_no: int, offset: int) -> int:
        """Read input byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportByte(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value & 0xFF

    def read_input_word(self, module_no: int, offset: int) -> int:
        """Read input word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportWord(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value & 0xFFFF

    def read_input_dword(self, module_no: int, offset: int) -> int:
        """Read input dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportDword(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value

    def write_output_bit(self, module_no: int, offset: int, value: bool) -> None:
        """Write single output bit."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        bit_value = 1 if value else 0
        result = self.dll.AxdoWriteOutportBit(module_no, offset, bit_value)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)

    def write_output_byte(self, module_no: int, offset: int, value: int) -> None:
        """Write output byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportByte(module_no, offset, value & 0xFF)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)

    def write_output_word(self, module_no: int, offset: int, value: int) -> None:
        """Write output word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportWord(module_no, offset, value & 0xFFFF)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)

    def write_output_dword(self, module_no: int, offset: int, value: int) -> None:
        """Write output dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportDword(module_no, offset, value)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)

    def read_output_bit(self, module_no: int, offset: int) -> bool:
        """Read single output bit state."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportBit(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return bool(value.value)

    def read_output_byte(self, module_no: int, offset: int) -> int:
        """Read output byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportByte(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value & 0xFF

    def read_output_word(self, module_no: int, offset: int) -> int:
        """Read output word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportWord(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value & 0xFFFF

    def read_output_dword(self, module_no: int, offset: int) -> int:
        """Read output dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportDword(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result)
        return value.value

    def batch_read_inputs(self, module_no: int, start_offset: int, count: int) -> List[bool]:
        """Optimized batch reading of multiple input bits."""
        if count <= 0:
            return []

        results = []
        for offset in range(start_offset, start_offset + count):
            try:
                bit_value = self.read_input_bit(module_no, offset)
                results.append(bit_value)
            except Exception:
                results.append(False)

        return results

    def batch_write_outputs(self, module_no: int, start_offset: int, values: List[bool]) -> None:
        """Batch writing of multiple output bits."""
        for idx, value in enumerate(values):
            try:
                self.write_output_bit(module_no, start_offset + idx, value)
            except Exception:
                pass

    def batch_read_outputs(self, module_no: int, start_offset: int, count: int) -> List[bool]:
        """Batch reading of multiple output bits."""
        if count <= 0:
            return []

        results = []
        for offset in range(start_offset, start_offset + count):
            try:
                bit_value = self.read_output_bit(module_no, offset)
                results.append(bit_value)
            except Exception:
                results.append(False)

        return results

    # === Connection Management ===
    @classmethod
    def get_instance(cls) -> "AXLWrapper":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self, irq_no: int = 7) -> None:
        """Connect to AXL library."""
        if self.is_opened():
            self._connection_count += 1
            return

        result = self.open(irq_no)
        if result == AXT_RT_SUCCESS:
            self._connection_count = 1
        else:
            error_msg = get_error_message(result)
            raise AXLError(f"Connection failed: {error_msg} (Code: {result})")

    def disconnect(self) -> None:
        """Disconnect from AXL library."""
        if self._connection_count <= 0:
            return

        self._connection_count -= 1

        if self._connection_count <= 0:
            if self.is_opened():
                self.close()
            self._connection_count = 0

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset singleton for testing."""
        if cls._instance:
            cls._instance._connection_count = 0
        cls._instance = None
        cls._initialized = False
