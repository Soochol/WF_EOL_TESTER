"""
Python wrapper for AJINEXTEK AXL Library - Digital I/O Functions

This module provides ctypes bindings for the AXL digital I/O library functions.
"""

# pylint: disable=no-member
# mypy: disable-error-code=attr-defined

import ctypes
import os
import platform
from ctypes import POINTER, c_long, wintypes
from typing import Any, List, Optional, Tuple

from loguru import logger

from infrastructure.implementation.hardware.digital_input.ajinextek.constants import (
    AXL_64BIT_LIBRARY_NAME,
    AXL_LIBRARY_NAME,
)
from infrastructure.implementation.hardware.digital_input.ajinextek.error_codes import (
    AjinextekHardwareError,
    create_hardware_error,
)

# Platform-specific WinDLL and function type handling
if platform.system() == "Windows":
    try:
        from ctypes import (  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
            WINFUNCTYPE,  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
            WinDLL,  # pylint: disable=ungrouped-imports  # type: ignore[attr-defined]
        )
        FuncType = WINFUNCTYPE
    except ImportError:
        # Fallback for Windows environments without WinDLL
        from ctypes import CFUNCTYPE
        FuncType = CFUNCTYPE
        class WinDLL:  # type: ignore[no-redef]
            def __init__(self, path: str) -> None:
                ...

else:
    # Use CFUNCTYPE for non-Windows systems
    from ctypes import CFUNCTYPE
    FuncType = CFUNCTYPE
    # Mock WinDLL class for non-Windows systems
    class WinDLL:  # type: ignore[no-redef]
        def __init__(self, path: str) -> None:
            ...


# AXL Return Codes
AXT_RT_SUCCESS = 0
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


