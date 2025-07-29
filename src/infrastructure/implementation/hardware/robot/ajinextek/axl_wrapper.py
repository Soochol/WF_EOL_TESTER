"""
Python wrapper for AJINEXTEK AXL Library

This module provides ctypes bindings for the AXL motion control library.
"""

import ctypes
from ctypes import POINTER, c_long, c_double, c_char_p
from typing import Optional, Any
import os
import platform

from infrastructure.implementation.hardware.robot.ajinextek.constants import DLL_PATH
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)

# 절대 import 사용 (권장)
from domain.exceptions.robot_exceptions import AXLError, AXLConnectionError, AXLMotionError


class AXLWrapper:
    """Wrapper class for AXL library functions"""

    def __init__(self):
        self.dll: Optional[Any] = None
        self.is_windows = platform.system() == "Windows"

        if self.is_windows:
            self._load_library()
            self._setup_functions()
        else:
            # Linux/개발환경에서는 경고 메시지만 출력
            print(
                "Warning: Running on non-Windows platform. " "DLL functions will not be available."
            )

    def _load_library(self):
        """Load the AXL DLL (Windows only)"""
        if not self.is_windows:
            return

        if not os.path.exists(DLL_PATH):
            raise FileNotFoundError(f"AXL DLL not found at {DLL_PATH}")

        try:
            # Load DLL with Windows calling convention
            WinDLL = getattr(ctypes, "WinDLL")
            self.dll = WinDLL(str(DLL_PATH))
        except OSError as e:
            raise RuntimeError(f"Failed to load AXL DLL: {e}")

    def _setup_functions(self):
        """Setup function signatures for ctypes (Windows only)"""
        if not self.is_windows or self.dll is None:
            return

        # === Library Functions ===
        # AxlOpen
        self.dll.AxlOpen.argtypes = [c_long]
        self.dll.AxlOpen.restype = c_long

        # AxlClose
        self.dll.AxlClose.argtypes = []
        self.dll.AxlClose.restype = c_long

        # AxlIsOpened
        self.dll.AxlIsOpened.argtypes = []
        self.dll.AxlIsOpened.restype = c_long

        # AxlGetBoardCount
        self.dll.AxlGetBoardCount.argtypes = [POINTER(c_long)]
        self.dll.AxlGetBoardCount.restype = c_long

        # AxlGetLibVersion
        self.dll.AxlGetLibVersion.argtypes = [c_char_p]
        self.dll.AxlGetLibVersion.restype = c_long

        # === Motion Functions ===
        # AxmInfoGetAxisCount
        self.dll.AxmInfoGetAxisCount.argtypes = [POINTER(c_long)]
        self.dll.AxmInfoGetAxisCount.restype = c_long

        # AxmMotSetPulseOutMethod
        self.dll.AxmMotSetPulseOutMethod.argtypes = [c_long, c_long]
        self.dll.AxmMotSetPulseOutMethod.restype = c_long

        # AxmMotSetMoveUnitPerPulse
        self.dll.AxmMotSetMoveUnitPerPulse.argtypes = [c_long, c_double, c_long]
        self.dll.AxmMotSetMoveUnitPerPulse.restype = c_long

        # AxmSignalServoOn
        self.dll.AxmSignalServoOn.argtypes = [c_long, c_long]
        self.dll.AxmSignalServoOn.restype = c_long

        # AxmSignalIsServoOn
        self.dll.AxmSignalIsServoOn.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxmSignalIsServoOn.restype = c_long

        # AxmStatusSetCmdPos
        self.dll.AxmStatusSetCmdPos.argtypes = [c_long, c_double]
        self.dll.AxmStatusSetCmdPos.restype = c_long

        # AxmStatusGetCmdPos
        self.dll.AxmStatusGetCmdPos.argtypes = [c_long, POINTER(c_double)]
        self.dll.AxmStatusGetCmdPos.restype = c_long

        # AxmStatusSetActPos
        self.dll.AxmStatusSetActPos.argtypes = [c_long, c_double]
        self.dll.AxmStatusSetActPos.restype = c_long

        # AxmStatusGetActPos
        self.dll.AxmStatusGetActPos.argtypes = [c_long, POINTER(c_double)]
        self.dll.AxmStatusGetActPos.restype = c_long

        # AxmMoveStartPos
        self.dll.AxmMoveStartPos.argtypes = [c_long, c_double, c_double, c_double, c_double]
        self.dll.AxmMoveStartPos.restype = c_long

        # AxmMoveStop
        self.dll.AxmMoveStop.argtypes = [c_long, c_double]
        self.dll.AxmMoveStop.restype = c_long

        # AxmStatusReadInMotion
        self.dll.AxmStatusReadInMotion.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxmStatusReadInMotion.restype = c_long

        # AxmHomeSetMethod
        self.dll.AxmHomeSetMethod.argtypes = [c_long, c_long, c_long, c_long, c_double]
        self.dll.AxmHomeSetMethod.restype = c_long

        # AxmHomeSetVel
        self.dll.AxmHomeSetVel.argtypes = [c_long, c_double, c_double, c_double, c_double]
        self.dll.AxmHomeSetVel.restype = c_long

        # AxmHomeSetStart
        self.dll.AxmHomeSetStart.argtypes = [c_long]
        self.dll.AxmHomeSetStart.restype = c_long

    # === Library Functions ===
    def open(self, irq_no: int = 7) -> int:
        """Initialize and open the AXL library"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxlOpen(irq_no)

    def close(self) -> int:
        """Close the AXL library"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxlClose()

    def is_opened(self) -> bool:
        """Check if library is opened"""
        if not self.is_windows or self.dll is None:
            return True  # Mock opened on non-Windows
        return self.dll.AxlIsOpened() == 1

    def get_board_count(self) -> int:
        """Get the number of boards"""
        if not self.is_windows or self.dll is None:
            return 1  # Mock 1 board on non-Windows

        count = c_long()
        result = self.dll.AxlGetBoardCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result, "AxlGetBoardCount")
        return count.value

    def get_lib_version(self) -> str:
        """Get library version"""
        if not self.is_windows or self.dll is None:
            return "Mock Version 1.0.0"  # Mock version on non-Windows

        version = ctypes.create_string_buffer(32)
        result = self.dll.AxlGetLibVersion(version)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result, "AxlGetLibVersion")
        return version.value.decode("ascii")

    # === Motion Functions ===
    def get_axis_count(self) -> int:
        """Get total number of axes"""
        if not self.is_windows or self.dll is None:
            return 6  # Mock 6 axes on non-Windows

        count = c_long()
        result = self.dll.AxmInfoGetAxisCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result, "AxmInfoGetAxisCount")
        return count.value

    def set_pulse_out_method(self, axis_no: int, method: int) -> int:
        """Set pulse output method"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMotSetPulseOutMethod(axis_no, method)

    def set_move_unit_per_pulse(self, axis_no: int, unit: float, pulse: int) -> int:
        """Set movement unit per pulse"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMotSetMoveUnitPerPulse(axis_no, unit, pulse)

    def servo_on(self, axis_no: int, on_off: int = 1) -> int:
        """Turn servo on/off"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmSignalServoOn(axis_no, on_off)

    def servo_off(self, axis_no: int) -> int:
        """Turn servo off (convenience method)"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmSignalServoOn(axis_no, 0)

    def is_servo_on(self, axis_no: int) -> bool:
        """Check if servo is on"""
        if not self.is_windows or self.dll is None:
            return True  # Mock servo on non-Windows

        status = c_long()
        result = self.dll.AxmSignalIsServoOn(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result, "AxmSignalIsServoOn")
        return status.value == 1

    def set_cmd_pos(self, axis_no: int, position: float) -> int:
        """Set command position"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmStatusSetCmdPos(axis_no, position)

    def get_cmd_pos(self, axis_no: int) -> float:
        """Get command position"""
        if not self.is_windows or self.dll is None:
            return 0.0  # Mock position on non-Windows

        position = c_double()
        result = self.dll.AxmStatusGetCmdPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result, "AxmStatusGetCmdPos")
        return position.value

    def set_act_pos(self, axis_no: int, position: float) -> int:
        """Set actual position"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmStatusSetActPos(axis_no, position)

    def get_act_pos(self, axis_no: int) -> float:
        """Get actual position"""
        if not self.is_windows or self.dll is None:
            return 0.0  # Mock position on non-Windows

        position = c_double()
        result = self.dll.AxmStatusGetActPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result, "AxmStatusGetActPos")
        return position.value

    def move_start_pos(
        self, axis_no: int, position: float, velocity: float, accel: float, decel: float
    ) -> int:
        """Start position move"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveStartPos(axis_no, position, velocity, accel, decel)

    def move_stop(self, axis_no: int, decel: float) -> int:
        """Stop motion"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveStop(axis_no, decel)

    def read_in_motion(self, axis_no: int) -> bool:
        """Check if axis is in motion"""
        if not self.is_windows or self.dll is None:
            return False  # Mock not moving on non-Windows

        status = c_long()
        result = self.dll.AxmStatusReadInMotion(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(get_error_message(result), result, "AxmStatusReadInMotion")
        return status.value == 1

    def home_set_method(
        self, axis_no: int, home_dir: int, signal_level: int, mode: int, offset: float
    ) -> int:
        """Set homing method"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmHomeSetMethod(axis_no, home_dir, signal_level, mode, offset)

    def home_set_vel(
        self, axis_no: int, vel_first: float, vel_second: float, accel: float, decel: float
    ) -> int:
        """Set homing velocities"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmHomeSetVel(axis_no, vel_first, vel_second, accel, decel)

    def home_set_start(self, axis_no: int) -> int:
        """Start homing"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmHomeSetStart(axis_no)
