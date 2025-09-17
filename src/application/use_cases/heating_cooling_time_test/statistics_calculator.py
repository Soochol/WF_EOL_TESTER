"""
Statistics Calculator for Heating/Cooling Time Test

Calculates statistics and energy consumption from heating/cooling test results.
Handles timing analysis and power consumption calculations.
"""

# Standard library imports
from typing import Any, Dict, List

# Third-party imports
from loguru import logger


class StatisticsCalculator:
    """
    Statistics calculator for heating/cooling time test

    Calculates timing statistics, energy consumption, and performance metrics
    from heating/cooling cycle test results.
    """

    @staticmethod
    def calculate_statistics(
        heating_results: List[Dict[str, Any]],
        cooling_results: List[Dict[str, Any]],
        power_data: Dict[str, Any],
        repeat_count: int,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics from test results

        Args:
            heating_results: List of heating cycle measurements
            cooling_results: List of cooling cycle measurements
            power_data: Power monitoring data
            repeat_count: Number of test cycles performed

        Returns:
            Dictionary containing calculated statistics
        """
        # Calculate timing statistics
        timing_stats = StatisticsCalculator._calculate_timing_statistics(
            heating_results, cooling_results
        )

        # Calculate power statistics
        power_stats = StatisticsCalculator._calculate_power_statistics(power_data)

        # Calculate energy consumption
        energy_stats = StatisticsCalculator._calculate_energy_consumption(
            heating_results, cooling_results, power_data
        )

        # Combine all statistics
        return {
            **timing_stats,
            **power_stats,
            **energy_stats,
            "total_cycles": repeat_count,
            "total_heating_cycles": len(heating_results),
            "total_cooling_cycles": len(cooling_results),
        }

    @staticmethod
    def _calculate_timing_statistics(
        heating_results: List[Dict[str, Any]], cooling_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate timing statistics from heating/cooling results

        Args:
            heating_results: List of heating cycle measurements
            cooling_results: List of cooling cycle measurements

        Returns:
            Dictionary containing timing statistics
        """
        avg_heating_time = (
            sum(h["total_duration_ms"] for h in heating_results) / len(heating_results)
            if heating_results
            else 0
        )
        avg_cooling_time = (
            sum(c["total_duration_ms"] for c in cooling_results) / len(cooling_results)
            if cooling_results
            else 0
        )
        avg_heating_ack = (
            sum(h["ack_duration_ms"] for h in heating_results) / len(heating_results)
            if heating_results
            else 0
        )
        avg_cooling_ack = (
            sum(c["ack_duration_ms"] for c in cooling_results) / len(cooling_results)
            if cooling_results
            else 0
        )

        return {
            "average_heating_time_ms": avg_heating_time,
            "average_cooling_time_ms": avg_cooling_time,
            "average_heating_ack_ms": avg_heating_ack,
            "average_cooling_ack_ms": avg_cooling_ack,
        }

    @staticmethod
    def _calculate_power_statistics(power_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate power consumption statistics

        Args:
            power_data: Power monitoring data

        Returns:
            Dictionary containing power statistics
        """
        return {
            "full_cycle_average_power_watts": power_data.get("average_power_watts", 0),
            "full_cycle_peak_power_watts": power_data.get("peak_power_watts", 0),
            "full_cycle_min_power_watts": power_data.get("min_power_watts", 0),
            "power_sample_count": power_data.get("sample_count", 0),
            "measurement_duration_seconds": power_data.get("duration_seconds", 0),
        }

    @staticmethod
    def _calculate_energy_consumption(
        heating_results: List[Dict[str, Any]],
        cooling_results: List[Dict[str, Any]],
        power_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Calculate energy consumption based on actual work time

        Args:
            heating_results: List of heating cycle measurements
            cooling_results: List of cooling cycle measurements
            power_data: Power monitoring data

        Returns:
            Dictionary containing energy consumption data
        """
        full_cycle_avg_power = power_data.get("average_power_watts", 0)

        # Calculate energy for ACTUAL heating/cooling work time only
        total_heating_time_s = (
            sum(h["total_duration_ms"] for h in heating_results) / 1000 if heating_results else 0
        )
        total_cooling_time_s = (
            sum(c["total_duration_ms"] for c in cooling_results) / 1000 if cooling_results else 0
        )
        actual_work_time_s = total_heating_time_s + total_cooling_time_s

        # Recalculate energy based on actual work time (not total monitoring time)
        if actual_work_time_s > 0 and full_cycle_avg_power > 0:
            total_energy_consumed = (full_cycle_avg_power * actual_work_time_s) / 3600  # Wh
            logger.info(
                f"Energy calculation - Work time: {actual_work_time_s:.1f}s, Avg power: {full_cycle_avg_power:.1f}W"
            )
            logger.info(
                f"Corrected energy (work time only): {total_energy_consumed:.4f}Wh vs Original (full period): {power_data.get('total_energy_wh', 0):.4f}Wh"
            )
        else:
            total_energy_consumed = power_data.get("total_energy_wh", 0)  # Fallback to original

        return {
            "total_energy_consumed_wh": total_energy_consumed,
        }

    @staticmethod
    def log_summary(statistics: Dict[str, Any]) -> None:
        """
        Log test summary statistics

        Args:
            statistics: Calculated statistics dictionary
        """
        logger.info("=== Test Summary ===")
        logger.info(f"Cycles completed: {statistics.get('total_cycles', 0)}")
        logger.info(f"Average heating time: {statistics.get('average_heating_time_ms', 0):.1f}ms")
        logger.info(f"Average cooling time: {statistics.get('average_cooling_time_ms', 0):.1f}ms")
        logger.info(
            f"Full cycle average power: {statistics.get('full_cycle_average_power_watts', 0):.1f}W"
        )
        logger.info(
            f"Full cycle peak power: {statistics.get('full_cycle_peak_power_watts', 0):.1f}W"
        )
        logger.info(f"Total energy consumed: {statistics.get('total_energy_consumed_wh', 0):.3f}Wh")
        logger.info(f"Power samples collected: {statistics.get('power_sample_count', 0)}")
        logger.info(
            f"Measurement duration: {statistics.get('measurement_duration_seconds', 0):.1f}s"
        )
