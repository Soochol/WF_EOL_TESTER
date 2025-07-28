"""
Test Result Entity

Represents the outcome and results of an EOL test execution.
"""

from typing import Dict, Any, List, Optional
from domain.value_objects.identifiers import TestId, MeasurementId
from domain.value_objects.time_values import Timestamp, TestDuration
from domain.enums.test_status import TestStatus
from domain.exceptions.validation_exceptions import ValidationException


class TestResult:
    """Test execution result entity"""
    
    def __init__(
        self,
        test_id: TestId,
        test_status: TestStatus,
        start_time: Timestamp,
        end_time: Optional[Timestamp] = None,
        measurement_ids: Optional[List[MeasurementId]] = None,
        pass_criteria: Optional[Dict[str, Any]] = None,
        actual_results: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        operator_notes: Optional[str] = None,
        test_parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize test result
        
        Args:
            test_id: ID of the test these results belong to
            test_status: Final status of test execution
            start_time: When test execution started
            end_time: When test execution ended (if finished)
            measurement_ids: List of measurement IDs collected during test
            pass_criteria: Criteria that determine pass/fail
            actual_results: Actual measured/calculated results
            error_message: Error message if test failed
            operator_notes: Additional notes from operator
            test_parameters: Parameters used during test execution
            
        Raises:
            ValidationException: If required fields are invalid
        """
        self._validate_required_fields(test_id, test_status, start_time)
        self._validate_time_consistency(start_time, end_time, test_status)
        
        self._test_id = test_id
        self._test_status = test_status
        self._start_time = start_time
        self._end_time = end_time
        self._measurement_ids = measurement_ids or []
        self._pass_criteria = pass_criteria or {}
        self._actual_results = actual_results or {}
        self._error_message = error_message
        self._operator_notes = operator_notes
        self._test_parameters = test_parameters or {}
        
        self._created_at = Timestamp.now()
    
    def _validate_required_fields(self, test_id: TestId, test_status: TestStatus, start_time: Timestamp) -> None:
        """Validate required fields"""
        if not isinstance(test_id, TestId):
            raise ValidationException("test_id", test_id, "Test ID must be TestId instance")
        
        if not isinstance(test_status, TestStatus):
            raise ValidationException("test_status", test_status, "Test status must be TestStatus enum")
        
        if not isinstance(start_time, Timestamp):
            raise ValidationException("start_time", start_time, "Start time must be Timestamp instance")
    
    def _validate_time_consistency(self, start_time: Timestamp, end_time: Optional[Timestamp], test_status: TestStatus) -> None:
        """Validate time consistency"""
        if end_time and end_time < start_time:
            raise ValidationException("end_time", end_time, "End time cannot be before start time")
        
        # If test is finished, end time should be provided
        if test_status.is_finished and not end_time:
            raise ValidationException("end_time", end_time, f"End time required for status {test_status.value}")
    
    @property
    def test_id(self) -> TestId:
        """Get test identifier"""
        return self._test_id
    
    @property
    def test_status(self) -> TestStatus:
        """Get test status"""
        return self._test_status
    
    @property
    def start_time(self) -> Timestamp:
        """Get start time"""
        return self._start_time
    
    @property
    def end_time(self) -> Optional[Timestamp]:
        """Get end time"""
        return self._end_time
    
    @property
    def measurement_ids(self) -> List[MeasurementId]:
        """Get measurement IDs"""
        return self._measurement_ids.copy()
    
    @property
    def pass_criteria(self) -> Dict[str, Any]:
        """Get pass criteria"""
        return self._pass_criteria.copy()
    
    @property
    def actual_results(self) -> Dict[str, Any]:
        """Get actual results"""
        return self._actual_results.copy()
    
    @property
    def error_message(self) -> Optional[str]:
        """Get error message"""
        return self._error_message
    
    @property
    def operator_notes(self) -> Optional[str]:
        """Get operator notes"""
        return self._operator_notes
    
    @property
    def test_parameters(self) -> Dict[str, Any]:
        """Get test parameters"""
        return self._test_parameters.copy()
    
    @property
    def created_at(self) -> Timestamp:
        """Get creation timestamp"""
        return self._created_at
    
    def get_duration(self) -> Optional[TestDuration]:
        """Get test execution duration"""
        if not self._end_time:
            return None
        return TestDuration.between_timestamps(self._start_time, self._end_time)
    
    def is_passed(self) -> bool:
        """Check if test passed"""
        return self._test_status == TestStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if test failed"""
        return self._test_status == TestStatus.FAILED
    
    def is_finished(self) -> bool:
        """Check if test execution is finished"""
        return self._test_status.is_finished
    
    def add_measurement_id(self, measurement_id: MeasurementId) -> None:
        """Add measurement ID to results"""
        if not isinstance(measurement_id, MeasurementId):
            raise ValidationException("measurement_id", measurement_id, "Measurement ID must be MeasurementId instance")
        
        if measurement_id not in self._measurement_ids:
            self._measurement_ids.append(measurement_id)
    
    def set_end_time(self, end_time: Timestamp) -> None:
        """Set test end time"""
        if not isinstance(end_time, Timestamp):
            raise ValidationException("end_time", end_time, "End time must be Timestamp instance")
        
        if end_time < self._start_time:
            raise ValidationException("end_time", end_time, "End time cannot be before start time")
        
        self._end_time = end_time
    
    def update_status(self, status: TestStatus, error_message: Optional[str] = None) -> None:
        """Update test status"""
        if not isinstance(status, TestStatus):
            raise ValidationException("status", status, "Status must be TestStatus enum")
        
        self._test_status = status
        
        if status in (TestStatus.FAILED, TestStatus.ERROR) and error_message:
            self._error_message = error_message
        elif status == TestStatus.COMPLETED:
            self._error_message = None
    
    def update_actual_results(self, results: Dict[str, Any]) -> None:
        """Update actual test results"""
        if not isinstance(results, dict):
            raise ValidationException("results", results, "Results must be a dictionary")
        
        self._actual_results.update(results)
    
    def get_pass_criterion(self, key: str, default: Any = None) -> Any:
        """Get specific pass criterion"""
        return self._pass_criteria.get(key, default)
    
    def get_actual_result(self, key: str, default: Any = None) -> Any:
        """Get specific actual result"""
        return self._actual_results.get(key, default)
    
    def get_test_parameter(self, key: str, default: Any = None) -> Any:
        """Get specific test parameter"""
        return self._test_parameters.get(key, default)
    
    def evaluate_pass_fail(self) -> bool:
        """
        Evaluate if test should pass based on criteria and results
        
        Returns:
            True if test should pass, False otherwise
        """
        if not self._pass_criteria or not self._actual_results:
            return False
        
        for criterion_name, criterion_value in self._pass_criteria.items():
            actual_value = self._actual_results.get(criterion_name)
            
            if actual_value is None:
                return False  # Missing required result
            
            if not self._evaluate_single_criterion(criterion_name, criterion_value, actual_value):
                return False
        
        return True
    
    def _evaluate_single_criterion(self, name: str, criterion: Any, actual: Any) -> bool:
        """Evaluate a single pass/fail criterion"""
        if isinstance(criterion, dict):
            # Range criterion: {"min": 10, "max": 20}
            if "min" in criterion and actual < criterion["min"]:
                return False
            if "max" in criterion and actual > criterion["max"]:
                return False
            return True
        elif isinstance(criterion, (int, float)):
            # Exact value criterion
            return abs(actual - criterion) < 1e-9
        elif isinstance(criterion, str):
            # String comparison
            return str(actual) == criterion
        else:
            # Direct comparison
            return actual == criterion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary representation"""
        return {
            'test_id': str(self._test_id),
            'test_status': self._test_status.value,
            'start_time': self._start_time.to_iso(),
            'end_time': self._end_time.to_iso() if self._end_time else None,
            'duration_seconds': self.get_duration().seconds if self.get_duration() else None,
            'measurement_ids': [str(mid) for mid in self._measurement_ids],
            'pass_criteria': self._pass_criteria,
            'actual_results': self._actual_results,
            'error_message': self._error_message,
            'operator_notes': self._operator_notes,
            'test_parameters': self._test_parameters,
            'created_at': self._created_at.to_iso(),
            'is_passed': self.is_passed(),
            'is_finished': self.is_finished()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create test result from dictionary representation"""
        end_time = None
        if data.get('end_time'):
            end_time = Timestamp.from_iso(data['end_time'])
        
        measurement_ids = [MeasurementId(mid) for mid in data.get('measurement_ids', [])]
        
        return cls(
            test_id=TestId(data['test_id']),
            test_status=TestStatus(data['test_status']),
            start_time=Timestamp.from_iso(data['start_time']),
            end_time=end_time,
            measurement_ids=measurement_ids,
            pass_criteria=data.get('pass_criteria', {}),
            actual_results=data.get('actual_results', {}),
            error_message=data.get('error_message'),
            operator_notes=data.get('operator_notes'),
            test_parameters=data.get('test_parameters', {})
        )
    
    def __str__(self) -> str:
        status_str = f"({self._test_status.value})"
        if self._end_time:
            duration = self.get_duration()
            status_str += f" in {duration}"
        
        return f"Test {self._test_id} {status_str}"
    
    def __repr__(self) -> str:
        return f"TestResult(test_id={self._test_id}, status={self._test_status.value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TestResult):
            return False
        return self._test_id == other._test_id
    
    def __hash__(self) -> int:
        return hash(self._test_id)