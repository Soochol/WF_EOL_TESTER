"""
Base Result Value Object

Abstract base class for all test result value objects in the domain layer.
Provides common structure and behavior for representing test execution outcomes.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Local application imports
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class BaseResult(ABC):
    """
    Abstract base class for all test result value objects

    Results encapsulate output data from test execution.
    They contain both success/failure status and relevant data.
    This is a pure domain object with no application or infrastructure dependencies.
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
        Initialize base result

        Args:
            test_status: Status of the test execution
            is_success: Whether the execution succeeded
            error_message: Error message if execution failed
            test_id: Unique identifier for this test execution
            execution_duration: How long the execution took
        """
        self._test_status = test_status
        self._is_success = is_success
        self._error_message = error_message
        self._test_id = test_id
        self._execution_duration = execution_duration

    @property
    def test_status(self) -> TestStatus:
        """Get the test status"""
        return self._test_status

    @property
    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self._is_success

    @property
    def is_passed(self) -> bool:
        """Check if test passed (alias for is_success for UI compatibility)"""
        return self._is_success

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if execution failed"""
        return self._error_message

    @property
    def test_id(self) -> Optional[TestId]:
        """Get the test ID"""
        return self._test_id

    @test_id.setter
    def test_id(self, value: TestId) -> None:
        """Set the test ID (used by use cases)"""
        self._test_id = value

    @property
    def execution_duration(self) -> Optional[TestDuration]:
        """Get the execution duration"""
        return self._execution_duration

    @execution_duration.setter
    def execution_duration(self, value: TestDuration) -> None:
        """Set the execution duration (used by use cases)"""
        self._execution_duration = value

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation

        Returns:
            Dictionary containing result data
        """
        pass

    @abstractmethod
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the result

        Returns:
            Summary string
        """
        pass
