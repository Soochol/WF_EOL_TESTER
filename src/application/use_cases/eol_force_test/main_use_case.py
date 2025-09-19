"""
Main EOL Test Executor

Orchestrates EOL test execution using focused components.
Refactored from monolithic class for better maintainability while preserving exact functionality.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.core.configuration_service import ConfigurationService
from application.services.core.configuration_validator import ConfigurationValidator
from application.services.core.exception_handler import ExceptionHandler
from application.services.core.repository_service import RepositoryService
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.emergency_stop_service import (
    EmergencyStopService,
)
from application.services.test.test_result_evaluator import TestResultEvaluator
from domain.entities.eol_test import EOLTest
from domain.enums.test_status import TestStatus
from domain.exceptions.test_exceptions import TestExecutionException
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.eol_test_result import EOLTestResult
from domain.value_objects.identifiers import TestId
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.time_values import TestDuration

# Local folder imports
from ..common.base_use_case import BaseUseCase
from ..common.command_result_patterns import BaseUseCaseInput
from ..common.execution_context import ExecutionContext
from .configuration_loader import TestConfigurationLoader
from .constants import TestExecutionConstants
from .hardware_test_executor import HardwareTestExecutor
from .measurement_converter import MeasurementConverter
from .result_evaluator import ResultEvaluator
from .test_entity_factory import TestEntityFactory
from .test_state_manager import TestStateManager


class EOLForceTestInput(BaseUseCaseInput):
    """EOL Test Execution Input Data"""

    def __init__(self, dut_info: DUTCommandInfo, operator_id: str = "system"):
        super().__init__(operator_id)
        self.dut_info = dut_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary representation"""
        return {
            "operator_id": self.operator_id,
            "dut_info": {
                "dut_id": self.dut_info.dut_id,
                "model_number": self.dut_info.model_number,
                "serial_number": self.dut_info.serial_number,
                "manufacturer": self.dut_info.manufacturer,
            },
        }


