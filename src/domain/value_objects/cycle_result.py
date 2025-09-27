"""
Cycle Result Value Object

Individual cycle result for repeat testing scenarios.
Contains measurements and status for a single test cycle within a larger test sequence.
"""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Union

# Local application imports
from domain.enums.test_status import TestStatus
from domain.exceptions.validation_exceptions import ValidationException
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.time_values import TestDuration


@dataclass(frozen=True)
class CycleResult:
    """
    Result for a single test cycle within a repeat test sequence

    Represents the outcome of one individual cycle when a test is repeated
    multiple times (repeat_count > 1). Contains cycle-specific measurements,
    timing, and status information.
    """

    cycle_number: int
    test_status: TestStatus
    is_passed: bool
    measurements: Optional[Union[TestMeasurements, Dict[str, Any]]] = None
    execution_duration: Optional[TestDuration] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    cycle_notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate cycle result data"""
        self._validate_cycle_number()
        self._validate_status_consistency()
        self._validate_optional_fields()

    def _validate_cycle_number(self) -> None:
        """Validate cycle number"""
        if self.cycle_number < 1:
            raise ValidationException(
                "cycle_number", self.cycle_number, "Cycle number must be at least 1"
            )

        if self.cycle_number > 1000:
            raise ValidationException(
                "cycle_number", self.cycle_number, "Cycle number must not exceed 1000"
            )

    def _validate_status_consistency(self) -> None:
        """Validate status and error message consistency"""
        if self.test_status == TestStatus.FAILED and not self.error_message:
            raise ValidationException(
                "error_message",
                self.error_message,
                "Error message is required when test status is FAILED",
            )

        if self.test_status == TestStatus.COMPLETED and self.error_message:
            raise ValidationException(
                "error_message",
                self.error_message,
                "Error message should not be present when test status is COMPLETED",
            )

    def _validate_optional_fields(self) -> None:
        """Validate optional fields"""
        if self.cycle_notes and len(self.cycle_notes) > 1000:
            raise ValidationException(
                "cycle_notes", self.cycle_notes, "Cycle notes must not exceed 1000 characters"
            )

    @property
    def is_successful_execution(self) -> bool:
        """Whether the cycle executed successfully (regardless of pass/fail)"""
        return self.test_status in (TestStatus.COMPLETED, TestStatus.FAILED)

    @property
    def is_device_passed(self) -> bool:
        """Whether the device passed this cycle's test criteria"""
        return self.is_passed and self.test_status == TestStatus.COMPLETED

    @property
    def is_device_failed(self) -> bool:
        """Whether the device failed this cycle's test criteria"""
        return not self.is_passed and self.test_status == TestStatus.COMPLETED

    @property
    def is_execution_error(self) -> bool:
        """Whether there was an execution error during this cycle"""
        return self.test_status not in (TestStatus.COMPLETED, TestStatus.FAILED)

    def format_duration(self) -> str:
        """Format execution duration as string"""
        if self.execution_duration:
            return f"{self.execution_duration.seconds:.3f}s"
        return "0.000s"

    def get_measurement_count(self) -> int:
        """Get number of measurements in this cycle"""
        if isinstance(self.measurements, TestMeasurements):
            return self.measurements.total_measurement_count
        elif isinstance(self.measurements, dict):
            # For dict-based measurements, try to count entries
            return len(self.measurements.get("measurements", {}))
        return 0

    def get_average_force(self) -> Optional[float]:
        """Get average force value from measurements"""
        if isinstance(self.measurements, TestMeasurements):
            return self.measurements.average_force
        elif isinstance(self.measurements, dict):
            # Try to extract average force from dict format
            forces = []
            measurements = self.measurements.get("measurements", {})
            for temp_data in measurements.values():
                if isinstance(temp_data, dict):
                    for pos_data in temp_data.values():
                        if isinstance(pos_data, dict) and "force" in pos_data:
                            forces.append(pos_data["force"])
            return sum(forces) / len(forces) if forces else None
        return None

    def get_temperature_range(self) -> tuple[Optional[float], Optional[float]]:
        """Get temperature range from measurements"""
        if isinstance(self.measurements, TestMeasurements):
            temps = self.measurements.temperatures
            return (min(temps), max(temps)) if temps else (None, None)
        elif isinstance(self.measurements, dict):
            measurements = self.measurements.get("measurements", {})
            temps = [
                float(temp) for temp in measurements.keys() if isinstance(temp, (int, float, str))
            ]
            return (min(temps), max(temps)) if temps else (None, None)
        return (None, None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert cycle result to dictionary representation"""
        return {
            "cycle_number": self.cycle_number,
            "test_status": self.test_status.value,
            "is_passed": self.is_passed,
            "execution_duration_seconds": (
                self.execution_duration.seconds if self.execution_duration else None
            ),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "cycle_notes": self.cycle_notes,
            "measurements": (
                self.measurements.to_dict()
                if isinstance(self.measurements, TestMeasurements)
                else self.measurements
            ),
            "measurement_count": self.get_measurement_count(),
            "average_force": self.get_average_force(),
            "temperature_range": self.get_temperature_range(),
        }

    @classmethod
    def create_successful(
        cls,
        cycle_number: int,
        is_passed: bool,
        measurements: Optional[Union[TestMeasurements, Dict[str, Any]]] = None,
        execution_duration: Optional[TestDuration] = None,
        completed_at: Optional[datetime] = None,
        cycle_notes: Optional[str] = None,
    ) -> "CycleResult":
        """
        Create a successful cycle result

        Args:
            cycle_number: Cycle number (1-based)
            is_passed: Whether device passed test criteria
            measurements: Cycle measurements
            execution_duration: Cycle execution time
            completed_at: Cycle completion timestamp
            cycle_notes: Optional cycle notes

        Returns:
            CycleResult for successful cycle execution
        """
        status = TestStatus.COMPLETED if is_passed else TestStatus.FAILED
        return cls(
            cycle_number=cycle_number,
            test_status=status,
            is_passed=is_passed,
            measurements=measurements,
            execution_duration=execution_duration,
            completed_at=completed_at,
            cycle_notes=cycle_notes,
        )

    @classmethod
    def create_failed(
        cls,
        cycle_number: int,
        error_message: str,
        execution_duration: Optional[TestDuration] = None,
        completed_at: Optional[datetime] = None,
        cycle_notes: Optional[str] = None,
    ) -> "CycleResult":
        """
        Create a failed cycle result

        Args:
            cycle_number: Cycle number (1-based)
            error_message: Error description
            execution_duration: Cycle execution time
            completed_at: Cycle completion timestamp
            cycle_notes: Optional cycle notes

        Returns:
            CycleResult for failed cycle execution
        """
        return cls(
            cycle_number=cycle_number,
            test_status=TestStatus.ERROR,
            is_passed=False,
            error_message=error_message,
            execution_duration=execution_duration,
            completed_at=completed_at,
            cycle_notes=cycle_notes,
        )

    def __str__(self) -> str:
        """String representation of cycle result"""
        status_info = f"{self.test_status.value}"
        if self.is_passed and self.test_status == TestStatus.COMPLETED:
            status_info += " (PASS)"
        elif not self.is_passed and self.test_status == TestStatus.COMPLETED:
            status_info += " (FAIL)"

        duration_info = f", {self.format_duration()}" if self.execution_duration else ""
        measurement_info = (
            f", {self.get_measurement_count()} measurements" if self.measurements else ""
        )

        return f"CycleResult(#{self.cycle_number}: {status_info}{duration_info}{measurement_info})"
        return f"CycleResult(#{self.cycle_number}: {status_info}{duration_info}{measurement_info})"
