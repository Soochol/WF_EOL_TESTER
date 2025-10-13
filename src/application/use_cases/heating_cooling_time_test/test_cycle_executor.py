"""
Test Cycle Executor for Heating/Cooling Time Test

Executes heating and cooling test cycles and manages power monitoring.
Handles the core test execution logic for temperature transitions.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.power_monitor import PowerMonitor

# Local folder imports
from .csv_logger import HeatingCoolingCSVLogger


class TestCycleExecutor:
    """
    Test cycle executor for heating/cooling time test

    Manages the execution of heating/cooling cycles including power monitoring
    and timing measurements.
    """

    def __init__(self, hardware_services: HardwareServiceFacade, power_monitor: PowerMonitor):
        """
        Initialize test cycle executor

        Args:
            hardware_services: Hardware service facade
            power_monitor: Power monitor instance
        """
        self._hardware_services = hardware_services
        self._power_monitor = power_monitor
        # Track partial results during execution
        self._partial_heating_results: List[Dict[str, Any]] = []
        self._partial_cooling_results: List[Dict[str, Any]] = []
        # CSV logger for test data
        self._csv_logger: Optional[HeatingCoolingCSVLogger] = None

    async def execute_test_cycles(
        self, hc_config, repeat_count: int, test_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute all heating/cooling test cycles

        Args:
            hc_config: Heating/cooling configuration
            repeat_count: Number of cycles to perform
            test_id: Optional test identifier for CSV logging

        Returns:
            Dictionary containing cycle results, power data, and execution status
        """
        logger.info(
            f"Temperature range: {hc_config.standby_temperature}°C ↔ {hc_config.activation_temperature}°C"
        )
        logger.info(
            f"Wait times - Heating: {hc_config.heating_wait_time}s, Cooling: {hc_config.cooling_wait_time}s, Stabilization: {hc_config.stabilization_wait_time}s"
        )

        # Clear partial results from previous runs
        self._partial_heating_results.clear()
        self._partial_cooling_results.clear()

        # Initialize CSV logger if test_id provided
        if test_id:
            self._csv_logger = HeatingCoolingCSVLogger(test_id, repeat_count)
            logger.info(f"CSV logging enabled: {self._csv_logger.get_file_path()}")

        # Start power monitoring BEFORE heating/cooling operations begin
        await self._start_power_monitoring(hc_config)

        execution_error = None
        full_cycle_power_data = {}

        try:
            # Perform test cycles
            await self._perform_cycles(hc_config, repeat_count)

            # Stop power monitoring and get data
            full_cycle_power_data = await self._stop_power_monitoring(hc_config)

            # Get timing data from MCU (uses partial results if available)
            timing_data = self._get_timing_data()

            logger.info(f"✅ All {repeat_count} test cycles completed successfully")

            # Write summary to CSV if logger is enabled
            if self._csv_logger:
                self._csv_logger.write_summary(completed_cycles=repeat_count)

            return {
                "success": True,
                "timing_data": timing_data,
                "power_data": full_cycle_power_data,
                "completed_cycles": repeat_count,
                "error_message": None,
            }

        except Exception as e:
            execution_error = e
            logger.error(
                f"❌ Test cycles failed after {len(self._partial_cooling_results)} completed cycles: {e}"
            )

            # Ensure power monitoring is stopped on error
            if hc_config.power_monitoring_enabled and self._power_monitor.is_monitoring():
                try:
                    full_cycle_power_data = await self._power_monitor.stop_monitoring()
                    logger.info("Power monitoring stopped and partial data collected")
                except Exception as stop_error:
                    logger.error(
                        f"Failed to stop power monitoring during error cleanup: {stop_error}"
                    )
                    full_cycle_power_data = {"error": str(stop_error), "sample_count": 0}

            # Return partial results instead of raising exception
            partial_timing_data = {
                "heating_results": self._partial_heating_results,
                "cooling_results": self._partial_cooling_results,
            }

            completed_cycles = len(self._partial_cooling_results)
            logger.warning(
                f"Returning partial results: {completed_cycles} completed cycles out of {repeat_count}"
            )

            # Write partial summary to CSV if logger is enabled
            if self._csv_logger:
                self._csv_logger.write_summary(completed_cycles=completed_cycles)

            return {
                "success": False,
                "timing_data": partial_timing_data,
                "power_data": full_cycle_power_data,
                "completed_cycles": completed_cycles,
                "requested_cycles": repeat_count,
                "error_message": str(execution_error),
                "partial": True,
            }

    async def _start_power_monitoring(self, hc_config) -> None:
        """
        Start power monitoring if enabled

        Args:
            hc_config: Heating/cooling configuration
        """
        if hc_config.power_monitoring_enabled:
            logger.debug("🔋 Starting power monitoring BEFORE heating/cooling operations...")
            logger.debug(
                f"Power Monitor object: {self._power_monitor} (type: {type(self._power_monitor)})"
            )
            logger.info(f"Power Monitor is_monitoring: {self._power_monitor.is_monitoring()}")

            try:
                await self._power_monitor.start_monitoring(
                    interval=hc_config.power_monitoring_interval
                )
                logger.info("✅ Power monitoring started successfully")

                # Wait a moment to ensure monitoring loop starts
                await asyncio.sleep(0.2)
                logger.info("🔋 Power monitoring loop ready - starting heating/cooling operations")

            except Exception as e:
                logger.error(f"❌ Failed to start power monitoring: {e}")
                logger.exception("Power monitoring start exception details:")

    async def _perform_cycles(self, hc_config, repeat_count: int) -> None:
        """
        Perform heating/cooling cycles

        Args:
            hc_config: Heating/cooling configuration
            repeat_count: Number of cycles to perform
        """
        mcu_service = self._hardware_services.mcu_service

        for i in range(repeat_count):
            # Create prominent test cycle header
            cycle_header = f"🔄 Test Cycle {i+1}/{repeat_count}"
            separator = "═" * 50
            logger.info(separator)
            logger.info(f"{cycle_header:^50}")
            logger.info(separator)

            try:
                # Heating phase (standby → activation)
                logger.info(
                    f"Heating: {hc_config.standby_temperature}°C → {hc_config.activation_temperature}°C"
                )
                await mcu_service.start_standby_heating(
                    operating_temp=hc_config.activation_temperature,
                    standby_temp=hc_config.standby_temperature,
                )

                # Wait after heating completion
                logger.info(f"Heating wait time: {hc_config.heating_wait_time}s")
                await asyncio.sleep(hc_config.heating_wait_time)

                # Collect heating timing data for this cycle
                self._collect_cycle_timing_data(cycle_number=i + 1, phase="heating")

                # Cooling phase (activation → standby)
                logger.info(
                    f"Cooling: {hc_config.activation_temperature}°C → {hc_config.standby_temperature}°C"
                )
                await mcu_service.start_standby_cooling()

                # Wait after cooling completion
                logger.info(f"Cooling wait time: {hc_config.cooling_wait_time}s")
                await asyncio.sleep(hc_config.cooling_wait_time)

                # Collect cooling timing data for this cycle
                self._collect_cycle_timing_data(cycle_number=i + 1, phase="cooling")

                logger.info(f"✅ Cycle {i+1}/{repeat_count} completed successfully")

            except Exception as cycle_error:
                logger.error(f"❌ Cycle {i+1}/{repeat_count} failed: {cycle_error}")
                # Re-raise to be handled at higher level with partial data
                raise cycle_error

            # Stabilization wait between cycles
            if i < repeat_count - 1:  # Don't wait after last cycle
                logger.info(f"Stabilization wait time: {hc_config.stabilization_wait_time}s")
                await asyncio.sleep(hc_config.stabilization_wait_time)

    async def _stop_power_monitoring(self, hc_config) -> Dict[str, Any]:
        """
        Stop power monitoring and get data

        Args:
            hc_config: Heating/cooling configuration

        Returns:
            Power monitoring data dictionary
        """
        full_cycle_power_data = {}

        if hc_config.power_monitoring_enabled:
            logger.info("🔋 Stopping power monitoring for full cycle...")
            try:
                full_cycle_power_data = await self._power_monitor.stop_monitoring()
                logger.info(f"✅ Power monitoring stopped. Data: {full_cycle_power_data}")
            except Exception as e:
                logger.error(f"❌ Failed to stop power monitoring: {e}")
                full_cycle_power_data = {"error": str(e), "sample_count": 0}

        return full_cycle_power_data

    def _collect_cycle_timing_data(self, cycle_number: int, phase: str) -> None:
        """
        Collect timing data for a specific cycle and phase

        Args:
            cycle_number: Current cycle number (1-based)
            phase: "heating" or "cooling"
        """
        try:
            mcu_service = self._hardware_services.mcu_service
            timing_data = mcu_service.get_all_timing_data()

            if phase == "heating":
                heating_transitions = timing_data.get("heating_transitions", [])
                # Get the latest heating transition data
                if heating_transitions and len(heating_transitions) >= cycle_number:
                    latest_heating = heating_transitions[cycle_number - 1]  # 0-based index
                    self._partial_heating_results.append(latest_heating)
                    logger.debug(
                        f"Collected heating data for cycle {cycle_number}: {latest_heating}"
                    )

            elif phase == "cooling":
                cooling_transitions = timing_data.get("cooling_transitions", [])
                # Get the latest cooling transition data
                if cooling_transitions and len(cooling_transitions) >= cycle_number:
                    latest_cooling = cooling_transitions[cycle_number - 1]  # 0-based index
                    self._partial_cooling_results.append(latest_cooling)
                    logger.debug(
                        f"Collected cooling data for cycle {cycle_number}: {latest_cooling}"
                    )

                    # Write cycle data to CSV when both heating and cooling are complete
                    if self._csv_logger and len(self._partial_heating_results) >= cycle_number:
                        heating_data = self._partial_heating_results[cycle_number - 1]
                        cooling_data = latest_cooling
                        self._csv_logger.write_cycle_data(cycle_number, heating_data, cooling_data)

        except Exception as timing_error:
            logger.warning(
                f"Failed to collect {phase} timing data for cycle {cycle_number}: {timing_error}"
            )

    def _get_timing_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get timing data from MCU for all cycles
        Fallback method - prefer using partial results collected during execution

        Returns:
            Dictionary containing heating and cooling timing results
        """
        # Use partial results if available, otherwise fallback to MCU query
        if self._partial_heating_results or self._partial_cooling_results:
            return {
                "heating_results": self._partial_heating_results,
                "cooling_results": self._partial_cooling_results,
            }

        # Fallback to original method
        mcu_service = self._hardware_services.mcu_service
        timing_data = mcu_service.get_all_timing_data()

        return {
            "heating_results": timing_data.get("heating_transitions", []),
            "cooling_results": timing_data.get("cooling_transitions", []),
        }

    def _get_partial_results(self) -> Dict[str, Any]:
        """
        Get partial results collected so far

        Returns:
            Dictionary containing partial timing and power data
        """
        return {
            "timing_data": {
                "heating_results": self._partial_heating_results.copy(),
                "cooling_results": self._partial_cooling_results.copy(),
            },
            "power_data": {},  # Power data will be collected separately
            "completed_cycles": len(
                self._partial_cooling_results
            ),  # Cooling is last phase of each cycle
            "partial": True,
        }
