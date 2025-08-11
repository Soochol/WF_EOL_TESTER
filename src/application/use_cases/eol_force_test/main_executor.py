"""
Main EOL Test Executor

Orchestrates EOL test execution using focused components.
Refactored from monolithic class for better maintainability while preserving exact functionality.
"""

import asyncio
from typing import Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.configuration_validator import ConfigurationValidator
from application.services.exception_handler import ExceptionHandler
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.test_result_evaluator import TestResultEvaluator
from domain.entities.eol_test import EOLTest
from domain.enums.test_status import TestStatus
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.eol_test_result import EOLTestResult
from domain.value_objects.identifiers import TestId
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.time_values import TestDuration

from .configuration_loader import TestConfigurationLoader
from .constants import TestExecutionConstants
from .hardware_test_executor import HardwareTestExecutor
from .measurement_converter import MeasurementConverter
from .result_evaluator import ResultEvaluator
from .test_entity_factory import TestEntityFactory
from .test_state_manager import TestStateManager


class EOLForceTestCommand:
    """EOL Test Execution Command"""

    def __init__(self, dut_info: DUTCommandInfo, operator_id: str):
        self.dut_info = dut_info
        self.operator_id = operator_id


class EOLForceTestUseCase:
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
    ):
        # Core service dependencies (unchanged)
        self._hardware_services = hardware_services
        self._exception_handler = exception_handler

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

        # Execution state for duplicate execution prevention
        self._is_running = False

    def is_running(self) -> bool:
        """
        Check if EOL test is currently running

        Returns:
            True if test is currently executing, False otherwise
        """
        return self._is_running

    async def execute(self, command: EOLForceTestCommand) -> EOLTestResult:
        """
        Execute EOL test using component-based architecture

        Args:
            command: Test execution command containing DUT info and operator ID

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

        # Set running flag to prevent duplicate execution
        self._is_running = True

        # Execute test with proper error handling
        start_time = asyncio.get_event_loop().time()
        measurements: Optional[TestMeasurements] = None
        test_entity = None

        try:
            # Phase 1: Initialize test setup
            await self._config_loader.load_and_validate_configurations()
            test_entity = await self._test_factory.create_test_entity(
                command.dut_info, command.operator_id, self._config_loader.test_config
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

        except Exception as e:
            # Phase 5: Handle test failure with proper error context
            return await self._handle_test_failure(
                e, test_entity, command, measurements, start_time
            )

        finally:
            # Phase 6: Cleanup hardware resources (always executed)
            await self._cleanup_hardware_resources(test_entity)

            # Clear running flag to allow future executions
            self._is_running = False

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
        command: EOLForceTestCommand,  # pylint: disable=unused-argument
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
