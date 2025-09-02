"""
Heating/Cooling Time Test Result

Result object for heating/cooling time test use case.
Contains all output data from the test execution.
"""

from typing import Any, Dict, Optional

from application.use_cases.common.command_result_patterns import BaseResult
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class HeatingCoolingTimeTestResult(BaseResult):
    """
    Result for Heating/Cooling Time Test
    
    Contains timing measurements, statistics, and power consumption data
    from heating/cooling cycle testing.
    """

    def __init__(
        self,
        test_status: TestStatus,
        is_success: bool,
        measurements: Dict[str, Any],
        error_message: Optional[str] = None,
        test_id: Optional[TestId] = None,
        execution_duration: Optional[TestDuration] = None,
    ):
        """
        Initialize test result

        Args:
            test_status: Test execution status
            is_success: Whether test passed or failed  
            measurements: Timing measurements and statistics
            error_message: Error message if test failed
            test_id: Unique test identifier
            execution_duration: Total test execution time
        """
        super().__init__(test_status, is_success, error_message, test_id, execution_duration)
        self.measurements = measurements

    @property
    def heating_count(self) -> int:
        """Number of heating measurements"""
        return len(self.measurements.get("heating_measurements", []))

    @property
    def cooling_count(self) -> int:
        """Number of cooling measurements"""
        return len(self.measurements.get("cooling_measurements", []))

    def format_duration(self) -> str:
        """Format execution duration as string"""
        if self.execution_duration:
            return f"{self.execution_duration.seconds:.3f}s"
        return "0.000s"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary representation
        
        Returns:
            Dictionary containing result data
        """
        return {
            "test_id": self.test_id.value if self.test_id else None,
            "test_status": self.test_status.value,
            "is_success": self.is_success,
            "execution_duration_seconds": self.execution_duration.seconds if self.execution_duration else 0,
            "measurements": self.measurements,
            "error_message": self.error_message,
            "heating_count": self.heating_count,
            "cooling_count": self.cooling_count,
        }

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the result
        
        Returns:
            Summary string
        """
        if not self.is_success:
            return f"Heating/Cooling Time Test FAILED: {self.error_message}"
        
        stats = self.measurements.get("statistics", {})
        avg_heating = stats.get("average_heating_time_ms", 0)
        avg_cooling = stats.get("average_cooling_time_ms", 0)
        cycles = stats.get("total_cycles", 0)
        energy = stats.get("total_energy_consumed_wh", 0)
        
        return (
            f"Heating/Cooling Time Test PASSED - "
            f"Cycles: {cycles}, "
            f"Avg Heating: {avg_heating:.1f}ms, "
            f"Avg Cooling: {avg_cooling:.1f}ms, "
            f"Energy: {energy:.3f}Wh"
        )
