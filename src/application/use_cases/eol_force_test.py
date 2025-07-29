"""
Execute EOL Test Use Case

Comprehensive use case for executing End-of-Line tests with full Exception First architecture.
This module implements robust error handling, hardware coordination, and test evaluation
following Exception First principles throughout the entire test execution workflow.

Key Features:
- Exception First error handling at all levels
- Comprehensive hardware service coordination
- Automated configuration management and validation
- Proper resource cleanup and error reporting
- Test result evaluation with detailed failure analysis
"""

import asyncio
from typing import Optional

from loguru import logger

from application.services.configuration_service import (
    ConfigurationService,
)
from application.services.configuration_validator import (
    ConfigurationValidator,
)
from application.services.exception_handler import (
    ExceptionHandler,
)
from application.services.hardware_service_facade import (
    HardwareServiceFacade,
)
from application.services.repository_service import (
    RepositoryService,
)
from application.services.test_result_evaluator import (
    TestResultEvaluator,
)
from domain.entities.dut import DUT
from domain.entities.eol_test import EOLTest
from domain.entities.test_result import TestResult

# Removed unused import: TestResult
from domain.enums.test_status import TestStatus
from domain.exceptions import (
    MultiConfigurationValidationError,
    TestEvaluationError,
)
from domain.exceptions.test_exceptions import (
    TestExecutionException,
)
from domain.value_objects.dut_command_info import (
    DUTCommandInfo,
)
from domain.value_objects.eol_test_result import (
    EOLTestResult,
)
from domain.value_objects.hardware_configuration import (
    HardwareConfiguration,
)
from domain.value_objects.identifiers import (
    DUTId,
    OperatorId,
    TestId,
)
from domain.value_objects.measurements import (
    TestMeasurements,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
)
from domain.value_objects.time_values import TestDuration, Timestamp


# Constants for readability and maintainability
class TestExecutionConstants:
    """Constants used throughout EOL test execution"""

    # Error messages
    TEST_CONFIG_REQUIRED_ERROR = "Test configuration must be loaded"
    HARDWARE_CONFIG_REQUIRED_ERROR = "Hardware configuration must be loaded"
    TEST_EVALUATION_FAILED_PREFIX = "Test evaluation failed: "
    CONFIG_VALIDATION_FAILED_PREFIX = "Configuration validation failed: "

    # Operations for exception context
    EXECUTE_EOL_TEST_OPERATION = "execute_eol_test"
    HARDWARE_SHUTDOWN_OPERATION = "hardware_shutdown_cleanup"


class EOLForceTestCommand:
    """EOL Test Execution Command"""

    def __init__(self, dut_info: DUTCommandInfo, operator_id: str):
        self.dut_info = dut_info
        self.operator_id = operator_id


