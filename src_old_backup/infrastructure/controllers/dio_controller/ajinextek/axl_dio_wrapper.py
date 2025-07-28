"""
DIO-specific AXL Wrapper for AJINEXTEK

Independent DIO wrapper that doesn't depend on robot controller.
Contains only library initialization and DIO-specific functions.
"""

import ctypes
from ctypes import POINTER, c_long, c_char_p
import platform
from typing import Optional, Any
import os

# Import constants from robot controller (temporary, will be moved later)
from ...robot_controller.ajinextek.constants import DLL_PATH
from ...robot_controller.ajinextek.error_codes import AXT_RT_SUCCESS, get_error_message
from ..exceptions import AXLDIOError
from ...robot_controller.exceptions import AXLError, AXLConnectionError


class AXLDIOWrapper:
    """DIO-specific AXL library wrapper"""

    def __init__(self):
        self.dll: Optional[Any] = None
        self.is_windows = platform.system() == "Windows"

        if self.is_windows:
            self._load_library()
            self._setup_dio_functions()
        else:
            # Linux/개발환경에서는 경고 메시지만 출력
            print("Warning: Running on non-Windows platform. "
                  "DLL functions will not be available.")

    def _load_library(self):
        """Load the AXL DLL (Windows only)"""
        if not self.is_windows:
            return

        if not os.path.exists(DLL_PATH):
            raise FileNotFoundError(f"AXL DLL not found at {DLL_PATH}")

        try:
            # Load DLL with Windows calling convention
            WinDLL = getattr(ctypes, 'WinDLL')
            self.dll = WinDLL(DLL_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to load AXL DLL: {e}")

    def _setup_dio_functions(self):
        """Setup DIO-specific function signatures (Windows only)"""
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

        # === DIO Functions ===
        # AxdInfoGetModuleCount
        self.dll.AxdInfoGetModuleCount.argtypes = [POINTER(c_long)]
        self.dll.AxdInfoGetModuleCount.restype = c_long

        # AxdInfoGetInputCount
        self.dll.AxdInfoGetInputCount.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxdInfoGetInputCount.restype = c_long

        # AxdInfoGetOutputCount
        self.dll.AxdInfoGetOutputCount.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxdInfoGetOutputCount.restype = c_long

        # AxdoReadOutport
        self.dll.AxdoReadOutport.argtypes = [c_long, c_long, POINTER(c_long)]
        self.dll.AxdoReadOutport.restype = c_long

        # AxdoWriteOutport
        self.dll.AxdoWriteOutport.argtypes = [c_long, c_long, c_long]
        self.dll.AxdoWriteOutport.restype = c_long

        # AxdiReadInport
        self.dll.AxdiReadInport.argtypes = [c_long, c_long, POINTER(c_long)]
        self.dll.AxdiReadInport.restype = c_long


    # === Library Functions ===
    def open(self, irq_no: int = 7) -> int:
        """Initialize and open the AXL library"""
        assert self.dll is not None
        return self.dll.AxlOpen(irq_no)

    def close(self) -> int:
        """Close the AXL library"""
        assert self.dll is not None
        return self.dll.AxlClose()

    def is_opened(self) -> bool:
        """Check if library is opened"""
        assert self.dll is not None
        return self.dll.AxlIsOpened() == 1

    def get_board_count(self) -> int:
        """Get the number of boards"""
        assert self.dll is not None
        count = c_long()
        result = self.dll.AxlGetBoardCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result, "AxlGetBoardCount")
        return count.value

    def get_lib_version(self) -> str:
        """Get library version"""
        assert self.dll is not None
        version = ctypes.create_string_buffer(32)
        result = self.dll.AxlGetLibVersion(version)
        if result != AXT_RT_SUCCESS:
            raise AXLError(get_error_message(result), result, "AxlGetLibVersion")
        return version.value.decode('ascii')

    # === DIO Functions ===
    def get_dio_module_count(self) -> int:
        """Get number of DIO modules"""
        assert self.dll is not None
        count = c_long()
        result = self.dll.AxdInfoGetModuleCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLDIOError(get_error_message(result), result, "AxdInfoGetModuleCount")
        return count.value

    def get_input_count(self, module_no: int) -> int:
        """Get number of inputs for module"""
        assert self.dll is not None
        count = c_long()
        result = self.dll.AxdInfoGetInputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLDIOError(get_error_message(result), result, "AxdInfoGetInputCount")
        return count.value

    def get_output_count(self, module_no: int) -> int:
        """Get number of outputs for module"""
        assert self.dll is not None
        count = c_long()
        result = self.dll.AxdInfoGetOutputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise AXLDIOError(get_error_message(result), result, "AxdInfoGetOutputCount")
        return count.value

    def read_output_port(self, module_no: int, offset: int) -> int:
        """Read output port value"""
        assert self.dll is not None
        value = c_long()
        result = self.dll.AxdoReadOutport(module_no, offset,
                                          ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLDIOError(get_error_message(result), result, "AxdoReadOutport")
        return value.value

    def write_output_port(self, module_no: int, offset: int,
                          value: int) -> int:
        """Write output port value"""
        assert self.dll is not None
        return self.dll.AxdoWriteOutport(module_no, offset, value)

    def read_input_port(self, module_no: int, offset: int) -> int:
        """Read input port value"""
        assert self.dll is not None
        value = c_long()
        result = self.dll.AxdiReadInport(module_no, offset,
                                         ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise AXLDIOError(get_error_message(result), result, "AxdiReadInport")
        return value.value
