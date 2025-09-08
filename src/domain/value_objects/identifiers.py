"""
Domain Identifiers

Immutable value objects that represent unique identifiers in the domain.
Provides type-safe identifier handling with validation, formatting,
and generation capabilities for various domain entities.
"""

# Standard library imports
from datetime import datetime, timezone
import re
from typing import Optional, Union
import uuid

# Local application imports
from domain.exceptions.validation_exceptions import (
    InvalidFormatException,
    ValidationException,
)


class BaseId:
    """
    Base class for domain identifiers

    Provides common functionality for all identifier types including
    validation, string handling, and standardized representation.
    All domain identifier classes inherit from this base.
    """

    def __init__(self, value: Union[str, uuid.UUID]) -> None:
        """
        Initialize identifier with validation

        Args:
            value: The identifier value (string or UUID)

        Raises:
            ValidationException: If value is invalid or empty
        """
        self._validate_input_type(value)

        if isinstance(value, uuid.UUID):
            self._value = str(value)
        elif isinstance(value, str):
            self._validate_string_format(value)
            self._value = value.strip()

    def _validate_input_type(self, value: Union[str, uuid.UUID]) -> None:
        """Validate input type"""
        if not isinstance(value, (str, uuid.UUID)):
            raise ValidationException(
                "identifier",
                value,
                "Identifier must be string or UUID",
            )

    def _validate_string_format(self, value: str) -> None:
        """Validate string format - override in subclasses

        Args:
            value: String value to validate

        Raises:
            ValidationException: If string is empty or invalid
        """
        if not value or not value.strip():
            raise ValidationException(
                "identifier",
                value,
                "Identifier cannot be empty",
            )

        if len(value.strip()) > 100:  # Reasonable maximum length
            raise ValidationException(
                "identifier",
                value,
                "Identifier cannot exceed 100 characters",
            )

    @property
    def value(self) -> str:
        """Get identifier value

        Returns:
            String representation of the identifier
        """
        return self._value

    def __str__(self) -> str:
        """String representation"""
        return self._value

    def __repr__(self) -> str:
        """Debug representation"""
        return f"{self.__class__.__name__}('{self._value}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another identifier"""
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Make identifier hashable for use in sets and as dict keys"""
        return hash((self.__class__.__name__, self._value))

    def is_valid(self) -> bool:
        """Check if identifier is valid

        Returns:
            True if identifier passes all validation rules
        """
        try:
            self._validate_string_format(self._value)
            return True
        except (ValidationException, InvalidFormatException):
            return False

    def is_uuid_format(self) -> bool:
        """Check if identifier is in UUID format

        Returns:
            True if identifier matches UUID pattern
        """
        uuid_pattern = (
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        return bool(re.match(uuid_pattern, self._value))

    def get_length(self) -> int:
        """Get identifier length

        Returns:
            Number of characters in identifier
        """
        return len(self._value)


class TestId(BaseId):
    """
    Unique identifier for EOL tests

    Supports multiple formats:
    - SerialNumber_YYYYMMDD_HHMMSS_XXX (e.g., ABC123_20240115_143052_001)
    - TEST_YYYYMMDD_HHMMSS_XXX (e.g., TEST_20240115_143052_001)
    - UUID format (e.g., 550e8400-e29b-41d4-a716-446655440000)
    """

    def _validate_string_format(self, value: str) -> None:
        """Validate test ID format"""
        super()._validate_string_format(value)

        # Test ID format patterns
        serial_pattern = r"^[A-Za-z0-9]+_\d{8}_\d{6}_\d{3}$"  # SerialNumber_YYYYMMDD_HHMMSS_XXX
        test_pattern = r"^TEST_\d{8}_\d{6}_\d{3}$"  # TEST_YYYYMMDD_HHMMSS_XXX
        uuid_pattern = (
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )

        value_stripped = value.strip()
        if not (
            re.match(serial_pattern, value_stripped)
            or re.match(test_pattern, value_stripped)
            or re.match(uuid_pattern, value_stripped)
        ):
            raise InvalidFormatException(
                "test_id",
                value,
                "Must be SerialNumber_YYYYMMDD_HHMMSS_XXX, TEST_YYYYMMDD_HHMMSS_XXX, or UUID format",
            )

    @classmethod
    def generate(cls) -> "TestId":
        """Generate a new random test ID using UUID format

        Returns:
            TestId with UUID format
        """
        return cls(str(uuid.uuid4()))

    @classmethod
    def generate_from_serial_datetime(
        cls,
        serial_number: str,
        timestamp: Optional[datetime] = None,
        sequence: Optional[int] = None,
    ) -> "TestId":
        """
        Generate a new test ID using serial number and datetime format

        Args:
            serial_number: DUT serial number
            timestamp: Test timestamp (defaults to now)
            sequence: Sequence number for duplicates (defaults to 001)

        Returns:
            TestId in format: SerialNumber_YYYYMMDD_HHMMSS_XXX

        Raises:
            ValidationException: If serial number is invalid
        """
        if not serial_number or not serial_number.strip():
            raise ValidationException(
                "serial_number",
                serial_number,
                "Serial number cannot be empty",
            )

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if sequence is None:
            sequence = 1

        if not (1 <= sequence <= 999):
            raise ValidationException(
                "sequence",
                sequence,
                "Sequence must be between 1 and 999",
            )

        # Clean serial number to ensure it's alphanumeric
        clean_serial = re.sub(r"[^A-Za-z0-9]", "", serial_number)
        if not clean_serial:
            clean_serial = "UNKNOWN"

        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")
        seq_str = f"{sequence:03d}"

        test_id_str = f"{clean_serial}_{date_str}_{time_str}_{seq_str}"
        return cls(test_id_str)

    @classmethod
    def generate_standard(
        cls, timestamp: Optional[datetime] = None, sequence: Optional[int] = None
    ) -> "TestId":
        """Generate standard format test ID (TEST_YYYYMMDD_HHMMSS_XXX)

        Args:
            timestamp: Test timestamp (defaults to now)
            sequence: Sequence number (defaults to 001)

        Returns:
            TestId in standard TEST format
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        if sequence is None:
            sequence = 1

        if not (1 <= sequence <= 999):
            raise ValidationException(
                "sequence",
                sequence,
                "Sequence must be between 1 and 999",
            )

        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")
        seq_str = f"{sequence:03d}"

        test_id_str = f"TEST_{date_str}_{time_str}_{seq_str}"
        return cls(test_id_str)

    def extract_timestamp(self) -> Optional[datetime]:
        """Extract timestamp from test ID if in datetime format

        Returns:
            Datetime object if ID contains timestamp, None for UUID format
        """
        # Pattern to match datetime in test ID
        datetime_pattern = r"_(?P<date>\d{8})_(?P<time>\d{6})_"
        match = re.search(datetime_pattern, self._value)

        if match:
            date_str = match.group("date")
            time_str = match.group("time")
            try:
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        return None

    def extract_serial_number(self) -> Optional[str]:
        """Extract serial number from test ID if in serial format

        Returns:
            Serial number if ID contains one, None otherwise
        """
        # Pattern to match serial number format
        serial_pattern = r"^(?P<serial>[A-Za-z0-9]+)_\d{8}_\d{6}_\d{3}$"
        match = re.match(serial_pattern, self._value)

        if match:
            return match.group("serial")

        return None


