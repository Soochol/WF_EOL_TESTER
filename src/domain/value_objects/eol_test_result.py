"""
EOL Test Result

Result object for EOL test execution use case.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union

from .identifiers import TestId, MeasurementId
from .time_values import TestDuration
from .measurements import TestMeasurements
from ..enums.test_status import TestStatus


@dataclass(frozen=True)
class EOLTestResult:
    """Result of EOL test execution"""

    test_id: TestId
    test_status: TestStatus
    execution_duration: Optional[TestDuration]
    is_passed: bool
    measurement_ids: List[MeasurementId]
    test_summary: Union[TestMeasurements, Dict[str, Any]]
    error_message: Optional[str] = None
    operator_notes: Optional[str] = None

    @property
    def is_successful(self) -> bool:
        """Check if test execution was successful (regardless of pass/fail)"""
        return self.test_status in (TestStatus.COMPLETED, TestStatus.FAILED)

    @property
    def is_failed_execution(self) -> bool:
        """Check if test execution failed (not device failure)"""
        return self.test_status in (TestStatus.ERROR, TestStatus.CANCELLED)

    @property
    def measurement_count(self) -> int:
        """Get number of measurements taken"""
        return len(self.measurement_ids)

    def get_summary_value(self, key: str, default: Any = None) -> Any:
        """Get specific value from test summary with type safety"""
        if isinstance(self.test_summary, dict) and not isinstance(self.test_summary, TestMeasurements):
            return self.test_summary.get(key, default)
        return default

    def format_duration(self) -> str:
        """Format execution duration as human-readable string"""
        if self.execution_duration is None:
            return "N/A"
        return str(self.execution_duration)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            'test_id': str(self.test_id),
            'test_status': self.test_status.value,
            'execution_duration_seconds': self.execution_duration.seconds if self.execution_duration else None,
            'is_passed': self.is_passed,
            'is_successful': self.is_successful,
            'is_failed_execution': self.is_failed_execution,
            'measurement_count': self.measurement_count,
            'measurement_ids': [str(mid) for mid in self.measurement_ids],
            'test_summary': self._convert_test_summary_to_dict(),
            'error_message': self.error_message,
            'operator_notes': self.operator_notes
        }

    def _convert_test_summary_to_dict(self) -> Dict[str, Any]:
        """Convert test summary to serializable dict"""
        if isinstance(self.test_summary, TestMeasurements):
            return self.test_summary.to_dict()
        return self.test_summary if isinstance(self.test_summary, dict) else {}
