"""
EOL Test Entity

Represents an End-of-Line test execution with its configuration and state.
"""

# Standard library imports
from typing import Any, Dict, Optional, Set

# Local application imports
from domain.entities.dut import DUT
from domain.entities.test_result import TestResult
from domain.enums.test_status import TestStatus
from domain.exceptions.business_rule_exceptions import (
    InvalidTestStateException,
)
from domain.exceptions.validation_exceptions import (
    ValidationException,
)
from domain.value_objects.identifiers import (
    MeasurementId,
    OperatorId,
    TestId,
)
from domain.value_objects.time_values import (
    TestDuration,
    Timestamp,
)


class EOLTest:
    """End-of-Line test entity representing a complete test execution"""

    def __init__(
        self,
        test_id: TestId,
        dut: DUT,
        operator_id: OperatorId,
        test_configuration: Optional[Dict[str, Any]] = None,
        pass_criteria: Optional[Dict[str, Any]] = None,
        created_at: Optional[Timestamp] = None,
        session_timestamp: Optional[str] = None,
    ):
        """
        Initialize EOL test

        Args:
            test_id: Unique identifier for this test
            dut: Device Under Test
            operator_id: Operator performing the test
            test_configuration: Test configuration parameters
            pass_criteria: Criteria that determine pass/fail
            created_at: When test was created (defaults to now)
            session_timestamp: Test session timestamp for grouping repeated tests

        Raises:
            ValidationException: If required fields are invalid
        """
        self._validate_required_fields(test_id, dut, operator_id)

        self._test_id = test_id
        self._dut = dut
        self._operator_id = operator_id
        self._test_configuration = test_configuration or {}
        self._pass_criteria = pass_criteria or {}
        self._created_at = created_at or Timestamp.now()
        self._session_timestamp = session_timestamp

        # Test execution state
        self._status = TestStatus.NOT_STARTED
        self._start_time: Optional[Timestamp] = None
        self._end_time: Optional[Timestamp] = None
        self._current_step = 0
        self._total_steps = 0

        # Test results and measurements
        self._measurement_ids: Set[MeasurementId] = set()
        self._test_result: Optional[TestResult] = None
        self._error_message: Optional[str] = None
        self._operator_notes: Optional[str] = None

    def _validate_required_fields(
        self,
        test_id: TestId,
        dut: DUT,
        operator_id: OperatorId,
    ) -> None:
        """Validate required fields"""
        if not isinstance(test_id, TestId):
            raise ValidationException(
                "test_id",
                test_id,
                "Test ID must be TestId instance",
            )

        if not isinstance(dut, DUT):
            raise ValidationException("dut", dut, "DUT must be DUT instance")

        if not isinstance(operator_id, OperatorId):
            raise ValidationException(
                "operator_id",
                operator_id,
                "Operator ID must be OperatorId instance",
            )

    @property
    def test_id(self) -> TestId:
        """Get test identifier"""
        return self._test_id

    @property
    def dut(self) -> DUT:
        """Get Device Under Test"""
        return self._dut

    @property
    def operator_id(self) -> OperatorId:
        """Get operator identifier"""
        return self._operator_id

    @property
    def test_configuration(self) -> Dict[str, Any]:
        """Get test configuration"""
        return self._test_configuration

    @property
    def pass_criteria(self) -> Dict[str, Any]:
        """Get pass criteria"""
        return self._pass_criteria

    @property
    def created_at(self) -> Timestamp:
        """Get creation timestamp"""
        return self._created_at

    @property
    def session_timestamp(self) -> Optional[str]:
        """Get session timestamp for CSV file grouping"""
        return self._session_timestamp

    @property
    def status(self) -> TestStatus:
        """Get current test status"""
        return self._status

    @property
    def start_time(self) -> Optional[Timestamp]:
        """Get test start time"""
        return self._start_time

    @property
    def end_time(self) -> Optional[Timestamp]:
        """Get test end time"""
        return self._end_time

    @property
    def current_step(self) -> int:
        """Get current step number"""
        return self._current_step

    @property
    def total_steps(self) -> int:
        """Get total number of steps"""
        return self._total_steps

    @property
    def progress_percentage(self) -> float:
        """Get progress percentage (0-100)"""
        if self._total_steps == 0:
            return 0.0
        return (self._current_step / self._total_steps) * 100.0

    @property
    def measurement_ids(self) -> Set[MeasurementId]:
        """Get measurement IDs"""
        return self._measurement_ids

    @property
    def test_result(self) -> Optional[TestResult]:
        """Get test result"""
        return self._test_result

    @property
    def error_message(self) -> Optional[str]:
        """Get error message"""
        return self._error_message

    @property
    def operator_notes(self) -> Optional[str]:
        """Get operator notes"""
        return self._operator_notes

    def get_duration(self) -> Optional[TestDuration]:
        """Get test execution duration"""
        if not self._start_time:
            return None

        end_time = self._end_time or Timestamp.now()
        return TestDuration.between_timestamps(self._start_time, end_time)

    def prepare_test(self, total_steps: int = 1) -> None:
        """
        Prepare test for execution (transition to PREPARING state)

        Args:
            total_steps: Total number of steps in the test

        Raises:
            InvalidTestStateException: If test cannot be prepared
        """
        if self._status != TestStatus.NOT_STARTED:
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.NOT_STARTED.value,
                "prepare_test",
                {"test_id": str(self._test_id)},
            )

        if total_steps < 1:
            raise ValidationException(
                "total_steps",
                total_steps,
                "Total steps must be at least 1",
            )

        self._status = TestStatus.PREPARING
        self._start_time = Timestamp.now()
        self._total_steps = total_steps
        self._current_step = 0
        self._error_message = None

    def start_execution(self) -> None:
        """Start actual test execution (transition from PREPARING to RUNNING)"""
        if self._status != TestStatus.PREPARING:
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.PREPARING.value,
                "start_execution",
                {"test_id": str(self._test_id)},
            )

        self._status = TestStatus.RUNNING

    def advance_step(self) -> None:
        """
        Advance to next test step

        Raises:
            InvalidTestStateException: If test is not running
        """
        if self._status != TestStatus.RUNNING:
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.RUNNING.value,
                "advance_step",
                {"test_id": str(self._test_id)},
            )

        if self._current_step < self._total_steps:
            self._current_step += 1

    def add_measurement_id(self, measurement_id: MeasurementId) -> None:
        """Add measurement ID to test"""
        self._measurement_ids.add(measurement_id)

    def complete_test(self, test_result: TestResult) -> None:
        """
        Complete test execution successfully

        Args:
            test_result: Final test result

        Raises:
            InvalidTestStateException: If test is not running
        """
        if self._status != TestStatus.RUNNING:
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.RUNNING.value,
                "complete_test",
                {"test_id": str(self._test_id)},
            )

        self._status = TestStatus.COMPLETED
        self._end_time = Timestamp.now()
        self._test_result = test_result
        self._current_step = self._total_steps
        self._error_message = None

    def fail_test(
        self,
        error_message: str,
        test_result: Optional[TestResult] = None,
    ) -> None:
        """
        Fail test execution

        Args:
            error_message: Reason for failure
            test_result: Partial test result if available

        Raises:
            InvalidTestStateException: If test is not active
        """
        if not self._status.is_active:
            raise InvalidTestStateException(
                self._status.value,
                "RUNNING or PREPARING",
                "fail_test",
                {"test_id": str(self._test_id)},
            )

        if not error_message or not error_message.strip():
            raise ValidationException(
                "error_message",
                error_message,
                "Error message is required",
            )

        self._status = TestStatus.FAILED
        self._end_time = Timestamp.now()
        self._error_message = error_message.strip()
        self._test_result = test_result

    def cancel_test(self, reason: Optional[str] = None) -> None:
        """
        Cancel test execution

        Args:
            reason: Reason for cancellation

        Raises:
            InvalidTestStateException: If test cannot be cancelled
        """
        if not self._status.is_active:
            raise InvalidTestStateException(
                self._status.value,
                "PREPARING or RUNNING",
                "cancel_test",
                {"test_id": str(self._test_id)},
            )

        self._status = TestStatus.CANCELLED
        self._end_time = Timestamp.now()
        if reason:
            self._error_message = f"Cancelled: {reason.strip()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert EOL test to dictionary representation"""
        duration = self.get_duration()

        result = {
            "test_id": str(self._test_id),
            "dut": self._dut.to_dict(),
            "operator_id": str(self._operator_id),
            "test_configuration": self._test_configuration,
            "pass_criteria": self._pass_criteria,
            "created_at": self._created_at.to_iso(),
            "status": self._status.value,
            "current_step": self._current_step,
            "total_steps": self._total_steps,
            "measurement_ids": [str(mid) for mid in self._measurement_ids],
            "error_message": self._error_message,
            "operator_notes": self._operator_notes,
        }

        # Add optional timestamp fields
        if self._start_time:
            result["start_time"] = self._start_time.to_iso()
        if self._end_time:
            result["end_time"] = self._end_time.to_iso()
        if duration:
            result["duration_seconds"] = duration.seconds
        if self._test_result:
            result["test_result"] = self._test_result.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EOLTest":
        """Create EOL test from dictionary representation"""
        dut = DUT.from_dict(data["dut"])

        test = cls(
            test_id=TestId(data["test_id"]),
            dut=dut,
            operator_id=OperatorId(data["operator_id"]),
            test_configuration=data.get("test_configuration", {}),
            pass_criteria=data.get("pass_criteria", {}),
            created_at=Timestamp.from_iso(data["created_at"]),
        )

        # Restore state
        test._status = TestStatus(data["status"])
        if data.get("start_time"):
            test._start_time = Timestamp.from_iso(data["start_time"])
        if data.get("end_time"):
            test._end_time = Timestamp.from_iso(data["end_time"])

        test._current_step = data.get("current_step", 0)
        test._total_steps = data.get("total_steps", 0)

        test._measurement_ids = {MeasurementId(mid) for mid in data.get("measurement_ids", [])}

        if data.get("test_result"):
            test._test_result = TestResult.from_dict(data["test_result"])

        test._error_message = data.get("error_message")
        test._operator_notes = data.get("operator_notes")

        return test

    def __str__(self) -> str:
        status_info = f"({self._status.value})"
        if self.progress_percentage > 0:
            status_info = f"({self._status.value} - {self.progress_percentage:.1f}%)"

        return f"EOL Test {self._test_id} for {self._dut} {status_info}"

    def __repr__(self) -> str:
        return f"EOLTest(id={self._test_id}, status={self._status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EOLTest):
            return False
        return self._test_id == other._test_id

    def __hash__(self) -> int:
        return hash(self._test_id)