class DUTId(BaseId):
    """
    Device Under Test identifier

    Supports alphanumeric characters, hyphens, and underscores.
    Length must be between 3 and 50 characters.
    Examples: ABC-123, WF_001, TEST_DEVICE_001
    """

    def _validate_string_format(self, value: str) -> None:
        """Validate DUT ID format"""
        super()._validate_string_format(value)

        value_stripped = value.strip()

        # Length validation
        if len(value_stripped) < 3 or len(value_stripped) > 50:
            raise ValidationException(
                "dut_id",
                value,
                "DUT ID must be between 3 and 50 characters",
            )

        # Format validation
        dut_id_pattern = r"^[A-Za-z0-9_-]+$"
        if not re.match(dut_id_pattern, value_stripped):
            raise InvalidFormatException(
                "dut_id",
                value,
                "Only alphanumeric characters, hyphens, and underscores allowed",
            )

        # Must start with alphanumeric character
        if not value_stripped[0].isalnum():
            raise InvalidFormatException(
                "dut_id",
                value,
                "DUT ID must start with an alphanumeric character",
            )


class OperatorId(BaseId):
    """
    Test operator identifier

    Supports alphanumeric characters, dots, hyphens, and underscores.
    Length must be between 2 and 30 characters.
    Examples: john.doe, operator_01, test-user
    """

    def _validate_string_format(self, value: str) -> None:
        """Validate operator ID format"""
        super()._validate_string_format(value)

        value_stripped = value.strip()

        # Length validation
        if len(value_stripped) < 2 or len(value_stripped) > 30:
            raise ValidationException(
                "operator_id",
                value,
                "Operator ID must be between 2 and 30 characters",
            )

        # Format validation
        operator_id_pattern = r"^[A-Za-z0-9._-]+$"
        if not re.match(operator_id_pattern, value_stripped):
            raise InvalidFormatException(
                "operator_id",
                value,
                "Only alphanumeric characters, dots, hyphens, and underscores allowed",
            )

        # Must start with alphanumeric character
        if not value_stripped[0].isalnum():
            raise InvalidFormatException(
                "operator_id",
                value,
                "Operator ID must start with an alphanumeric character",
            )

        # Cannot end with special characters
        if value_stripped[-1] in "._-":
            raise InvalidFormatException(
                "operator_id",
                value,
                "Operator ID cannot end with special characters",
            )


