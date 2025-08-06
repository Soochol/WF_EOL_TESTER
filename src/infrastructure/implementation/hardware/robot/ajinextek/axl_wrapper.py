"""
Python wrapper for AJINEXTEK AXL Library

This module provides ctypes bindings for the AXL motion control library.
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

import ctypes
import os
import platform
from ctypes import POINTER, c_char_p, c_double, c_long, c_ulong
from typing import Any, Optional

from domain.exceptions.robot_exceptions import (
    AXLError,
    AXLMotionError,
)
from infrastructure.implementation.hardware.robot.ajinextek.constants import (
    DLL_PATH,
)
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)

# Platform-specific WinDLL handling
if platform.system() == "Windows":
    try:
        from ctypes import (  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
            WinDLL,  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
        )
    except ImportError:
        # Fallback for Windows environments without WinDLL
        class WinDLL:  # type: ignore[no-redef]
            def __init__(self, path: str) -> None:
                ...

else:
    # Mock WinDLL class for non-Windows systems
    class WinDLL:  # type: ignore[no-redef]
        def __init__(self, path: str) -> None:
            ...


class AXLWrapper:
    """Wrapper class for AXL library functions"""

    def __init__(self) -> None:
        self.dll: Optional[Any] = None
        self.is_windows = platform.system() == "Windows"

        # Initialize instance variables
        self.board_count: int = 0
        self.version: str = "Unknown"

        if not self.is_windows:
            raise AXLError(
                "AXL Motion library is only supported on Windows platform. "
                "For development/testing on other platforms, use MockRobot instead."
            )
            
        self._load_library()
        self._setup_functions()
        # Initialize board count and version after setup
        self.board_count = self._get_board_count_internal()
        self.version = self._get_lib_version_internal()

    def _load_library(self) -> None:
        """Load the AXL DLL"""
        if not os.path.exists(DLL_PATH):
            raise FileNotFoundError(f"AXL DLL not found at {DLL_PATH}")

        try:
            # Load DLL with Windows calling convention
            self.dll = WinDLL(str(DLL_PATH))
        except OSError as e:
            raise RuntimeError(f"Failed to load AXL DLL: {e}") from e

    def _setup_functions(self) -> None:
        """Setup function signatures for ctypes"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        # Track missing functions for logging
        missing_functions = []

        # === Library Functions ===
        # AxlOpen
        try:
            self.dll.AxlOpen.argtypes = [c_long]
            self.dll.AxlOpen.restype = c_long
        except AttributeError:
            missing_functions.append("AxlOpen")

        # AxlClose
        try:
            self.dll.AxlClose.argtypes = []
            self.dll.AxlClose.restype = c_long
        except AttributeError:
            missing_functions.append("AxlClose")

        # AxlIsOpened
        try:
            self.dll.AxlIsOpened.argtypes = []
            self.dll.AxlIsOpened.restype = c_long
        except AttributeError:
            missing_functions.append("AxlIsOpened")

        # AxlGetBoardCount
        try:
            self.dll.AxlGetBoardCount.argtypes = [POINTER(c_long)]
            self.dll.AxlGetBoardCount.restype = c_long
        except AttributeError:
            missing_functions.append("AxlGetBoardCount")

        # AxlGetLibVersion
        try:
            self.dll.AxlGetLibVersion.argtypes = [c_char_p]
            self.dll.AxlGetLibVersion.restype = c_long
        except AttributeError:
            missing_functions.append("AxlGetLibVersion")

        # === Motion Functions ===
        # AxmInfoGetAxisCount
        try:
            self.dll.AxmInfoGetAxisCount.argtypes = [POINTER(c_long)]
            self.dll.AxmInfoGetAxisCount.restype = c_long
        except AttributeError:
            missing_functions.append("AxmInfoGetAxisCount")

        # AxmMotSetPulseOutMethod
        try:
            self.dll.AxmMotSetPulseOutMethod.argtypes = [
                c_long,
                c_long,
            ]
            self.dll.AxmMotSetPulseOutMethod.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetPulseOutMethod")

        # AxmMotSetMoveUnitPerPulse
        try:
            self.dll.AxmMotSetMoveUnitPerPulse.argtypes = [
                c_long,
                c_double,
                c_long,
            ]
            self.dll.AxmMotSetMoveUnitPerPulse.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetMoveUnitPerPulse")

        # AxmSignalServoOn
        try:
            self.dll.AxmSignalServoOn.argtypes = [
                c_long,
                c_long,
            ]
            self.dll.AxmSignalServoOn.restype = c_long
        except AttributeError:
            missing_functions.append("AxmSignalServoOn")

        # AxmSignalIsServoOn
        try:
            self.dll.AxmSignalIsServoOn.argtypes = [
                c_long,
                POINTER(c_long),
            ]
            self.dll.AxmSignalIsServoOn.restype = c_long
        except AttributeError:
            missing_functions.append("AxmSignalIsServoOn")

        # AxmStatusSetCmdPos
        try:
            self.dll.AxmStatusSetCmdPos.argtypes = [
                c_long,
                c_double,
            ]
            self.dll.AxmStatusSetCmdPos.restype = c_long
        except AttributeError:
            missing_functions.append("AxmStatusSetCmdPos")

        # AxmStatusGetCmdPos
        try:
            self.dll.AxmStatusGetCmdPos.argtypes = [
                c_long,
                POINTER(c_double),
            ]
            self.dll.AxmStatusGetCmdPos.restype = c_long
        except AttributeError:
            missing_functions.append("AxmStatusGetCmdPos")

        # AxmStatusSetActPos
        try:
            self.dll.AxmStatusSetActPos.argtypes = [
                c_long,
                c_double,
            ]
            self.dll.AxmStatusSetActPos.restype = c_long
        except AttributeError:
            missing_functions.append("AxmStatusSetActPos")

        # AxmStatusGetActPos
        try:
            self.dll.AxmStatusGetActPos.argtypes = [
                c_long,
                POINTER(c_double),
            ]
            self.dll.AxmStatusGetActPos.restype = c_long
        except AttributeError:
            missing_functions.append("AxmStatusGetActPos")

        # AxmMoveStartPos
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
            missing_functions.append("AxmMoveStartPos")

        # AxmMoveStop
        try:
            self.dll.AxmMoveStop.argtypes = [c_long, c_double]
            self.dll.AxmMoveStop.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveStop")

        # AxmMoveEStop - Emergency stop
        try:
            self.dll.AxmMoveEStop.argtypes = [c_long]
            self.dll.AxmMoveEStop.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveEStop")

        # AxmMoveSStop - Smooth stop with deceleration
        try:
            self.dll.AxmMoveSStop.argtypes = [c_long]
            self.dll.AxmMoveSStop.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveSStop")

        # AxmStatusReadInMotion
        try:
            self.dll.AxmStatusReadInMotion.argtypes = [
                c_long,
                POINTER(c_long),
            ]
            self.dll.AxmStatusReadInMotion.restype = c_long
        except AttributeError:
            missing_functions.append("AxmStatusReadInMotion")

        # AxmHomeSetMethod
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
            missing_functions.append("AxmHomeSetMethod")

        # AxmHomeSetVel
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
            missing_functions.append("AxmHomeSetVel")

        # AxmHomeSetStart
        try:
            self.dll.AxmHomeSetStart.argtypes = [c_long]
            self.dll.AxmHomeSetStart.restype = c_long
        except AttributeError:
            missing_functions.append("AxmHomeSetStart")

        # AxmHomeGetResult
        try:
            self.dll.AxmHomeGetResult.argtypes = [c_long, POINTER(c_ulong)]
            self.dll.AxmHomeGetResult.restype = c_long
        except AttributeError:
            missing_functions.append("AxmHomeGetResult")

        # AxmHomeGetRate
        try:
            self.dll.AxmHomeGetRate.argtypes = [c_long, POINTER(c_ulong), POINTER(c_ulong)]
            self.dll.AxmHomeGetRate.restype = c_long
        except AttributeError:
            missing_functions.append("AxmHomeGetRate")

        # === Additional Status and Safety Functions ===
        # AxmSignalReadServoAlarm
        try:
            self.dll.AxmSignalReadServoAlarm.argtypes = [
                c_long,
                POINTER(c_long),
            ]
            self.dll.AxmSignalReadServoAlarm.restype = c_long
        except AttributeError:
            missing_functions.append("AxmSignalReadServoAlarm")

        # AxmSignalReadLimit
        try:
            self.dll.AxmSignalReadLimit.argtypes = [
                c_long,
                POINTER(c_long),
                POINTER(c_long),
            ]
            self.dll.AxmSignalReadLimit.restype = c_long
        except AttributeError:
            missing_functions.append("AxmSignalReadLimit")

        # AxmSignalSetLimit
        try:
            self.dll.AxmSignalSetLimit.argtypes = [
                c_long,
                c_long,
                c_long,
                c_long,
            ]
            self.dll.AxmSignalSetLimit.restype = c_long
        except AttributeError:
            missing_functions.append("AxmSignalSetLimit")

        # AxmMotSetAbsRelMode
        try:
            self.dll.AxmMotSetAbsRelMode.argtypes = [
                c_long,
                c_long,
            ]
            self.dll.AxmMotSetAbsRelMode.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetAbsRelMode")

        # AxmMotGetAbsRelMode
        try:
            self.dll.AxmMotGetAbsRelMode.argtypes = [
                c_long,
                POINTER(c_long),
            ]
            self.dll.AxmMotGetAbsRelMode.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotGetAbsRelMode")

        # === Velocity Motion Functions ===
        # AxmMoveStartVel
        try:
            self.dll.AxmMoveStartVel.argtypes = [
                c_long,
                c_double,
                c_double,
                c_double,
            ]
            self.dll.AxmMoveStartVel.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveStartVel")

        # AxmMoveSignalSearch
        try:
            self.dll.AxmMoveSignalSearch.argtypes = [
                c_long,
                c_double,
                c_double,
                c_double,
                c_double,
            ]
            self.dll.AxmMoveSignalSearch.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveSignalSearch")

        # === Multi-axis Functions ===
        # AxmMoveMultiStart
        try:
            self.dll.AxmMoveMultiStart.argtypes = [
                POINTER(c_long),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                c_long,
            ]
            self.dll.AxmMoveMultiStart.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveMultiStart")

        # AxmMoveMultiStop
        try:
            self.dll.AxmMoveMultiStop.argtypes = [
                POINTER(c_long),
                POINTER(c_double),
                c_long,
            ]
            self.dll.AxmMoveMultiStop.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMoveMultiStop")

        # === Parameter Loading/Saving Functions ===
        # AxmMotLoadParaAll
        try:
            self.dll.AxmMotLoadParaAll.argtypes = [c_char_p]
            self.dll.AxmMotLoadParaAll.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotLoadParaAll")

        # AxmMotSaveParaAll
        try:
            self.dll.AxmMotSaveParaAll.argtypes = [c_char_p]
            self.dll.AxmMotSaveParaAll.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSaveParaAll")

        # AxmMotLoadPara
        try:
            self.dll.AxmMotLoadPara.argtypes = [c_long, c_char_p]
            self.dll.AxmMotLoadPara.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotLoadPara")

        # AxmMotSavePara
        try:
            self.dll.AxmMotSavePara.argtypes = [c_long, c_char_p]
            self.dll.AxmMotSavePara.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSavePara")

        # === Motion Parameter Get/Set Functions ===
        # AxmMotSetMaxVel
        try:
            self.dll.AxmMotSetMaxVel.argtypes = [c_long, c_double]
            self.dll.AxmMotSetMaxVel.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetMaxVel")

        # AxmMotGetMaxVel
        try:
            self.dll.AxmMotGetMaxVel.argtypes = [c_long, POINTER(c_double)]
            self.dll.AxmMotGetMaxVel.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotGetMaxVel")

        # AxmMotSetMinVel
        try:
            self.dll.AxmMotSetMinVel.argtypes = [c_long, c_double]
            self.dll.AxmMotSetMinVel.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetMinVel")

        # AxmMotGetMinVel
        try:
            self.dll.AxmMotGetMinVel.argtypes = [c_long, POINTER(c_double)]
            self.dll.AxmMotGetMinVel.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotGetMinVel")

        # AxmMotSetAccelUnit
        try:
            self.dll.AxmMotSetAccelUnit.argtypes = [c_long, c_long]
            self.dll.AxmMotSetAccelUnit.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetAccelUnit")

        # AxmMotGetAccelUnit
        try:
            self.dll.AxmMotGetAccelUnit.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmMotGetAccelUnit.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotGetAccelUnit")

        # AxmMotSetProfileMode
        try:
            self.dll.AxmMotSetProfileMode.argtypes = [c_long, c_long]
            self.dll.AxmMotSetProfileMode.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotSetProfileMode")

        # AxmMotGetProfileMode
        try:
            self.dll.AxmMotGetProfileMode.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxmMotGetProfileMode.restype = c_long
        except AttributeError:
            missing_functions.append("AxmMotGetProfileMode")

        # Log all missing functions at once
        if missing_functions:
            print(f"Warning: {len(missing_functions)} AXL functions not found in DLL:")
            for func in missing_functions:
                print(f"  - {func}")
            print("Hardware service will create successfully but some functions may not work.")

    # === Library Functions ===
    def open(self, irq_no: int = 7) -> int:
        """Initialize and open the AXL library"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlOpen(irq_no)  # type: ignore[no-any-return]

    def close(self) -> int:
        """Close the AXL library"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlClose()  # type: ignore[no-any-return]

    def is_opened(self) -> bool:
        """Check if library is opened"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxlIsOpened() == 1  # type: ignore[no-any-return]

    def _get_board_count_internal(self) -> int:
        """Internal method to get the number of boards"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxlGetBoardCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxlGetBoardCount",
            )
        return count.value

    def get_board_count(self) -> int:
        """Get the number of boards (cached)"""
        return self.board_count

    def _get_lib_version_internal(self) -> str:
        """Internal method to get library version"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        version = ctypes.create_string_buffer(32)
        result = self.dll.AxlGetLibVersion(version)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxlGetLibVersion",
            )
        return version.value.decode("ascii")

    def get_lib_version(self) -> str:
        """Get library version (cached)"""
        return self.version

    # === Motion Functions ===
    def get_axis_count(self) -> int:
        """Get total number of axes"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxmInfoGetAxisCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmInfoGetAxisCount",
            )
        return count.value

    def set_pulse_out_method(self, axis_no: int, method: int) -> int:
        """Set pulse output method"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetPulseOutMethod(axis_no, method)  # type: ignore[no-any-return]

    def set_move_unit_per_pulse(self, axis_no: int, unit: float, pulse: int) -> int:
        """Set movement unit per pulse"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMoveUnitPerPulse(  # type: ignore[no-any-return]
            axis_no, unit, pulse
        )

    def servo_on(self, axis_no: int, on_off: int = 1) -> int:
        """Turn servo on/off"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoOn(axis_no, on_off)  # type: ignore[no-any-return]

    def servo_off(self, axis_no: int) -> int:
        """Turn servo off (convenience method)"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoOn(axis_no, 0)  # type: ignore[no-any-return]

    def is_servo_on(self, axis_no: int) -> bool:
        """Check if servo is on"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = c_long()
        result = self.dll.AxmSignalIsServoOn(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmSignalIsServoOn",
            )
        return status.value == 1

    def set_cmd_pos(self, axis_no: int, position: float) -> int:
        """Set command position"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmStatusSetCmdPos(axis_no, position)  # type: ignore[no-any-return]

    def get_cmd_pos(self, axis_no: int) -> float:
        """Get command position"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        position = c_double()
        result = self.dll.AxmStatusGetCmdPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmStatusGetCmdPos",
            )
        return position.value

    def set_act_pos(self, axis_no: int, position: float) -> int:
        """Set actual position"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmStatusSetActPos(axis_no, position)  # type: ignore[no-any-return]

    def get_act_pos(self, axis_no: int) -> float:
        """Get actual position"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        position = c_double()
        result = self.dll.AxmStatusGetActPos(axis_no, ctypes.byref(position))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmStatusGetActPos",
            )
        return position.value

    def move_start_pos(
        self,
        axis_no: int,
        position: float,
        velocity: float,
        accel: float,
        decel: float,
    ) -> int:
        """Start position move"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMoveStartPos(  # type: ignore[no-any-return]
            axis_no, position, velocity, accel, decel
        )

    def move_stop(self, axis_no: int, decel: float) -> int:
        """Stop motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMoveStop(axis_no, decel)  # type: ignore[no-any-return]

    def move_emergency_stop(self, axis_no: int) -> int:
        """Emergency stop - immediate stop without deceleration"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveEStop(axis_no)  # type: ignore[no-any-return]

    def move_smooth_stop(self, axis_no: int) -> int:
        """Smooth stop - stop with deceleration using axis default deceleration parameters"""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveSStop(axis_no)  # type: ignore[no-any-return]

    def read_in_motion(self, axis_no: int) -> bool:
        """Check if axis is in motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = c_long()
        result = self.dll.AxmStatusReadInMotion(axis_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmStatusReadInMotion",
            )
        return status.value == 1

    def home_set_method(
        self,
        axis_no: int,
        home_dir: int,
        signal_level: int,
        mode: int,
        offset: float,
    ) -> int:
        """Set homing method"""
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
        """Set homing velocities"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmHomeSetVel(  # type: ignore[no-any-return]
            axis_no, vel_first, vel_second, accel, decel
        )

    def home_set_start(self, axis_no: int) -> int:
        """Start homing"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmHomeSetStart(axis_no)  # type: ignore[no-any-return]

    # === Additional Status and Safety Functions ===
    def read_servo_alarm(self, axis_no: int) -> bool:
        """Read servo alarm status"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        alarm_status = c_long()
        result = self.dll.AxmSignalReadServoAlarm(axis_no, ctypes.byref(alarm_status))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmSignalReadServoAlarm",
            )
        return alarm_status.value == 1

    def read_limit_status(self, axis_no: int) -> tuple[bool, bool]:
        """Read positive and negative limit sensor status"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        pos_limit = c_long()
        neg_limit = c_long()
        result = self.dll.AxmSignalReadLimit(
            axis_no, ctypes.byref(pos_limit), ctypes.byref(neg_limit)
        )
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmSignalReadLimit",
            )
        return (pos_limit.value == 1, neg_limit.value == 1)

    def set_limit_config(self, axis_no: int, pos_level: int, neg_level: int, stop_mode: int) -> int:
        """Set limit sensor configuration"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalSetLimit(axis_no, pos_level, neg_level, stop_mode)  # type: ignore[no-any-return]

    def set_abs_rel_mode(self, axis_no: int, mode: int) -> int:
        """Set absolute/relative coordinate mode"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetAbsRelMode(axis_no, mode)  # type: ignore[no-any-return]

    def get_abs_rel_mode(self, axis_no: int) -> int:
        """Get current coordinate mode"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        mode = c_long()
        result = self.dll.AxmMotGetAbsRelMode(axis_no, ctypes.byref(mode))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetAbsRelMode",
            )
        return mode.value

    # === Velocity Motion Functions ===
    def move_start_vel(self, axis_no: int, velocity: float, accel: float, decel: float) -> int:
        """Start velocity (jog) motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        
        # Check if function is available
        if not hasattr(self.dll, 'AxmMoveStartVel'):
            print(f"Warning: AxmMoveStartVel function not available, returning success")
            return 0  # Return success code
            
        return self.dll.AxmMoveStartVel(axis_no, velocity, accel, decel)  # type: ignore[no-any-return]

    def move_signal_search(
        self,
        axis_no: int,
        velocity: float,
        accel: float,
        decel: float,
        search_distance: float,
    ) -> int:
        """Start signal search motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMoveSignalSearch(  # type: ignore[no-any-return]
            axis_no, velocity, accel, decel, search_distance
        )

    # === Multi-axis Functions ===
    def move_multi_start(
        self,
        axis_list: list[int],
        positions: list[float],
        velocities: list[float],
        accels: list[float],
        decels: list[float],
    ) -> int:
        """Start multi-axis synchronized motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        axis_count = len(axis_list)
        if not all(len(lst) == axis_count for lst in [positions, velocities, accels, decels]):
            raise ValueError("All parameter lists must have the same length")

        # Convert lists to ctypes arrays
        axis_array = (c_long * axis_count)(*axis_list)
        pos_array = (c_double * axis_count)(*positions)
        vel_array = (c_double * axis_count)(*velocities)
        accel_array = (c_double * axis_count)(*accels)
        decel_array = (c_double * axis_count)(*decels)

        return self.dll.AxmMoveMultiStart(  # type: ignore[no-any-return]
            axis_array, pos_array, vel_array, accel_array, decel_array, axis_count
        )

    def move_multi_stop(self, axis_list: list[int], decels: list[float]) -> int:
        """Stop multi-axis motion"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        axis_count = len(axis_list)
        if len(decels) != axis_count:
            raise ValueError("Deceleration list must match axis list length")

        # Convert lists to ctypes arrays
        axis_array = (c_long * axis_count)(*axis_list)
        decel_array = (c_double * axis_count)(*decels)

        return self.dll.AxmMoveMultiStop(axis_array, decel_array, axis_count)  # type: ignore[no-any-return]

    # === Parameter Loading/Saving Functions ===
    def save_para_all(self, file_path: str) -> int:
        """Save all motion parameters to file"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotSaveParaAll(file_path_bytes)  # type: ignore[no-any-return]

    def load_para(self, axis_no: int, file_path: str) -> int:
        """Load motion parameters for specific axis from file"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotLoadPara(axis_no, file_path_bytes)  # type: ignore[no-any-return]

    def save_para(self, axis_no: int, file_path: str) -> int:
        """Save motion parameters for specific axis to file"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotSavePara(axis_no, file_path_bytes)  # type: ignore[no-any-return]

    # === Motion Parameter Get/Set Functions ===
    def set_max_vel(self, axis_no: int, max_vel: float) -> int:
        """Set maximum velocity for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMaxVel(axis_no, max_vel)  # type: ignore[no-any-return]

    def get_max_vel(self, axis_no: int) -> float:
        """Get maximum velocity for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        max_vel = c_double()
        result = self.dll.AxmMotGetMaxVel(axis_no, ctypes.byref(max_vel))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetMaxVel",
            )
        return max_vel.value

    def set_min_vel(self, axis_no: int, min_vel: float) -> int:
        """Set minimum velocity for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMinVel(axis_no, min_vel)  # type: ignore[no-any-return]

    def get_min_vel(self, axis_no: int) -> float:
        """Get minimum velocity for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        min_vel = c_double()
        result = self.dll.AxmMotGetMinVel(axis_no, ctypes.byref(min_vel))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetMinVel",
            )
        return min_vel.value

    def set_accel_unit(self, axis_no: int, accel_unit: int) -> int:
        """Set acceleration unit for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetAccelUnit(axis_no, accel_unit)  # type: ignore[no-any-return]

    def get_accel_unit(self, axis_no: int) -> int:
        """Get acceleration unit for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        accel_unit = c_long()
        result = self.dll.AxmMotGetAccelUnit(axis_no, ctypes.byref(accel_unit))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetAccelUnit",
            )
        return accel_unit.value

    def set_profile_mode(self, axis_no: int, profile_mode: int) -> int:
        """Set motion profile mode for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetProfileMode(axis_no, profile_mode)  # type: ignore[no-any-return]

    def get_profile_mode(self, axis_no: int) -> int:
        """Get motion profile mode for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        profile_mode = c_long()
        result = self.dll.AxmMotGetProfileMode(axis_no, ctypes.byref(profile_mode))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetProfileMode",
            )
        return profile_mode.value

    def home_get_result(self, axis_no: int) -> int:
        """Get homing result status for axis"""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        home_result = c_ulong()
        result = self.dll.AxmHomeGetResult(axis_no, ctypes.byref(home_result))
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmHomeGetResult",
            )
        return home_result.value

    def home_get_rate(self, axis_no: int) -> tuple[int, int]:
        """Get homing progress rate for axis

        Returns:
            tuple: (main_step_number, step_number) progress percentages
        """
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        home_main_step = c_ulong()
        home_step = c_ulong()
        result = self.dll.AxmHomeGetRate(
            axis_no, ctypes.byref(home_main_step), ctypes.byref(home_step)
        )
        if result != AXT_RT_SUCCESS:
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmHomeGetRate",
            )
        return (home_main_step.value, home_step.value)
