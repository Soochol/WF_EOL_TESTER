"""
Ajinextek DIO Error Codes and Handling

This module defines error codes and error handling utilities for Ajinextek DIO cards.
"""

from enum import IntEnum
from typing import Optional, List, Dict, Any


class AjinextekErrorCode(IntEnum):
    """Ajinextek DIO specific error codes"""

    # Hardware Connection Errors
    HARDWARE_NOT_FOUND = 2001
    HARDWARE_NOT_CONNECTED = 2002
    HARDWARE_INITIALIZATION_FAILED = 2003
    HARDWARE_COMMUNICATION_FAILED = 2004
    HARDWARE_TIMEOUT = 2005

    # Board and Module Errors
    BOARD_NOT_DETECTED = 2101
    BOARD_ALREADY_OPEN = 2102
    MODULE_NOT_FOUND = 2103
    MODULE_TYPE_MISMATCH = 2104
    MODULE_CONFIGURATION_ERROR = 2105

    # Channel and Pin Errors
    INVALID_CHANNEL_NUMBER = 2201
    CHANNEL_NOT_CONFIGURED = 2202
    CHANNEL_ACCESS_DENIED = 2203
    PIN_MODE_CONFLICT = 2204
    PIN_ALREADY_IN_USE = 2205

    # Operation Errors
    OPERATION_NOT_SUPPORTED = 2301
    OPERATION_TIMEOUT = 2302
    OPERATION_INTERRUPTED = 2303
    INVALID_PARAMETER = 2304
    BUFFER_OVERFLOW = 2305

    # Library and Driver Errors
    LIBRARY_NOT_LOADED = 2401
    LIBRARY_VERSION_MISMATCH = 2402
    DRIVER_NOT_INSTALLED = 2403
    DRIVER_VERSION_INCOMPATIBLE = 2404

    # Configuration Errors
    INVALID_CONFIGURATION = 2501
    CONFIGURATION_CONFLICT = 2502
    CONFIGURATION_NOT_APPLIED = 2503

    # Runtime Errors
    INTERRUPT_HANDLING_ERROR = 2601
    DEBOUNCE_ERROR = 2602
    SIGNAL_INTEGRITY_ERROR = 2603
    POWER_SUPPLY_ERROR = 2604


class AjinextekDIOError(Exception):
    """Base Ajinextek DIO error"""

    def __init__(self, message: str, error_code: int = 0, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self) -> str:
        base_msg = self.message
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        return base_msg


class AjinextekHardwareError(AjinextekDIOError):
    """Ajinextek hardware connection and initialization errors"""

    pass


class AjinextekConfigurationError(AjinextekDIOError):
    """Ajinextek configuration and setup errors"""

    pass


class AjinextekOperationError(AjinextekDIOError):
    """Ajinextek operation and runtime errors"""

    pass


class AjinextekChannelError(AjinextekDIOError):
    """Ajinextek channel and pin related errors"""

    pass


def validate_board_number(board_number: int, max_boards: int = 32) -> None:
    """
    Validate board number range

    Args:
        board_number: Board number to validate
        max_boards: Maximum allowed board number

    Raises:
        AjinextekConfigurationError: If board number is invalid
    """
    if not (0 <= board_number < max_boards):
        raise AjinextekConfigurationError(
            f"Board number {board_number} is out of range [0, {max_boards-1}]",
            error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
        )


def validate_channel_number(channel: int, max_channels: int = 32) -> None:
    """
    Validate channel number range

    Args:
        channel: Channel number to validate
        max_channels: Maximum allowed channel number

    Raises:
        AjinextekChannelError: If channel number is invalid
    """
    if not (0 <= channel < max_channels):
        raise AjinextekChannelError(
            f"Channel {channel} is out of range [0, {max_channels-1}]",
            error_code=int(AjinextekErrorCode.INVALID_CHANNEL_NUMBER),
        )


