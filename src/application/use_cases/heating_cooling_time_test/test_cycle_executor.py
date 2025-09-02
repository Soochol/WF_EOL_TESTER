"""
Test Cycle Executor for Heating/Cooling Time Test

Executes heating and cooling test cycles and manages power monitoring.
Handles the core test execution logic for temperature transitions.
"""

import asyncio
from typing import Dict, List, Any
from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.test.power_monitor import PowerMonitor


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

    async def execute_test_cycles(self, hc_config, repeat_count: int) -> Dict[str, Any]:
        """
        Execute all heating/cooling test cycles
        
        Args:
            hc_config: Heating/cooling configuration
            repeat_count: Number of cycles to perform
            
        Returns:
            Dictionary containing cycle results and power data
        """
        logger.info(f"Temperature range: {hc_config.standby_temperature}°C ↔ {hc_config.activation_temperature}°C")
        logger.info(f"Wait times - Heating: {hc_config.heating_wait_time}s, Cooling: {hc_config.cooling_wait_time}s, Stabilization: {hc_config.stabilization_wait_time}s")
        
        # Start power monitoring BEFORE heating/cooling operations begin
        await self._start_power_monitoring(hc_config)
        
        try:
            # Perform test cycles
            await self._perform_cycles(hc_config, repeat_count)
            
            # Stop power monitoring and get data
            full_cycle_power_data = await self._stop_power_monitoring(hc_config)
            
            # Get timing data from MCU
            timing_data = self._get_timing_data()
            
            return {
                "timing_data": timing_data,
                "power_data": full_cycle_power_data,
            }
            
        except Exception as e:
            # Ensure power monitoring is stopped on error
            if hc_config.power_monitoring_enabled and self._power_monitor.is_monitoring():
                try:
                    await self._power_monitor.stop_monitoring()
                except Exception as stop_error:
                    logger.error(f"Failed to stop power monitoring during error cleanup: {stop_error}")
            raise e

    async def _start_power_monitoring(self, hc_config) -> None:
        """
        Start power monitoring if enabled
        
        Args:
            hc_config: Heating/cooling configuration
        """
        if hc_config.power_monitoring_enabled:
            logger.debug("🔋 Starting power monitoring BEFORE heating/cooling operations...")
            logger.debug(f"Power Monitor object: {self._power_monitor} (type: {type(self._power_monitor)})")
            logger.info(f"Power Monitor is_monitoring: {self._power_monitor.is_monitoring()}")
            
            try:
                await self._power_monitor.start_monitoring(interval=hc_config.power_monitoring_interval)
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
            logger.info(f"=== Test Cycle {i+1}/{repeat_count} ===")

            # Heating phase (standby → activation)
            logger.info(f"Heating: {hc_config.standby_temperature}°C → {hc_config.activation_temperature}°C")
            await mcu_service.start_standby_heating(
                operating_temp=hc_config.activation_temperature, 
                standby_temp=hc_config.standby_temperature
            )
            
            # Wait after heating completion
            logger.info(f"Heating wait time: {hc_config.heating_wait_time}s")
            await asyncio.sleep(hc_config.heating_wait_time)

            # Cooling phase (activation → standby)
            logger.info(f"Cooling: {hc_config.activation_temperature}°C → {hc_config.standby_temperature}°C")
            await mcu_service.start_standby_cooling()
            
            # Wait after cooling completion  
            logger.info(f"Cooling wait time: {hc_config.cooling_wait_time}s")
            await asyncio.sleep(hc_config.cooling_wait_time)

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

    def _get_timing_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get timing data from MCU for all cycles
        
        Returns:
            Dictionary containing heating and cooling timing results
        """
        mcu_service = self._hardware_services.mcu_service
        timing_data = mcu_service.get_all_timing_data()
        
        return {
            "heating_results": timing_data.get("heating_transitions", []),
            "cooling_results": timing_data.get("cooling_transitions", []),
        }
