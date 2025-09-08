"""
Time-related Value Objects

Immutable value objects representing time measurements and timestamps.
"""

# Standard library imports
from datetime import datetime, timezone
import time
from typing import Union

# Local application imports
from domain.exceptions.validation_exceptions import (
    InvalidRangeException,
    ValidationException,
)


class Timestamp:
    """Immutable timestamp value object"""

    def __init__(self, value: Union[float, datetime]):
        """
        Initialize timestamp

        Args:
            value: Unix timestamp (float) or datetime object

        Raises:
            ValidationException: If timestamp is invalid
        """
        if isinstance(value, datetime):
            # Convert datetime to UTC timestamp
            if value.tzinfo is None:
                # Assume local timezone if not specified
                value = value.replace(tzinfo=timezone.utc)
            self._timestamp = value.timestamp()
        elif isinstance(value, (int, float)):
            # Validate timestamp range (reasonable bounds)
            if not (0 <= value <= 4102444800):  # 1970-2100 range
                raise InvalidRangeException(
                    "timestamp",
                    value,
                    0,
                    4102444800,
                    {"range_description": "Unix timestamp between 1970 and 2100"},
                )
            self._timestamp = float(value)
        else:
            raise ValidationException(
                "timestamp",
                value,
                "Timestamp must be float or datetime",
            )

    @property
    def value(self) -> float:
        """Get Unix timestamp value"""
        return self._timestamp

    @property
    def datetime(self) -> datetime:
        """Get datetime representation (UTC)"""
        return datetime.fromtimestamp(self._timestamp, tz=timezone.utc)

    @classmethod
    def now(cls) -> "Timestamp":
        """Create timestamp for current time"""
        return cls(time.time())

    @classmethod
    def from_iso(cls, iso_string: str) -> "Timestamp":
        """Create timestamp from ISO format string"""
        try:
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            return cls(dt)
        except ValueError as e:
            raise ValidationException(
                "iso_timestamp",
                iso_string,
                f"Invalid ISO timestamp format: {e}",
            ) from e

    def to_iso(self) -> str:
        """Convert to ISO format string"""
        return self.datetime.isoformat()

    def __str__(self) -> str:
        return self.to_iso()

    def __repr__(self) -> str:
        return f"Timestamp({self._timestamp})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Timestamp):
            return False
        return abs(self._timestamp - other._timestamp) < 1e-6  # Microsecond precision

    def __hash__(self) -> int:
        return hash(round(self._timestamp, 6))

    def __lt__(self, other) -> bool:
        if not isinstance(other, Timestamp):
            raise TypeError(f"Cannot compare Timestamp with {type(other).__name__}")
        return self._timestamp < other._timestamp

    def __le__(self, other) -> bool:
        return bool(self < other or self == other)

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other


class TestDuration:
    """Test execution duration value object"""

    def __init__(self, seconds: Union[int, float]):
        """
        Initialize test duration

        Args:
            seconds: Duration in seconds

        Raises:
            ValidationException: If duration is invalid
        """
        if not isinstance(seconds, (int, float)):
            raise ValidationException(
                "duration",
                seconds,
                "Duration must be numeric",
            )

        if seconds < 0:
            raise InvalidRangeException(
                "duration",
                seconds,
                0,
                float("inf"),
                {"constraint": "Duration cannot be negative"},
            )

        # Reasonable upper bound for test duration (24 hours)
        if seconds > 86400:
            raise InvalidRangeException(
                "duration",
                seconds,
                0,
                86400,
                {"constraint": "Duration cannot exceed 24 hours"},
            )

        self._seconds = float(seconds)

    @property
    def seconds(self) -> float:
        """Get duration in seconds"""
        return self._seconds

    @property
    def milliseconds(self) -> float:
        """Get duration in milliseconds"""
        return self._seconds * 1000.0

    @property
    def minutes(self) -> float:
        """Get duration in minutes"""
        return self._seconds / 60.0

    @property
    def hours(self) -> float:
        """Get duration in hours"""
        return self._seconds / 3600.0

    @classmethod
    def from_milliseconds(cls, milliseconds: Union[int, float]) -> "TestDuration":
        """Create duration from milliseconds"""
        return cls(milliseconds / 1000.0)

    @classmethod
    def from_minutes(cls, minutes: Union[int, float]) -> "TestDuration":
        """Create duration from minutes"""
        return cls(minutes * 60.0)

    @classmethod
    def from_seconds(cls, seconds: Union[int, float]) -> "TestDuration":
        """Create duration from seconds"""
        return cls(seconds)

    @classmethod
    def between_timestamps(cls, start: Timestamp, end: Timestamp) -> "TestDuration":
        """Create duration between two timestamps"""
        if end < start:
            raise ValidationException(
                "duration_calculation",
                (start, end),
                "End timestamp must be after start timestamp",
            )
        return cls(end.value - start.value)

    def format_human_readable(self) -> str:
        """Format duration in human-readable format"""
        if self._seconds < 1:
            return f"{self.milliseconds:.0f}ms"
        if self._seconds < 60:
            return f"{self._seconds:.1f}s"
        if self._seconds < 3600:
            minutes = int(self._seconds // 60)
            seconds = self._seconds % 60
            return f"{minutes}m {seconds:.1f}s"
        hours = int(self._seconds // 3600)
        minutes = int((self._seconds % 3600) // 60)
        seconds = self._seconds % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"

    def __str__(self) -> str:
        return self.format_human_readable()

    def __repr__(self) -> str:
        return f"TestDuration({self._seconds})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, TestDuration):
            return False
        return abs(self._seconds - other._seconds) < 1e-6

    def __hash__(self) -> int:
        return hash(round(self._seconds, 6))

    def __lt__(self, other) -> bool:
        if not isinstance(other, TestDuration):
            raise TypeError(f"Cannot compare TestDuration with {type(other).__name__}")
        return self._seconds < other._seconds

    def __le__(self, other) -> bool:
        return bool(self < other or self == other)

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other

    def __add__(self, other) -> "TestDuration":
        if not isinstance(other, TestDuration):
            raise TypeError(f"Cannot add TestDuration with {type(other).__name__}")
        return TestDuration(self._seconds + other._seconds)

    def __sub__(self, other) -> "TestDuration":
        if not isinstance(other, TestDuration):
            raise TypeError(f"Cannot subtract {type(other).__name__} from TestDuration")
        result_seconds = self._seconds - other._seconds
        if result_seconds < 0:
            raise ValidationException(
                "duration_subtraction",
                result_seconds,
                "Duration subtraction cannot result in negative duration",
            )
        return TestDuration(result_seconds)
