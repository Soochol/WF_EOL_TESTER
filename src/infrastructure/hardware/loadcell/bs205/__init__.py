"""
BS205 LoadCell Hardware Module

This module contains the BS205 loadcell hardware implementation with
structured constants, error handling, and communication protocols.
"""

from infrastructure.hardware.loadcell.bs205.bs205_loadcell_adapter import BS205LoadCellAdapter
from infrastructure.hardware.loadcell.bs205.constants import (
    DEFAULT_BAUDRATE, DEFAULT_TIMEOUT, DEFAULT_INDICATOR_ID,
    CMD_READ_WEIGHT, CMD_ZERO, CMD_IDENTITY,
    KG_TO_NEWTON, SUPPORTED_UNITS, DEFAULT_CONFIG
)
from infrastructure.hardware.loadcell.bs205.error_codes import (
    BS205Error, BS205CommunicationError, BS205HardwareError, 
    BS205OperationError, BS205DataError, BS205ErrorCode,
    parse_weight_response, convert_weight_to_force,
    validate_weight_range, validate_sample_parameters
)

__all__ = [
    # Main service
    'BS205LoadCellAdapter',
    
    # Constants
    'DEFAULT_BAUDRATE', 'DEFAULT_TIMEOUT', 'DEFAULT_INDICATOR_ID',
    'CMD_READ_WEIGHT', 'CMD_ZERO', 'CMD_IDENTITY',
    'KG_TO_NEWTON', 'SUPPORTED_UNITS', 'DEFAULT_CONFIG',
    
    # Error handling
    'BS205Error', 'BS205CommunicationError', 'BS205HardwareError',
    'BS205OperationError', 'BS205DataError', 'BS205ErrorCode',
    
    # Utility functions
    'parse_weight_response', 'convert_weight_to_force',
    'validate_weight_range', 'validate_sample_parameters'
]