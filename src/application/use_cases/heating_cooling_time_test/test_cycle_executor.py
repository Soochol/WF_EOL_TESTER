"""
Test Cycle Executor for Heating/Cooling Time Test

Executes heating and cooling test cycles and manages power monitoring.
Handles the core test execution logic for temperature transitions.
"""

# Standard library imports
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.power_monitor import PowerMonitor
from domain.value_objects.hardware_config import HardwareConfig

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
        # Track force measurement results
        self._force_measurements: List[Dict[str, Any]] = []
        # CSV logger for test data
        self._csv_logger: Optional[HeatingCoolingCSVLogger] = None
        # Hardware configuration (set during execute_test_cycles)
        self._hardware_config: Optional[HardwareConfig] = None

    async def execute_test_cycles(
        self, hc_config, hardware_config, repeat_count: int, test_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute all heating/cooling test cycles

        Args:
            hc_config: Heating/cooling configuration
            hardware_config: Hardware configuration object
            repeat_count: Number of cycles to perform
            test_id: Optional test identifier for CSV logging

        Returns:
            Dictionary containing cycle results, power data, and execution status
        """
        # Store hardware_config for use in force measurement
        self._hardware_config = hardware_config
        logger.info(
            f"Temperature range: {hc_config.standby_temperature}°C ↔ {hc_config.activation_temperature}°C"
        )
        logger.info(
            f"Wait times - Heating: {hc_config.heating_wait_time}s, Cooling: {hc_config.cooling_wait_time}s, Stabilization: {hc_config.stabilization_wait_time}s"
        )

        # Clear partial results from previous runs
        self._partial_heating_results.clear()
        self._partial_cooling_results.clear()
        self._force_measurements.clear()

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

                # Write power data CSV if raw samples are available
                if full_cycle_power_data and "raw_samples" in full_cycle_power_data:
                    raw_samples = full_cycle_power_data["raw_samples"]
                    if raw_samples:
                        self._csv_logger.write_power_data(raw_samples)
                        logger.info(
                            f"Power data CSV written: {self._csv_logger.get_power_file_path()}"
                        )

                # Write force data CSV if force measurements are available
                if self._force_measurements:
                    self._csv_logger.write_force_data(self._force_measurements)
                    logger.info(f"Force data CSV written: {self._csv_logger.get_force_file_path()}")

            return {
                "success": True,
                "timing_data": timing_data,
                "power_data": full_cycle_power_data,
                "force_measurements": self._force_measurements,
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

                # Write power data CSV even for partial results if available
                if full_cycle_power_data and "raw_samples" in full_cycle_power_data:
                    raw_samples = full_cycle_power_data["raw_samples"]
                    if raw_samples:
                        self._csv_logger.write_power_data(raw_samples)
                        logger.info(
                            f"Partial power data CSV written: {self._csv_logger.get_power_file_path()}"
                        )

            return {
                "success": False,
                "timing_data": partial_timing_data,
                "power_data": full_cycle_power_data,
                "force_measurements": self._force_measurements,
                "completed_cycles": completed_cycles,
                "requested_cycles": repeat_count,
                "error_message": str(execution_error),
                "partial": True,
            }

    async def measure_force_at_positions(self, cycle_num: int, hc_config) -> List[Dict[str, Any]]:
        """
        Measure force at multiple positions after heating

        Sequence:
        1. Move robot to each measurement position
        2. Measure force with loadcell
        3. Return to initial position

        Note: Temperature is maintained at operating level during measurement

        Args:
            cycle_num: Current cycle number
            hc_config: Heating/cooling configuration

        Returns:
            List of force measurement dictionaries
        """
        if not hc_config.enable_force_measurement:
            logger.debug("Force measurement disabled, skipping")
            return []

        # Ensure hardware config is available
        if self._hardware_config is None:
            logger.error("Hardware configuration not initialized")
            raise RuntimeError("Hardware configuration must be set before force measurement")

        logger.info(
            f"📏 [Cycle {cycle_num}] Starting force measurement at "
            f"{len(hc_config.measurement_positions)} positions..."
        )

        # Access services via facade (Clean Architecture)
        robot_service = self._hardware_services.robot_service
        loadcell_service = self._hardware_services.loadcell_service

        force_results = []

        # Measure force at each position
        for idx, position in enumerate(hc_config.measurement_positions, 1):
            # Move robot to measurement position
            logger.info(
                f"🤖 [Cycle {cycle_num}] Moving robot to position "
                f"{idx}/{len(hc_config.measurement_positions)}: {position}μm"
            )
            await robot_service.move_absolute(
                position=position,
                axis_id=self._hardware_config.robot.axis_id,
                velocity=hc_config.velocity,
                acceleration=hc_config.acceleration,
                deceleration=hc_config.deceleration,
            )

            # Stabilization delay
            await asyncio.sleep(hc_config.robot_move_stabilization)

            # Additional measurement delay
            if hc_config.force_measurement_delay > 0:
                await asyncio.sleep(hc_config.force_measurement_delay)

            # Measure force
            force = await loadcell_service.read_peak_force()

            force_results.append(
                {
                    "cycle": cycle_num,
                    "position_um": position,
                    "force_kgf": force.value,
                    "velocity": hc_config.velocity,
                    "acceleration": hc_config.acceleration,
                    "deceleration": hc_config.deceleration,
                    "heating_wait_s": hc_config.heating_wait_time,
                    "cooling_wait_s": hc_config.cooling_wait_time,
                    "total_energy_wh": 0.0,  # Will be updated after cycle completes
                    "avg_power_w": 0.0,  # Will be updated after cycle completes
                    "cycle_duration_s": 0.0,  # Will be updated after cycle completes
                    "timestamp": datetime.now().isoformat(sep=' ', timespec='milliseconds'),
                }
            )

            logger.info(f"⚖️  [Cycle {cycle_num}] Force at {position}μm: {force.value:.3f}kgf")

        # Return to initial position
        logger.info(
            f"🏠 [Cycle {cycle_num}] Returning robot to initial position: "
            f"{hc_config.initial_position}μm"
        )
        await robot_service.move_absolute(
            position=hc_config.initial_position,
            axis_id=self._hardware_config.robot.axis_id,
            velocity=hc_config.velocity,
            acceleration=hc_config.acceleration,
            deceleration=hc_config.deceleration,
        )
        await asyncio.sleep(hc_config.robot_move_stabilization)

        logger.info(
            f"✅ [Cycle {cycle_num}] Force measurement completed: {len(force_results)} measurements"
        )

        return force_results

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

            # Track if cycle integration was started (for cleanup in finally block)
            cycle_integration_started = False

            try:
                # Start per-cycle power measurement (if power monitoring enabled and integration capable)
                if (
                    hc_config.power_monitoring_enabled
                    and self._power_monitor.has_integration_capability()
                ):
                    try:
                        await self._power_monitor.start_cycle_power_measurement()
                        cycle_integration_started = True  # Mark as started for cleanup
                        logger.debug(f"🔋 [Cycle {i+1}] Power integration started")
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Failed to start cycle power measurement: {e}. Continuing without per-cycle power data."
                        )

                # Heating phase (standby → activation)
                logger.info(
                    f"Heating: {hc_config.standby_temperature}°C → {hc_config.activation_temperature}°C"
                )
                heating_start = time.time()
                await mcu_service.start_standby_heating(
                    operating_temp=hc_config.activation_temperature,
                    standby_temp=hc_config.standby_temperature,
                )
                heating_elapsed = time.time() - heating_start

                # Force measurement phase (if enabled) - MOVED HERE (after heating, before wait)
                robot_start = time.time()
                robot_elapsed = 0.0
                force_results = []
                if hc_config.enable_robot and hc_config.enable_force_measurement:
                    force_results = await self.measure_force_at_positions(
                        cycle_num=i + 1, hc_config=hc_config
                    )
                    # Store force results (will update total_energy_wh and avg_power_w later)
                    if force_results:
                        self._force_measurements.extend(force_results)
                robot_elapsed = time.time() - robot_start

                # Calculate adjusted heating wait time (heating + robot time)
                total_elapsed = heating_elapsed + robot_elapsed
                remaining_heating_wait = max(0, hc_config.heating_wait_time - total_elapsed)
                if remaining_heating_wait > 0:
                    logger.info(
                        f"Heating: {heating_elapsed:.1f}s + Robot: {robot_elapsed:.1f}s = {total_elapsed:.1f}s elapsed, "
                        f"waiting {remaining_heating_wait:.1f}s more to reach minimum {hc_config.heating_wait_time}s"
                    )
                    await asyncio.sleep(remaining_heating_wait)
                else:
                    logger.info(
                        f"Heating + Robot: {total_elapsed:.1f}s (exceeds minimum {hc_config.heating_wait_time}s, no additional wait needed)"
                    )

                # Collect heating timing data for this cycle
                self._collect_cycle_timing_data(cycle_number=i + 1, phase="heating")

                # Cooling phase (activation → standby)
                logger.info(
                    f"Cooling: {hc_config.activation_temperature}°C → {hc_config.standby_temperature}°C"
                )
                cooling_start = time.time()
                await mcu_service.start_standby_cooling()
                cooling_elapsed = time.time() - cooling_start

                # Calculate remaining wait time to reach minimum cooling time
                remaining_cooling_wait = max(0, hc_config.cooling_wait_time - cooling_elapsed)
                if remaining_cooling_wait > 0:
                    logger.info(
                        f"Cooling: {cooling_elapsed:.1f}s elapsed, waiting {remaining_cooling_wait:.1f}s more to reach minimum {hc_config.cooling_wait_time}s"
                    )
                    await asyncio.sleep(remaining_cooling_wait)
                else:
                    logger.info(
                        f"Cooling: {cooling_elapsed:.1f}s (exceeds minimum {hc_config.cooling_wait_time}s)"
                    )

                # Collect cooling timing data for this cycle
                self._collect_cycle_timing_data(cycle_number=i + 1, phase="cooling")

                # Stop per-cycle power measurement and update force measurements
                if (
                    hc_config.power_monitoring_enabled
                    and self._power_monitor.has_integration_capability()
                ):
                    try:
                        cycle_power_data = await self._power_monitor.stop_cycle_power_measurement()
                        cycle_energy_wh = cycle_power_data["energy_wh"]
                        cycle_avg_power = cycle_power_data["average_power_w"]
                        logger.info(
                            f"🔋 [Cycle {i+1}] Energy: {cycle_energy_wh:.4f}Wh, "
                            f"Average power: {cycle_avg_power:.2f}W "
                            f"(Duration: {cycle_power_data['elapsed_seconds']:.2f}s)"
                        )

                        # Update force measurements with cycle energy, average power, and duration
                        if force_results:
                            for measurement in force_results:
                                measurement["total_energy_wh"] = cycle_energy_wh
                                measurement["avg_power_w"] = cycle_avg_power
                                measurement["cycle_duration_s"] = cycle_power_data["elapsed_seconds"]
                            logger.debug(
                                f"Updated {len(force_results)} force measurements with "
                                f"energy: {cycle_energy_wh:.4f}Wh, avg power: {cycle_avg_power:.2f}W, "
                                f"duration: {cycle_power_data['elapsed_seconds']:.2f}s"
                            )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to get cycle power data: {e}")
                        # Set all power-related values to 0.0 for this cycle's force measurements
                        if force_results:
                            for measurement in force_results:
                                measurement["total_energy_wh"] = 0.0
                                measurement["avg_power_w"] = 0.0
                                measurement["cycle_duration_s"] = 0.0

                logger.info(f"✅ Cycle {i+1}/{repeat_count} completed successfully")

            except Exception as cycle_error:
                logger.error(f"❌ Cycle {i+1}/{repeat_count} failed: {cycle_error}")
                # Re-raise to be handled at higher level with partial data
                raise cycle_error

            finally:
                # Ensure integration is reset if cycle was interrupted (cleanup on error)
                # Note: Normal completion already calls stop_cycle_power_measurement() which has its own finally block
                # This handles the case where cycle fails between start and stop
                if cycle_integration_started and hc_config.power_monitoring_enabled:
                    try:
                        if self._power_monitor.has_integration_capability():
                            # Force stop to ensure integration is reset
                            # stop_cycle_power_measurement() is idempotent and has its own finally block
                            # This ensures cleanup even if cycle failed mid-execution
                            logger.debug(f"🔄 [Cycle {i+1}] Ensuring integration cleanup in finally block")
                            await self._power_monitor.stop_cycle_power_measurement()
                    except Exception as cleanup_error:
                        logger.warning(
                            f"⚠️ [Cycle {i+1}] Failed to cleanup cycle integration in finally block: {cleanup_error}"
                        )

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
