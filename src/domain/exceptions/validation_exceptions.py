"""
Validation Exceptions

Contains exceptions related to domain object validation and constraints.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Local application imports
from domain.exceptions.domain_exceptions import (
    DomainException,
)


class ValidationException(DomainException):
    """Exception raised when domain object validation fails"""

    def __init__(
        self,
        field_name: str,
        value,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize validation exception

        Args:
            field_name: Name of the field that failed validation
            value: The invalid value
            message: Description of validation failure
            details: Additional validation context
        """
        super().__init__(message, details)
        self.field_name = field_name
        self.value = value


class InvalidRangeException(ValidationException):
    """Exception raised when a value is outside acceptable range"""

    def __init__(
        self,
        field_name: str,
        value,
        min_value,
        max_value,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize range validation exception

        Args:
            field_name: Name of the field with invalid range
            value: The value that's out of range
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
            details: Additional context
        """
        message = (
            f"{field_name} value {value} is outside acceptable range [{min_value}, {max_value}]"
        )
        details = details or {}
        details.update(
            {
                "min_value": min_value,
                "max_value": max_value,
                "actual_value": value,
            }
        )
        super().__init__(field_name, value, message, details)
        self.min_value = min_value
        self.max_value = max_value


class InvalidFormatException(ValidationException):
    """Exception raised when a value has invalid format"""

    def __init__(
        self,
        field_name: str,
        value,
        expected_format: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize format validation exception

        Args:
            field_name: Name of the field with invalid format
            value: The value with invalid format
            expected_format: Description of expected format
            details: Additional context
        """
        message = f"{field_name} value '{value}' has invalid format. Expected: {expected_format}"
        details = details or {}
        details.update(
            {
                "expected_format": expected_format,
                "actual_value": str(value),
            }
        )
        super().__init__(field_name, value, message, details)
