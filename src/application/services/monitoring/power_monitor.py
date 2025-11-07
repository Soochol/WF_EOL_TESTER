"""
Power Monitor Service

Service for monitoring power consumption during test operations.
Provides real-time power measurement and analysis capabilities.
"""

# Standard library imports
import statistics
import time
from typing import Any, cast, Dict, List, Optional, Union

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.power_analyzer import PowerAnalyzerService
from domain.value_objects.integration_state import IntegrationState, IntegrationStateManager


class PowerMonitor:
    """
    Power consumption monitoring service

    Monitors voltage, current, and calculates power consumption
    in real-time during test operations.

    Supports both PowerService (power supply with measurement) and
    PowerAnalyzerService (measurement-only analyzer) interfaces.
    """

    def __init__(self, power_device: Union[PowerService, PowerAnalyzerService]):
        """
        Initialize Power Monitor

        Args:
            power_device: Power supply or power analyzer service interface
        """
        self._power_device = power_device
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        self._using_integration = False  # Track if using hardware integration
        self._power_data: List[Dict[str, float]] = []
        self._start_time = 0.0

        # Integration state management (Clean Architecture - Domain Layer)
        self._integration_state_manager = IntegrationStateManager()

    def has_integration_capability(self) -> bool:
        """
        Check if power device supports hardware integration

        Returns:
            True if device is PowerAnalyzerService (supports integration), False otherwise
        """
        return isinstance(self._power_device, PowerAnalyzerService)

    async def start_monitoring(self, interval: float = 0.5, use_integration: bool = True) -> None:
        """
        Start power monitoring with automatic method selection

        Args:
            interval: Sampling interval in seconds (default: 0.5s, used for polling mode)
            use_integration: Enable hardware integration if available (default: True)
        """
        logger.debug(f"🔋 PowerMonitor.start_monitoring() called with interval={interval}s")

        if self._is_monitoring:
            logger.warning("Power monitoring is already active")
            return

        # Verify power device is available
        if not self._power_device:
            logger.error("❌ Power device is None - cannot start monitoring")
            raise RuntimeError("Power device is not initialized")

        logger.debug(
            f"Power device object: {self._power_device} (type: {type(self._power_device)})"
        )

        try:
            # Test power device connection
            is_connected = await self._power_device.is_connected()
            logger.info(
                f"Power service connection status: {'✅ CONNECTED' if is_connected else '❌ DISCONNECTED'}"
            )

            if not is_connected:
                logger.error("❌ Power service is not connected - cannot start monitoring")
                raise RuntimeError("Power service is not connected")

        except Exception as e:
            logger.error(f"❌ Failed to check power service connection: {e}")
            raise RuntimeError(f"Power service connection check failed: {e}") from e

        # Auto-select measurement method
        if use_integration and self.has_integration_capability():
            # Power Analyzer available: Use hardware integration
            logger.info("🔋 Starting hardware integration (Power Analyzer)")
            try:
                await self._setup_hardware_integration()
                self._using_integration = True
                logger.info("✅ Hardware integration started successfully")
            except Exception as e:
                logger.warning(f"⚠️ Hardware integration setup failed, falling back to polling: {e}")
                # Fallback to polling mode
                await self._start_polling_monitoring(interval)
                self._using_integration = False
        else:
            # Power Supply or integration disabled: Use polling
            logger.info("🔋 Starting numerical integration (Power Supply polling)")
            await self._start_polling_monitoring(interval)
            self._using_integration = False

    async def _setup_hardware_integration(self) -> None:
        """
        Configure WT1800E hardware integration for accurate energy measurement

        Follows Clean Architecture with proper state management from domain layer.

        Raises:
            RuntimeError: If integration setup fails
        """
        analyzer = cast(PowerAnalyzerService, self._power_device)

        # Reset to IDLE state (safe from any previous state)
        if not self._integration_state_manager.is_idle():
            logger.debug(
                f"Resetting integration from {self._integration_state_manager.get_state_name()} to IDLE"
            )
            await analyzer.reset_integration()
            self._integration_state_manager.reset()

        # Setup integration parameters (IDLE → CONFIGURED)
        if not self._integration_state_manager.can_configure():
            raise RuntimeError(
                f"Cannot configure integration: {self._integration_state_manager.last_error}"
            )

        await analyzer.setup_integration(
            mode="normal",  # or "continuous"
            timer=3600,  # 1 hour max (will be stopped when test completes)
        )
        self._integration_state_manager.configure()
        logger.debug(f"Integration state: {self._integration_state_manager.get_state_name()}")

        # Reset integration counters
        await analyzer.reset_integration()

        # Start integration (CONFIGURED → RUNNING)
        if not self._integration_state_manager.can_start():
            raise RuntimeError(
                f"Cannot start integration: {self._integration_state_manager.last_error}"
            )

        await analyzer.start_integration()
        self._integration_state_manager.start()

        self._is_monitoring = True
        self._start_time = time.perf_counter()

        logger.info(
            f"✅ WT1800E hardware integration configured and started (state: {self._integration_state_manager.get_state_name()})"
        )

    async def _start_polling_monitoring(self, interval: float) -> None:
        """
        Start polling-based power monitoring (legacy method)

        Args:
            interval: Sampling interval in seconds
        """
        self._is_monitoring = True
        self._power_data = []
        self._start_time = time.perf_counter()

        try:
            self._monitoring_task = asyncio.create_task(self._monitor_loop(interval))
            logger.info("✅ Power monitoring polling task created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create monitoring task: {e}")
            self._is_monitoring = False
            raise RuntimeError(f"Failed to create monitoring task: {e}") from e

    async def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop monitoring and return power consumption data

        Returns:
            Dictionary containing power analysis results
        """
        logger.info("🔋 PowerMonitor.stop_monitoring() called")

        if not self._is_monitoring:
            logger.warning("⚠️  Power monitoring is not active")
            return {}

        logger.info("🔋 Stopping power monitoring...")
        self._is_monitoring = False

        # Choose method based on what was used for monitoring
        if self._using_integration:
            # Get energy from hardware integration
            return await self._stop_integration_monitoring()
        else:
            # Calculate energy from polling data
            return await self._stop_polling_monitoring()

    async def _stop_integration_monitoring(self) -> Dict[str, Any]:
        """
        Stop hardware integration monitoring and get accurate energy data

        Uses state manager to ensure safe stop operation.

        Returns:
            Dictionary containing integration results
        """
        analyzer = cast(PowerAnalyzerService, self._power_device)

        try:
            # Stop integration with state validation (RUNNING → STOPPED)
            if self._integration_state_manager.can_stop():
                await analyzer.stop_integration()
                self._integration_state_manager.stop()
                logger.info(
                    f"✅ Hardware integration stopped (state: {self._integration_state_manager.get_state_name()})"
                )
            elif self._integration_state_manager.is_stopped():
                logger.info(
                    "ℹ️  Integration already stopped, retrieving data (idempotent operation)"
                )
            else:
                logger.warning(
                    f"⚠️  Integration in unexpected state: {self._integration_state_manager.get_state_name()}"
                )

            # Get integration data
            integration_data = await analyzer.get_integration_data()
            logger.info(
                f"📊 Integration data: {integration_data['active_energy_wh']:.4f} Wh (active)"
            )

            # Get current instantaneous measurements for reference
            measurements = await analyzer.get_measurements()

            duration = time.perf_counter() - self._start_time

            result = {
                # Energy from hardware integration (most accurate)
                "total_energy_wh": integration_data["active_energy_wh"],
                "apparent_energy_vah": integration_data.get("apparent_energy_vah", 0.0),
                "reactive_energy_varh": integration_data.get("reactive_energy_varh", 0.0),
                # Current measurements
                "average_power_watts": measurements["power"],
                "peak_power_watts": measurements["power"],  # Instantaneous only
                "average_voltage": measurements["voltage"],
                "average_current": measurements["current"],
                # Metadata
                "measurement_method": "hardware_integration",
                "sample_count": 0,  # Not applicable for integration
                "duration_seconds": round(duration, 2),
                "sampling_rate_hz": 0.0,  # Not applicable
                # Phase analysis not available
                "phase_analysis": {},
            }

            logger.info(
                f"✅ Hardware integration completed: {result['total_energy_wh']:.4f} Wh, "
                f"{result['average_power_watts']:.2f}W avg, {duration:.2f}s"
            )

            # Reset integration to IDLE for front panel menu access
            await analyzer.reset_integration()
            self._integration_state_manager.reset()
            logger.info("🔄 Integration reset to IDLE - front panel menu accessible")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to get integration data: {e}")
            # Return minimal data on error
            return {
                "total_energy_wh": 0.0,
                "measurement_method": "hardware_integration_failed",
                "error": str(e),
                "duration_seconds": round(time.perf_counter() - self._start_time, 2),
            }

    async def _stop_polling_monitoring(self) -> Dict[str, Any]:
        """
        Stop polling monitoring and calculate energy from collected data

        Returns:
            Dictionary containing polling analysis results
        """
        if self._monitoring_task:
            try:
                logger.info("🔋 Cancelling monitoring task...")
                self._monitoring_task.cancel()
                await self._monitoring_task
                logger.info("✅ Monitoring task completed")
            except asyncio.CancelledError:
                logger.info("🔋 Monitoring task was cancelled")
            except Exception as e:
                logger.error(f"❌ Error while stopping monitoring task: {e}")

        analysis_result = self._analyze_power_data()
        logger.info(f"✅ Power monitoring completed: {len(self._power_data)} samples collected")
        logger.info(
            f"📊 Analysis result summary: {analysis_result.get('sample_count', 0)} samples, "
            f"{analysis_result.get('average_power_watts', 0):.4f}W avg"
        )

        return analysis_result

    async def _monitor_loop(self, interval: float) -> None:
        """
        Background monitoring loop

        Args:
            interval: Sampling interval in seconds
        """
        failures = 0
        max_failures = 3

        logger.info(f"🔋 Power monitoring loop started with {interval}s interval")

        try:
            while self._is_monitoring:
                try:
                    logger.debug(f"📊 Taking power measurement sample #{len(self._power_data)}...")

                    # Get all measurements at once
                    # Works with both PowerService and PowerAnalyzerService
                    if isinstance(self._power_device, PowerAnalyzerService):
                        # PowerAnalyzerService interface (power analyzer)
                        measurements = await self._power_device.get_measurements()
                    else:
                        # PowerService interface (power supply)
                        measurements = await self._power_device.get_all_measurements()

                    voltage = measurements["voltage"]
                    current = measurements["current"]
                    power = measurements["power"]
                    timestamp = time.perf_counter() - self._start_time

                    # Log detailed measurement info for debugging
                    if (
                        len(self._power_data) % 5 == 0
                    ):  # Log every 5th measurement (reduced from 10)
                        logger.debug(
                            f"📊 Power monitoring sample #{len(self._power_data)}: {voltage:.4f}V, {current:.4f}A, {power:.4f}W at {timestamp:.2f}s"
                        )
                        # Force immediate output flush
                        # Standard library imports
                        import sys

                        sys.stdout.flush()
                        sys.stderr.flush()

                    # Store data point
                    self._power_data.append(
                        {
                            "timestamp": timestamp,
                            "voltage": voltage,
                            "current": current,
                            "power": power,
                        }
                    )

                    failures = 0  # Reset failure count on success

                except Exception as e:
                    failures += 1
                    logger.warning(f"⚠️  Power measurement failed ({failures}/{max_failures}): {e}")

                    if failures >= max_failures:
                        logger.error("❌ Power monitoring stopped due to repeated failures")
                        break

                # Break down sleep into smaller chunks for better cancellation responsiveness
                sleep_chunk = 0.1  # 100ms chunks
                remaining_sleep = interval
                while remaining_sleep > 0 and self._is_monitoring:
                    chunk_sleep = min(sleep_chunk, remaining_sleep)
                    await asyncio.sleep(chunk_sleep)
                    remaining_sleep -= chunk_sleep

        except asyncio.CancelledError:
            logger.info("🔋 Power monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"❌ Power monitoring loop error: {e}")

        logger.info(
            f"🔋 Power monitoring loop ended. Total samples collected: {len(self._power_data)}"
        )

    def _analyze_power_data(self) -> Dict[str, Any]:
        """
        Analyze collected power data

        Returns:
            Dictionary containing power consumption analysis
        """
        if not self._power_data:
            return {"sample_count": 0, "error": "No power data collected"}

        # Extract power values
        powers = [d["power"] for d in self._power_data]
        voltages = [d["voltage"] for d in self._power_data]
        currents = [d["current"] for d in self._power_data]

        total_duration = self._power_data[-1]["timestamp"] if self._power_data else 0

        # Basic statistics
        peak_power = max(powers)
        min_power = min(powers)
        avg_power = sum(powers) / len(powers)
        median_power = statistics.median(powers)
        std_dev_power = statistics.stdev(powers) if len(powers) > 1 else 0.0

        # Energy calculation (trapezoidal integration)
        total_energy_wh = self._calculate_energy()

        # Phase analysis
        phases = self._detect_power_phases()

        # Cost estimation (Korean electricity rate: ~150 KRW/kWh)
        electricity_rate_krw = 150.0  # KRW per kWh
        cost_estimate = total_energy_wh * electricity_rate_krw / 1000  # Convert Wh to kWh

        return {
            # Basic statistics
            "peak_power_watts": round(peak_power, 2),
            "min_power_watts": round(min_power, 2),
            "average_power_watts": round(avg_power, 2),  # Key metric
            "median_power_watts": round(median_power, 2),
            "power_std_dev_watts": round(std_dev_power, 2),
            # Voltage/Current stats
            "average_voltage": round(sum(voltages) / len(voltages), 2),
            "average_current": round(sum(currents) / len(currents), 3),
            # Energy and duration
            "total_energy_wh": round(total_energy_wh, 4),
            "duration_seconds": round(total_duration, 2),
            # Cost estimation
            "estimated_cost_krw": round(cost_estimate, 4),
            # Phase analysis
            "phase_analysis": phases,
            # Quality metrics
            "sample_count": len(self._power_data),
            "sampling_rate_hz": len(self._power_data) / total_duration if total_duration > 0 else 0,
            # Efficiency ratios
            "power_stability_ratio": round(avg_power / peak_power, 3) if peak_power > 0 else 0,
            "power_utilization_ratio": round(avg_power / min(avg_power * 1.5, peak_power), 3),
            # Raw measurement samples for CSV logging
            "raw_samples": self._power_data.copy(),  # Include raw data for external processing
        }

    def _calculate_energy(self) -> float:
        """
        Calculate total energy consumption using trapezoidal integration

        Returns:
            Total energy in watt-hours (Wh)
        """
        if len(self._power_data) < 2:
            return 0.0

        total_energy = 0.0

        for i in range(1, len(self._power_data)):
            # Time difference in hours
            dt_hours = (
                self._power_data[i]["timestamp"] - self._power_data[i - 1]["timestamp"]
            ) / 3600

            # Average power between two points
            avg_power = (self._power_data[i]["power"] + self._power_data[i - 1]["power"]) / 2

            # Energy = Power × Time
            total_energy += avg_power * dt_hours

        return total_energy

    def _detect_power_phases(self) -> Dict[str, Any]:
        """
        Detect different power consumption phases

        Returns:
            Dictionary containing phase analysis
        """
        if len(self._power_data) < 10:
            return {"phases": "insufficient_data"}

        powers = [d["power"] for d in self._power_data]
        timestamps = [d["timestamp"] for d in self._power_data]

        total_duration = timestamps[-1]

        # Simple phase detection based on power levels
        # Initial burst: first 20% of time or high power period
        initial_phase_end = min(total_duration * 0.2, 5.0)  # Max 5 seconds
        initial_indices = [i for i, t in enumerate(timestamps) if t <= initial_phase_end]

        # Maintenance: last 20% of time or low power period
        maintenance_phase_start = max(
            total_duration * 0.8, total_duration - 3.0
        )  # Min last 3 seconds
        maintenance_indices = [i for i, t in enumerate(timestamps) if t >= maintenance_phase_start]

        # Stabilization: middle period
        stabilization_indices = [
            i
            for i in range(len(powers))
            if i not in initial_indices and i not in maintenance_indices
        ]

        phases = {}

        # Initial phase analysis
        if initial_indices:
            initial_powers = [powers[i] for i in initial_indices]
            phases["initial_burst"] = {
                "average_watts": round(sum(initial_powers) / len(initial_powers), 2),
                "peak_watts": round(max(initial_powers), 2),
                "duration_s": round(timestamps[initial_indices[-1]], 2),
                "energy_wh": round(
                    sum(initial_powers) * initial_phase_end / 3600 / len(initial_powers), 4
                ),
            }

        # Stabilization phase analysis
        if stabilization_indices:
            stab_powers = [powers[i] for i in stabilization_indices]
            stab_duration = (
                (timestamps[stabilization_indices[-1]] - timestamps[stabilization_indices[0]])
                if stabilization_indices
                else 0
            )
            phases["stabilization"] = {
                "average_watts": round(sum(stab_powers) / len(stab_powers), 2),
                "duration_s": round(stab_duration, 2),
                "energy_wh": round(sum(stab_powers) * stab_duration / 3600 / len(stab_powers), 4),
            }

        # Maintenance phase analysis
        if maintenance_indices:
            maint_powers = [powers[i] for i in maintenance_indices]
            maint_duration = timestamps[-1] - timestamps[maintenance_indices[0]]
            phases["maintenance"] = {
                "average_watts": round(sum(maint_powers) / len(maint_powers), 2),
                "duration_s": round(maint_duration, 2),
                "energy_wh": round(
                    sum(maint_powers) * maint_duration / 3600 / len(maint_powers), 4
                ),
            }

        return phases

    def is_monitoring(self) -> bool:
        """
        Check if monitoring is currently active

        Returns:
            True if monitoring is active, False otherwise
        """
        return self._is_monitoring

    def get_current_power_reading(self) -> Optional[Dict[str, float]]:
        """
        Get the most recent power reading

        Returns:
            Most recent power data point or None if no data
        """
        return self._power_data[-1] if self._power_data else None

    def clear_data(self) -> None:
        """Clear all collected power data"""
        self._power_data.clear()
        logger.debug("Power monitoring data cleared")

    async def start_cycle_power_measurement(self) -> None:
        """
        Start power measurement for a single test cycle

        Uses hardware integration (PowerAnalyzerService) to accurately measure
        energy consumption for one cycle.

        IMPORTANT: This method is designed to work within an active monitoring session.
        It safely handles integration state transitions even if integration is already running.

        Raises:
            RuntimeError: If device doesn't support integration
            HardwareConnectionError: If device is not connected
        """
        if not self.has_integration_capability():
            raise RuntimeError(
                "Cycle power measurement requires PowerAnalyzerService with integration capability"
            )

        analyzer = cast(PowerAnalyzerService, self._power_device)

        # Check current state and handle accordingly
        current_state = self._integration_state_manager.state

        if current_state == IntegrationState.RUNNING:
            # Integration already running from start_monitoring()
            # Stop current integration, then restart for this cycle
            logger.debug(
                "🔋 Integration already running, stopping and restarting for cycle measurement"
            )
            if self._integration_state_manager.can_stop():
                await analyzer.stop_integration()
                self._integration_state_manager.stop()

        # Reset to IDLE for fresh cycle measurement
        if not self._integration_state_manager.is_idle():
            await analyzer.reset_integration()
            self._integration_state_manager.reset()

        # Configure integration for this cycle (IDLE → CONFIGURED)
        if self._integration_state_manager.can_configure():
            await analyzer.setup_integration(mode="normal", timer=3600)
            self._integration_state_manager.configure()
        else:
            raise RuntimeError(
                f"Cannot configure for cycle measurement: {self._integration_state_manager.last_error}"
            )

        # Reset counters and start integration for this cycle (CONFIGURED → RUNNING)
        await analyzer.reset_integration()

        if self._integration_state_manager.can_start():
            await analyzer.start_integration()
            self._integration_state_manager.start()
            logger.debug(
                f"🔋 Cycle power measurement started (state: {self._integration_state_manager.get_state_name()})"
            )
        else:
            raise RuntimeError(
                f"Cannot start cycle measurement: {self._integration_state_manager.last_error}"
            )

    async def stop_cycle_power_measurement(self) -> Dict[str, float]:
        """
        Stop cycle power measurement and return average power

        Uses state manager with hardware synchronization to ensure safe stop operation.
        Implements idempotent behavior with automatic error recovery.

        Returns:
            Dictionary containing:
            - 'average_power_w': Average power in watts for this cycle
            - 'energy_wh': Total energy consumed in watt-hours
            - 'elapsed_seconds': Cycle duration in seconds

        Raises:
            RuntimeError: If device doesn't support integration
            HardwareConnectionError: If device is not connected
        """
        if not self.has_integration_capability():
            raise RuntimeError(
                "Cycle power measurement requires PowerAnalyzerService with integration capability"
            )

        analyzer = cast(PowerAnalyzerService, self._power_device)

        # Synchronize state manager with actual hardware state (Clean Architecture)
        try:
            hw_state = await analyzer.get_integration_state()
            logger.debug(f"🔋 Hardware integration state: {hw_state}")

            # Update state manager to match hardware reality
            if hw_state == "START" and not self._integration_state_manager.is_running():
                # Hardware is running but state manager thinks it's not - sync
                logger.warning(
                    "⚠️  State desync detected: Hardware=START, Manager="
                    f"{self._integration_state_manager.get_state_name()}"
                )
                self._integration_state_manager._state = IntegrationState.RUNNING

            elif hw_state in ["STOP", "RESET"] and self._integration_state_manager.is_running():
                # Hardware is stopped but state manager thinks it's running - sync
                logger.warning(
                    f"⚠️  State desync detected: Hardware={hw_state}, Manager="
                    f"{self._integration_state_manager.get_state_name()}"
                )
                self._integration_state_manager._state = IntegrationState.STOPPED

        except Exception as sync_error:
            logger.warning(f"⚠️  Failed to sync hardware state: {sync_error}")

        # Stop integration with state validation (RUNNING → STOPPED)
        if self._integration_state_manager.can_stop():
            await analyzer.stop_integration()
            self._integration_state_manager.stop()
            logger.debug(
                f"🔋 Cycle integration stopped (state: {self._integration_state_manager.get_state_name()})"
            )
        elif self._integration_state_manager.is_stopped():
            logger.debug("ℹ️  Cycle integration already stopped (idempotent)")
        else:
            logger.warning(
                f"⚠️  Unexpected state during cycle stop: {self._integration_state_manager.get_state_name()}"
            )

        # Get integration data (includes elapsed time from WT1800E TIME item)
        integration_data = await analyzer.get_integration_data()

        # Extract elapsed time from integration data (WT1800E internal time measurement)
        elapsed_seconds = integration_data.get("elapsed_time_seconds", 0.0)
        elapsed_hours = elapsed_seconds / 3600.0

        # Calculate average power (P = E / t)
        avg_power_w = (
            integration_data["active_energy_wh"] / elapsed_hours if elapsed_hours > 0 else 0.0
        )

        logger.debug(
            f"🔋 Cycle power measurement stopped: {avg_power_w:.2f}W avg, "
            f"{integration_data['active_energy_wh']:.4f}Wh, {elapsed_seconds:.2f}s"
        )

        # Reset integration to IDLE for front panel menu access
        await analyzer.reset_integration()
        self._integration_state_manager.reset()
        logger.debug("🔄 Cycle integration reset to IDLE - front panel menu accessible")

        return {
            "average_power_w": avg_power_w,
            "energy_wh": integration_data["active_energy_wh"],
            "elapsed_seconds": elapsed_seconds,
        }
