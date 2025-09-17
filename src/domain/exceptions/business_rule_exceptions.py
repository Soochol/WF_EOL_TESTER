# Business Rule Exceptions
# Standard library imports
from typing import Any, Dict, Optional

# Local application imports
from domain.exceptions.domain_exceptions import (
    DomainException,
)


class BusinessRuleViolationException(DomainException):
    def __init__(
        self,
        rule_name: str,
        message: str,
        context: Optional[Dict[Any, Any]] = None,
    ) -> None:
        super().__init__(message, details=context)
        self.rule_name = rule_name


class UnsafeOperationException(BusinessRuleViolationException):
    def __init__(
        self,
        operation: str,
        reason: str,
        context: Optional[Dict[Any, Any]] = None,
    ) -> None:
        message = f"Unsafe operation '{operation}': {reason}"
        super().__init__("SAFETY_RULE", message, context)
        self.operation = operation
        self.reason = reason


class InvalidTestStateException(BusinessRuleViolationException):
    def __init__(
        self,
        current_state: str,
        required_state: str,
        operation: str,
        context: Optional[Dict[Any, Any]] = None,
    ) -> None:
        message = f"Cannot perform '{operation}' in state '{current_state}'. Required state: '{required_state}'"
        ctx = context or {}
        ctx.update(
            {
                "current_state": current_state,
                "required_state": required_state,
                "operation": operation,
            }
        )
        super().__init__("TEST_STATE_RULE", message, ctx)
        self.current_state = current_state
        self.required_state = required_state
        self.operation = operation


class HardwareNotReadyException(BusinessRuleViolationException):
    def __init__(
        self,
        hardware_type: str,
        current_status: str,
        operation: str,
        context: Optional[Dict[Any, Any]] = None,
    ) -> None:
        message = f"Hardware '{hardware_type}' not ready for '{operation}'. Current status: {current_status}"
        ctx = context or {}
        ctx.update(
            {
                "hardware_type": hardware_type,
                "current_status": current_status,
                "operation": operation,
            }
        )
        super().__init__("HARDWARE_READY_RULE", message, ctx)
        self.hardware_type = hardware_type
        self.current_status = current_status
        self.operation = operation
