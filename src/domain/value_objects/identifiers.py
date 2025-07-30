"""
Domain Identifiers

Immutable value objects that represent unique identifiers in the domain.
"""

import re
import uuid
from datetime import datetime
from typing import Union, Optional

from domain.exceptions.validation_exceptions import (
    InvalidFormatException,
    ValidationException,
)


class BaseId:
    """Base class for domain identifiers"""

    def __init__(self, value: Union[str, uuid.UUID]):
        """
        Initialize identifier

        Args:
            value: The identifier value (string or UUID)

        Raises:
            ValidationException: If value is invalid
        """
        if isinstance(value, uuid.UUID):
            self._value = str(value)
        elif isinstance(value, str):
            self._validate_string_format(value)
            self._value = value.strip()
        else:
            raise ValidationException(
                "identifier",
                value,
                "Identifier must be string or UUID",
            )

    def _validate_string_format(self, value: str) -> None:
        """Validate string format - override in subclasses"""
        if not value or not value.strip():
            raise ValidationException(
                "identifier",
                value,
                "Identifier cannot be empty",
            )

    @property
    def value(self) -> str:
        """Get identifier value"""
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._value}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self._value))


class TestId(BaseId):
    """Unique identifier for EOL tests"""

    def _validate_string_format(self, value: str) -> None:
        super()._validate_string_format(value)

        # Test ID format: SerialNumber_YYYYMMDD_HHMMSS_XXX, TEST_YYYYMMDD_HHMMSS_XXX, or UUID
        test_id_pattern = r"^([A-Za-z0-9]+_\d{8}_\d{6}_\d{3}|TEST_\d{8}_\d{6}_\d{3}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$"

        if not re.match(test_id_pattern, value.strip()):
            raise InvalidFormatException(
                "test_id",
                value,
                "SerialNumber_YYYYMMDD_HHMMSS_XXX, TEST_YYYYMMDD_HHMMSS_XXX, or UUID format",
            )

    @classmethod
    def generate(cls) -> "TestId":
        """Generate a new random test ID using UUID format"""
        return cls(str(uuid.uuid4()))

    @classmethod
    def generate_from_serial_datetime(
        cls,
        serial_number: str,
        timestamp: Optional[datetime] = None,
        sequence: Optional[int] = None
    ) -> "TestId":
        """
        Generate a new test ID using serial number and datetime format

        Args:
            serial_number: DUT serial number
            timestamp: Test timestamp (defaults to now)
            sequence: Sequence number for duplicates (defaults to 001)

        Returns:
            TestId in format: SerialNumber_YYYYMMDD_HHMMSS_XXX
        """
        if timestamp is None:
            timestamp = datetime.now()

        if sequence is None:
            sequence = 1

        # Clean serial number to ensure it's alphanumeric
        clean_serial = re.sub(r'[^A-Za-z0-9]', '', serial_number)
        if not clean_serial:
            clean_serial = "UNKNOWN"

        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")
        seq_str = f"{sequence:03d}"

        test_id_str = f"{clean_serial}_{date_str}_{time_str}_{seq_str}"
        return cls(test_id_str)

    @classmethod
    def from_timestamp(
        cls, timestamp_suffix: str
    ) -> "TestId":
        """Create test ID with timestamp format"""
        # This would typically use current datetime, simplified for now
        return cls(f"TEST_{timestamp_suffix}")


class DUTId(BaseId):
    """Device Under Test identifier"""

    def _validate_string_format(self, value: str) -> None:
        super()._validate_string_format(value)

        # DUT ID format: alphanumeric, hyphens, underscores allowed
        # Length: 3-50 characters
        if (
            len(value.strip()) < 3
            or len(value.strip()) > 50
        ):
            raise ValidationException(
                "dut_id",
                value,
                "DUT ID must be between 3 and 50 characters",
            )

        dut_id_pattern = r"^[A-Za-z0-9_-]+$"
        if not re.match(dut_id_pattern, value.strip()):
            raise InvalidFormatException(
                "dut_id",
                value,
                "alphanumeric characters, hyphens, and underscores only",
            )


class OperatorId(BaseId):
    """Test operator identifier"""

    def _validate_string_format(self, value: str) -> None:
        super()._validate_string_format(value)

        # Operator ID format: alphanumeric, dots, hyphens, underscores
        # Length: 2-30 characters
        if (
            len(value.strip()) < 2
            or len(value.strip()) > 30
        ):
            raise ValidationException(
                "operator_id",
                value,
                "Operator ID must be between 2 and 30 characters",
            )

        operator_id_pattern = r"^[A-Za-z0-9._-]+$"
        if not re.match(operator_id_pattern, value.strip()):
            raise InvalidFormatException(
                "operator_id",
                value,
                "alphanumeric characters, dots, hyphens, and underscores only",
            )


class MeasurementId(BaseId):
    """Measurement record identifier"""

    def _validate_string_format(self, value: str) -> None:
        super()._validate_string_format(value)

        # Measurement ID can be UUID or sequential format
        uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        sequential_pattern = (
            r"^M\d{10}$"  # M followed by 10 digits
        )

        if not (
            re.match(uuid_pattern, value.strip())
            or re.match(sequential_pattern, value.strip())
        ):
            raise InvalidFormatException(
                "measurement_id",
                value,
                "UUID format or M followed by 10 digits (e.g., M0000000001)",
            )

    @classmethod
    def generate(cls) -> "MeasurementId":
        """Generate a new random measurement ID"""
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_sequence(
        cls, sequence: int
    ) -> "MeasurementId":
        """Create measurement ID from sequence number"""
        return cls(f"M{sequence:010d}")
