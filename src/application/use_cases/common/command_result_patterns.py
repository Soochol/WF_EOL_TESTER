"""
Use Case Input and Result Patterns

Base classes for input and result objects used across all use cases.
Implements consistent patterns and ensures type safety.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class BaseUseCaseInput(ABC):
    """
    Abstract base class for all use case input data

    Input objects encapsulate parameters for use case execution.
    They should be immutable and contain all necessary information.
    """

    def __init__(self, operator_id: str = "system"):
        """
        Initialize base use case input

        Args:
            operator_id: ID of the operator executing the use case
        """
        self._operator_id = operator_id

    @property
    def operator_id(self) -> str:
        """Get the operator ID"""
        return self._operator_id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert input to dictionary representation

        Returns:
            Dictionary containing input data
        """
        pass


class BaseResult(ABC):
    """
    Abstract base class for all use case results

    Results encapsulate output data from use case execution.
    They contain both success/failure status and relevant data.
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
    def error_message(self) -> Optional[str]:
        """Get error message if execution failed"""
        return self._error_message

    @property
    def test_id(self) -> Optional[TestId]:
        """Get the test ID"""
        return self._test_id

    @test_id.setter
    def test_id(self, value: TestId) -> None:
        """Set the test ID (used by BaseUseCase)"""
        self._test_id = value

    @property
    def execution_duration(self) -> Optional[TestDuration]:
        """Get the execution duration"""
        return self._execution_duration

    @execution_duration.setter
    def execution_duration(self, value: TestDuration) -> None:
        """Set the execution duration (used by BaseUseCase)"""
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
