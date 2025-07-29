"""
LMA MCU Controller Error Codes and Handling

This module defines error codes and error handling utilities for LMA MCU controllers.
"""

from enum import IntEnum


class LMAErrorCode(IntEnum):
    """LMA specific error codes"""
    # Communication Errors
    COMM_TIMEOUT = 1001
    COMM_FRAME_ERROR = 1002
    COMM_CHECKSUM_ERROR = 1003
    COMM_BUFFER_OVERFLOW = 1004
    COMM_SERIAL_ERROR = 1005

    # Protocol Errors
    PROTOCOL_INVALID_COMMAND = 2001
    PROTOCOL_INVALID_DATA = 2002
    PROTOCOL_FRAME_TOO_LONG = 2003
    PROTOCOL_UNEXPECTED_RESPONSE = 2004

    # Hardware Errors
    HARDWARE_NOT_CONNECTED = 3001
    HARDWARE_INITIALIZATION_FAILED = 3002
    HARDWARE_TEMPERATURE_FAULT = 3003
    HARDWARE_FAN_FAULT = 3004
    HARDWARE_POWER_FAULT = 3005

    # Operation Errors
    OPERATION_INVALID_PARAMETER = 4001
    OPERATION_INVALID_MODE = 4002
    OPERATION_TEMPERATURE_OUT_OF_RANGE = 4003
    OPERATION_FAN_SPEED_OUT_OF_RANGE = 4004
    OPERATION_TIMEOUT = 4005
    OPERATION_FAILED = 4006

    # Safety Errors
    SAFETY_OVER_TEMPERATURE = 5001
    SAFETY_UNDER_TEMPERATURE = 5002
    SAFETY_THERMAL_RUNAWAY = 5003
    SAFETY_EMERGENCY_STOP = 5004


class LMAError(Exception):
    """Base LMA MCU error"""

    def __init__(self, message: str, error_code: int = 0, details: str = None):
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


class LMACommunicationError(LMAError):
    """LMA communication errors"""
    pass


class LMAHardwareError(LMAError):
    """LMA hardware errors"""
    pass


class LMAOperationError(LMAError):
    """LMA operation errors"""
    pass


def validate_temperature(temperature: float, min_temp: float = -40.0, max_temp: float = 150.0) -> None:
    """
    Validate temperature range

    Args:
        temperature: Temperature to validate
        min_temp: Minimum allowed temperature
        max_temp: Maximum allowed temperature

    Raises:
        LMAOperationError: If temperature is out of range
    """
    if not (min_temp <= temperature <= max_temp):
        raise LMAOperationError(
            f"Temperature {temperature}°C is out of range [{min_temp}, {max_temp}]",
            error_code=int(LMAErrorCode.OPERATION_TEMPERATURE_OUT_OF_RANGE)
        )


def validate_fan_speed(fan_speed: int, min_speed: int = 1, max_speed: int = 10) -> None:
    """
    Validate fan speed range

    Args:
        fan_speed: Fan speed to validate
        min_speed: Minimum allowed fan speed
        max_speed: Maximum allowed fan speed

    Raises:
        LMAOperationError: If fan speed is out of range
    """
    if not (min_speed <= fan_speed <= max_speed):
        raise LMAOperationError(
            f"Fan speed {fan_speed} is out of range [{min_speed}, {max_speed}]",
            error_code=int(LMAErrorCode.OPERATION_FAN_SPEED_OUT_OF_RANGE)
        )