class AXLDIOWrapper:
    """
    Wrapper class for AXL DIO library functions
    """

    def __init__(self) -> None:
        self.dll: Optional[Any] = None
        self.is_windows = platform.system() == "Windows"

        if not self.is_windows:
            raise AjinextekHardwareError(
                "AXL DIO library is only supported on Windows platform. "
                "For development/testing on other platforms, use MockDIO instead."
            )

        self._load_library()
        self._setup_functions()

    def _load_library(self) -> None:
        """Load the AXL DLL"""
        # Try to find AXL library
        library_paths = [
            AXL_64BIT_LIBRARY_NAME if platform.machine().endswith("64") else AXL_LIBRARY_NAME,
            os.path.join(
                "C:\\AJINEXTEK\\AXL\\Library",
                AXL_64BIT_LIBRARY_NAME if platform.machine().endswith("64") else AXL_LIBRARY_NAME,
            ),
            os.path.join(
                os.getcwd(),
                "src",
                "driver",
                "ajinextek",
                "AXL(Library)",
                "Library",
                "64Bit" if platform.machine().endswith("64") else "32Bit",
                "AXL.dll",
            ),
        ]

        for library_path in library_paths:
            try:
                if os.path.exists(library_path):
                    self.dll = WinDLL(str(library_path))
                    logger.info(f"AXL library loaded from: {library_path}")
                    return
            except OSError as e:
                logger.debug(f"Failed to load AXL library from {library_path}: {e}")
                continue

        raise AjinextekHardwareError(f"AXL DLL not found. Searched paths: {library_paths}")

    def _setup_functions(self) -> None:
        """Setup function signatures for ctypes"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        # === Board and Module Information Functions ===
        # AxdInfoIsDIOModule
        self.dll.AxdInfoIsDIOModule.argtypes = [POINTER(wintypes.DWORD)]
        self.dll.AxdInfoIsDIOModule.restype = wintypes.DWORD

        # AxdInfoGetModuleCount
        self.dll.AxdInfoGetModuleCount.argtypes = [POINTER(c_long)]
        self.dll.AxdInfoGetModuleCount.restype = wintypes.DWORD

        # AxdInfoGetModuleNo
        self.dll.AxdInfoGetModuleNo.argtypes = [c_long, c_long, POINTER(c_long)]
        self.dll.AxdInfoGetModuleNo.restype = wintypes.DWORD

        # AxdInfoGetInputCount
        self.dll.AxdInfoGetInputCount.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxdInfoGetInputCount.restype = wintypes.DWORD

        # AxdInfoGetOutputCount
        self.dll.AxdInfoGetOutputCount.argtypes = [c_long, POINTER(c_long)]
        self.dll.AxdInfoGetOutputCount.restype = wintypes.DWORD

        # AxdInfoGetModule
        self.dll.AxdInfoGetModule.argtypes = [
            c_long,
            POINTER(c_long),
            POINTER(c_long),
            POINTER(wintypes.DWORD),
        ]
        self.dll.AxdInfoGetModule.restype = wintypes.DWORD

        # AxdInfoGetModuleStatus
        self.dll.AxdInfoGetModuleStatus.argtypes = [c_long]
        self.dll.AxdInfoGetModuleStatus.restype = wintypes.DWORD

        # === Input Reading Functions ===
        # AxdiReadInportBit
        self.dll.AxdiReadInportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiReadInportBit.restype = wintypes.DWORD

        # AxdiReadInportByte
        self.dll.AxdiReadInportByte.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiReadInportByte.restype = wintypes.DWORD

        # AxdiReadInportWord
        self.dll.AxdiReadInportWord.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiReadInportWord.restype = wintypes.DWORD

        # AxdiReadInportDword
        self.dll.AxdiReadInportDword.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiReadInportDword.restype = wintypes.DWORD

        # === Output Writing Functions ===
        # AxdoWriteOutportBit
        self.dll.AxdoWriteOutportBit.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdoWriteOutportBit.restype = wintypes.DWORD

        # AxdoWriteOutportByte
        self.dll.AxdoWriteOutportByte.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdoWriteOutportByte.restype = wintypes.DWORD

        # AxdoWriteOutportWord
        self.dll.AxdoWriteOutportWord.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdoWriteOutportWord.restype = wintypes.DWORD

        # AxdoWriteOutportDword
        self.dll.AxdoWriteOutportDword.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdoWriteOutportDword.restype = wintypes.DWORD

        # === Level Configuration Functions ===
        # AxdiLevelSetInportBit
        self.dll.AxdiLevelSetInportBit.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdiLevelSetInportBit.restype = wintypes.DWORD

        # AxdiLevelGetInportBit
        self.dll.AxdiLevelGetInportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiLevelGetInportBit.restype = wintypes.DWORD

        # AxdoLevelSetOutportBit
        self.dll.AxdoLevelSetOutportBit.argtypes = [c_long, c_long, wintypes.DWORD]
        self.dll.AxdoLevelSetOutportBit.restype = wintypes.DWORD

        # AxdoLevelGetOutportBit
        self.dll.AxdoLevelGetOutportBit.argtypes = [c_long, c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdoLevelGetOutportBit.restype = wintypes.DWORD

        # === Interrupt Functions ===
        # AxdiInterruptSetModule
        self.dll.AxdiInterruptSetModule.argtypes = [
            c_long,
            wintypes.HWND,
            wintypes.DWORD,
            FuncType(None),
            POINTER(wintypes.HANDLE),
        ]
        self.dll.AxdiInterruptSetModule.restype = wintypes.DWORD

        # AxdiInterruptSetModuleEnable
        self.dll.AxdiInterruptSetModuleEnable.argtypes = [c_long, wintypes.DWORD]
        self.dll.AxdiInterruptSetModuleEnable.restype = wintypes.DWORD

        # AxdiInterruptEdgeSetBit
        self.dll.AxdiInterruptEdgeSetBit.argtypes = [c_long, c_long, wintypes.DWORD, wintypes.DWORD]
        self.dll.AxdiInterruptEdgeSetBit.restype = wintypes.DWORD

        # AxdiInterruptRead
        self.dll.AxdiInterruptRead.argtypes = [c_long, POINTER(wintypes.DWORD)]
        self.dll.AxdiInterruptRead.restype = wintypes.DWORD

        # === Core Library Functions ===
        # AxlOpen
        self.dll.AxlOpen.argtypes = [c_long]
        self.dll.AxlOpen.restype = wintypes.DWORD

        # AxlClose
        self.dll.AxlClose.argtypes = []
        self.dll.AxlClose.restype = wintypes.DWORD

        # AxlIsOpened
        self.dll.AxlIsOpened.argtypes = []
        self.dll.AxlIsOpened.restype = wintypes.DWORD

    # === Core Library Functions ===
    def axl_open(self, irq_no: int) -> int:
        """Open AXL library with specified IRQ number"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxlOpen(irq_no)
        return result

    def axl_close(self) -> bool:
        """Close AXL library"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxlClose()
        return result == AXT_RT_SUCCESS

    def is_opened(self) -> bool:
        """Check if AXL library is opened"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        return self.dll.AxlIsOpened() == 1

    # === Board and Module Information Functions ===
    def is_dio_module(self) -> bool:
        """Check if DIO modules exist"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        status = wintypes.DWORD()
        result = self.dll.AxdInfoIsDIOModule(ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error("Failed to check DIO module existence", result)
        return bool(status.value)

    def get_module_count(self) -> int:
        """Get total number of DIO modules"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetModuleCount(ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error("Failed to get module count", result)
        return count.value

    def get_module_no(self, board_no: int, module_pos: int) -> int:
        """Get module number from board number and position"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        module_no = c_long()
        result = self.dll.AxdInfoGetModuleNo(board_no, module_pos, ctypes.byref(module_no))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to get module number for board {board_no}, position {module_pos}", result
            )
        return module_no.value

    def get_input_count(self, module_no: int) -> int:
        """Get input channel count for module"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetInputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(f"Failed to get input count for module {module_no}", result)
        return count.value

    def get_output_count(self, module_no: int) -> int:
        """Get output channel count for module"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        count = c_long()
        result = self.dll.AxdInfoGetOutputCount(module_no, ctypes.byref(count))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to get output count for module {module_no}", result
            )
        return count.value

    def get_module_info(self, module_no: int) -> Tuple[int, int, int]:
        """Get module information (board_no, module_pos, module_id)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        board_no = c_long()
        module_pos = c_long()
        module_id = wintypes.DWORD()

        result = self.dll.AxdInfoGetModule(
            module_no, ctypes.byref(board_no), ctypes.byref(module_pos), ctypes.byref(module_id)
        )

        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(f"Failed to get module info for module {module_no}", result)

        return (board_no.value, module_pos.value, module_id.value)

    def get_module_status(self, module_no: int) -> int:
        """Get module status"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdInfoGetModuleStatus(module_no)
        return result

    # === Input Reading Functions ===
    def read_input_bit(self, module_no: int, offset: int) -> bool:
        """Read single input bit"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportBit(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to read input bit {offset} on module {module_no}", result
            )
        return bool(value.value)

    def read_input_byte(self, module_no: int, offset: int) -> int:
        """Read input byte (8 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportByte(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to read input byte {offset} on module {module_no}", result
            )
        return value.value & 0xFF

    def read_input_word(self, module_no: int, offset: int) -> int:
        """Read input word (16 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportWord(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to read input word {offset} on module {module_no}", result
            )
        return value.value & 0xFFFF

    def read_input_dword(self, module_no: int, offset: int) -> int:
        """Read input dword (32 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        value = wintypes.DWORD()
        result = self.dll.AxdiReadInportDword(module_no, offset, ctypes.byref(value))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to read input dword {offset} on module {module_no}", result
            )
        return value.value

    # === Output Writing Functions ===
    def write_output_bit(self, module_no: int, offset: int, value: bool) -> None:
        """Write single output bit"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        bit_value = 1 if value else 0
        result = self.dll.AxdoWriteOutportBit(module_no, offset, bit_value)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to write output bit {offset} on module {module_no}", result
            )

    def write_output_byte(self, module_no: int, offset: int, value: int) -> None:
        """Write output byte (8 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportByte(module_no, offset, value & 0xFF)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to write output byte {offset} on module {module_no}", result
            )

    def write_output_word(self, module_no: int, offset: int, value: int) -> None:
        """Write output word (16 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportWord(module_no, offset, value & 0xFFFF)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to write output word {offset} on module {module_no}", result
            )

    def write_output_dword(self, module_no: int, offset: int, value: int) -> None:
        """Write output dword (32 bits)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdoWriteOutportDword(module_no, offset, value)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to write output dword {offset} on module {module_no}", result
            )

    # === Level Configuration Functions ===
    def set_input_level(self, module_no: int, offset: int, level: int) -> None:
        """Set input signal level (HIGH/LOW active)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdiLevelSetInportBit(module_no, offset, level)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to set input level for bit {offset} on module {module_no}", result
            )

    def get_input_level(self, module_no: int, offset: int) -> int:
        """Get input signal level configuration"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        level = wintypes.DWORD()
        result = self.dll.AxdiLevelGetInportBit(module_no, offset, ctypes.byref(level))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to get input level for bit {offset} on module {module_no}", result
            )
        return level.value

    def set_output_level(self, module_no: int, offset: int, level: int) -> None:
        """Set output signal level (HIGH/LOW active)"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdoLevelSetOutportBit(module_no, offset, level)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to set output level for bit {offset} on module {module_no}", result
            )

    def get_output_level(self, module_no: int, offset: int) -> int:
        """Get output signal level configuration"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        level = wintypes.DWORD()
        result = self.dll.AxdoLevelGetOutportBit(module_no, offset, ctypes.byref(level))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to get output level for bit {offset} on module {module_no}", result
            )
        return level.value

    # === Interrupt Functions ===
    def setup_interrupt_callback(self, module_no: int, callback_func) -> None:
        """Setup interrupt with callback function"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        result = self.dll.AxdiInterruptSetModule(
            module_no,
            None,  # hWnd (not used for callback method)
            0,  # uMessage (not used for callback method)
            callback_func,  # Callback function
            None,  # pEvent (not used for callback method)
        )

        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to setup interrupt callback for module {module_no}", result
            )

    def enable_module_interrupt(self, module_no: int, enable: bool = True) -> None:
        """Enable/disable interrupts for module"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        enable_value = 1 if enable else 0
        result = self.dll.AxdiInterruptSetModuleEnable(module_no, enable_value)
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to {'enable' if enable else 'disable'} interrupts for module {module_no}",
                result,
            )

    def set_interrupt_edge(
        self, module_no: int, offset: int, edge_mode: str, value: int = 1
    ) -> None:
        """Set interrupt edge trigger mode for input bit"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        edge_mapping = {
            "rising": UP_EDGE,
            "falling": DOWN_EDGE,
            "both": BOTH_EDGE,
        }

        edge_value = edge_mapping.get(edge_mode, UP_EDGE)
        result = self.dll.AxdiInterruptEdgeSetBit(module_no, offset, edge_value, value)

        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to set interrupt edge for bit {offset} on module {module_no}", result
            )

    def read_interrupt_status(self, module_no: int) -> int:
        """Read interrupt status for module"""
        if self.dll is None:
            raise AjinextekHardwareError("AXL DLL not loaded")

        status = wintypes.DWORD()
        result = self.dll.AxdiInterruptRead(module_no, ctypes.byref(status))
        if result != AXT_RT_SUCCESS:
            raise create_hardware_error(
                f"Failed to read interrupt status for module {module_no}", result
            )
        return status.value

    # === Utility Functions ===
    def batch_read_inputs(self, module_no: int, start_offset: int, count: int) -> List[bool]:
        """Optimized batch reading of multiple input bits"""
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
        """Optimized batch writing of multiple output bits"""
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
