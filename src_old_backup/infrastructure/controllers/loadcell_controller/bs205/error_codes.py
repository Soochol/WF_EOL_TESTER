"""
BS205 Loadcell Controller Error Codes and Handling

This module defines error codes and validation utilities for BS205 loadcell controllers.
"""

from enum import IntEnum
from typing import Optional, List


class LoadcellError(IntEnum):
    """Loadcell specific error codes"""
    # Communication Errors (1000-1999)
    COMM_TIMEOUT = 1001
    COMM_SERIAL_ERROR = 1002
    COMM_INVALID_RESPONSE = 1003
    COMM_BUFFER_OVERFLOW = 1004
    COMM_PORT_NOT_FOUND = 1005
    COMM_PORT_ACCESS_DENIED = 1006

    # Protocol Errors (2000-2999)
    PROTOCOL_INVALID_COMMAND = 2001
    PROTOCOL_INVALID_ID = 2002
    PROTOCOL_MALFORMED_RESPONSE = 2003
    PROTOCOL_CHECKSUM_ERROR = 2004
    PROTOCOL_UNEXPECTED_DATA = 2005

    # Hardware Errors (3000-3999)
    HARDWARE_NOT_CONNECTED = 3001
    HARDWARE_INITIALIZATION_FAILED = 3002
    HARDWARE_SENSOR_FAULT = 3003
    HARDWARE_CALIBRATION_ERROR = 3004
    HARDWARE_OVERLOAD = 3005

    # Operation Errors (4000-4999)
    OPERATION_INVALID_PARAMETER = 4001
    OPERATION_INVALID_ID_RANGE = 4002
    OPERATION_VALUE_OUT_OF_RANGE = 4003
    OPERATION_TIMEOUT = 4004
    OPERATION_FAILED = 4005
    OPERATION_NOT_SUPPORTED = 4006

    # Data Errors (5000-5999)
    DATA_PARSING_ERROR = 5001
    DATA_INVALID_FORMAT = 5002
    DATA_NUMERIC_OVERFLOW = 5003
    DATA_MISSING_FIELDS = 5004
    DATA_INCONSISTENT = 5005


# Error message lookup table
ERROR_MESSAGES = {
    # Communication Errors
    LoadcellError.COMM_TIMEOUT: "Communication timeout",
    LoadcellError.COMM_SERIAL_ERROR: "Serial communication error",
    LoadcellError.COMM_INVALID_RESPONSE: "Invalid response received",
    LoadcellError.COMM_BUFFER_OVERFLOW: "Communication buffer overflow",
    LoadcellError.COMM_PORT_NOT_FOUND: "Serial port not found",
    LoadcellError.COMM_PORT_ACCESS_DENIED: "Serial port access denied",

    # Protocol Errors
    LoadcellError.PROTOCOL_INVALID_COMMAND: "Invalid command",
    LoadcellError.PROTOCOL_INVALID_ID: "Invalid indicator ID",
    LoadcellError.PROTOCOL_MALFORMED_RESPONSE: "Malformed response",
    LoadcellError.PROTOCOL_CHECKSUM_ERROR: "Protocol checksum error",
    LoadcellError.PROTOCOL_UNEXPECTED_DATA: "Unexpected protocol data",

    # Hardware Errors
    LoadcellError.HARDWARE_NOT_CONNECTED: "Hardware not connected",
    LoadcellError.HARDWARE_INITIALIZATION_FAILED: "Hardware initialization failed",
    LoadcellError.HARDWARE_SENSOR_FAULT: "Sensor fault detected",
    LoadcellError.HARDWARE_CALIBRATION_ERROR: "Calibration error",
    LoadcellError.HARDWARE_OVERLOAD: "Sensor overload detected",

    # Operation Errors
    LoadcellError.OPERATION_INVALID_PARAMETER: "Invalid parameter",
    LoadcellError.OPERATION_INVALID_ID_RANGE: "Indicator ID out of range",
    LoadcellError.OPERATION_VALUE_OUT_OF_RANGE: "Value out of range",
    LoadcellError.OPERATION_TIMEOUT: "Operation timeout",
    LoadcellError.OPERATION_FAILED: "Operation failed",
    LoadcellError.OPERATION_NOT_SUPPORTED: "Operation not supported",

    # Data Errors
    LoadcellError.DATA_PARSING_ERROR: "Data parsing error",
    LoadcellError.DATA_INVALID_FORMAT: "Invalid data format",
    LoadcellError.DATA_NUMERIC_OVERFLOW: "Numeric overflow",
    LoadcellError.DATA_MISSING_FIELDS: "Missing required data fields",
    LoadcellError.DATA_INCONSISTENT: "Inconsistent data",
}


def get_error_message(error_code: LoadcellError) -> str:
    """
    Get error message for error code
    
    Args:
        error_code: Loadcell error code
        
    Returns:
        str: Error message
    """
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")


# Function removed - not used anywhere in the codebase


def validate_indicator_id(indicator_id: int, min_id: int = 1, max_id: int = 255) -> None:
    """
    Validate indicator ID range
    
    Args:
        indicator_id: ID to validate
        min_id: Minimum allowed ID
        max_id: Maximum allowed ID
        
    Raises:
        ValueError: If ID is out of range
    """
    if not (min_id <= indicator_id <= max_id):
        raise ValueError(f"Indicator ID {indicator_id} is out of range [{min_id}, {max_id}]")




# No backward compatibility aliases needed - use BS205-specific exceptions instead