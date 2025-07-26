"""
Execute EOL Test Use Case

Simplified use case for executing End-of-Line tests.
"""

import asyncio
from typing import Optional
from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
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
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.exceptions.test_exceptions import TestExecutionException


class ExecuteEOLTestCommand:
    """EOL Test Execution Command"""

    def __init__(
        self,
        dut_info: DUTCommandInfo,
        operator_id: str
    ):
        self.dut_info = dut_info
        self.operator_id = operator_id


class ExecuteEOLTestUseCase:
    """EOL Test Execution Use Case with Direct Service Dependencies"""

    def __init__(
        self,
        hardware_services: HardwareServiceFacade,
        repository_service: RepositoryService,
        exception_handler: ExceptionHandler,
        configuration_validator: ConfigurationValidator,
        test_result_evaluator: TestResultEvaluator
    ):
        self._hardware = hardware_services
        self._repository = repository_service
        self._exception_handler = exception_handler
        self._configuration_validator = configuration_validator
        self._test_result_evaluator = test_result_evaluator
        self._profile_name: Optional[str] = None
        self._test_config: Optional[TestConfiguration] = None
        self._hardware_config: Optional[HardwareConfiguration] = None

    async def execute(self, command: ExecuteEOLTestCommand) -> EOLTestResult:
        """
        Execute EOL test

        Args:
            command: Test execution command

        Returns:
            Test execution result
        """
        logger.info(f"Starting EOL test for DUT {command.dut_info.dut_id}")

        # Load profile name
        self._profile_name = await self._repository.get_active_profile_name()

        # Load configurations
        self._test_config, self._hardware_config = await self._repository.load_configurations(
            self._profile_name
        )

        # Validate configurations
        all_valid, validation_errors = await self._configuration_validator.validate_all_configurations(
            self._test_config, self._hardware_config
        )

        if not all_valid:
            error_summary = self._format_validation_errors(validation_errors)
            raise ValueError(f"Configuration validation failed: {error_summary}")

        # Mark profile as used (fire-and-forget)
        try:
            await self._repository.mark_profile_as_used(self._profile_name)
        except Exception as pref_error:
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
            await self._hardware.initialize_hardware(self._test_config, self._hardware_config)

            # setup test sequence
            await self._hardware.setup_test(self._test_config, self._hardware_config)

            # Main Test phase - Use hardware facade
            measurements = await self._hardware.perform_force_test_sequence(self._test_config, self._hardware_config)

            # Test Teardown test sequence
            await self._hardware.teardown_test(self._test_config, self._hardware_config)

            # Evaluate results using test result evaluator
            passed, failed_points = await self._test_result_evaluator.evaluate_measurements(
                measurements, self._test_config.pass_criteria
            )

            # Test completion
            if passed:
                test.complete_test()
            else:
                test.fail_test("Measurements outside acceptable range")

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

    def _format_validation_errors(self, validation_errors):
        """Format validation errors into a readable summary"""
        error_parts = []
        
        for config_type, errors in validation_errors.items():
            if errors:
                error_list = "; ".join(errors)
                error_parts.append(f"{config_type}: {error_list}")
        
        return " | ".join(error_parts) if error_parts else "Unknown validation errors"