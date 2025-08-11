"""
Measurement Converter

Handles conversion of measurements between different formats for evaluation.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

from typing import Any, Dict

from src.domain.enums.measurement_units import MeasurementUnit
from src.domain.value_objects.measurements import ForceValue, TestMeasurements


class MeasurementConverter:
    """Handles measurement format conversion for test evaluation"""

    def convert_for_evaluation(self, measurements: TestMeasurements) -> Dict[str, Dict[str, Any]]:
        """
        Convert measurements to format required for evaluation

        Converts nested measurement structure to flat dictionary format
        required by the test result evaluator.

        Args:
            measurements: Test measurements to convert

        Returns:
            dict: Flattened measurements in evaluator-compatible format
        """
        # Convert measurements to dict format
        measurements_dict = measurements.to_legacy_dict()

        # Convert nested dict to flat dict for evaluator
        # Format: {temperature: {position: {"temperature": temp, "stroke": pos, "force": force}}}
        # Convert to: {"temp_pos": {"temperature": temp, "position": pos, "force": force}}
        flat_measurements = {}
        for temp, positions in measurements_dict.items():
            for position, measurement_data in positions.items():
                key = f"{temp}_{position}"
                flat_measurements[key] = {
                    "temperature": temp,  # Use raw temperature value
                    "position": position,
                    "force": ForceValue(measurement_data["force"], MeasurementUnit.NEWTON),
                }

        return flat_measurements
