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
from typing import Optional, Any
from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.configuration_service import ConfigurationService
from application.services.exception_handler import ExceptionHandler
from application.services.configuration_validator import ConfigurationValidator
from application.services.test_result_evaluator import TestResultEvaluator
from domain.entities.eol_test import EOLTest
from domain.entities.dut import DUT
from domain.enums.test_status import TestStatus
from domain.value_objects.eol_test_result import EOLTestResult
from domain.value_objects.identifiers import TestId, MeasurementId
from domain.value_objects.time_values import TestDuration
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.test_configuration import TestConfiguration
from domain.exceptions.test_exceptions import TestExecutionException
from domain.exceptions import (
    MultiConfigurationValidationError,
    TestEvaluationError,
    RepositoryAccessError,
    ConfigurationNotFoundError
)


class EOLForceTestCommand:
    """EOL Test Execution Command"""

    def __init__(
        self,
        dut_info: DUTCommandInfo,
        operator_id: str
    ):
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

    def __init__(
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
        configuration_validator: ConfigurationValidator,
        repository_service: RepositoryService,
        exception_handler: ExceptionHandler,
        test_result_evaluator: TestResultEvaluator
    ):
        self._hardware = hardware_services
        self._configuration = configuration_service
        self._configuration_validator = configuration_validator
        self._repository = repository_service
        self._exception_handler = exception_handler
        self._test_result_evaluator = test_result_evaluator
        self._profile_name: Optional[str] = None
        self._test_config: Optional[TestConfiguration] = None

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

        # Load profile name
        self._profile_name = await self._configuration.get_active_profile_name()

        # Load configuration
        self._test_config = await self._configuration.load_configuration(
            self._profile_name
        )

        # Validate configuration
        try:
            await self._configuration_validator.validate_test_configuration(
                self._test_config
            )
            logger.info("Configuration validation passed")
        except MultiConfigurationValidationError as e:
            logger.error(f"Configuration validation failed: {e.message}")
            raise TestExecutionException(
                f"Configuration validation failed: {e.get_context('total_errors')} errors found"
            )

        # Mark profile as used (non-critical operation - don't fail test on error)
        try:
            await self._configuration.mark_profile_as_used(self._profile_name)
            logger.debug(f"Profile '{self._profile_name}' marked as used successfully")
        except Exception as pref_error:
            # Profile usage tracking failure should not interrupt test execution
            logger.warning(f"Failed to mark profile '{self._profile_name}' as used: {pref_error}")

        # Create test entity
        dut = DUT.from_command_info(command.dut_info)

        test = EOLTest(
            test_id=TestId.generate(),
            dut=dut,
            operator_id=command.operator_id
        )

        # Save test
        await self._repository.test_repository.save(test)

        measurements = {}
        start_time = asyncio.get_event_loop().time()

        try:
            test.start_test()

            # Setup phase
            await self._hardware.connect_all_hardware()
            await self._hardware.initialize_hardware(self._test_config)

            # setup test sequence
            await self._hardware.setup_test(self._test_config)

            # Main Test phase - Use hardware facade
            measurements = await self._hardware.perform_force_test_sequence(self._test_config)

            # Test Teardown test sequence
            await self._hardware.teardown_test(self._test_config)

            # Evaluate results using test result evaluator
            try:
                await self._test_result_evaluator.evaluate_measurements(
                    measurements, self._test_config.pass_criteria
                )
                # If no exception, test passed
                test.complete_test()
                passed = True
            except TestEvaluationError as e:
                # Test failed - use exception data
                test.fail_test(f"Test evaluation failed: {e.get_failure_summary()}")
                passed = False

            # Save final test state
            await self._repository.test_repository.update(test)

            # Calculate execution duration
            duration = asyncio.get_event_loop().time() - start_time

            logger.info(f"EOL test completed: {test.test_id}, passed: {passed}")

            return EOLTestResult(
                test_id=test.test_id,
                test_status=test.status,
                execution_duration=TestDuration.from_seconds(duration),
                is_passed=passed,
                measurement_ids=[MeasurementId.generate() for _ in measurements],
                test_summary=measurements,
                error_message=None
            )

        except Exception as e:
            # Handle exception through exception handler
            context = {
                "operation": "execute_eol_test",
                "test_id": str(test.test_id),
                "dut_id": command.dut_info.dut_id,
                "measurements_count": len(measurements)
            }
            handled_exception = await self._exception_handler.handle_exception(e, context)

            test.fail_test(str(handled_exception))
            await self._repository.test_repository.update(test)

            duration = asyncio.get_event_loop().time() - start_time

            return EOLTestResult(
                test_id=test.test_id,
                test_status=TestStatus.FAILED,
                execution_duration=TestDuration.from_seconds(duration),
                is_passed=False,
                measurement_ids=[MeasurementId.generate() for _ in measurements],
                test_summary=measurements,
                error_message=str(handled_exception)
            )

        finally:
            # 3. Clean Up phase (always executed)
            try:
                await self._hardware.shutdown_hardware()
            except Exception as cleanup_error:
                context = {
                    "operation": "hardware_shutdown_cleanup",
                    "test_id": str(test.test_id) if 'test' in locals() else None
                }
                await self._exception_handler.handle_exception(cleanup_error, context)

