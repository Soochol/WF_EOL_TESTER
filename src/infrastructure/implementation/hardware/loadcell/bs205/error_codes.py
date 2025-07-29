"""
BS205 LoadCell Error Codes and Handling

This module defines error codes and error handling utilities for BS205 LoadCell.
"""

from enum import IntEnum
from typing import Optional


class BS205ErrorCode(IntEnum):
    """BS205 specific error codes"""
    # Communication Errors
    COMM_TIMEOUT = 1001
    COMM_SERIAL_ERROR = 1002
    COMM_PORT_NOT_AVAILABLE = 1003
    COMM_INVALID_RESPONSE = 1004
    COMM_BUFFER_OVERFLOW = 1005

    # Protocol Errors
    PROTOCOL_INVALID_COMMAND = 2001
    PROTOCOL_MALFORMED_RESPONSE = 2002
    PROTOCOL_UNEXPECTED_RESPONSE = 2003
    PROTOCOL_CHECKSUM_ERROR = 2004

    # Hardware Errors
    HARDWARE_NOT_CONNECTED = 3001
    HARDWARE_INITIALIZATION_FAILED = 3002
    HARDWARE_CALIBRATION_FAILED = 3003
    HARDWARE_OVERLOAD = 3004
    HARDWARE_UNDERLOAD = 3005
    HARDWARE_UNSTABLE = 3006

    # Operation Errors
    OPERATION_ZERO_FAILED = 4001
    OPERATION_TARE_FAILED = 4002
    OPERATION_WEIGHT_OUT_OF_RANGE = 4003
    OPERATION_INVALID_UNIT = 4004
    OPERATION_SAMPLING_FAILED = 4005
    OPERATION_TIMEOUT = 4006

    # Data Errors
    DATA_CONVERSION_ERROR = 5001
    DATA_PARSING_ERROR = 5002
    DATA_VALIDATION_ERROR = 5003
    DATA_INVALID_FORMAT = 5004


class BS205Error(Exception):
    """Base BS205 LoadCell error"""

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


class BS205CommunicationError(BS205Error):
    """BS205 communication errors"""
    pass


class BS205HardwareError(BS205Error):
    """BS205 hardware errors"""
    pass


class BS205OperationError(BS205Error):
    """BS205 operation errors"""
    pass


class BS205DataError(BS205Error):
    """BS205 data processing errors"""
    pass


def validate_weight_range(weight_kg: float, min_weight: float = -500.0, max_weight: float = 500.0) -> None:
    """
    Validate weight measurement range

    Args:
        weight_kg: Weight value in kg to validate
        min_weight: Minimum allowed weight in kg
        max_weight: Maximum allowed weight in kg

    Raises:
        BS205OperationError: If weight is out of range
    """
    if not (min_weight <= weight_kg <= max_weight):
        raise BS205OperationError(
            f"Weight {weight_kg}kg is out of range [{min_weight}, {max_weight}]",
            error_code=int(BS205ErrorCode.OPERATION_WEIGHT_OUT_OF_RANGE)
        )


def validate_force_range(force_n: float, min_force: float = -4905.0, max_force: float = 4905.0) -> None:
    """
    Validate force measurement range

    Args:
        force_n: Force value in Newtons to validate
        min_force: Minimum allowed force in N
        max_force: Maximum allowed force in N

    Raises:
        BS205OperationError: If force is out of range
    """
    if not (min_force <= force_n <= max_force):
        raise BS205OperationError(
            f"Force {force_n}N is out of range [{min_force}, {max_force}]",
            error_code=int(BS205ErrorCode.OPERATION_WEIGHT_OUT_OF_RANGE)
        )


def validate_sample_parameters(count: int, interval_ms: int) -> None:
    """
    Validate sampling parameters

    Args:
        count: Number of samples
        interval_ms: Interval between samples in milliseconds

    Raises:
        BS205OperationError: If parameters are invalid
    """
    if count < 1:
        raise BS205OperationError(
            f"Sample count must be positive, got {count}",
            error_code=int(BS205ErrorCode.OPERATION_SAMPLING_FAILED)
        )

    if count > 1000:
        raise BS205OperationError(
            f"Sample count {count} exceeds maximum of 1000",
            error_code=int(BS205ErrorCode.OPERATION_SAMPLING_FAILED)
        )

    if interval_ms < 50:
        raise BS205OperationError(
            f"Sample interval {interval_ms}ms is too short, minimum is 50ms",
            error_code=int(BS205ErrorCode.OPERATION_SAMPLING_FAILED)
        )


def validate_unit(unit: str, supported_units: list[str]) -> None:
    """
    Validate measurement unit

    Args:
        unit: Unit string to validate
        supported_units: List of supported unit strings

    Raises:
        BS205OperationError: If unit is not supported
    """
    if unit not in supported_units:
        raise BS205OperationError(
            f"Unit '{unit}' not supported. Supported units: {supported_units}",
            error_code=int(BS205ErrorCode.OPERATION_INVALID_UNIT)
        )


