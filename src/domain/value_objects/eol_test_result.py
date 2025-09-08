"""
EOL Test Result

Immutable value object representing the complete result of an EOL test execution.
Contains test outcome, measurements, timing information, and metadata.
"""

# Standard library imports
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Local application imports
from application.use_cases.common.command_result_patterns import BaseResult
from domain.enums.test_status import TestStatus
from domain.exceptions.validation_exceptions import ValidationException
from domain.value_objects.identifiers import MeasurementId, TestId
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.time_values import TestDuration


class EOLTestResult(BaseResult):
    """
    EOL test execution result value object

    Immutable value object representing the complete outcome of an EOL test.
    Contains test identification, execution status, measurement data, timing
    information, and any relevant metadata or error information.

    The result distinguishes between:
    - Test execution success/failure (technical execution)
    - Device pass/fail status (test criteria evaluation)
    """

    def __init__(
        self,
        test_id: TestId,
        test_status: TestStatus,
        is_passed: bool,
        error_message: Optional[str] = None,
        execution_duration: Optional[TestDuration] = None,
        completed_at: Optional[datetime] = None,
        measurement_ids: Optional[List[MeasurementId]] = None,
        test_summary: Optional[Union[TestMeasurements, Dict[str, Any]]] = None,
        operator_notes: Optional[str] = None,
    ):
        """
        Initialize EOL test result

        Args:
            test_id: Unique test identifier
            test_status: Execution status
            is_passed: Whether device passed test criteria
            error_message: Error details if failed
            execution_duration: Test execution time
            completed_at: Test completion timestamp
            measurement_ids: Individual measurement IDs
            test_summary: Measurement data
            operator_notes: Manual operator notes
        """
        # Initialize BaseResult
        is_success = test_status in (TestStatus.COMPLETED, TestStatus.FAILED)
        super().__init__(
            test_status=test_status,
            is_success=is_success,
            error_message=error_message,
            test_id=test_id,
            execution_duration=execution_duration,
        )

        # Store EOL-specific fields
        self._is_passed = is_passed
        self._completed_at = completed_at
        self._measurement_ids = measurement_ids or []
        self._test_summary = test_summary
        self._operator_notes = operator_notes

        self._validate_test_data_consistency()
        self._validate_measurement_data()
        self._validate_optional_fields()

    @property
    def is_passed(self) -> bool:
        """Whether device passed test criteria"""
        return self._is_passed

    @property
    def completed_at(self) -> Optional[datetime]:
        """Test completion timestamp"""
        return self._completed_at

    @property
    def measurement_ids(self) -> List[MeasurementId]:
        """Individual measurement IDs"""
        return self._measurement_ids

    @property
    def test_summary(self) -> Optional[Union[TestMeasurements, Dict[str, Any]]]:
        """Measurement data"""
        return self._test_summary

    @property
    def operator_notes(self) -> Optional[str]:
        """Manual operator notes"""
        return self._operator_notes

    def _validate_test_data_consistency(self) -> None:
        """Validate consistency between test status and other fields"""
        # Error cases should have error messages
        if self.test_status == TestStatus.ERROR and not self.error_message:
            raise ValidationException(
                "error_message",
                self.error_message,
                "Error message is required when test status is ERROR",
            )

        # Completed tests should have measurements (unless it's a dry run)
        if (
            self.test_status == TestStatus.COMPLETED
            and not self.measurement_ids
            and self.test_summary is None
        ):
            raise ValidationException(
                "measurements",
                None,
                "Completed tests should have measurement data",
            )

        # Failed execution tests cannot be marked as passed
        if self.is_failed_execution and self.is_passed:
            raise ValidationException(
                "is_passed",
                self.is_passed,
                "Failed execution tests cannot be marked as passed",
            )

    def _validate_measurement_data(self) -> None:
        """Validate measurement-related data"""
        # All measurement IDs must be valid
        for i, mid in enumerate(self.measurement_ids):
            if not isinstance(mid, MeasurementId):
                raise ValidationException(
                    f"measurement_ids[{i}]",
                    mid,
                    "All measurement IDs must be MeasurementId instances",
                )

        # Check for duplicate measurement IDs
        if len(self.measurement_ids) != len(set(self.measurement_ids)):
            raise ValidationException(
                "measurement_ids",
                self.measurement_ids,
                "Duplicate measurement IDs are not allowed",
            )

    def _validate_optional_fields(self) -> None:
        """Validate optional string fields"""
        if self.error_message is not None and len(self.error_message) > 1000:
            raise ValidationException(
                "error_message",
                self.error_message,
                "Error message cannot exceed 1000 characters",
            )

        if self.operator_notes is not None and len(self.operator_notes) > 2000:
            raise ValidationException(
                "operator_notes",
                self.operator_notes,
                "Operator notes cannot exceed 2000 characters",
            )

    @property
    def is_successful(self) -> bool:
        """Check if test execution was successful (regardless of device pass/fail)

        Returns:
            True if test executed successfully (COMPLETED or FAILED status)
        """
        return self.test_status in (TestStatus.COMPLETED, TestStatus.FAILED)

    @property
    def is_success(self) -> bool:
        """BaseResult compatibility property - same as is_successful

        Returns:
            True if test executed successfully (COMPLETED or FAILED status)
        """
        return self.is_successful

    @property
    def is_failed_execution(self) -> bool:
        """Check if test execution failed (technical failure, not device failure)

        Returns:
            True if test execution encountered errors or was cancelled
        """
        return self.test_status in (TestStatus.ERROR, TestStatus.CANCELLED)

    @property
    def is_device_passed(self) -> bool:
        """Check if device passed the test criteria

        Returns:
            True if device met all test criteria (only valid for successful execution)
        """
        return self.is_successful and self.is_passed

    @property
    def is_device_failed(self) -> bool:
        """Check if device failed the test criteria

        Returns:
            True if device failed test criteria (only valid for successful execution)
        """
        return self.is_successful and not self.is_passed

    @property
    def measurement_count(self) -> int:
        """Get number of individual measurements taken

        Returns:
            Number of measurement records
        """
        return len(self.measurement_ids) if self.measurement_ids else 0

    @property
    def has_measurements(self) -> bool:
        """Check if result contains measurement data

        Returns:
            True if measurement data is available
        """
        return self.measurement_count > 0 or self.test_summary is not None

    @property
    def has_error(self) -> bool:
        """Check if result contains error information

        Returns:
            True if error message is present
        """
        return self.error_message is not None and len(self.error_message.strip()) > 0

    @property
    def has_notes(self) -> bool:
        """Check if result contains operator notes

        Returns:
            True if operator notes are present
        """
        return self.operator_notes is not None and len(self.operator_notes.strip()) > 0

    def get_summary_value(self, key: str, default: Any = None) -> Any:
        """Get specific value from test summary with type safety

        Args:
            key: Key to look up in summary data
            default: Default value if key not found

        Returns:
            Value from summary or default
        """
        if isinstance(self.test_summary, dict) and not isinstance(
            self.test_summary, TestMeasurements
        ):
            return self.test_summary.get(key, default)
        return default

    def get_measurement_summary(self) -> Optional[TestMeasurements]:
        """Get measurement data if available

        Returns:
            TestMeasurements instance if available, None otherwise
        """
        if isinstance(self.test_summary, TestMeasurements):
            return self.test_summary
        return None

    def format_duration(self) -> str:
        """Format execution duration as human-readable string

        Returns:
            Formatted duration string or 'N/A' if not available
        """
        if self.execution_duration is None:
            return "N/A"
        return str(self.execution_duration)

    def get_duration_seconds(self) -> Optional[float]:
        """Get execution duration in seconds

        Returns:
            Duration in seconds or None if not available
        """
        if self.execution_duration is None:
            return None
        return self.execution_duration.seconds

    def format_completion_time(self) -> str:
        """Format completion timestamp as human-readable string

        Returns:
            Formatted timestamp string or 'N/A' if not available
        """
        if self.completed_at is None:
            return "N/A"
        return self.completed_at.strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation (BaseResult implementation)

        Returns:
            Dictionary containing all result data
        """
        return {
            # Core identification
            "test_id": str(self.test_id),
            "test_status": self.test_status.value,
            # Test outcome
            "is_passed": self.is_passed,
            "is_successful": self.is_successful,
            "is_failed_execution": self.is_failed_execution,
            "is_device_passed": self.is_device_passed,
            "is_device_failed": self.is_device_failed,
            # Timing information
            "execution_duration_seconds": self.get_duration_seconds(),
            "execution_duration_formatted": self.format_duration(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completed_at_formatted": self.format_completion_time(),
            # Measurement data
            "measurement_count": self.measurement_count,
            "has_measurements": self.has_measurements,
            "measurement_ids": (
                [str(mid) for mid in self.measurement_ids] if self.measurement_ids else []
            ),
            "test_summary": self._convert_test_summary_to_dict(),
            # Error and notes
            "error_message": self.error_message,
            "has_error": self.has_error,
            "operator_notes": self.operator_notes,
            "has_notes": self.has_notes,
        }

    def get_summary(self) -> str:
        """Get human-readable summary of the result (BaseResult implementation)

        Returns:
            Summary string
        """
        status_info = f"{self.test_status.value}"
        if self.is_successful:
            result_info = "PASS" if self.is_passed else "FAIL"
            status_info += f" ({result_info})"

        duration_info = f", {self.format_duration()}" if self.execution_duration else ""
        measurement_info = (
            f", {self.measurement_count} measurements" if self.has_measurements else ""
        )

        return f"EOL Test {self.test_id}: {status_info}{duration_info}{measurement_info}"

    def _convert_test_summary_to_dict(self) -> Dict[str, Any]:
        """Convert test summary to serializable dict

        Returns:
            Dictionary representation of test summary
        """
        if isinstance(self.test_summary, TestMeasurements):
            return self.test_summary.to_dict()
        return self.test_summary if isinstance(self.test_summary, dict) else {}

    @classmethod
    def create_success(
        cls,
        test_id: TestId,
        is_passed: bool,
        measurements: Optional[TestMeasurements] = None,
        measurement_ids: Optional[List[MeasurementId]] = None,
        duration: Optional[TestDuration] = None,
        notes: Optional[str] = None,
    ) -> "EOLTestResult":
        """Create successful test result

        Args:
            test_id: Test identifier
            is_passed: Whether device passed test criteria
            measurements: Test measurement data
            measurement_ids: List of measurement identifiers
            duration: Test execution duration
            notes: Optional operator notes

        Returns:
            EOLTestResult for successful test execution
        """
        status = TestStatus.COMPLETED if is_passed else TestStatus.FAILED
        return cls(
            test_id=test_id,
            test_status=status,
            is_passed=is_passed,
            execution_duration=duration,
            completed_at=datetime.now(),
            measurement_ids=measurement_ids or [],
            test_summary=measurements,
            operator_notes=notes,
        )

    @classmethod
    def create_error(
        cls, test_id: TestId, error_message: str, duration: Optional[TestDuration] = None
    ) -> "EOLTestResult":
        """Create error test result

        Args:
            test_id: Test identifier
            error_message: Description of the error
            duration: Partial test execution duration

        Returns:
            EOLTestResult for failed test execution
        """
        return cls(
            test_id=test_id,
            test_status=TestStatus.ERROR,
            is_passed=False,
            execution_duration=duration,
            completed_at=datetime.now(),
            measurement_ids=[],
            error_message=error_message,
        )

    @classmethod
    def create_cancelled(
        cls, test_id: TestId, reason: Optional[str] = None, duration: Optional[TestDuration] = None
    ) -> "EOLTestResult":
        """Create cancelled test result

        Args:
            test_id: Test identifier
            reason: Optional cancellation reason
            duration: Partial test execution duration

        Returns:
            EOLTestResult for cancelled test execution
        """
        return cls(
            test_id=test_id,
            test_status=TestStatus.CANCELLED,
            is_passed=False,
            execution_duration=duration,
            completed_at=datetime.now(),
            measurement_ids=[],
            error_message=reason,
        )

    def __str__(self) -> str:
        """Human-readable string representation"""
        status_info = f"{self.test_status.value}"
        if self.is_successful:
            result_info = "PASS" if self.is_passed else "FAIL"
            status_info += f" ({result_info})"

        duration_info = f", {self.format_duration()}" if self.execution_duration else ""
        measurement_info = (
            f", {self.measurement_count} measurements" if self.has_measurements else ""
        )

        return f"EOLTestResult({self.test_id}: {status_info}{duration_info}{measurement_info})"

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"EOLTestResult(test_id={self.test_id!r}, test_status={self.test_status!r}, "
            f"is_passed={self.is_passed}, measurement_count={self.measurement_count})"
        )
