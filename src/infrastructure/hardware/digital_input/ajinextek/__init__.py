"""
Ajinextek DIO Hardware Module

This module contains the Ajinextek Digital I/O hardware implementation with
structured constants, error handling, and communication protocols.
"""

from infrastructure.hardware.digital_input.ajinextek.ajinextek_input_service import AjinextekInputService
from infrastructure.hardware.digital_input.ajinextek.constants import (
    DEFAULT_BOARD_NUMBER, DEFAULT_MODULE_POSITION, MAX_INPUT_CHANNELS, MAX_OUTPUT_CHANNELS,
    PIN_MODE_INPUT, PIN_MODE_OUTPUT, PIN_MODE_INPUT_PULLUP, PIN_MODE_INPUT_PULLDOWN,
    LOGIC_LOW, LOGIC_HIGH, DEFAULT_CONFIG, STATUS_MESSAGES, COMMAND_DESCRIPTIONS
)
from infrastructure.hardware.digital_input.ajinextek.error_codes import (
    AjinextekDIOError, AjinextekHardwareError, AjinextekConfigurationError,
    AjinextekOperationError, AjinextekChannelError, AjinextekErrorCode,
    validate_board_number, validate_channel_number, validate_channel_list,
    validate_pin_values, create_hardware_error
)

__all__ = [
    # Main service
    'AjinextekInputService',
    
    # Constants
    'DEFAULT_BOARD_NUMBER', 'DEFAULT_MODULE_POSITION', 'MAX_INPUT_CHANNELS', 'MAX_OUTPUT_CHANNELS',
    'PIN_MODE_INPUT', 'PIN_MODE_OUTPUT', 'PIN_MODE_INPUT_PULLUP', 'PIN_MODE_INPUT_PULLDOWN',
    'LOGIC_LOW', 'LOGIC_HIGH', 'DEFAULT_CONFIG', 'STATUS_MESSAGES', 'COMMAND_DESCRIPTIONS',
    
    # Error handling
    'AjinextekDIOError', 'AjinextekHardwareError', 'AjinextekConfigurationError',
    'AjinextekOperationError', 'AjinextekChannelError', 'AjinextekErrorCode',
    
    # Utility functions
    'validate_board_number', 'validate_channel_number', 'validate_channel_list',
    'validate_pin_values', 'create_hardware_error'
]