def parse_weight_response(response: str) -> tuple[float, str]:
    """
    Parse weight response from BS205

    Args:
        response: Raw response string from device

    Returns:
        Tuple of (weight_value, unit)

    Raises:
        BS205DataError: If response cannot be parsed
    """
    if not response or not response.strip():
        raise BS205DataError(
            "Empty response from device",
            error_code=int(BS205ErrorCode.DATA_INVALID_FORMAT)
        )

    try:
        # Expected format: "R,+012.34,kg"
        parts = response.strip().split(',')
        if len(parts) < 3:
            raise BS205DataError(
                f"Invalid response format: expected 3 fields, got {len(parts)}",
                error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
                details=f"Response: {response}"
            )

        # Parse weight value (remove + sign and spaces)
        weight_str = parts[1].replace('+', '').replace(' ', '')
        try:
            weight_value = float(weight_str)
        except ValueError as e:
            raise BS205DataError(
                f"Cannot convert weight '{weight_str}' to float",
                error_code=int(BS205ErrorCode.DATA_CONVERSION_ERROR),
                details=str(e)
            )

        # Extract unit
        unit = parts[2].strip()

        return weight_value, unit

    except BS205DataError:
        raise
    except Exception as e:
        raise BS205DataError(
            f"Unexpected error parsing response: {response}",
            error_code=int(BS205ErrorCode.DATA_PARSING_ERROR),
            details=str(e)
        )


def convert_weight_to_force(weight_kg: float, gravity: float = 9.81) -> float:
    """
    Convert weight in kg to force in Newtons

    Args:
        weight_kg: Weight in kilograms
        gravity: Gravitational acceleration (default: 9.81 m/s²)

    Returns:
        Force in Newtons

    Raises:
        BS205DataError: If conversion fails
    """
    try:
        force_n = weight_kg * gravity
        return round(force_n, 3)  # Round to 3 decimal places
    except (TypeError, ValueError) as e:
        raise BS205DataError(
            f"Cannot convert weight {weight_kg}kg to force",
            error_code=int(BS205ErrorCode.DATA_CONVERSION_ERROR),
            details=str(e)
        )


# Error code to message mapping
ERROR_MESSAGES = {
    # Communication Errors
    BS205ErrorCode.COMM_TIMEOUT: "Communication timeout",
    BS205ErrorCode.COMM_SERIAL_ERROR: "Serial communication error",
    BS205ErrorCode.COMM_PORT_NOT_AVAILABLE: "Serial port not available",
    BS205ErrorCode.COMM_INVALID_RESPONSE: "Invalid response received",
    BS205ErrorCode.COMM_BUFFER_OVERFLOW: "Communication buffer overflow",

    # Protocol Errors
    BS205ErrorCode.PROTOCOL_INVALID_COMMAND: "Invalid command sent to device",
    BS205ErrorCode.PROTOCOL_MALFORMED_RESPONSE: "Malformed response from device",
    BS205ErrorCode.PROTOCOL_UNEXPECTED_RESPONSE: "Unexpected response from device",
    BS205ErrorCode.PROTOCOL_CHECKSUM_ERROR: "Response checksum error",

    # Hardware Errors
    BS205ErrorCode.HARDWARE_NOT_CONNECTED: "Device not connected",
    BS205ErrorCode.HARDWARE_INITIALIZATION_FAILED: "Device initialization failed",
    BS205ErrorCode.HARDWARE_CALIBRATION_FAILED: "Device calibration failed",
    BS205ErrorCode.HARDWARE_OVERLOAD: "Device overload detected",
    BS205ErrorCode.HARDWARE_UNDERLOAD: "Device underload detected",
    BS205ErrorCode.HARDWARE_UNSTABLE: "Device measurement unstable",

    # Operation Errors
    BS205ErrorCode.OPERATION_ZERO_FAILED: "Zero calibration failed",
    BS205ErrorCode.OPERATION_TARE_FAILED: "Tare operation failed",
    BS205ErrorCode.OPERATION_WEIGHT_OUT_OF_RANGE: "Weight measurement out of range",
    BS205ErrorCode.OPERATION_INVALID_UNIT: "Invalid measurement unit",
    BS205ErrorCode.OPERATION_SAMPLING_FAILED: "Sampling operation failed",
    BS205ErrorCode.OPERATION_TIMEOUT: "Operation timeout",

    # Data Errors
    BS205ErrorCode.DATA_CONVERSION_ERROR: "Data conversion error",
    BS205ErrorCode.DATA_PARSING_ERROR: "Data parsing error",
    BS205ErrorCode.DATA_VALIDATION_ERROR: "Data validation error",
    BS205ErrorCode.DATA_INVALID_FORMAT: "Invalid data format"
}


def get_error_message(error_code: BS205ErrorCode) -> str:
    """
    Get error message for error code

    Args:
        error_code: BS205 error code

    Returns:
        Human readable error message
    """
    return ERROR_MESSAGES.get(error_code, f"Unknown error code: {error_code}")
