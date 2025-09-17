"""
Ajinextek DIO Hardware Module

This module contains the Ajinextek Digital I/O hardware implementation with
structured constants, error handling, and communication protocols.
"""

# Local application imports
from infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio import AjinextekDIO
from infrastructure.implementation.hardware.digital_io.ajinextek.constants import (
    COMMAND_DESCRIPTIONS,
    DEFAULT_BOARD_NUMBER,
    DEFAULT_CONFIG,
    DEFAULT_MODULE_POSITION,
    LOGIC_HIGH,
    LOGIC_LOW,
    MAX_INPUT_CHANNELS,
    MAX_OUTPUT_CHANNELS,
    PIN_MODE_INPUT,
    PIN_MODE_INPUT_PULLDOWN,
    PIN_MODE_INPUT_PULLUP,
    PIN_MODE_OUTPUT,
    STATUS_MESSAGES,
)
from infrastructure.implementation.hardware.digital_io.ajinextek.error_codes import (
    AjinextekChannelError,
    AjinextekConfigurationError,
    AjinextekDIOError,
    AjinextekErrorCode,
    AjinextekHardwareError,
    AjinextekOperationError,
    create_hardware_error,
    validate_board_number,
    validate_channel_list,
    validate_channel_number,
    validate_pin_values,
)


__all__ = [
    # Main service
    "AjinextekDIO",
    # Constants
    "DEFAULT_BOARD_NUMBER",
    "DEFAULT_MODULE_POSITION",
    "MAX_INPUT_CHANNELS",
    "MAX_OUTPUT_CHANNELS",
    "PIN_MODE_INPUT",
    "PIN_MODE_OUTPUT",
    "PIN_MODE_INPUT_PULLUP",
    "PIN_MODE_INPUT_PULLDOWN",
    "LOGIC_LOW",
    "LOGIC_HIGH",
    "DEFAULT_CONFIG",
    "STATUS_MESSAGES",
    "COMMAND_DESCRIPTIONS",
    # Error handling
    "AjinextekDIOError",
    "AjinextekHardwareError",
    "AjinextekConfigurationError",
    "AjinextekOperationError",
    "AjinextekChannelError",
    "AjinextekErrorCode",
    # Utility functions
    "validate_board_number",
    "validate_channel_number",
    "validate_channel_list",
    "validate_pin_values",
    "create_hardware_error",
]
