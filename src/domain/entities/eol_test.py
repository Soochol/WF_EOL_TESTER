"""
EOL Test Entity

Represents an End-of-Line test execution with its configuration and state.
"""

from typing import Dict, Any, List, Optional
from domain.value_objects.identifiers import TestId, DUTId, OperatorId, MeasurementId
from domain.value_objects.time_values import Timestamp, TestDuration
from domain.enums.test_status import TestStatus
from domain.exceptions.validation_exceptions import ValidationException
from domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    InvalidTestStateException,
)
from domain.entities.dut import DUT
from domain.entities.test_result import TestResult


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

        # Test execution state
        self._status = TestStatus.NOT_STARTED
        self._start_time: Optional[Timestamp] = None
        self._end_time: Optional[Timestamp] = None
        self._current_step = 0
        self._total_steps = 0
        self._progress_percentage = 0.0

        # Test results and measurements
        self._measurement_ids: List[MeasurementId] = []
        self._test_result: Optional[TestResult] = None
        self._error_message: Optional[str] = None
        self._operator_notes: Optional[str] = None

        # Hardware state tracking
        self._required_hardware: List[str] = []
        self._connected_hardware: Dict[str, bool] = {}

    def _validate_required_fields(self, test_id: TestId, dut: DUT, operator_id: OperatorId) -> None:
        """Validate required fields"""
        if not isinstance(test_id, TestId):
            raise ValidationException("test_id", test_id, "Test ID must be TestId instance")

        if not isinstance(dut, DUT):
            raise ValidationException("dut", dut, "DUT must be DUT instance")

        if not isinstance(operator_id, OperatorId):
            raise ValidationException(
                "operator_id", operator_id, "Operator ID must be OperatorId instance"
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
        return self._test_configuration.copy()

    @property
    def pass_criteria(self) -> Dict[str, Any]:
        """Get pass criteria"""
        return self._pass_criteria.copy()

    @property
    def created_at(self) -> Timestamp:
        """Get creation timestamp"""
        return self._created_at

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
        return self._progress_percentage

    @property
    def measurement_ids(self) -> List[MeasurementId]:
        """Get measurement IDs"""
        return self._measurement_ids.copy()

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

    @property
    def required_hardware(self) -> List[str]:
        """Get required hardware types"""
        return self._required_hardware.copy()

    @property
    def connected_hardware(self) -> Dict[str, bool]:
        """Get connected hardware status"""
        return self._connected_hardware.copy()

    def get_duration(self) -> Optional[TestDuration]:
        """Get test execution duration"""
        if not self._start_time:
            return None

        end_time = self._end_time or Timestamp.now()
        return TestDuration.between_timestamps(self._start_time, end_time)

    def get_configuration_parameter(self, key: str, default: Any = None) -> Any:
        """Get specific configuration parameter"""
        return self._test_configuration.get(key, default)

    def get_pass_criterion(self, key: str, default: Any = None) -> Any:
        """Get specific pass criterion"""
        return self._pass_criteria.get(key, default)

    def is_active(self) -> bool:
        """Check if test is currently active"""
        return self._status.is_active

    def is_finished(self) -> bool:
        """Check if test execution is finished"""
        return self._status.is_finished

    def is_passed(self) -> bool:
        """Check if test passed"""
        return self._status == TestStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if test failed"""
        return self._status == TestStatus.FAILED

    def can_start(self) -> bool:
        """Check if test can be started"""
        return self._status == TestStatus.NOT_STARTED

    def can_cancel(self) -> bool:
        """Check if test can be cancelled"""
        return self._status.is_active

    def start_test(self, total_steps: int = 1) -> None:
        """
        Start test execution

        Args:
            total_steps: Total number of steps in the test

        Raises:
            InvalidTestStateException: If test cannot be started
        """
        if not self.can_start():
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.NOT_STARTED.value,
                "start_test",
                {"test_id": str(self._test_id)},
            )

        if total_steps < 1:
            raise ValidationException("total_steps", total_steps, "Total steps must be at least 1")

        self._status = TestStatus.PREPARING
        self._start_time = Timestamp.now()
        self._total_steps = total_steps
        self._current_step = 0
        self._progress_percentage = 0.0
        self._error_message = None

    def begin_execution(self) -> None:
        """Begin actual test execution (after preparation)"""
        if self._status != TestStatus.PREPARING:
            raise InvalidTestStateException(
                self._status.value,
                TestStatus.PREPARING.value,
                "begin_execution",
                {"test_id": str(self._test_id)},
            )

        self._status = TestStatus.RUNNING

    def advance_step(self, step_description: Optional[str] = None) -> None:
        """
        Advance to next test step

        Args:
            step_description: Description of current step

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
            self._progress_percentage = (self._current_step / self._total_steps) * 100.0

    def add_measurement_id(self, measurement_id: MeasurementId) -> None:
        """Add measurement ID to test"""
        if not isinstance(measurement_id, MeasurementId):
            raise ValidationException(
                "measurement_id", measurement_id, "Measurement ID must be MeasurementId instance"
            )

        if measurement_id not in self._measurement_ids:
            self._measurement_ids.append(measurement_id)

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

        if not isinstance(test_result, TestResult):
            raise ValidationException(
                "test_result", test_result, "Test result must be TestResult instance"
            )

        self._status = TestStatus.COMPLETED
        self._end_time = Timestamp.now()
        self._test_result = test_result
        self._progress_percentage = 100.0
        self._current_step = self._total_steps
        self._error_message = None

    def fail_test(self, error_message: str, test_result: Optional[TestResult] = None) -> None:
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
            raise ValidationException("error_message", error_message, "Error message is required")

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
        if not self.can_cancel():
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

    def set_operator_notes(self, notes: str) -> None:
        """Set operator notes"""
        self._operator_notes = notes.strip() if notes else None

    def set_required_hardware(self, hardware_types: List[str]) -> None:
        """Set required hardware types for this test"""
        if not isinstance(hardware_types, list):
            raise ValidationException(
                "hardware_types", hardware_types, "Hardware types must be a list"
            )

        self._required_hardware = [hw.lower().strip() for hw in hardware_types]
        # Initialize connection status
        self._connected_hardware = {hw: False for hw in self._required_hardware}

    def set_hardware_connection_status(self, hardware_type: str, connected: bool) -> None:
        """Set connection status for specific hardware"""
        hardware_type = hardware_type.lower().strip()
        if hardware_type in self._connected_hardware:
            self._connected_hardware[hardware_type] = connected

    def are_all_hardware_connected(self) -> bool:
        """Check if all required hardware is connected"""
        return all(self._connected_hardware.values()) if self._connected_hardware else True

    def get_missing_hardware(self) -> List[str]:
        """Get list of hardware that is not connected"""
        return [hw for hw, connected in self._connected_hardware.items() if not connected]

    def to_dict(self) -> Dict[str, Any]:
        """Convert EOL test to dictionary representation"""
        return {
            "test_id": str(self._test_id),
            "dut": self._dut.to_dict(),
            "operator_id": str(self._operator_id),
            "test_configuration": self._test_configuration,
            "pass_criteria": self._pass_criteria,
            "created_at": self._created_at.to_iso(),
            "status": self._status.value,
            "start_time": self._start_time.to_iso() if self._start_time else None,
            "end_time": self._end_time.to_iso() if self._end_time else None,
            "current_step": self._current_step,
            "total_steps": self._total_steps,
            "progress_percentage": self._progress_percentage,
            "duration_seconds": self.get_duration().seconds if self.get_duration() else None,
            "measurement_ids": [str(mid) for mid in self._measurement_ids],
            "test_result": self._test_result.to_dict() if self._test_result else None,
            "error_message": self._error_message,
            "operator_notes": self._operator_notes,
            "required_hardware": self._required_hardware,
            "connected_hardware": self._connected_hardware,
            "is_active": self.is_active(),
            "is_finished": self.is_finished(),
            "is_passed": self.is_passed(),
        }

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
        test._progress_percentage = data.get("progress_percentage", 0.0)

        test._measurement_ids = [MeasurementId(mid) for mid in data.get("measurement_ids", [])]

        if data.get("test_result"):
            test._test_result = TestResult.from_dict(data["test_result"])

        test._error_message = data.get("error_message")
        test._operator_notes = data.get("operator_notes")
        test._required_hardware = data.get("required_hardware", [])
        test._connected_hardware = data.get("connected_hardware", {})

        return test

    def __str__(self) -> str:
        status_info = f"({self._status.value})"
        if self._progress_percentage > 0:
            status_info = f"({self._status.value} - {self._progress_percentage:.1f}%)"

        return f"EOL Test {self._test_id} for {self._dut} {status_info}"

    def __repr__(self) -> str:
        return f"EOLTest(id={self._test_id}, status={self._status.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, EOLTest):
            return False
        return self._test_id == other._test_id

    def __hash__(self) -> int:
        return hash(self._test_id)
