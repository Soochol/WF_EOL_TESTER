"""
Python wrapper for AJINEXTEK AXL Library.

This module provides ctypes bindings for the AXL motion control library.
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

# Standard library imports
import ctypes
from ctypes import c_char_p, c_double, c_long, c_ulong, POINTER, wintypes
from pathlib import Path
import platform
from typing import Any, List, Optional, Tuple

# Local application imports
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
        # Standard library imports
        from ctypes import (
            WinDLL,  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]; pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
        )
    except ImportError:
        # Fallback for Windows environments without WinDLL
        class WinDLL:  # type: ignore[no-redef]
            """Fallback WinDLL class for Windows environments without WinDLL."""

            def __init__(self, path: str) -> None:
                """Initialize WinDLL with path."""
                ...

else:
    # Mock WinDLL class for non-Windows systems
    class WinDLL:  # type: ignore[no-redef]
        """Mock WinDLL class for non-Windows systems."""

        def __init__(self, path: str) -> None:
            """Initialize mock WinDLL with path."""
            ...


# Digital I/O Constants
# DIO Return Codes (additional to motion codes)
AXT_RT_DIO_NOT_MODULE = 3051
AXT_RT_DIO_INVALID_MODULE_NO = 3101
AXT_RT_DIO_INVALID_OFFSET_NO = 3102
AXT_RT_DIO_INVALID_VALUE = 3105

# Input Level Constants
LEVEL_LOW = 0
LEVEL_HIGH = 1

# Interrupt Edge Constants
UP_EDGE = 1
DOWN_EDGE = 0
BOTH_EDGE = 2

# Interrupt Methods
INTERRUPT_METHOD_MESSAGE = 0
INTERRUPT_METHOD_CALLBACK = 1
INTERRUPT_METHOD_EVENT = 2

# Platform-specific function type handling for DIO
if platform.system() == "Windows":
    try:
        # Standard library imports
        from ctypes import WINFUNCTYPE  # type: ignore[attr-defined]

        FuncType = WINFUNCTYPE
    except ImportError:
        # Standard library imports
        from ctypes import CFUNCTYPE

        FuncType = CFUNCTYPE
else:
    # Standard library imports
    from ctypes import CFUNCTYPE

    FuncType = CFUNCTYPE


class AXLWrapper:
    """Wrapper class for AXL library functions."""

    _instance: Optional["AXLWrapper"] = None
    _initialized: bool = False

    def __new__(cls) -> "AXLWrapper":
        """싱글톤 패턴 구현 - 하나의 인스턴스만 생성."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize AXL wrapper instance."""
        # 중복 초기화 방지
        if AXLWrapper._initialized:
            return

        self.dll: Optional[Any] = None
        self.is_windows = platform.system() == "Windows"

        # Initialize instance variables
        self.board_count: int = 0
        self.version: str = "Unknown"

        # Connection management
        self._connection_count: int = 0

        if not self.is_windows:
            # For development/testing, we can create a mock wrapper that simulates the DLL loading
            # Standard library imports
            import os

            if os.getenv("AXL_MOCK_MODE", "").lower() == "true":
                print("Warning: Running in AXL mock mode (no actual hardware control)")
                self.dll = None  # Mock mode - no DLL
                self.board_count = 1
                self.version = "Mock AXL v1.0.0"
                AXLWrapper._initialized = True
                return  # Skip DLL loading and function setup
            else:
                raise AXLError(
                    "AXL Motion library is only supported on Windows platform. "
                    "For development/testing on other platforms, use MockRobot instead."
                )

        # On Windows platform, proceed with DLL loading
        self._load_library()
        self._setup_functions()
        AXLWrapper._initialized = True

    def _load_library(self) -> None:
        """Load the AXL DLL with enhanced diagnostics."""  # Enhanced DLL path verification
        dll_path_info = self._verify_dll_path()

        if not dll_path_info["exists"]:
            raise FileNotFoundError(
                f"AXL DLL not found at {DLL_PATH}\n" f"Path details: {dll_path_info}"
            )

        try:
            # Load DLL with Windows calling convention
            self.dll = WinDLL(str(DLL_PATH))

        except OSError as e:
            raise RuntimeError(f"Failed to load AXL DLL: {e}") from e

    def _setup_functions(self) -> None:
        """Set up function signatures for ctypes."""
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

        # === Digital I/O Functions ===
        # Board and Module Information Functions
        try:
            self.dll.AxdInfoIsDIOModule.argtypes = [POINTER(wintypes.DWORD)]
            self.dll.AxdInfoIsDIOModule.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoIsDIOModule")

        try:
            self.dll.AxdInfoGetModuleCount.argtypes = [POINTER(c_long)]
            self.dll.AxdInfoGetModuleCount.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetModuleCount")

        try:
            self.dll.AxdInfoGetModuleNo.argtypes = [c_long, c_long, POINTER(c_long)]
            self.dll.AxdInfoGetModuleNo.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetModuleNo")

        try:
            self.dll.AxdInfoGetInputCount.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxdInfoGetInputCount.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetInputCount")

        try:
            self.dll.AxdInfoGetOutputCount.argtypes = [c_long, POINTER(c_long)]
            self.dll.AxdInfoGetOutputCount.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetOutputCount")

        try:
            self.dll.AxdInfoGetModule.argtypes = [
                c_long,
                POINTER(c_long),
                POINTER(c_long),
                POINTER(wintypes.DWORD),
            ]
            self.dll.AxdInfoGetModule.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetModule")

        try:
            self.dll.AxdInfoGetModuleStatus.argtypes = [c_long]
            self.dll.AxdInfoGetModuleStatus.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdInfoGetModuleStatus")

        # Input Reading Functions
        try:
            self.dll.AxdiReadInportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiReadInportBit")

        try:
            self.dll.AxdiReadInportByte.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportByte.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiReadInportByte")

        try:
            self.dll.AxdiReadInportWord.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportWord.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiReadInportWord")

        try:
            self.dll.AxdiReadInportDword.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiReadInportDword.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiReadInportDword")

        # Output Writing Functions
        try:
            self.dll.AxdoWriteOutportBit.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoWriteOutportBit")

        try:
            self.dll.AxdoWriteOutportByte.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportByte.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoWriteOutportByte")

        try:
            self.dll.AxdoWriteOutportWord.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportWord.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoWriteOutportWord")

        try:
            self.dll.AxdoWriteOutportDword.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoWriteOutportDword.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoWriteOutportDword")

        # Output Reading Functions
        try:
            self.dll.AxdoReadOutportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoReadOutportBit")

        try:
            self.dll.AxdoReadOutportByte.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportByte.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoReadOutportByte")

        try:
            self.dll.AxdoReadOutportWord.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportWord.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoReadOutportWord")

        try:
            self.dll.AxdoReadOutportDword.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoReadOutportDword.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoReadOutportDword")

        # Level Configuration Functions
        try:
            self.dll.AxdiLevelSetInportBit.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdiLevelSetInportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiLevelSetInportBit")

        try:
            self.dll.AxdiLevelGetInportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiLevelGetInportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiLevelGetInportBit")

        try:
            self.dll.AxdoLevelSetOutportBit.argtypes = [c_long, c_long, wintypes.DWORD]
            self.dll.AxdoLevelSetOutportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoLevelSetOutportBit")

        try:
            self.dll.AxdoLevelGetOutportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdoLevelGetOutportBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdoLevelGetOutportBit")

        # Interrupt Functions
        try:
            self.dll.AxdiInterruptSetModule.argtypes = [
                c_long,
                wintypes.HWND,
                wintypes.DWORD,
                FuncType(None),
                POINTER(wintypes.HANDLE),
            ]
            self.dll.AxdiInterruptSetModule.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiInterruptSetModule")

        try:
            self.dll.AxdiInterruptSetModuleEnable.argtypes = [c_long, wintypes.DWORD]
            self.dll.AxdiInterruptSetModuleEnable.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiInterruptSetModuleEnable")

        try:
            self.dll.AxdiInterruptEdgeSetBit.argtypes = [
                c_long,
                c_long,
                wintypes.DWORD,
                wintypes.DWORD,
            ]
            self.dll.AxdiInterruptEdgeSetBit.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiInterruptEdgeSetBit")

        try:
            self.dll.AxdiInterruptRead.argtypes = [c_long, POINTER(wintypes.DWORD)]
            self.dll.AxdiInterruptRead.restype = wintypes.DWORD
        except AttributeError:
            missing_functions.append("AxdiInterruptRead")

        # Log all missing functions at once
        if missing_functions:
            from loguru import logger
            logger.warning(f"AXL Library: {len(missing_functions)} functions not found in DLL {DLL_PATH}")
            for func in missing_functions:
                logger.warning(f"  Missing function: {func}")
            logger.info("Hardware service will continue but some functions may have limited functionality")

    # === Library Functions ===
    def open(self, irq_no: int = 7) -> int:  # pylint: disable=redefined-builtin  # noqa: A003
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

    def _get_board_count_internal(self) -> int:
        """Get the number of boards internally."""
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
        """Get the number of boards (cached)."""
        return self.board_count

    def _get_lib_version_internal(self) -> str:
        """Get library version internally."""
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
        """Get library version (cached)."""
        return self.version

    # === Motion Functions ===
    def get_axis_count(self) -> int:
        """Get total number of axes."""
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
        """Set pulse output method."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetPulseOutMethod(axis_no, method)  # type: ignore[no-any-return]

    def set_move_unit_per_pulse(self, axis_no: int, unit: float, pulse: int) -> int:
        """Set movement unit per pulse."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMoveUnitPerPulse(  # type: ignore[no-any-return]
            axis_no, unit, pulse
        )

    def servo_on(self, axis_no: int, on_off: int = 1) -> int:
        """Turn servo on/off."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalServoOn(axis_no, on_off)  # type: ignore[no-any-return]

    def servo_off(self, axis_no: int) -> int:
        """Turn servo off (convenience method)."""
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
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmSignalIsServoOn",
            )
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
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmStatusGetCmdPos",
            )
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
        """Emergency stop - immediate stop without deceleration."""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveEStop(axis_no)  # type: ignore[no-any-return]

    def move_smooth_stop(self, axis_no: int) -> int:
        """Smooth stop - stop with deceleration using axis default deceleration parameters."""
        if not self.is_windows or self.dll is None:
            return AXT_RT_SUCCESS  # Mock success on non-Windows
        return self.dll.AxmMoveSStop(axis_no)  # type: ignore[no-any-return]

    def read_in_motion(self, axis_no: int) -> bool:
        """Check if axis is in motion."""
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

    # === Additional Status and Safety Functions ===
    def read_servo_alarm(self, axis_no: int) -> bool:
        """Read servo alarm status."""
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
        """Read positive and negative limit sensor status."""
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
        """Set limit sensor configuration."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmSignalSetLimit(axis_no, pos_level, neg_level, stop_mode)  # type: ignore[no-any-return]

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
            raise AXLMotionError(
                get_error_message(result),
                result,
                "AxmMotGetAbsRelMode",
            )
        return mode.value

    # === Velocity Motion Functions ===
    def move_start_vel(self, axis_no: int, velocity: float, accel: float, decel: float) -> int:
        """Start velocity (jog) motion."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        # Check if function is available
        if not hasattr(self.dll, "AxmMoveStartVel"):
            from loguru import logger
            logger.warning(f"AxmMoveStartVel function not available in AXL DLL, returning success code")
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
        """Start signal search motion."""
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
        """Start multi-axis synchronized motion."""
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
        """Stop multi-axis motion."""
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
    def load_para_all(self, file_path: str) -> int:
        """Load all motion parameters from file."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotLoadParaAll(file_path_bytes)  # type: ignore[no-any-return]

    def save_para_all(self, file_path: str) -> int:
        """Save all motion parameters to file."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotSaveParaAll(file_path_bytes)  # type: ignore[no-any-return]

    def load_para(self, axis_no: int, file_path: str) -> int:
        """Load motion parameters for specific axis from file."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotLoadPara(axis_no, file_path_bytes)  # type: ignore[no-any-return]

    def save_para(self, axis_no: int, file_path: str) -> int:
        """Save motion parameters for specific axis to file."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        file_path_bytes = file_path.encode("ascii")
        return self.dll.AxmMotSavePara(axis_no, file_path_bytes)  # type: ignore[no-any-return]

    # === Motion Parameter Get/Set Functions ===
    def set_max_vel(self, axis_no: int, max_vel: float) -> int:
        """Set maximum velocity for axis."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMaxVel(axis_no, max_vel)  # type: ignore[no-any-return]

    def get_max_vel(self, axis_no: int) -> float:
        """Get maximum velocity for axis."""
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
        """Set minimum velocity for axis."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetMinVel(axis_no, min_vel)  # type: ignore[no-any-return]

    def get_min_vel(self, axis_no: int) -> float:
        """Get minimum velocity for axis."""
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
        """Set acceleration unit for axis."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetAccelUnit(axis_no, accel_unit)  # type: ignore[no-any-return]

    def get_accel_unit(self, axis_no: int) -> int:
        """Get acceleration unit for axis."""
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
        """Set motion profile mode for axis."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")
        return self.dll.AxmMotSetProfileMode(axis_no, profile_mode)  # type: ignore[no-any-return]

    def get_profile_mode(self, axis_no: int) -> int:
        """Get motion profile mode for axis."""
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

    def _verify_dll_path(self) -> dict:
        """Verify DLL path and provide detailed information."""
        dll_path = Path(DLL_PATH)
        info = {
            "path": str(dll_path),
            "exists": dll_path.exists(),
            "is_file": dll_path.is_file() if dll_path.exists() else False,
            "size": dll_path.stat().st_size if dll_path.exists() else 0,
            "parent_exists": dll_path.parent.exists(),
        }

        if dll_path.exists():
            try:
                # Try to get file version info on Windows
                if platform.system() == "Windows":
                    # Third-party imports
                    import win32api

                    info["version"] = win32api.GetFileVersionInfo(
                        str(dll_path), "\\StringFileInfo\\040904B0\\FileVersion"
                    )
            except (ImportError, Exception):
                info["version"] = "Unable to determine"

        return info

    def home_get_result(self, axis_no: int) -> int:
        """Get homing result status for axis."""
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
        """Get homing progress rate for axis.

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

    # === Digital I/O Functions ===
    # Board and Module Information Functions
    def is_dio_module(self) -> bool:
        """Check if DIO modules exist."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = wintypes.DWORD()
        result = self.dll.AxdInfoIsDIOModule(ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoIsDIOModule",
            )
        return bool(status.value)

    def get_dio_module_count(self) -> int:
        """Get total number of DIO modules."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetModuleCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoGetModuleCount",
            )
        return count.value

    def get_dio_module_no(self, board_no: int, module_pos: int) -> int:
        """Get module number from board number and position."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        module_no = c_long()
        result = self.dll.AxdInfoGetModuleNo(board_no, module_pos, ctypes.byref(module_no))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoGetModuleNo",
            )
        return module_no.value

    def get_input_count(self, module_no: int) -> int:
        """Get input channel count for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetInputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoGetInputCount",
            )
        return count.value

    def get_output_count(self, module_no: int) -> int:
        """Get output channel count for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetOutputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoGetOutputCount",
            )
        return count.value

    def get_module_info(self, module_no: int) -> Tuple[int, int, int]:
        """Get module information (board_no, module_pos, module_id)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        board_no = c_long()
        module_pos = c_long()
        module_id = wintypes.DWORD()

        result = self.dll.AxdInfoGetModule(
            module_no, ctypes.byref(board_no), ctypes.byref(module_pos), ctypes.byref(module_id)
        )

        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdInfoGetModule",
            )

        return (board_no.value, module_pos.value, module_id.value)

    def get_dio_module_status(self, module_no: int) -> int:
        """Get module status."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdInfoGetModuleStatus(module_no)
        return result

    # Input Reading Functions
    def read_input_bit(self, module_no: int, offset: int) -> bool:
        """Read single input bit."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportBit(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiReadInportBit",
            )
        return bool(value.value)

    def read_input_byte(self, module_no: int, offset: int) -> int:
        """Read input byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportByte(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiReadInportByte",
            )
        return value.value & 0xFF

    def read_input_word(self, module_no: int, offset: int) -> int:
        """Read input word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportWord(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiReadInportWord",
            )
        return value.value & 0xFFFF

    def read_input_dword(self, module_no: int, offset: int) -> int:
        """Read input dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportDword(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiReadInportDword",
            )
        return value.value

    # Output Writing Functions
    def write_output_bit(self, module_no: int, offset: int, value: bool) -> None:
        """Write single output bit."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        bit_value = 1 if value else 0
        result = self.dll.AxdoWriteOutportBit(module_no, offset, bit_value)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoWriteOutportBit",
            )

    def write_output_byte(self, module_no: int, offset: int, value: int) -> None:
        """Write output byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportByte(module_no, offset, value & 0xFF)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoWriteOutportByte",
            )

    def write_output_word(self, module_no: int, offset: int, value: int) -> None:
        """Write output word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportWord(module_no, offset, value & 0xFFFF)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoWriteOutportWord",
            )

    def write_output_dword(self, module_no: int, offset: int, value: int) -> None:
        """Write output dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportDword(module_no, offset, value)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoWriteOutportDword",
            )

    def read_output_bit(self, module_no: int, offset: int) -> bool:
        """Read single output bit state."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportBit(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoReadOutportBit",
            )
        return bool(value.value)

    def read_output_byte(self, module_no: int, offset: int) -> int:
        """Read output byte (8 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportByte(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoReadOutportByte",
            )
        return value.value & 0xFF

    def read_output_word(self, module_no: int, offset: int) -> int:
        """Read output word (16 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportWord(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoReadOutportWord",
            )
        return value.value & 0xFFFF

    def read_output_dword(self, module_no: int, offset: int) -> int:
        """Read output dword (32 bits)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdoReadOutportDword(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoReadOutportDword",
            )
        return value.value

    # Level Configuration Functions
    def set_input_level(self, module_no: int, offset: int, level: int) -> None:
        """Set input signal level (HIGH/LOW active)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdiLevelSetInportBit(module_no, offset, level)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiLevelSetInportBit",
            )

    def get_input_level(self, module_no: int, offset: int) -> int:
        """Get input signal level configuration."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        level = wintypes.DWORD()
        result = self.dll.AxdiLevelGetInportBit(module_no, offset, ctypes.byref(level))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiLevelGetInportBit",
            )
        return level.value

    def set_output_level(self, module_no: int, offset: int, level: int) -> None:
        """Set output signal level (HIGH/LOW active)."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdoLevelSetOutportBit(module_no, offset, level)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoLevelSetOutportBit",
            )

    def get_output_level(self, module_no: int, offset: int) -> int:
        """Get output signal level configuration."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        level = wintypes.DWORD()
        result = self.dll.AxdoLevelGetOutportBit(module_no, offset, ctypes.byref(level))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdoLevelGetOutportBit",
            )
        return level.value

    # Interrupt Functions
    def setup_interrupt_callback(self, module_no: int, callback_func) -> None:
        """Set up interrupt with callback function."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        result = self.dll.AxdiInterruptSetModule(
            module_no,
            None,  # hWnd (not used for callback method)
            0,  # uMessage (not used for callback method)
            callback_func,  # Callback function
            None,  # pEvent (not used for callback method)
        )

        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiInterruptSetModule",
            )

    def enable_module_interrupt(self, module_no: int, enable: bool = True) -> None:
        """Enable/disable interrupts for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        enable_value = 1 if enable else 0
        result = self.dll.AxdiInterruptSetModuleEnable(module_no, enable_value)
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiInterruptSetModuleEnable",
            )

    def set_interrupt_edge(
        self, module_no: int, offset: int, edge_mode: str, value: int = 1
    ) -> None:
        """Set interrupt edge trigger mode for input bit."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        edge_mapping = {
            "rising": UP_EDGE,
            "falling": DOWN_EDGE,
            "both": BOTH_EDGE,
        }

        edge_value = edge_mapping.get(edge_mode, UP_EDGE)
        result = self.dll.AxdiInterruptEdgeSetBit(module_no, offset, edge_value, value)

        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiInterruptEdgeSetBit",
            )

    def read_interrupt_status(self, module_no: int) -> int:
        """Read interrupt status for module."""
        if self.dll is None:
            raise AXLError("AXL DLL not loaded")

        status = wintypes.DWORD()
        result = self.dll.AxdiInterruptRead(module_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise AXLError(
                get_error_message(result),
                result,
                "AxdiInterruptRead",
            )
        return status.value

    # Utility Functions
    def batch_read_inputs(self, module_no: int, start_offset: int, count: int) -> List[bool]:
        """Optimized batch reading of multiple input bits."""
        if count <= 0:
            return []

        results = []

        # Try to use word/dword reads for efficiency
        if count >= 32 and start_offset % 32 == 0:
            # Read full dwords
            dwords_needed = (count + 31) // 32
            for dword_idx in range(dwords_needed):
                try:
                    dword_value = self.read_input_dword(module_no, start_offset // 32 + dword_idx)
                    for bit_idx in range(32):
                        if len(results) < count:
                            bit_value = (dword_value >> bit_idx) & 1
                            results.append(bool(bit_value))
                except Exception:
                    # Fallback to individual bit reads
                    for bit_idx in range(32):
                        if len(results) < count:
                            try:
                                bit_value = self.read_input_bit(
                                    module_no, start_offset + len(results)
                                )
                                results.append(bit_value)
                            except Exception:
                                results.append(False)

        elif count >= 16 and start_offset % 16 == 0:
            # Read full words
            words_needed = (count + 15) // 16
            for word_idx in range(words_needed):
                try:
                    word_value = self.read_input_word(module_no, start_offset // 16 + word_idx)
                    for bit_idx in range(16):
                        if len(results) < count:
                            bit_value = (word_value >> bit_idx) & 1
                            results.append(bool(bit_value))
                except Exception:
                    # Fallback to individual bit reads
                    for bit_idx in range(16):
                        if len(results) < count:
                            try:
                                bit_value = self.read_input_bit(
                                    module_no, start_offset + len(results)
                                )
                                results.append(bit_value)
                            except Exception:
                                results.append(False)
        else:
            # Individual bit reads
            for offset in range(start_offset, start_offset + count):
                try:
                    bit_value = self.read_input_bit(module_no, offset)
                    results.append(bit_value)
                except Exception:
                    results.append(False)

        return results[:count]

    def batch_write_outputs(self, module_no: int, start_offset: int, values: List[bool]) -> None:
        """Optimized batch writing of multiple output bits."""
        if not values:
            return

        count = len(values)

        # Try to use word/dword writes for efficiency
        if count >= 32 and start_offset % 32 == 0:
            # Write full dwords
            dwords_needed = (count + 31) // 32
            for dword_idx in range(dwords_needed):
                dword_value = 0
                start_idx = dword_idx * 32
                end_idx = min(start_idx + 32, count)

                for bit_idx in range(end_idx - start_idx):
                    if values[start_idx + bit_idx]:
                        dword_value |= 1 << bit_idx

                try:
                    self.write_output_dword(module_no, start_offset // 32 + dword_idx, dword_value)
                except Exception:
                    # Fallback to individual bit writes
                    for bit_idx in range(end_idx - start_idx):
                        try:
                            self.write_output_bit(
                                module_no,
                                start_offset + start_idx + bit_idx,
                                values[start_idx + bit_idx],
                            )
                        except Exception:
                            pass  # Continue with other bits

        elif count >= 16 and start_offset % 16 == 0:
            # Write full words
            words_needed = (count + 15) // 16
            for word_idx in range(words_needed):
                word_value = 0
                start_idx = word_idx * 16
                end_idx = min(start_idx + 16, count)

                for bit_idx in range(end_idx - start_idx):
                    if values[start_idx + bit_idx]:
                        word_value |= 1 << bit_idx

                try:
                    self.write_output_word(module_no, start_offset // 16 + word_idx, word_value)
                except Exception:
                    # Fallback to individual bit writes
                    for bit_idx in range(end_idx - start_idx):
                        try:
                            self.write_output_bit(
                                module_no,
                                start_offset + start_idx + bit_idx,
                                values[start_idx + bit_idx],
                            )
                        except Exception:
                            pass  # Continue with other bits
        else:
            # Individual bit writes
            for idx, value in enumerate(values):
                try:
                    self.write_output_bit(module_no, start_offset + idx, value)
                except Exception:
                    pass  # Continue with other bits

    def batch_read_outputs(self, module_no: int, start_offset: int, count: int) -> List[bool]:
        """Optimized batch reading of multiple output bits."""
        if count <= 0:
            return []

        results = []

        # Try to use word/dword reads for efficiency
        if count >= 32 and start_offset % 32 == 0:
            # Read full dwords
            dwords_needed = (count + 31) // 32
            for dword_idx in range(dwords_needed):
                try:
                    dword_value = self.read_output_dword(module_no, start_offset // 32 + dword_idx)
                    for bit_idx in range(32):
                        if len(results) < count:
                            bit_value = (dword_value >> bit_idx) & 1
                            results.append(bool(bit_value))
                except Exception:
                    # Fallback to individual bit reads
                    for bit_idx in range(32):
                        if len(results) < count:
                            try:
                                bit_value = self.read_output_bit(
                                    module_no, start_offset + len(results)
                                )
                                results.append(bit_value)
                            except Exception:
                                results.append(False)

        elif count >= 16 and start_offset % 16 == 0:
            # Read full words
            words_needed = (count + 15) // 16
            for word_idx in range(words_needed):
                try:
                    word_value = self.read_output_word(module_no, start_offset // 16 + word_idx)
                    for bit_idx in range(16):
                        if len(results) < count:
                            bit_value = (word_value >> bit_idx) & 1
                            results.append(bool(bit_value))
                except Exception:
                    # Fallback to individual bit reads
                    for bit_idx in range(16):
                        if len(results) < count:
                            try:
                                bit_value = self.read_output_bit(
                                    module_no, start_offset + len(results)
                                )
                                results.append(bit_value)
                            except Exception:
                                results.append(False)
        else:
            # Individual bit reads
            for offset in range(start_offset, start_offset + count):
                try:
                    bit_value = self.read_output_bit(module_no, offset)
                    results.append(bit_value)
                except Exception:
                    results.append(False)

        return results[:count]

    @classmethod
    def get_instance(cls) -> "AXLWrapper":
        """
        싱글톤 인스턴스 반환.

        Returns:
            AXLWrapper의 유일한 인스턴스
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self, irq_no: int = 7) -> None:
        """
        중앙화된 연결 관리.

        Args:
            irq_no: IRQ 번호 (기본값: 7)

        Raises:
            AXLError: 연결 실패 시
        """
        # Third-party imports
        from loguru import logger

        if self.is_opened():
            self._connection_count += 1
            logger.info(f"AXL already connected (ref count: {self._connection_count})")
            return

        logger.info(f"Connecting AXL with IRQ {irq_no}...")
        result = self.open(irq_no)
        if result == AXT_RT_SUCCESS:
            self._connection_count = 1
            logger.info("AXL connected successfully")
        else:
            # Local application imports
            from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
                get_error_message,
            )

            error_msg = get_error_message(result)
            logger.error(f"AXL connection failed: {error_msg} (Code: {result})")
            raise AXLError(f"Connection failed: {error_msg} (Code: {result})")

    def disconnect(self) -> None:
        """참조 카운팅으로 안전한 해제."""
        # Third-party imports
        from loguru import logger

        if self._connection_count <= 0:
            logger.warning("disconnect() called but connection count is already 0")
            return

        self._connection_count -= 1
        logger.info(f"AXL disconnect requested (ref count: {self._connection_count})")

        if self._connection_count <= 0:
            if self.is_opened():
                result = self.close()
                if result == AXT_RT_SUCCESS:
                    logger.info("AXL disconnected successfully")
                else:
                    logger.warning(f"AXL disconnect failed (Code: {result})")
            self._connection_count = 0

    @classmethod
    def reset_for_testing(cls) -> None:
        """
        테스트용 싱글톤 리셋.

        주의: 이 메서드는 테스트 목적으로만 사용하세요.
        """
        if cls._instance:
            cls._instance._connection_count = 0
        cls._instance = None
        cls._initialized = False
