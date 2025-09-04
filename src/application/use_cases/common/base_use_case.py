"""
Base Use Case

Abstract base class providing common functionality for all use cases.
Implements common patterns and ensures consistency across use cases.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from loguru import logger

from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration, Timestamp

from .command_result_patterns import BaseResult, BaseUseCaseInput
from .execution_context import ExecutionContext

if TYPE_CHECKING:
    from application.services.monitoring.emergency_stop_service import EmergencyStopService


class BaseUseCase(ABC):
    """
    Abstract base class for all use cases

    Provides:
    - Common execution patterns
    - Error handling framework
    - Logging standardization
    - Timing and context management
    """

    def __init__(self, use_case_name: str, emergency_stop_service: Optional["EmergencyStopService"] = None):
        """
        Initialize base use case

        Args:
            use_case_name: Human-readable name for this use case
            emergency_stop_service: Emergency stop service for hardware safety (optional)
        """
        self._use_case_name = use_case_name
        self._is_running = False
        self._emergency_stop_service = emergency_stop_service

    @property
    def use_case_name(self) -> str:
        """Get the use case name"""
        return self._use_case_name

    @property
    def is_running(self) -> bool:
        """Check if use case is currently executing"""
        return self._is_running

    async def execute(self, command: BaseUseCaseInput) -> BaseResult:
        """
        Execute the use case with proper error handling and context management

        Args:
            command: Command object containing execution parameters

        Returns:
            Result object containing execution results

        Raises:
            ValueError: If use case is already running
            Exception: Any exception from the concrete implementation
        """
        if self._is_running:
            raise ValueError(f"Use case '{self._use_case_name}' is already running")

        self._is_running = True
        context = ExecutionContext(
            test_id=TestId.generate(),
            use_case_name=self._use_case_name,
            operator_id=command.operator_id,
            start_time=Timestamp.now(),
        )

        logger.info(
            f"Starting use case '{self._use_case_name}' with test_id={context.test_id.value}"
        )

        try:
            result = await self._execute_implementation(command, context)

            context.end_time = Timestamp.now()
            execution_duration = TestDuration(context.end_time.value - context.start_time.value)

            # Update result with execution context information
            result.test_id = context.test_id
            result.execution_duration = execution_duration

            logger.info(
                f"Completed use case '{self._use_case_name}' - "
                f"Duration: {execution_duration.seconds}s, "
                f"Success: {result.is_success}"
            )

            return result

        except KeyboardInterrupt:
            logger.info(f"Use case '{self._use_case_name}' interrupted by user (Ctrl+C)")
            context.end_time = Timestamp.now()
            execution_duration = TestDuration(context.end_time.value - context.start_time.value)

            # Execute emergency stop if service is available and not already active
            if self._emergency_stop_service and not self._emergency_stop_service.is_emergency_active():
                try:
                    logger.info("Executing emergency stop from UseCase...")
                    await self._emergency_stop_service.execute_emergency_stop()
                    logger.info("Emergency stop completed from UseCase")
                except Exception as e:
                    logger.error(f"Emergency stop failed in UseCase: {e}")
                    # Continue with normal interrupt handling even if emergency stop fails

            # Create interruption result
            result = self._create_failure_result(
                command, context, execution_duration, "Test interrupted by user"
            )

            # Re-raise KeyboardInterrupt to allow proper cleanup handling at higher levels
            raise

        except Exception as e:
            logger.error(f"Use case '{self._use_case_name}' failed: {e}")
            context.end_time = Timestamp.now()
            execution_duration = TestDuration(context.end_time.value - context.start_time.value)

            # Create failure result
            result = self._create_failure_result(command, context, execution_duration, str(e))
            return result

        finally:
            self._is_running = False

    @abstractmethod
    async def _execute_implementation(
        self, command: BaseUseCaseInput, context: ExecutionContext
    ) -> BaseResult:
        """
        Concrete implementation of the use case logic

        Args:
            command: Command object containing execution parameters
            context: Execution context with timing and identification info

        Returns:
            Result object containing execution results
        """
        pass

    @abstractmethod
    def _create_failure_result(
        self,
        command: BaseUseCaseInput,
        context: ExecutionContext,
        execution_duration: TestDuration,
        error_message: str,
    ) -> BaseResult:
        """
        Create a failure result when execution fails

        Args:
            command: Original command that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description

        Returns:
            Result object indicating failure
        """
        pass