def validate_channel_list(channels: List[int], max_channels: int = 32) -> None:
    """
    Validate list of channel numbers

    Args:
        channels: List of channel numbers to validate
        max_channels: Maximum allowed channel number

    Raises:
        AjinextekChannelError: If any channel number is invalid
    """
    if not channels:
        raise AjinextekChannelError(
            "Channel list cannot be empty", error_code=int(AjinextekErrorCode.INVALID_PARAMETER)
        )

    for channel in channels:
        validate_channel_number(channel, max_channels)

    # Check for duplicates
    if len(channels) != len(set(channels)):
        duplicates = [ch for ch in set(channels) if channels.count(ch) > 1]
        raise AjinextekChannelError(
            f"Duplicate channels found: {duplicates}",
            error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
        )


def validate_pin_values(pin_values: Dict[int, int], max_channels: int = 32) -> None:
    """
    Validate pin-value mapping

    Args:
        pin_values: Dictionary of pin numbers to values
        max_channels: Maximum allowed channel number

    Raises:
        AjinextekChannelError: If pin-value mapping is invalid
    """
    if not pin_values:
        raise AjinextekChannelError(
            "Pin values dictionary cannot be empty",
            error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
        )

    for pin, value in pin_values.items():
        validate_channel_number(pin, max_channels)

        if value not in [0, 1]:
            raise AjinextekChannelError(
                f"Invalid logic level {value} for pin {pin}. Must be 0 or 1",
                error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
            )


def validate_module_position(position: int, max_modules: int = 4) -> None:
    """
    Validate module position

    Args:
        position: Module position to validate
        max_modules: Maximum modules per board

    Raises:
        AjinextekConfigurationError: If module position is invalid
    """
    if not (0 <= position < max_modules):
        raise AjinextekConfigurationError(
            f"Module position {position} is out of range [0, {max_modules-1}]",
            error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
        )


def validate_debounce_time(debounce_ms: int, max_debounce: int = 1000) -> None:
    """
    Validate debounce time setting

    Args:
        debounce_ms: Debounce time in milliseconds
        max_debounce: Maximum allowed debounce time

    Raises:
        AjinextekConfigurationError: If debounce time is invalid
    """
    if not (0 <= debounce_ms <= max_debounce):
        raise AjinextekConfigurationError(
            f"Debounce time {debounce_ms}ms is out of range [0, {max_debounce}]",
            error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
        )


def create_hardware_error(
    message: str, axl_error_code: Optional[int] = None
) -> AjinextekHardwareError:
    """
    Create hardware error with AXL library error code mapping

    Args:
        message: Error message
        axl_error_code: AXL library specific error code

    Returns:
        AjinextekHardwareError instance
    """
    error_code = int(AjinextekErrorCode.HARDWARE_COMMUNICATION_FAILED)
    details = None

    if axl_error_code is not None:
        details = f"AXL Error Code: {axl_error_code}"

        # Map common AXL error codes to our error codes
        axl_error_mapping = {
            -1: AjinextekErrorCode.HARDWARE_NOT_FOUND,
            -2: AjinextekErrorCode.BOARD_NOT_DETECTED,
            -3: AjinextekErrorCode.MODULE_NOT_FOUND,
            -4: AjinextekErrorCode.INVALID_CHANNEL_NUMBER,
            -5: AjinextekErrorCode.HARDWARE_TIMEOUT,
            -6: AjinextekErrorCode.LIBRARY_NOT_LOADED,
        }

        error_code = int(
            axl_error_mapping.get(axl_error_code, AjinextekErrorCode.HARDWARE_COMMUNICATION_FAILED)
        )

    return AjinextekHardwareError(message, error_code, details)


