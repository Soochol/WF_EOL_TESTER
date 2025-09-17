"""
Result Evaluator

Handles test result evaluation and determination of pass/fail status.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

# Standard library imports
from typing import Any, Optional

# Third-party imports
from loguru import logger

# Local application imports
from application.services.test.test_result_evaluator import TestResultEvaluator
from domain.entities.eol_test import EOLTest
from domain.entities.test_result import TestResult
from domain.enums.test_status import TestStatus
from domain.exceptions import TestEvaluationError
from domain.exceptions.test_exceptions import TestExecutionException
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.time_values import Timestamp

# Local folder imports
from .constants import TestExecutionConstants
from .measurement_converter import MeasurementConverter
from .test_state_manager import TestStateManager


class ResultEvaluator:
    """Handles test result evaluation and pass/fail determination"""

    def __init__(
        self,
        test_result_evaluator: TestResultEvaluator,
        measurement_converter: MeasurementConverter,
        test_state_manager: TestStateManager,
    ):
        self._test_result_evaluator = test_result_evaluator
        self._measurement_converter = measurement_converter
        self._test_state_manager = test_state_manager

    async def evaluate_measurements_and_update_test(
        self,
        test_entity: EOLTest,
        measurements: TestMeasurements,
        test_config: TestConfiguration,
    ) -> bool:
        """
        Evaluate test results and determine pass/fail status

        Args:
            test_entity: Test entity to update with results
            measurements: Collected test measurements
            test_config: Test configuration with pass criteria

        Returns:
            bool: True if test passed, False if failed

        Raises:
            TestExecutionException: If test evaluation fails critically
        """
        logger.info(TestExecutionConstants.LOG_TEST_EVALUATION_START)

        # Validate test configuration is available
        if test_config is None:
            raise TestExecutionException(TestExecutionConstants.TEST_CONFIG_BEFORE_EVALUATION_ERROR)

        test_pass_criteria = test_config.pass_criteria
        evaluation_ready_measurements = self._measurement_converter.convert_for_evaluation(
            measurements
        )

        try:
            # Perform test evaluation using the evaluator service
            # This will raise TestEvaluationError if evaluation fails
            await self._test_result_evaluator.evaluate_measurements(
                evaluation_ready_measurements, test_pass_criteria
            )

            # If we reach here, evaluation passed
            test_result = self._create_test_result(
                test_entity, measurements, test_pass_criteria, TestStatus.COMPLETED
            )
            test_entity.complete_test(test_result)
            logger.info(TestExecutionConstants.LOG_TEST_EVALUATION_PASSED)
            return True

        except TestEvaluationError as eval_error:
            # Test evaluation failed - measurements didn't meet criteria
            error_message = self._format_evaluation_error_message(eval_error)
            logger.error(error_message)

            test_result = self._create_test_result(
                test_entity, measurements, test_pass_criteria, TestStatus.FAILED, error_message
            )
            test_entity.fail_test(error_message, test_result)
            logger.info(TestExecutionConstants.LOG_TEST_EVALUATION_FAILED, error_message)
            return False

    def _create_test_result(
        self,
        test_entity: EOLTest,
        measurements: TestMeasurements,
        pass_criteria: Any,
        status: TestStatus,
        error_message: Optional[str] = None,
    ) -> TestResult:
        """
        Create TestResult with common parameters

        Args:
            test_entity: Test entity containing test metadata
            measurements: Test measurements data
            pass_criteria: Pass criteria configuration
            status: Test status (COMPLETED, FAILED, etc.)
            error_message: Optional error message for failed tests

        Returns:
            TestResult: Configured test result object
        """
        return TestResult(
            test_id=test_entity.test_id,
            test_status=status,
            start_time=test_entity.start_time or Timestamp.now(),
            end_time=Timestamp.now(),
            measurement_ids=self._test_state_manager.generate_measurement_ids(measurements),
            pass_criteria=pass_criteria.to_dict(),
            actual_results=measurements.to_dict(),
            error_message=error_message,
        )

    def _format_evaluation_error_message(self, eval_error: TestEvaluationError) -> str:
        """
        Format evaluation error into user-friendly message

        Args:
            eval_error: TestEvaluationError with failure details

        Returns:
            str: Formatted error message
        """
        return f"Test evaluation failed: {len(eval_error.failed_points)} out of {eval_error.total_points} measurements failed"