class EOLForceTestUseCase(BaseUseCase):
    """
    EOL Test Execution Use Case with Component-Based Architecture

    Orchestrates the complete End-of-Line testing process using focused components
    for better maintainability while preserving exact functionality and execution order.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
        configuration_validator: ConfigurationValidator,
        test_result_evaluator: TestResultEvaluator,
        repository_service: RepositoryService,
        exception_handler: ExceptionHandler,
        emergency_stop_service: Optional[EmergencyStopService] = None,
    ):
        # Initialize BaseUseCase
        super().__init__("EOL Force Test", emergency_stop_service)

        # Core service dependencies (unchanged)
        self._hardware_services = hardware_services
        self._exception_handler = exception_handler

        # Inject repository service into hardware facade for cycle-by-cycle saving
        if hasattr(hardware_services, '_repository_service'):
            hardware_services._repository_service = repository_service

        # Initialize focused components
        self._config_loader = TestConfigurationLoader(
            configuration_service, configuration_validator
        )
        self._test_factory = TestEntityFactory(repository_service)
        self._hardware_executor = HardwareTestExecutor(hardware_services)
        self._measurement_converter = MeasurementConverter()
        self._state_manager = TestStateManager(repository_service)
        self._result_evaluator = ResultEvaluator(
            test_result_evaluator, self._measurement_converter, self._state_manager
        )

        # Emergency stop and interruption handling
        self._keyboard_interrupt_raised = False

    async def _execute_implementation(
        self, input_data: BaseUseCaseInput, context: ExecutionContext
    ) -> EOLTestResult:
        """
        Execute EOL test implementation (BaseUseCase abstract method)

        Args:
            input_data: Base input (will be cast to EOLForceTestInput)
            context: Execution context with timing and identification info

        Returns:
            EOLTestResult containing test outcome and execution details
        """
        # Cast to specific input type
        if not isinstance(input_data, EOLForceTestInput):
            raise ValueError(f"Expected EOLForceTestInput, got {type(input_data)}")

        eol_input = input_data

        # Execute single test - repeat_count is now handled within the force test sequence
        return await self.execute_single(eol_input)

    async def execute(self, input_data: EOLForceTestInput) -> EOLTestResult:
        """
        Execute EOL test (public interface)

        This method delegates to BaseUseCase.execute for consistent behavior.
        """
        result = await super().execute(input_data)
        # Result is guaranteed to be EOLTestResult since _execute_implementation returns one
        return result  # type: ignore

    def _create_failure_result(
        self,
        input_data: BaseUseCaseInput,
        context: ExecutionContext,
        execution_duration: TestDuration,
        error_message: str,
    ) -> EOLTestResult:
        """
        Create failure result for BaseUseCase compatibility

        Args:
            command: Original command that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description

        Returns:
            EOLTestResult indicating failure
        """
        return EOLTestResult.create_error(
            test_id=context.test_id, error_message=error_message, duration=execution_duration
        )

    async def execute_single(
        self, command: EOLForceTestInput, session_timestamp: Optional[str] = None
    ) -> EOLTestResult:
        """
        Execute EOL test using component-based architecture

        Args:
            command: Test execution command containing DUT info and operator ID
            session_timestamp: Optional session timestamp for CSV file grouping

        Returns:
            EOLTestResult containing test outcome, measurements, and execution details

        Raises:
            TestExecutionException: If configuration validation fails or critical test errors occur
            ConfigurationNotFoundError: If specified profile cannot be found
            RepositoryAccessError: If test data cannot be saved
            HardwareConnectionException: If hardware connection fails

        Note:
            This method follows Exception First principles - all operations either succeed
            or raise descriptive exceptions. Test failures are captured in the result
            object rather than raised as exceptions.
        """
        logger.info(TestExecutionConstants.LOG_TEST_EXECUTION_START, command.dut_info.dut_id)

        # Reset KeyboardInterrupt flag for each execution
        self._keyboard_interrupt_raised = False

        # Execute test with proper error handling (BaseUseCase handles _is_running)
        start_time = asyncio.get_event_loop().time()
        measurements: Optional[TestMeasurements] = None
        test_entity = None

        try:
            # Phase 1: Initialize test setup
            await self._config_loader.load_and_validate_configurations()
            test_entity = await self._test_factory.create_test_entity(
                command.dut_info,
                command.operator_id,
                self._config_loader.test_config,
                session_timestamp,
            )

            # Phase 2: Execute test
            test_entity.prepare_test()

            # Validate configurations are loaded (will raise exception if None)
            assert self._config_loader.test_config is not None
            assert self._config_loader.hardware_config is not None

            self._hardware_executor.validate_configurations_loaded(
                self._config_loader.test_config, self._config_loader.hardware_config
            )

            # Start test execution (transition from PREPARING to RUNNING)
            test_entity.start_execution()

            # Phase 3: Execute hardware test phases
            measurements = await self._hardware_executor.execute_hardware_test_phases(
                self._config_loader.test_config, self._config_loader.hardware_config
            )

            # Phase 4: Evaluate results and create success result
            is_test_passed = await self._result_evaluator.evaluate_measurements_and_update_test(
                test_entity, measurements, self._config_loader.test_config
            )
            await self._state_manager.save_test_state(test_entity)

            execution_duration = self._calculate_execution_duration(start_time)
            result_status = (
                TestExecutionConstants.TEST_RESULT_PASSED
                if is_test_passed
                else TestExecutionConstants.TEST_RESULT_FAILED
            )
            logger.info(
                TestExecutionConstants.LOG_TEST_EXECUTION_COMPLETED,
                test_entity.test_id,
                result_status,
            )

            return self._create_success_result(
                test_entity,
                measurements,
                execution_duration,
                is_test_passed,
            )

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt with emergency stop priority
            # Set flag to prevent normal cleanup in finally block
            self._keyboard_interrupt_raised = True
            # Don't perform normal cleanup - let emergency stop handle hardware safety
            # Re-raise to allow emergency stop service to execute
            raise
        except asyncio.CancelledError:
            # Handle CancelledError (from asyncio.sleep interruptions) as KeyboardInterrupt
            # Set flag to prevent normal cleanup in finally block
            self._keyboard_interrupt_raised = True
            # Convert CancelledError back to KeyboardInterrupt for emergency stop service
            raise KeyboardInterrupt("Test cancelled by user interrupt") from None
        except Exception as e:
            # Phase 5: Handle test failure with proper error context
            return await self._handle_test_failure(
                e, test_entity, command, measurements, start_time
            )

        finally:
            # Phase 6: Cleanup hardware resources (only if not interrupted)
            # Skip cleanup entirely if KeyboardInterrupt was raised - let Emergency Stop handle hardware safety
            if self._keyboard_interrupt_raised:
                # Skip cleanup - Emergency Stop Service will handle hardware safety
                pass
            else:
                # Normal cleanup for successful/failed tests (not interrupted)
                try:
                    await self._cleanup_hardware_resources(test_entity)
                except KeyboardInterrupt:
                    # If KeyboardInterrupt occurs during cleanup, prioritize emergency stop
                    self._keyboard_interrupt_raised = True
                    raise
                except Exception as cleanup_error:
                    # If standard cleanup fails, ensure power is still turned off for safety
                    logger.warning(
                        "Standard cleanup failed: {}, attempting emergency power off", cleanup_error
                    )
                    await self._emergency_power_off()

    def _calculate_execution_duration(self, start_time: float) -> TestDuration:
        """
        Calculate test execution duration

        Args:
            start_time: Test start time from event loop

        Returns:
            TestDuration: Calculated execution duration
        """
        end_time = asyncio.get_event_loop().time()
        duration_seconds = end_time - start_time
        return TestDuration.from_seconds(duration_seconds)

    def _create_success_result(
        self,
        test_entity: EOLTest,
        measurements: TestMeasurements,
        execution_duration: TestDuration,
        is_test_passed: bool,
    ) -> EOLTestResult:
        """
        Create successful test result object

        Args:
            test_entity: Completed test entity
            measurements: Test measurements
            execution_duration: Total execution time
            is_test_passed: Whether test passed or failed

        Returns:
            EOLTestResult: Success result with all test data
        """
        return EOLTestResult(
            test_id=test_entity.test_id,
            test_status=(TestStatus.COMPLETED if is_test_passed else TestStatus.FAILED),
            execution_duration=execution_duration,
            is_passed=is_test_passed,
            measurement_ids=self._state_manager.generate_measurement_ids(measurements),
            test_summary=measurements,
            error_message=None,
        )

    async def _handle_test_failure(  # pylint: disable=too-many-arguments
        self,
        error: Exception,
        test_entity: Optional[EOLTest],
        command: EOLForceTestInput,  # pylint: disable=unused-argument
        measurements: Optional[TestMeasurements],
        start_time: float,
    ) -> EOLTestResult:
        """
        Handle test failure and create appropriate result

        Args:
            error: Exception that caused the failure
            test_entity: Test entity (may be incomplete)
            command: Original command for fallback data
            measurements: Measurements collected before failure (if any)
            start_time: Test start time for duration calculation

        Returns:
            EOLTestResult: Failure result with error details
        """
        execution_duration = self._calculate_execution_duration(start_time)
        error_context = await self._exception_handler.handle_exception(
            error,
            TestExecutionConstants.EXECUTE_EOL_TEST_OPERATION,
        )

        logger.error("EOL test execution failed: {}", error_context.get("user_message", str(error)))

        # Try to save failure state if test entity exists
        if test_entity is not None:
            try:
                test_entity.fail_test(error_context.get("user_message", str(error)))
                await self._state_manager.save_test_state(test_entity)
            except Exception as save_error:
                logger.warning("Failed to save test entity failure state: {}", save_error)

        # Create failure result with available data
        return EOLTestResult(
            test_id=(test_entity.test_id if test_entity else TestId.generate()),
            test_status=TestStatus.ERROR,
            execution_duration=execution_duration,
            is_passed=False,
            measurement_ids=(
                self._state_manager.generate_measurement_ids(measurements) if measurements else []
            ),
            test_summary=measurements or {},
            error_message=error_context.get("user_message", str(error)),
        )

    async def _cleanup_hardware_resources(self, test_entity: Optional[EOLTest]) -> None:
        """
        Clean up hardware resources and connections

        Args:
            test_entity: Test entity for logging context (optional)

        Note:
            Cleanup failures are logged but never raise exceptions
        """
        try:
            # Only perform teardown if test configuration is available
            if self._config_loader.test_config and self._config_loader.hardware_config:
                await self._hardware_services.teardown_test(
                    self._config_loader.test_config, self._config_loader.hardware_config
                )
            await self._hardware_services.shutdown_hardware()
            logger.debug(TestExecutionConstants.LOG_HARDWARE_CLEANUP_SUCCESS)
        except Exception as cleanup_error:
            # Hardware cleanup errors should never fail the test
            test_context = f" for test entity {test_entity.test_id}" if test_entity else ""
            logger.warning("Hardware cleanup failed{}: {}", test_context, cleanup_error)

    async def _emergency_power_off(self) -> None:
        """
        Emergency power off when standard cleanup fails

        Attempts to disable power output regardless of configuration state
        for safety purposes. This is a last resort when normal teardown fails.
        """
        try:
            # Direct power service access for emergency shutdown
            power_service = self._hardware_services.power_service
            if power_service and await power_service.is_connected():
                await power_service.disable_output()
                logger.info("Emergency power off completed successfully")
            else:
                logger.warning("Power service not available for emergency power off")
        except Exception as emergency_error:
            # Even emergency power off failed - log critical error but don't raise
            logger.critical("Emergency power off failed: {}", emergency_error)

