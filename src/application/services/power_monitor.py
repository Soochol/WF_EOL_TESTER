"""
Power Monitor Service

Service for monitoring power consumption during test operations.
Provides real-time power measurement and analysis capabilities.
"""

import asyncio
import statistics
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from application.interfaces.hardware.power import PowerService


class PowerMonitor:
    """
    Power consumption monitoring service

    Monitors voltage, current, and calculates power consumption
    in real-time during test operations.
    """

    def __init__(self, power_service: PowerService):
        """
        Initialize Power Monitor

        Args:
            power_service: Power supply service interface
        """
        self._power_service = power_service
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        self._power_data: List[Dict[str, float]] = []
        self._start_time = 0.0

    async def start_monitoring(self, interval: float = 0.5) -> None:
        """
        Start power monitoring

        Args:
            interval: Sampling interval in seconds (default: 0.5s)
        """
        logger.debug(f"🔋 PowerMonitor.start_monitoring() called with interval={interval}s")
        
        if self._is_monitoring:
            logger.warning("Power monitoring is already active")
            return

        # Verify power service is available
        if not self._power_service:
            logger.error("❌ Power service is None - cannot start monitoring")
            raise RuntimeError("Power service is not initialized")
        
        logger.debug(f"Power service object: {self._power_service} (type: {type(self._power_service)})")
        
        try:
            # Test power service connection
            is_connected = await self._power_service.is_connected()
            logger.info(f"Power service connection status: {'✅ CONNECTED' if is_connected else '❌ DISCONNECTED'}")
            
            if not is_connected:
                logger.error("❌ Power service is not connected - cannot start monitoring")
                raise RuntimeError("Power service is not connected")
                
        except Exception as e:
            logger.error(f"❌ Failed to check power service connection: {e}")
            raise RuntimeError(f"Power service connection check failed: {e}") from e

        logger.info(f"Starting power monitoring with {interval}s interval")
        self._is_monitoring = True
        self._power_data = []
        self._start_time = time.perf_counter()

        try:
            self._monitoring_task = asyncio.create_task(self._monitor_loop(interval))
            logger.info("✅ Power monitoring task created successfully")
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

        if self._monitoring_task:
            try:
                logger.info("🔋 Waiting for monitoring task to complete...")
                await self._monitoring_task
                logger.info("✅ Monitoring task completed")
            except asyncio.CancelledError:
                logger.info("🔋 Monitoring task was cancelled")
            except Exception as e:
                logger.error(f"❌ Error while stopping monitoring task: {e}")

        analysis_result = self._analyze_power_data()
        logger.info(f"✅ Power monitoring completed: {len(self._power_data)} samples collected")
        logger.info(f"📊 Analysis result summary: {analysis_result.get('sample_count', 0)} samples, {analysis_result.get('average_power_watts', 0):.4f}W avg")

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
        
        while self._is_monitoring:
            try:
                logger.debug(f"📊 Taking power measurement sample #{len(self._power_data)}...")
                
                # Get all measurements at once using MEAS:ALL? command
                measurements = await self._power_service.get_all_measurements()
                voltage = measurements["voltage"]
                current = measurements["current"]
                power = measurements["power"]
                timestamp = time.perf_counter() - self._start_time

                # Log detailed measurement info for debugging
                if len(self._power_data) % 5 == 0:  # Log every 5th measurement (reduced from 10)
                    logger.info(f"📊 Power monitoring sample #{len(self._power_data)}: {voltage:.4f}V, {current:.4f}A, {power:.4f}W at {timestamp:.2f}s")

                # Store data point
                self._power_data.append(
                    {"timestamp": timestamp, "voltage": voltage, "current": current, "power": power}
                )

                failures = 0  # Reset failure count on success

            except Exception as e:
                failures += 1
                logger.warning(f"⚠️  Power measurement failed ({failures}/{max_failures}): {e}")

                if failures >= max_failures:
                    logger.error("❌ Power monitoring stopped due to repeated failures")
                    break

            await asyncio.sleep(interval)
        
        logger.info(f"🔋 Power monitoring loop ended. Total samples collected: {len(self._power_data)}")

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
