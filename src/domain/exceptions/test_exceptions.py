"""
Test Execution Domain Exceptions

Contains exceptions related to test execution business rules and constraints.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Local application imports
from domain.exceptions.domain_exceptions import (
    DomainException,
)


class TestExecutionException(DomainException):
    """Base exception for test execution business rule violations"""

    def __init__(
        self,
        message: str,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test execution exception

        Args:
            message: Human-readable error message
            test_id: ID of the test involved in the exception
            details: Additional context about the test execution error
        """
        super().__init__(message, details)
        self.test_id = test_id


class InvalidTestStateException(TestExecutionException):
    """Exception raised when test is in invalid state for operation according to business rules"""

    def __init__(
        self,
        current_state: str,
        required_state: str,
        operation: str,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize invalid test state exception

        Args:
            current_state: Current test state
            required_state: Required state for operation
            operation: The operation that was attempted
            test_id: ID of the test
            details: Additional state context
        """
        message = f"Cannot perform '{operation}' in state '{current_state}'. Required state: '{required_state}'"

        exception_details = details or {}
        exception_details.update(
            {
                "current_state": current_state,
                "required_state": required_state,
                "operation": operation,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.current_state = current_state
        self.required_state = required_state
        self.operation = operation


class TestSequenceException(TestExecutionException):
    """Exception raised when test sequence violates business rules"""

    def __init__(
        self,
        step_name: str,
        sequence_violation: str,
        expected_previous_step: Optional[str] = None,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test sequence exception

        Args:
            step_name: Name of the step that violated sequence
            sequence_violation: Description of sequence violation
            expected_previous_step: Step that should have been completed first
            test_id: ID of the test
            details: Additional sequence context
        """
        if expected_previous_step:
            message = f"Test sequence violation at step '{step_name}': {sequence_violation}. Expected previous step: '{expected_previous_step}'"
        else:
            message = f"Test sequence violation at step '{step_name}': {sequence_violation}"

        exception_details = details or {}
        exception_details.update(
            {
                "step_name": step_name,
                "sequence_violation": sequence_violation,
                "expected_previous_step": expected_previous_step,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.step_name = step_name
        self.sequence_violation = sequence_violation
        self.expected_previous_step = expected_previous_step


class MeasurementValidationException(TestExecutionException):
    """Exception raised when measurement validation violates business rules"""

    def __init__(
        self,
        measurement_type: str,
        measured_value: float,
        validation_failure: str,
        expected_range: Optional[Dict[str, float]] = None,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize measurement validation exception

        Args:
            measurement_type: Type of measurement (e.g., 'force', 'temperature', 'voltage')
            measured_value: The measured value that failed validation
            validation_failure: Description of validation failure
            expected_range: Expected range (e.g., {'min': 10.0, 'max': 50.0})
            test_id: ID of the test
            details: Additional measurement context
        """
        if expected_range:
            range_str = f"[{expected_range.get('min', '-∞')} to {expected_range.get('max', '+∞')}]"
            message = f"Measurement validation failed for {measurement_type}: {measured_value} not in range {range_str}. {validation_failure}"
        else:
            message = f"Measurement validation failed for {measurement_type}: {measured_value}. {validation_failure}"

        exception_details = details or {}
        exception_details.update(
            {
                "measurement_type": measurement_type,
                "measured_value": measured_value,
                "validation_failure": validation_failure,
                "expected_range": expected_range,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.measurement_type = measurement_type
        self.measured_value = measured_value
        self.validation_failure = validation_failure
        self.expected_range = expected_range


class TestTimeoutException(TestExecutionException):
    """Exception raised when test execution times out violating business rules"""

    def __init__(
        self,
        step_name: str,
        timeout_seconds: float,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test timeout exception

        Args:
            step_name: Name of the step that timed out
            timeout_seconds: Timeout duration in seconds
            test_id: ID of the test
            details: Additional timeout context
        """
        message = f"Test step '{step_name}' timed out after {timeout_seconds} seconds"

        exception_details = details or {}
        exception_details.update(
            {
                "step_name": step_name,
                "timeout_seconds": timeout_seconds,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.step_name = step_name
        self.timeout_seconds = timeout_seconds


class TestResourceException(TestExecutionException):
    """Exception raised when test resources violate business rules"""

    def __init__(
        self,
        resource_type: str,
        resource_issue: str,
        required_resources: Optional[List[str]] = None,
        available_resources: Optional[List[str]] = None,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test resource exception

        Args:
            resource_type: Type of resource with issue (e.g., 'hardware', 'configuration', 'file')
            resource_issue: Description of resource issue
            required_resources: List of required resources
            available_resources: List of available resources
            test_id: ID of the test
            details: Additional resource context
        """
        message = f"Test resource issue with {resource_type}: {resource_issue}"

        if required_resources and available_resources:
            missing = set(required_resources) - set(available_resources)
            if missing:
                message += f". Missing resources: {list(missing)}"

        exception_details = details or {}
        exception_details.update(
            {
                "resource_type": resource_type,
                "resource_issue": resource_issue,
                "required_resources": required_resources,
                "available_resources": available_resources,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.resource_type = resource_type
        self.resource_issue = resource_issue
        self.required_resources = required_resources
        self.available_resources = available_resources


class TestDataException(TestExecutionException):
    """Exception raised when test data violates business rules"""

    def __init__(
        self,
        data_type: str,
        data_issue: str,
        invalid_data: Any = None,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test data exception

        Args:
            data_type: Type of data with issue (e.g., 'measurement', 'configuration', 'result')
            data_issue: Description of data issue
            invalid_data: The invalid data that caused the issue
            test_id: ID of the test
            details: Additional data context
        """
        if invalid_data is not None:
            message = (
                f"Test data issue with {data_type}: {data_issue}. Invalid data: {invalid_data}"
            )
        else:
            message = f"Test data issue with {data_type}: {data_issue}"

        exception_details = details or {}
        exception_details.update(
            {
                "data_type": data_type,
                "data_issue": data_issue,
                "invalid_data": invalid_data,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.data_type = data_type
        self.data_issue = data_issue
        self.invalid_data = invalid_data


class TestCriteriaException(TestExecutionException):
    """Exception raised when test criteria violate business rules"""

    def __init__(
        self,
        criteria_type: str,
        criteria_violation: str,
        actual_value: Any = None,
        expected_criteria: Optional[Dict[str, Any]] = None,
        test_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize test criteria exception

        Args:
            criteria_type: Type of criteria violated (e.g., 'pass_fail', 'quality', 'performance')
            criteria_violation: Description of criteria violation
            actual_value: Actual value that violated criteria
            expected_criteria: Expected criteria that were violated
            test_id: ID of the test
            details: Additional criteria context
        """
        if actual_value is not None and expected_criteria:
            message = f"Test criteria violation for {criteria_type}: {criteria_violation}. Actual: {actual_value}, Expected: {expected_criteria}"
        else:
            message = f"Test criteria violation for {criteria_type}: {criteria_violation}"

        exception_details = details or {}
        exception_details.update(
            {
                "criteria_type": criteria_type,
                "criteria_violation": criteria_violation,
                "actual_value": actual_value,
                "expected_criteria": expected_criteria,
            }
        )

        super().__init__(message, test_id, exception_details)
        self.criteria_type = criteria_type
        self.criteria_violation = criteria_violation
        self.actual_value = actual_value
        self.expected_criteria = expected_criteria
