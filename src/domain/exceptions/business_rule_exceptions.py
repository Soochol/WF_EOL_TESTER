"""
Business Rule Exceptions

Contains exceptions related to business rule violations in the domain.
"""

from domain.exceptions.domain_exceptions import DomainException


class BusinessRuleViolationException(DomainException):
    """Exception raised when a business rule is violated"""

    def __init__(self, rule_name: str, message: str, context: dict = None):
        """
        Initialize business rule violation exception

        Args:
            rule_name: Name or identifier of the violated rule
            message: Description of the rule violation
            context: Additional context about the violation
        """
        super().__init__(message, context)
        self.rule_name = rule_name


class UnsafeOperationException(BusinessRuleViolationException):
    """Exception raised when an operation would be unsafe"""

    def __init__(self, operation: str, reason: str, context: dict = None):
        """
        Initialize unsafe operation exception

        Args:
            operation: The operation that would be unsafe
            reason: Why the operation is unsafe
            context: Additional safety context
        """
        message = f"Unsafe operation '{operation}': {reason}"
        super().__init__("SAFETY_RULE", message, context)
        self.operation = operation
        self.reason = reason


class InvalidTestStateException(BusinessRuleViolationException):
    """Exception raised when test is in invalid state for operation"""

    def __init__(
        self, current_state: str, required_state: str, operation: str, context: dict = None
    ):
        """
        Initialize invalid test state exception

        Args:
            current_state: Current test state
            required_state: Required state for operation
            operation: The operation that was attempted
            context: Additional state context
        """
        message = f"Cannot perform '{operation}' in state '{current_state}'. Required state: '{required_state}'"
        context = context or {}
        context.update(
            {
                "current_state": current_state,
                "required_state": required_state,
                "operation": operation,
            }
        )
        super().__init__("TEST_STATE_RULE", message, context)
        self.current_state = current_state
        self.required_state = required_state
        self.operation = operation


class HardwareNotReadyException(BusinessRuleViolationException):
    """Exception raised when hardware is not ready for operation"""

    def __init__(
        self, hardware_type: str, current_status: str, operation: str, context: dict = None
    ):
        """
        Initialize hardware not ready exception

        Args:
            hardware_type: Type of hardware (e.g., 'loadcell', 'power_supply')
            current_status: Current hardware status
            operation: The operation that was attempted
            context: Additional hardware context
        """
        message = f"Hardware '{hardware_type}' not ready for '{operation}'. Current status: {current_status}"
        context = context or {}
        context.update(
            {
                "hardware_type": hardware_type,
                "current_status": current_status,
                "operation": operation,
            }
        )
        super().__init__("HARDWARE_READY_RULE", message, context)
        self.hardware_type = hardware_type
        self.current_status = current_status
        self.operation = operation
