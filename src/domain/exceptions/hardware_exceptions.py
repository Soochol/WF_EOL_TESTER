"""
Hardware-related Domain Exceptions

Contains exceptions related to hardware business rules and constraints.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Local application imports
from domain.exceptions.domain_exceptions import (
    DomainException,
)


class HardwareException(DomainException):
    """Base exception for hardware-related business rule violations"""

    def __init__(
        self,
        message: str,
        hardware_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware exception

        Args:
            message: Human-readable error message
            hardware_type: Type of hardware involved (e.g., 'robot', 'mcu', 'loadcell', 'power')
            details: Additional context about the hardware error
        """
        super().__init__(message, details)
        self.hardware_type = hardware_type


class HardwareNotReadyException(HardwareException):
    """Exception raised when hardware is not ready for operation according to business rules"""

    def __init__(
        self,
        message: str,
        hardware_type: Optional[str] = None,
        current_status: Optional[str] = None,
        required_status: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware not ready exception

        Args:
            message: Exception message
            hardware_type: Type of hardware (e.g., 'robot', 'mcu', 'loadcell', 'power')
            current_status: Current hardware status
            required_status: Required status for the operation
            operation: The operation that was attempted
            details: Additional hardware context
        """
        exception_details = details or {}

        if hardware_type:
            exception_details["hardware_type"] = hardware_type
        if current_status:
            exception_details["current_status"] = current_status
        if required_status:
            exception_details["required_status"] = required_status
        if operation:
            exception_details["operation"] = operation

        super().__init__(
            message,
            hardware_type or "unknown",
            exception_details,
        )
        self.current_status = current_status
        self.required_status = required_status
        self.operation = operation


class HardwareConnectionException(HardwareException):
    """Exception raised when hardware connection violates business rules"""

    def __init__(
        self,
        message: str,
        hardware_type: Optional[str] = None,
        connection_status: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware connection exception

        Args:
            message: Exception message
            hardware_type: Type of hardware (optional)
            connection_status: Current connection status (optional)
            operation: Operation that requires connection (optional)
            details: Additional connection context
        """
        exception_details = details or {}

        if hardware_type:
            exception_details["hardware_type"] = hardware_type
        if connection_status:
            exception_details["connection_status"] = connection_status
        if operation:
            exception_details["operation"] = operation

        super().__init__(
            message,
            hardware_type or "unknown",
            exception_details,
        )
        self.connection_status = connection_status
        self.operation = operation


class UnsafeOperationException(HardwareException):
    """Exception raised when an operation would violate safety business rules"""

    def __init__(
        self,
        operation: str,
        safety_violation: str,
        hardware_type: Optional[str] = None,
        current_value: Optional[Any] = None,
        safe_limit: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize unsafe operation exception

        Args:
            operation: The operation that would be unsafe
            safety_violation: Description of the safety rule violation
            hardware_type: Hardware involved in unsafe operation
            current_value: Current value that violates safety
            safe_limit: Safe limit that was exceeded
            details: Additional safety context
        """
        if current_value is not None and safe_limit is not None:
            message = f"Unsafe operation '{operation}': {safety_violation} (Current: {current_value}, Limit: {safe_limit})"
        else:
            message = f"Unsafe operation '{operation}': {safety_violation}"

        exception_details = details or {}
        exception_details.update(
            {
                "operation": operation,
                "safety_violation": safety_violation,
                "current_value": current_value,
                "safe_limit": safe_limit,
            }
        )

        super().__init__(message, hardware_type, exception_details)
        self.operation = operation
        self.safety_violation = safety_violation
        self.current_value = current_value
        self.safe_limit = safe_limit


class HardwareCalibrationException(HardwareException):
    """Exception raised when hardware calibration violates business rules"""

    def __init__(
        self,
        hardware_type: str,
        calibration_issue: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware calibration exception

        Args:
            hardware_type: Type of hardware with calibration issue
            calibration_issue: Description of calibration problem
            operation: Operation that requires proper calibration
            details: Additional calibration context
        """
        if operation:
            message = f"Hardware '{hardware_type}' calibration issue for '{operation}': {calibration_issue}"
        else:
            message = f"Hardware '{hardware_type}' calibration issue: {calibration_issue}"

        exception_details = details or {}
        exception_details.update(
            {
                "calibration_issue": calibration_issue,
                "operation": operation,
            }
        )

        super().__init__(message, hardware_type, exception_details)
        self.calibration_issue = calibration_issue
        self.operation = operation


class HardwareTimeoutException(HardwareException):
    """Exception raised when hardware operation times out violating business rules"""

    def __init__(
        self,
        hardware_type: str,
        operation: str,
        timeout_seconds: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware timeout exception

        Args:
            hardware_type: Type of hardware that timed out
            operation: Operation that timed out
            timeout_seconds: Timeout duration in seconds
            details: Additional timeout context
        """
        message = f"Hardware '{hardware_type}' timeout during '{operation}' after {timeout_seconds} seconds"

        exception_details = details or {}
        exception_details.update(
            {
                "operation": operation,
                "timeout_seconds": timeout_seconds,
            }
        )

        super().__init__(message, hardware_type, exception_details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class HardwareLimitExceededException(HardwareException):
    """Exception raised when hardware limits are exceeded violating business rules"""

    def __init__(
        self,
        hardware_type: str,
        limit_type: str,
        current_value: float,
        limit_value: float,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize hardware limit exceeded exception

        Args:
            hardware_type: Type of hardware
            limit_type: Type of limit exceeded (e.g., 'temperature', 'force', 'voltage')
            current_value: Current value that exceeded limit
            limit_value: The limit that was exceeded
            operation: Operation during which limit was exceeded
            details: Additional limit context
        """
        if operation:
            message = f"Hardware '{hardware_type}' {limit_type} limit exceeded during '{operation}': {current_value} > {limit_value}"
        else:
            message = f"Hardware '{hardware_type}' {limit_type} limit exceeded: {current_value} > {limit_value}"

        exception_details = details or {}
        exception_details.update(
            {
                "limit_type": limit_type,
                "current_value": current_value,
                "limit_value": limit_value,
                "operation": operation,
            }
        )

        super().__init__(message, hardware_type, exception_details)
        self.limit_type = limit_type
        self.current_value = current_value
        self.limit_value = limit_value
        self.operation = operation
