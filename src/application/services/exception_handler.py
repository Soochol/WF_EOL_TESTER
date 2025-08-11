"""
Exception Handler Service

Service for classifying, handling, and providing recovery strategies for exceptions.
"""

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type

from loguru import logger

from src.domain.exceptions.configuration_exceptions import (
    ConfigurationSecurityException,
    InvalidConfigurationException,
    MissingConfigurationException,
)
from src.domain.exceptions.hardware_exceptions import (
    HardwareConnectionException,
    HardwareLimitExceededException,
    HardwareTimeoutException,
    UnsafeOperationException,
)
from src.domain.exceptions.test_exceptions import (
    InvalidTestStateException,
    MeasurementValidationException,
    TestTimeoutException,
)


class ExceptionCategory(Enum):
    """Categories of exceptions for handling strategy"""

    RECOVERABLE = "recoverable"
    CRITICAL = "critical"
    TIMEOUT = "timeout"
    CONFIGURATION = "configuration"
    HARDWARE = "hardware"
    BUSINESS_RULE = "business_rule"
    UNKNOWN = "unknown"


class ExceptionSeverity(Enum):
    """Severity levels for exceptions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExceptionClassification:
    """Classification result for an exception"""

    category: ExceptionCategory
    severity: ExceptionSeverity
    retry_allowed: bool
    max_retry_attempts: int
    retry_delay_seconds: float
    auto_recovery: bool
    notification_required: bool
    escalation_required: bool
    description: str
    recovery_strategy: Optional[str] = None
    user_message: Optional[str] = None


@dataclass
class RetryContext:
    """Context for retry operations"""

    attempt_count: int
    total_attempts: int
    last_exception: Exception
    start_time: float
    operation_name: str
    backoff_multiplier: float = 1.5
    max_delay_seconds: float = 60.0


class ExceptionHandler:
    """
    Service for handling and classifying exceptions with recovery strategies
    """

    def __init__(self) -> None:
        """Initialize exception handler with classification rules"""
        self._classification_rules: Dict[Type[Exception], ExceptionClassification] = {}
        self._recovery_strategies: Dict[str, Callable] = {}
        self._retry_contexts: Dict[str, RetryContext] = {}

        # Initialize default classification rules
        self._initialize_classification_rules()
        self._initialize_recovery_strategies()

    def _initialize_classification_rules(self) -> None:
        """Initialize default exception classification rules"""

        # Hardware exceptions
        self._classification_rules[HardwareConnectionException] = ExceptionClassification(
            category=ExceptionCategory.HARDWARE,
            severity=ExceptionSeverity.HIGH,
            retry_allowed=True,
            max_retry_attempts=3,
            retry_delay_seconds=2.0,
            auto_recovery=True,
            notification_required=True,
            escalation_required=False,
            description="Hardware connection failure",
            recovery_strategy="reconnect_hardware",
            user_message="Hardware connection issue. Attempting to reconnect...",
        )

        self._classification_rules[HardwareTimeoutException] = ExceptionClassification(
            category=ExceptionCategory.TIMEOUT,
            severity=ExceptionSeverity.MEDIUM,
            retry_allowed=True,
            max_retry_attempts=2,
            retry_delay_seconds=1.0,
            auto_recovery=True,
            notification_required=False,
            escalation_required=False,
            description="Hardware operation timeout",
            recovery_strategy="retry_with_longer_timeout",
            user_message="Hardware operation timed out. Retrying...",
        )

        self._classification_rules[UnsafeOperationException] = ExceptionClassification(
            category=ExceptionCategory.CRITICAL,
            severity=ExceptionSeverity.CRITICAL,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=True,
            escalation_required=True,
            description="Unsafe operation attempted",
            recovery_strategy="emergency_stop",
            user_message="Unsafe operation detected. System stopped for safety.",
        )

        self._classification_rules[HardwareLimitExceededException] = ExceptionClassification(
            category=ExceptionCategory.CRITICAL,
            severity=ExceptionSeverity.HIGH,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=True,
            notification_required=True,
            escalation_required=True,
            description="Hardware safety limit exceeded",
            recovery_strategy="safe_shutdown",
            user_message="Safety limit exceeded. Initiating safe shutdown.",
        )

        # Test execution exceptions
        self._classification_rules[InvalidTestStateException] = ExceptionClassification(
            category=ExceptionCategory.BUSINESS_RULE,
            severity=ExceptionSeverity.MEDIUM,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=False,
            escalation_required=False,
            description="Invalid test state for operation",
            user_message="Test is not in the correct state for this operation.",
        )

        self._classification_rules[TestTimeoutException] = ExceptionClassification(
            category=ExceptionCategory.TIMEOUT,
            severity=ExceptionSeverity.MEDIUM,
            retry_allowed=True,
            max_retry_attempts=2,
            retry_delay_seconds=5.0,
            auto_recovery=True,
            notification_required=True,
            escalation_required=False,
            description="Test operation timeout",
            recovery_strategy="retry_with_extended_timeout",
            user_message="Test operation timed out. Retrying with extended timeout...",
        )

        self._classification_rules[MeasurementValidationException] = ExceptionClassification(
            category=ExceptionCategory.BUSINESS_RULE,
            severity=ExceptionSeverity.MEDIUM,
            retry_allowed=True,
            max_retry_attempts=1,
            retry_delay_seconds=2.0,
            auto_recovery=True,
            notification_required=False,
            escalation_required=False,
            description="Measurement validation failure",
            recovery_strategy="recalibrate_and_retry",
            user_message="Measurement validation failed. Recalibrating and retrying...",
        )

        # Configuration exceptions
        self._classification_rules[InvalidConfigurationException] = ExceptionClassification(
            category=ExceptionCategory.CONFIGURATION,
            severity=ExceptionSeverity.HIGH,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=True,
            escalation_required=False,
            description="Invalid configuration parameter",
            user_message="Configuration error. Please check configuration parameters.",
        )

        self._classification_rules[MissingConfigurationException] = ExceptionClassification(
            category=ExceptionCategory.CONFIGURATION,
            severity=ExceptionSeverity.HIGH,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=True,
            escalation_required=False,
            description="Missing required configuration",
            user_message="Missing required configuration. Please check configuration file.",
        )

        self._classification_rules[ConfigurationSecurityException] = ExceptionClassification(
            category=ExceptionCategory.CRITICAL,
            severity=ExceptionSeverity.CRITICAL,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=True,
            escalation_required=True,
            description="Configuration security violation",
            user_message="Security violation in configuration. System access restricted.",
        )

    def _initialize_recovery_strategies(self) -> None:
        """Initialize recovery strategy functions"""

        self._recovery_strategies = {
            "reconnect_hardware": self._reconnect_hardware_strategy,
            "retry_with_longer_timeout": self._retry_with_longer_timeout_strategy,
            "emergency_stop": self._emergency_stop_strategy,
            "safe_shutdown": self._safe_shutdown_strategy,
            "retry_with_extended_timeout": self._retry_with_extended_timeout_strategy,
            "recalibrate_and_retry": self._recalibrate_and_retry_strategy,
        }

    def classify_exception(self, exception: Exception) -> ExceptionClassification:
        """
        Classify an exception and determine handling strategy

        Args:
            exception: Exception to classify

        Returns:
            ExceptionClassification with handling strategy
        """
        exception_type = type(exception)

        # Check for exact type match
        if exception_type in self._classification_rules:
            classification = self._classification_rules[exception_type]
            logger.debug(
                f"Classified exception {exception_type.__name__} as {classification.category.value}"
            )
            return classification

        # Check for inheritance match
        for (
            rule_type,
            classification,
        ) in self._classification_rules.items():
            if isinstance(exception, rule_type):
                logger.debug(
                    f"Classified exception {exception_type.__name__} as {classification.category.value} (inherited from {rule_type.__name__})"
                )
                return classification

        # Default classification for unknown exceptions
        logger.warning(
            f"Unknown exception type {exception_type.__name__}, using default classification"
        )
        return ExceptionClassification(
            category=ExceptionCategory.UNKNOWN,
            severity=ExceptionSeverity.MEDIUM,
            retry_allowed=False,
            max_retry_attempts=0,
            retry_delay_seconds=0.0,
            auto_recovery=False,
            notification_required=True,
            escalation_required=False,
            description=f"Unknown exception: {exception_type.__name__}",
            user_message="An unexpected error occurred. Please contact support.",
        )

    def should_retry(
        self,
        exception: Exception,
        operation_name: str,
        attempt_count: int = 0,
    ) -> bool:
        """
        Determine if an operation should be retried after an exception

        Args:
            exception: The exception that occurred
            operation_name: Name of the operation for context tracking
            attempt_count: Current attempt count

        Returns:
            True if operation should be retried, False otherwise
        """
        classification = self.classify_exception(exception)

        if not classification.retry_allowed:
            logger.debug(f"Retry not allowed for {type(exception).__name__}")
            return False

        if attempt_count >= classification.max_retry_attempts:
            logger.debug(
                f"Max retry attempts ({classification.max_retry_attempts}) exceeded for {operation_name}"
            )
            return False

        # Update retry context
        if operation_name not in self._retry_contexts:
            self._retry_contexts[operation_name] = RetryContext(
                attempt_count=attempt_count,
                total_attempts=classification.max_retry_attempts,
                last_exception=exception,
                start_time=time.time(),
                operation_name=operation_name,
            )
        else:
            context = self._retry_contexts[operation_name]
            context.attempt_count = attempt_count
            context.last_exception = exception

        logger.info(
            f"Retry allowed for {operation_name}: attempt {attempt_count + 1}/{classification.max_retry_attempts}"
        )
        return True

    async def get_retry_delay(
        self,
        exception: Exception,
        operation_name: str,
        attempt_count: int,
    ) -> float:
        """
        Calculate retry delay for an operation

        Args:
            exception: The exception that occurred
            operation_name: Name of the operation
            attempt_count: Current attempt count

        Returns:
            Delay in seconds before retry
        """
        classification = self.classify_exception(exception)
        context = self._retry_contexts.get(operation_name)

        base_delay = classification.retry_delay_seconds

        if context:
            # Apply exponential backoff
            backoff_delay = base_delay * (context.backoff_multiplier**attempt_count)
            delay = min(backoff_delay, context.max_delay_seconds)
        else:
            delay = base_delay

        logger.debug(f"Retry delay for {operation_name}: {delay}s")
        return delay

    async def get_recovery_strategy(self, exception: Exception) -> Optional[Callable]:
        """
        Get recovery strategy function for an exception

        Args:
            exception: Exception that occurred

        Returns:
            Recovery strategy function or None if no strategy available
        """
        classification = self.classify_exception(exception)

        if classification.recovery_strategy:
            strategy = self._recovery_strategies.get(classification.recovery_strategy)
            if strategy:
                logger.debug(
                    f"Recovery strategy '{classification.recovery_strategy}' found for {type(exception).__name__}"
                )
                return strategy

            logger.warning(
                f"Recovery strategy '{classification.recovery_strategy}' not implemented"
            )

        return None

    async def handle_exception(
        self,
        exception: Exception,
        operation_name: str = "unknown_operation",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle an exception with full classification and recovery

        Args:
            exception: Exception to handle
            operation_name: Name of the operation that failed
            context: Additional context information

        Returns:
            Dictionary with handling results and recommendations
        """
        classification = self.classify_exception(exception)

        # Log the exception
        if classification.severity in [
            ExceptionSeverity.HIGH,
            ExceptionSeverity.CRITICAL,
        ]:
            logger.error(
                "Handling exception in {}: {}",
                operation_name,
                exception,
            )
        else:
            logger.warning(
                "Handling exception in {}: {}",
                operation_name,
                exception,
            )

        # Prepare handling result
        result = {
            "exception_type": type(exception).__name__,
            "operation_name": operation_name,
            "classification": classification,
            "handled": True,
            "recovery_attempted": False,
            "recovery_successful": False,
            "user_message": classification.user_message,
            "requires_escalation": classification.escalation_required,
            "context": context or {},
        }

        # Attempt automatic recovery if enabled
        if classification.auto_recovery:
            recovery_strategy = await self.get_recovery_strategy(exception)
            if recovery_strategy:
                try:
                    result["recovery_attempted"] = True
                    await recovery_strategy(exception, context or {})
                    result["recovery_successful"] = True
                    logger.info(f"Recovery successful for {operation_name}")
                except Exception as recovery_exception:
                    logger.error(f"Recovery failed for {operation_name}: {recovery_exception}")
                    result["recovery_exception"] = str(recovery_exception)

        # Clean up retry context if operation completed
        if operation_name in self._retry_contexts and not classification.retry_allowed:
            del self._retry_contexts[operation_name]

        return result

    def get_user_friendly_message(self, exception: Exception) -> str:
        """
        Get user-friendly error message for an exception

        Args:
            exception: Exception to get message for

        Returns:
            User-friendly error message
        """
        classification = self.classify_exception(exception)

        if classification.user_message:
            return classification.user_message

        # Fallback to exception message if no user message defined
        return str(exception)

    def clear_retry_context(self, operation_name: str) -> None:
        """
        Clear retry context for an operation

        Args:
            operation_name: Name of operation to clear context for
        """
        if operation_name in self._retry_contexts:
            del self._retry_contexts[operation_name]
            logger.debug(f"Cleared retry context for {operation_name}")

    # Recovery strategy implementations

    async def _reconnect_hardware_strategy(
        self, exception: Exception, context: Dict[str, Any]
    ) -> None:
        """Recovery strategy for hardware connection issues"""
        logger.info("Executing reconnect hardware recovery strategy")
        # Implementation would reconnect to hardware
        # This is a placeholder for actual hardware reconnection logic
        await asyncio.sleep(1.0)  # Simulate reconnection time

    async def _retry_with_longer_timeout_strategy(
        self, exception: Exception, context: Dict[str, Any]
    ) -> None:
        """Recovery strategy for timeout issues with extended timeout"""
        logger.info("Executing retry with longer timeout recovery strategy")
        # Implementation would retry operation with longer timeout
        await asyncio.sleep(0.5)  # Simulate strategy execution time

    async def _emergency_stop_strategy(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Recovery strategy for emergency stop situations"""
        logger.critical("Executing emergency stop recovery strategy")
        # Implementation would perform emergency stop of all hardware
        await asyncio.sleep(0.1)  # Simulate emergency stop time

    async def _safe_shutdown_strategy(self, exception: Exception, context: Dict[str, Any]) -> None:
        """Recovery strategy for safe system shutdown"""
        logger.warning("Executing safe shutdown recovery strategy")
        # Implementation would safely shut down all systems
        await asyncio.sleep(2.0)  # Simulate safe shutdown time

    async def _retry_with_extended_timeout_strategy(
        self, exception: Exception, context: Dict[str, Any]
    ) -> None:
        """Recovery strategy for test timeouts with extended timeout"""
        logger.info("Executing retry with extended timeout recovery strategy")
        # Implementation would retry test with extended timeout
        await asyncio.sleep(1.0)  # Simulate strategy execution time

    async def _recalibrate_and_retry_strategy(
        self, exception: Exception, context: Dict[str, Any]
    ) -> None:
        """Recovery strategy for measurement validation issues"""
        logger.info("Executing recalibrate and retry recovery strategy")
        # Implementation would recalibrate measurement devices and retry
        await asyncio.sleep(3.0)  # Simulate recalibration time
