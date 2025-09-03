"""
Simple MCU Test Result

Result object for simple MCU communication test.
Contains test outcomes and detailed step results.
"""

from typing import Any, Dict, List, Optional

from application.use_cases.common.command_result_patterns import BaseResult
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class SimpleMCUTestResult(BaseResult):
    """
    Result for Simple MCU Communication Test

    Contains test outcomes and detailed results from MCU communication testing.
    """

    def __init__(
        self,
        test_status: TestStatus,
        is_success: bool,
        test_results: List[Dict[str, Any]],
        error_message: Optional[str] = None,
        test_id: Optional[TestId] = None,
        execution_duration: Optional[TestDuration] = None,
    ):
        """
        Initialize simple MCU test result

        Args:
            test_status: Test execution status
            is_success: Whether test passed or failed
            test_results: List of individual test step results
            error_message: Error message if test failed
            test_id: Unique test identifier
            execution_duration: Total test execution time
        """
        super().__init__(test_status, is_success, error_message, test_id, execution_duration)
        self.test_results = test_results

    @property
    def measurement_count(self) -> int:
        """Number of successful measurements"""
        return len([r for r in self.test_results if r.get("success", False)])

    @property
    def total_steps(self) -> int:
        """Total number of test steps"""
        return len(self.test_results)

    def format_duration(self) -> str:
        """Format execution duration as string"""
        if self.execution_duration:
            return f"{self.execution_duration.seconds:.3f}s"
        return "0.000s"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation

        Returns:
            Dictionary containing result data
        """
        return {
            "test_id": self.test_id.value if self.test_id else None,
            "test_status": self.test_status.value,
            "is_success": self.is_success,
            "execution_duration_seconds": (
                self.execution_duration.seconds if self.execution_duration else 0
            ),
            "test_results": self.test_results,
            "measurement_count": self.measurement_count,
            "total_steps": self.total_steps,
            "error_message": self.error_message,
        }

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the result

        Returns:
            Summary string
        """
        if not self.is_success:
            return f"Simple MCU Test FAILED: {self.error_message}"

        successful_steps = self.measurement_count
        total_steps = self.total_steps

        return f"Simple MCU Test PASSED - " f"Success: {successful_steps}/{total_steps} steps"