class EOLForceTestUseCase:
    """
    EOL Test Execution Use Case with Exception First Architecture

    This use case orchestrates the complete End-of-Line testing process using
    Exception First principles for robust error handling. It coordinates hardware
    services, configuration management, and test evaluation while ensuring proper
    cleanup and error reporting.

    All operations follow Exception First patterns - methods either succeed or
    raise descriptive exceptions with detailed context for troubleshooting.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
        configuration_validator: ConfigurationValidator,
        repository_service: RepositoryService,
        exception_handler: ExceptionHandler,
        test_result_evaluator: TestResultEvaluator,
    ):
        # Core service dependencies
        self._hardware_services = hardware_services
        self._configuration = configuration_service
        self._configuration_validator = configuration_validator
        self._repository = repository_service
        self._exception_handler = exception_handler
        self._test_result_evaluator = test_result_evaluator

        # Configuration state
        self._profile_name: Optional[str] = None
        self._test_config: Optional[TestConfiguration] = None
        self._hardware_config: Optional[HardwareConfiguration] = None

    async def execute(self, command: EOLForceTestCommand) -> EOLTestResult:
        """
        Execute EOL test using Exception First principles

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
        logger.info(f"Starting EOL test for DUT {command.dut_info.dut_id}")

        # Phase 1: Initialize test setup
        await self._load_and_validate_configurations()
        test = await self._initialize_test_entity(command)

        # Phase 2: Execute test with proper error handling
        start_time = asyncio.get_event_loop().time()
        measurements: Optional[TestMeasurements] = None

        try:
            test.start_test()
            self._validate_configurations_loaded()

            # Phase 3: Execute hardware test phases
            measurements = await self._execute_hardware_test_phases()

            # Phase 4: Evaluate results and create success result
            is_test_passed = await self._evaluate_test_results(test, measurements)
            await self._save_test_state(test)

            execution_duration = self._calculate_execution_duration(start_time)
            logger.info(f"EOL test completed: {test.test_id}, passed: {is_test_passed}")

            return self._create_success_result(
                test,
                measurements,
                execution_duration,
                is_test_passed,
            )

        except Exception as e:
            # Phase 5: Handle test failure with proper error context
            return await self._handle_test_failure(e, test, command, measurements, start_time)

        finally:
            # Phase 6: Cleanup hardware resources (always executed)
            await self._cleanup_hardware_resources(test if "test" in locals() else None)

    async def _load_and_validate_configurations(
        self,
    ) -> None:
        """
        Load and validate all configurations for test execution

        This method handles the complete configuration loading workflow:
        1. Load active profile name
        2. Load test configuration
        3. Load hardware configuration
        4. Validate configurations
        5. Mark profile as used

        Raises:
            TestExecutionException: If configuration loading or validation fails
        """
        # Load profile name
        self._profile_name = await self._configuration.get_active_profile_name()

        # Load configuration
        self._test_config = await self._configuration.load_configuration(self._profile_name)

        # Load Hardware Configuration - this method doesn't exist, needs to be implemented
        # For now, create a default hardware configuration
        # pylint: disable=fixme
        # TODO: Implement load_hardware_config method in ConfigurationService
        self._hardware_config = HardwareConfiguration()

        # Validate configuration
        try:
            await self._configuration_validator.validate_test_configuration(self._test_config)
            logger.info("Configuration validation passed")
        except MultiConfigurationValidationError as e:
            logger.error(f"Configuration validation failed: {e.message}")
            raise TestExecutionException(
                f"Configuration validation failed: {e.get_context('total_errors')} errors found"
            ) from e

        # Mark profile as used (non-critical operation - don't fail test on error)
        try:
            await self._configuration.mark_profile_as_used(self._profile_name)
            logger.debug(f"Profile '{self._profile_name}' marked as used successfully")
        except Exception as pref_error:
            # Profile usage tracking failure should not interrupt test execution
            logger.warning(f"Failed to mark profile '{self._profile_name}' as used: {pref_error}")

    async def _initialize_test_entity(self, command: EOLForceTestCommand) -> EOLTest:
        """
        Initialize test entity with command data

        Args:
            command: Test execution command with DUT info and operator ID

        Returns:
            EOLTest: Initialized test entity ready for execution
        """
        # Create DUT entity from command info
        dut = DUT(
            dut_id=DUTId(command.dut_info.dut_id),
            model_number=command.dut_info.model_number,
            serial_number=command.dut_info.serial_number,
            manufacturer=command.dut_info.manufacturer,
        )

        # Create and configure test entity
        test = EOLTest(
            test_id=TestId.generate(),
            dut=dut,
            operator_id=OperatorId(command.operator_id),
            test_configuration=self._test_config.to_dict() if self._test_config else None,
        )

        return test

    def _validate_configurations_loaded(self) -> None:
        """
        Validate that all required configurations are loaded

        Raises:
            TestExecutionException: If any required configuration is missing
        """
        if self._test_config is None:
            raise TestExecutionException(TestExecutionConstants.TEST_CONFIG_REQUIRED_ERROR)

        if self._hardware_config is None:
            raise TestExecutionException(TestExecutionConstants.HARDWARE_CONFIG_REQUIRED_ERROR)

    async def _execute_hardware_test_phases(
        self,
    ) -> TestMeasurements:
        """
        Execute all hardware test phases and collect measurements

        Returns:
            TestMeasurements: Collected measurements from hardware tests

        Raises:
            TestExecutionException: If hardware test execution fails
        """
        logger.info("Starting hardware test phase execution")

        try:
            # Ensure configurations are validated and not None
            if self._test_config is None or self._hardware_config is None:
                raise TestExecutionException(
                    "Configurations must be loaded before hardware test execution"
                )

            # Connect all hardware
            await self._hardware_services.connect_all_hardware(self._hardware_config)
            logger.debug("Hardware connections initialized successfully")

            # Initialize hardware with configuration
            await self._hardware_services.initialize_hardware(
                self._test_config, self._hardware_config
            )

            # Setup test environment
            await self._hardware_services.setup_test(self._test_config, self._hardware_config)

            # Execute test measurements
            measurements = await self._hardware_services.perform_force_test_sequence(
                self._test_config, self._hardware_config
            )
            logger.info(
                f"Hardware test phases completed, {len(measurements)} measurements collected"
            )

            return measurements

        except Exception as hardware_error:
            logger.error(f"Hardware test execution failed: {hardware_error}")
            raise TestExecutionException(
                f"Hardware test execution failed: {str(hardware_error)}"
            ) from hardware_error

    async def _evaluate_test_results(self, test: EOLTest, measurements: TestMeasurements) -> bool:
        """
        Evaluate test results and determine pass/fail status

        Args:
            test: Test entity to update with results
            measurements: Collected test measurements

        Returns:
            bool: True if test passed, False if failed

        Raises:
            TestExecutionException: If test evaluation fails critically
        """
        logger.info("Starting test result evaluation")

        try:
            # Ensure test configuration is loaded (should be guaranteed by validation)
            if self._test_config is None:
                raise TestExecutionException("Test configuration must be loaded before evaluation")

            # Convert measurements to dict format and get pass criteria from config
            measurements_dict = measurements.to_dict()["measurements"]
            pass_criteria = self._test_config.pass_criteria

            # Perform test evaluation using the evaluator service
            # This will raise TestEvaluationError if evaluation fails
            await self._test_result_evaluator.evaluate_measurements(
                measurements_dict, pass_criteria
            )

            # If we reach here, evaluation passed
            # Create TestResult for successful test completion
            test_result = TestResult(
                test_id=test.test_id,
                test_status=TestStatus.COMPLETED,
                start_time=test.start_time or Timestamp.now(),
                end_time=Timestamp.now(),
                measurement_ids=[],  # TODO: Extract measurement IDs from measurements
                pass_criteria=pass_criteria.to_dict(),
                actual_results=measurements_dict,
            )
            test.complete_test(test_result)
            logger.info("Test evaluation: PASSED")
            return True

        except TestEvaluationError as eval_error:
            # Test evaluation failed - measurements didn't meet criteria
            error_message = f"Test evaluation failed: {len(eval_error.failed_points)} out of {eval_error.total_points} measurements failed"
            logger.error(error_message)

            # Create TestResult for failed test evaluation
            test_result = TestResult(
                test_id=test.test_id,
                test_status=TestStatus.FAILED,
                start_time=test.start_time or Timestamp.now(),
                end_time=Timestamp.now(),
                measurement_ids=[],  # TODO: Extract measurement IDs from measurements
                pass_criteria=pass_criteria.to_dict(),
                actual_results=measurements_dict,
                error_message=error_message,
            )
            # Mark test as failed with detailed error message
            test.fail_test(error_message, test_result)
            logger.info(f"Test evaluation: FAILED - {error_message}")
            return False

    async def _save_test_state(self, test: EOLTest) -> None:
        """
        Save test state to repository

        Args:
            test: Test entity to save

        Note:
            Failures in saving are logged but don't fail the test execution
        """
        try:
            await self._repository.save_test_result(test)
            logger.debug(f"Test state saved successfully for test ID: {test.test_id}")
        except Exception as save_error:
            # Repository save failures should not fail the test
            logger.warning(f"Failed to save test state: {save_error}")

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
        test: EOLTest,
        measurements: TestMeasurements,
        execution_duration: TestDuration,
        is_test_passed: bool,
    ) -> EOLTestResult:
        """
        Create successful test result object

        Args:
            test: Completed test entity
            measurements: Test measurements
            execution_duration: Total execution time
            is_test_passed: Whether test passed or failed

        Returns:
            EOLTestResult: Success result with all test data
        """
        return EOLTestResult(
            test_id=test.test_id,
            test_status=(TestStatus.COMPLETED if is_test_passed else TestStatus.FAILED),
            execution_duration=execution_duration,
            is_passed=is_test_passed,
            measurement_ids=[],  # TODO: Extract measurement IDs from measurements
            test_summary=measurements,
            error_message=None,
        )

    async def _handle_test_failure(  # pylint: disable=too-many-arguments
        self,
        error: Exception,
        test: EOLTest,
        command: EOLForceTestCommand,
        measurements: Optional[TestMeasurements],
        start_time: float,
    ) -> EOLTestResult:
        """
        Handle test failure and create appropriate result

        Args:
            error: Exception that caused the failure
            test: Test entity (may be incomplete)
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

        logger.error(f"EOL test failed: {error_context.get('user_message', str(error))}")

        # Try to save failure state if test entity exists
        if test is not None:
            try:
                test.fail_test(error_context.get("user_message", str(error)))
                await self._save_test_state(test)
            except Exception as save_error:
                logger.warning(f"Failed to save test failure state: {save_error}")

        # Create failure result with available data
        return EOLTestResult(
            test_id=(test.test_id if test else TestId.generate()),
            test_status=TestStatus.ERROR,
            execution_duration=execution_duration,
            is_passed=False,
            measurement_ids=[],  # TODO: Extract measurement IDs from measurements if available
            test_summary=measurements or {},
            error_message=error_context.get("user_message", str(error)),
        )

    async def _cleanup_hardware_resources(self, test: Optional[EOLTest]) -> None:
        """
        Clean up hardware resources and connections

        Args:
            test: Test entity for logging context (optional)

        Note:
            Cleanup failures are logged but never raise exceptions
        """
        try:
            # Only perform teardown if configurations are available
            if self._test_config and self._hardware_config:
                await self._hardware_services.teardown_test(
                    self._test_config, self._hardware_config
                )
            await self._hardware_services.shutdown_hardware()
            logger.debug("Hardware resources cleaned up successfully")
        except Exception as cleanup_error:
            # Hardware cleanup errors should never fail the test
            test_context = f" for test {test.test_id}" if test else ""
            logger.warning(f"Hardware cleanup failed{test_context}: {cleanup_error}")