def parse_axl_error(axl_return_code: int) -> str:
    """
    Parse AXL library return code to human readable message

    Args:
        axl_return_code: Return code from AXL library function

    Returns:
        Human readable error message
    """
    axl_error_messages = {
        0: "Success",
        -1: "Board not found or not opened",
        -2: "Invalid board number",
        -3: "Invalid module position",
        -4: "Invalid channel number",
        -5: "Communication timeout",
        -6: "Library not initialized",
        -7: "Invalid parameter",
        -8: "Module not detected",
        -9: "Hardware fault detected",
        -10: "Operation not supported by this module",
    }

    return axl_error_messages.get(axl_return_code, f"Unknown AXL error code: {axl_return_code}")


# Error code to message mapping
ERROR_MESSAGES = {
    # Hardware Connection Errors
    AjinextekErrorCode.HARDWARE_NOT_FOUND: "DIO hardware not found",
    AjinextekErrorCode.HARDWARE_NOT_CONNECTED: "DIO hardware not connected",
    AjinextekErrorCode.HARDWARE_INITIALIZATION_FAILED: "DIO hardware initialization failed",
    AjinextekErrorCode.HARDWARE_COMMUNICATION_FAILED: "Communication with DIO hardware failed",
    AjinextekErrorCode.HARDWARE_TIMEOUT: "DIO hardware operation timeout",
    # Board and Module Errors
    AjinextekErrorCode.BOARD_NOT_DETECTED: "DIO board not detected",
    AjinextekErrorCode.BOARD_ALREADY_OPEN: "DIO board already open",
    AjinextekErrorCode.MODULE_NOT_FOUND: "DIO module not found",
    AjinextekErrorCode.MODULE_TYPE_MISMATCH: "DIO module type mismatch",
    AjinextekErrorCode.MODULE_CONFIGURATION_ERROR: "DIO module configuration error",
    # Channel and Pin Errors
    AjinextekErrorCode.INVALID_CHANNEL_NUMBER: "Invalid channel number",
    AjinextekErrorCode.CHANNEL_NOT_CONFIGURED: "Channel not configured",
    AjinextekErrorCode.CHANNEL_ACCESS_DENIED: "Channel access denied",
    AjinextekErrorCode.PIN_MODE_CONFLICT: "Pin mode conflict",
    AjinextekErrorCode.PIN_ALREADY_IN_USE: "Pin already in use",
    # Operation Errors
    AjinextekErrorCode.OPERATION_NOT_SUPPORTED: "Operation not supported",
    AjinextekErrorCode.OPERATION_TIMEOUT: "Operation timeout",
    AjinextekErrorCode.OPERATION_INTERRUPTED: "Operation interrupted",
    AjinextekErrorCode.INVALID_PARAMETER: "Invalid parameter",
    AjinextekErrorCode.BUFFER_OVERFLOW: "Buffer overflow",
    # Library and Driver Errors
    AjinextekErrorCode.LIBRARY_NOT_LOADED: "AXL library not loaded",
    AjinextekErrorCode.LIBRARY_VERSION_MISMATCH: "AXL library version mismatch",
    AjinextekErrorCode.DRIVER_NOT_INSTALLED: "AXL driver not installed",
    AjinextekErrorCode.DRIVER_VERSION_INCOMPATIBLE: "AXL driver version incompatible",
    # Configuration Errors
    AjinextekErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
    AjinextekErrorCode.CONFIGURATION_CONFLICT: "Configuration conflict",
    AjinextekErrorCode.CONFIGURATION_NOT_APPLIED: "Configuration not applied",
    # Runtime Errors
    AjinextekErrorCode.INTERRUPT_HANDLING_ERROR: "Interrupt handling error",
    AjinextekErrorCode.DEBOUNCE_ERROR: "Debounce configuration error",
    AjinextekErrorCode.SIGNAL_INTEGRITY_ERROR: "Signal integrity error",
    AjinextekErrorCode.POWER_SUPPLY_ERROR: "Power supply error",
}


def get_error_message(error_code: AjinextekErrorCode) -> str:
    """
    Get error message for error code

    Args:
        error_code: Ajinextek error code

    Returns:
        Human readable error message
    """
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")
