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
from domain.exceptions.test_exceptions import TestExecutionException
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
        Execute EOL test with support for repetition
        
        This method handles test repetition based on the repeat_count configuration.
        For repeat_count > 1, it executes multiple test cycles and aggregates results.
        For repeat_count = 1, it behaves as a single test execution.
        
        Args:
            command: Test execution command containing DUT info and operator ID
            
        Returns:
            EOLTestResult containing aggregated test outcome and execution details
            
        Raises:
            TestExecutionException: If configuration validation fails or critical test errors occur
            ConfigurationNotFoundError: If specified profile cannot be found
            RepositoryAccessError: If test data cannot be saved
            HardwareConnectionException: If hardware connection fails
        """
        # Load configuration to check repeat_count
        await self._config_loader.load_and_validate_configurations()
        test_config = self._config_loader.test_config
        
        if test_config is None:
            raise TestExecutionException(
                message="Test configuration could not be loaded",
                details={"command": str(command)}
            )
        
        repeat_count = test_config.repeat_count
        
        if repeat_count == 1:
            # Single execution - use original logic
            return await self.execute_single(command)
        else:
            # Multiple executions - handle repetition
            return await self._execute_repeated(command, repeat_count)
    
    async def execute_single(self, command: EOLForceTestCommand) -> EOLTestResult:
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

    async def _execute_repeated(self, command: EOLForceTestCommand, repeat_count: int) -> EOLTestResult:
        """
        Execute repeated test cycles and aggregate results
        
        Args:
            command: Original test execution command
            repeat_count: Number of test repetitions to perform
            
        Returns:
            EOLTestResult containing aggregated results from all repetitions
        """
        logger.info(f"Starting repeated EOL test execution: {repeat_count} repetitions for DUT {command.dut_info.dut_id}")
        
        # Set running flag to prevent duplicate execution
        self._is_running = True
        overall_start_time = asyncio.get_event_loop().time()
        
        all_results = []
        successful_tests = 0
        failed_tests = 0
        
        try:
            for cycle in range(1, repeat_count + 1):
                logger.info(f"Executing test cycle {cycle}/{repeat_count} for DUT {command.dut_info.dut_id}")
                
                # Create unique DUT info for this cycle
                cycle_dut_info = DUTCommandInfo(
                    dut_id=f"{command.dut_info.dut_id}_cycle_{cycle:03d}",
                    model_number=command.dut_info.model_number,
                    serial_number=f"{command.dut_info.serial_number}_C{cycle:03d}",
                    manufacturer=command.dut_info.manufacturer
                )
                
                cycle_command = EOLForceTestCommand(
                    dut_info=cycle_dut_info,
                    operator_id=command.operator_id
                )
                
                try:
                    # Execute single test cycle
                    result = await self.execute_single(cycle_command)
                    all_results.append(result)
                    
                    if result.is_passed:
                        successful_tests += 1
                        logger.info(f"Test cycle {cycle}/{repeat_count} PASSED for DUT {cycle_dut_info.dut_id}")
                    else:
                        failed_tests += 1
                        logger.warning(f"Test cycle {cycle}/{repeat_count} FAILED for DUT {cycle_dut_info.dut_id}")
                        
                except Exception as cycle_error:
                    failed_tests += 1
                    logger.error(f"Test cycle {cycle}/{repeat_count} ERROR for DUT {cycle_dut_info.dut_id}: {cycle_error}")
                    # Continue with next cycle even if one fails
                
                # Add delay between cycles for hardware stabilization (except for last cycle)
                if cycle < repeat_count:
                    stabilization_delay = 2.0  # 2 seconds between cycles
                    logger.debug(f"Waiting {stabilization_delay}s between test cycles...")
                    await asyncio.sleep(stabilization_delay)
            
            # Create aggregated result
            overall_duration = self._calculate_execution_duration(overall_start_time)
            overall_passed = successful_tests > 0  # At least one test must pass
            
            # Use the first successful result as template, or first result if none successful
            template_result = None
            for result in all_results:
                if result.is_passed:
                    template_result = result
                    break
            if template_result is None and all_results:
                template_result = all_results[0]
            
            if template_result is None:
                # No results at all - create a failure result
                return EOLTestResult(
                    test_id=TestId.generate(),
                    test_status=TestStatus.ERROR,
                    is_passed=False,
                    execution_duration=overall_duration,
                    error_message=f"All {repeat_count} test cycles failed to execute"
                )
            
            # Create summary result
            summary_result = EOLTestResult(
                test_id=TestId.generate(),
                test_status=TestStatus.COMPLETED if overall_passed else TestStatus.FAILED,
                is_passed=overall_passed,
                test_summary=template_result.test_summary,  # Use template measurements
                execution_duration=overall_duration,
                error_message=f"Repeated test summary: {successful_tests}/{repeat_count} cycles passed, {failed_tests}/{repeat_count} cycles failed" if failed_tests > 0 else None,
                completed_at=template_result.completed_at
            )
            
            logger.info(f"Repeated EOL test completed: {successful_tests}/{repeat_count} cycles passed for DUT {command.dut_info.dut_id}")
            return summary_result
            
        finally:
            # Clear running flag
            self._is_running = False