class MeasurementId(BaseId):
    """
    Measurement record identifier

    Supports two formats:
    - UUID format (e.g., 550e8400-e29b-41d4-a716-446655440000)
    - Sequential format: M followed by 10 digits (e.g., M0000000001)
    """

    def _validate_string_format(self, value: str) -> None:
        """Validate measurement ID format"""
        super()._validate_string_format(value)

        value_stripped = value.strip()

        # Measurement ID can be UUID or sequential format
        uuid_pattern = (
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        sequential_pattern = r"^M\d{10}$"  # M followed by 10 digits

        if not (
            re.match(uuid_pattern, value_stripped) or re.match(sequential_pattern, value_stripped)
        ):
            raise InvalidFormatException(
                "measurement_id",
                value,
                "Must be UUID format or M followed by 10 digits (e.g., M0000000001)",
            )

    @classmethod
    def generate(cls) -> "MeasurementId":
        """Generate a new random measurement ID using UUID format

        Returns:
            MeasurementId with UUID format
        """
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_sequence(cls, sequence: int) -> "MeasurementId":
        """Create measurement ID from sequence number

        Args:
            sequence: Sequence number (0-9999999999)

        Returns:
            MeasurementId in sequential format

        Raises:
            ValidationException: If sequence is out of range
        """
        if not (0 <= sequence <= 9999999999):
            raise ValidationException(
                "sequence",
                sequence,
                "Sequence must be between 0 and 9999999999",
            )
        return cls(f"M{sequence:010d}")

    def extract_sequence(self) -> Optional[int]:
        """Extract sequence number from measurement ID if in sequential format

        Returns:
            Sequence number if ID is in sequential format, None for UUID
        """
        sequential_pattern = r"^M(\d{10})$"
        match = re.match(sequential_pattern, self._value)

        if match:
            return int(match.group(1))

        return None

    def is_sequential_format(self) -> bool:
        """Check if measurement ID is in sequential format

        Returns:
            True if ID is in M followed by digits format
        """
        sequential_pattern = r"^M\d{10}$"
        return bool(re.match(sequential_pattern, self._value))
