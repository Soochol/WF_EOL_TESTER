"""
Robot Home Result

Result object for robot homing operation.
Contains operation outcome and execution details.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Local application imports
from application.use_cases.common.command_result_patterns import BaseResult
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class RobotHomeResult(BaseResult):
    """
    Result for Robot Homing Operation

    Contains operation outcome and execution timing information.
    """

    def __init__(
        self,
        test_status: TestStatus,
        is_success: bool,
        error_message: Optional[str] = None,
        test_id: Optional[TestId] = None,
        execution_duration: Optional[TestDuration] = None,
    ):
        """
        Initialize robot home result

        Args:
            test_status: Test execution status
            is_success: Whether operation was successful
            error_message: Error message if operation failed
            test_id: Unique operation identifier
            execution_duration: Operation execution time
        """
        super().__init__(test_status, is_success, error_message, test_id, execution_duration)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation

        Returns:
            Dictionary containing result data
        """
        return {
            "operation_id": self.test_id.value if self.test_id else None,
            "test_status": self.test_status.value,
            "is_success": self.is_success,
            "execution_duration_seconds": (
                self.execution_duration.seconds if self.execution_duration else 0
            ),
            "error_message": self.error_message,
        }

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the result

        Returns:
            Summary string
        """
        if not self.is_success:
            return f"Robot Homing FAILED: {self.error_message}"

        duration = self.execution_duration.seconds if self.execution_duration else 0
        return f"Robot Homing COMPLETED successfully - Duration: {duration:.2f}s"
