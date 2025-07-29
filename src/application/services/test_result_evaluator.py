"""
Test Result Evaluator Service

Business service for evaluating test measurements against pass criteria.
Uses Exception First principles for error handling.
"""

from typing import Any, Dict, List

from loguru import logger

from domain.exceptions import TestEvaluationError, create_test_evaluation_error
from domain.value_objects.pass_criteria import PassCriteria


class TestResultEvaluator:
    """
    Service responsible for evaluating test measurement results

    This service encapsulates the business logic for determining whether
    test measurements pass or fail based on configured criteria.
    """

    def __init__(self):
        """Initialize the test result evaluator"""
        pass

    async def evaluate_measurements(self, measurements: Dict[str, Any], criteria: PassCriteria) -> None:
        """
        Evaluate measurement results against pass criteria

        Args:
            measurements: Dictionary of measurement data
            criteria: Pass/fail criteria to evaluate against

        Raises:
            TestEvaluationError: If evaluation fails or measurements don't meet criteria
            ValueError: If measurements or criteria are invalid
        """
        if not measurements:
            logger.warning("No measurements provided for evaluation")
            raise create_test_evaluation_error([{"error": "No measurements to evaluate"}], 0)

        if not criteria:
            logger.error("No pass criteria provided for evaluation")
            raise ValueError("Pass criteria cannot be None")

        failed_points = []
        total_points = 0

        logger.info(f"Starting evaluation of {len(measurements)} measurement entries")

        for key, measurement in measurements.items():
            # Skip non-measurement entries
            if not isinstance(measurement, dict):
                logger.debug(f"Skipping non-dict entry: {key}")
                continue

            # Extract measurement data
            temperature_obj = measurement.get("temperature")
            stroke = measurement.get("position")
            force_obj = measurement.get("force")

            # Extract numeric values from value objects
            temperature = temperature_obj.value if hasattr(temperature_obj, "value") else temperature_obj
            force = force_obj.value if hasattr(force_obj, "value") else force_obj

            # Validate measurement completeness
            if any(val is None for val in [temperature, stroke, force]):
                warning_msg = f"Incomplete measurement data in {key}: temp={temperature}, stroke={stroke}, force={force}"
                logger.warning(warning_msg)
                failed_points.append(
                    {
                        "key": key,
                        "error": "incomplete_data",
                        "message": warning_msg,
                        "temperature": temperature,
                        "stroke": stroke,
                        "force": force,
                    }
                )
                continue

            total_points += 1

            try:
                # Evaluate this measurement point
                evaluation_result = await self._evaluate_single_point(key, temperature, stroke, force, criteria)

                if not evaluation_result["passed"]:
                    failed_points.append(evaluation_result)

            except Exception as e:
                error_msg = f"Failed to evaluate measurement {key}: {e}"
                logger.error(error_msg)
                failed_points.append(
                    {
                        "key": key,
                        "error": "evaluation_failure",
                        "message": error_msg,
                        "exception": str(e),
                        "temperature": temperature,
                        "stroke": stroke,
                        "force": force,
                    }
                )

        # Log evaluation summary and raise exception if there are failures
        if failed_points:
            logger.warning(f"❌ Evaluation FAILED: {len(failed_points)}/{total_points} measurements outside specification")

            # Log first few failures for debugging
            for i, failure in enumerate(failed_points[:3]):
                if "force" in failure:
                    logger.warning(f"  Failure {i+1}: {failure['key']} - {failure.get('message', 'Unknown error')}")

            if len(failed_points) > 3:
                logger.warning(f"  ... and {len(failed_points) - 3} more failures")

            raise create_test_evaluation_error(failed_points, total_points)
        else:
            logger.info(f"✅ Evaluation PASSED: All {total_points} measurements within specification limits")

    async def _evaluate_single_point(
        self, key: str, temperature: float, stroke: float, force: float, criteria: PassCriteria
    ) -> Dict[str, Any]:
        """
        Evaluate a single measurement point against criteria

        Args:
            key: Measurement identifier
            temperature: Temperature value (°C)
            stroke: Stroke position value (mm)
            force: Force measurement value (N)
            criteria: Pass criteria to evaluate against

        Returns:
            Dictionary containing evaluation result and details
        """
        try:
            # Get interpolated force limits for this temperature-stroke point
            lower_limit, upper_limit = criteria.get_force_limits_at_point(temperature, stroke)

            # Check if measured force is within interpolated limits
            force_within_limits = lower_limit <= force <= upper_limit

            if force_within_limits:
                logger.debug(
                    f"✅ {key}: Force {force}N within limits [{lower_limit:.2f}, {upper_limit:.2f}]N at {temperature}°C, {stroke}mm"
                )
                return {
                    "key": key,
                    "passed": True,
                    "temperature": temperature,
                    "stroke": stroke,
                    "force": force,
                    "lower_limit": lower_limit,
                    "upper_limit": upper_limit,
                }
            else:
                failure_msg = (
                    f"Force {force}N outside limits [{lower_limit:.2f}, {upper_limit:.2f}]N at {temperature}°C, {stroke}mm"
                )
                logger.warning(f"❌ {key}: {failure_msg}")

                return {
                    "key": key,
                    "passed": False,
                    "error": "force_out_of_range",
                    "message": failure_msg,
                    "temperature": temperature,
                    "stroke": stroke,
                    "force": force,
                    "lower_limit": lower_limit,
                    "upper_limit": upper_limit,
                    "deviation": {
                        "from_lower": force - lower_limit,
                        "from_upper": force - upper_limit,
                        "percentage_lower": ((force - lower_limit) / lower_limit * 100) if lower_limit != 0 else float("inf"),
                        "percentage_upper": ((force - upper_limit) / upper_limit * 100) if upper_limit != 0 else float("inf"),
                    },
                }

        except Exception as e:
            error_msg = f"Failed to get force limits for {temperature}°C, {stroke}mm: {e}"
            logger.error(f"❌ {key}: {error_msg}")

            return {
                "key": key,
                "passed": False,
                "error": "criteria_evaluation_error",
                "message": error_msg,
                "exception": str(e),
                "temperature": temperature,
                "stroke": stroke,
                "force": force,
            }

    async def get_evaluation_summary(
        self, measurements: Dict[str, Any], test_evaluation_error: TestEvaluationError = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive evaluation summary

        Args:
            measurements: Original measurement data
            test_evaluation_error: Optional TestEvaluationError containing failure details

        Returns:
            Dictionary containing evaluation summary statistics
        """
        total_measurements = len([m for m in measurements.values() if isinstance(m, dict)])

        if test_evaluation_error:
            failed_points = test_evaluation_error.failed_points
            failed_count = len(failed_points)
            passed_count = total_measurements - failed_count

            # Categorize failures by type
            failure_categories = {}
            for failure in failed_points:
                error_type = failure.get("error", "unknown")
                if error_type not in failure_categories:
                    failure_categories[error_type] = []
                failure_categories[error_type].append(failure)
        else:
            failed_points = []
            failed_count = 0
            passed_count = total_measurements
            failure_categories = {}

        # Calculate statistics
        pass_rate = (passed_count / total_measurements * 100) if total_measurements > 0 else 0

        summary = {
            "overall_passed": failed_count == 0,
            "total_measurements": total_measurements,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pass_rate_percentage": round(pass_rate, 2),
            "failure_categories": {category: len(failures) for category, failures in failure_categories.items()},
            "detailed_failures": failed_points,
        }

        logger.info(f"Evaluation Summary: {passed_count}/{total_measurements} passed ({pass_rate:.1f}%)")

        return summary
