"""
MCU Service Implementation

Concrete implementation of MCUService interface using MCUAdapter.
"""

from typing import Dict, Any, Optional, Callable
from loguru import logger

from ...application.interfaces.mcu_service import MCUService, TestMode, MCUStatus
from ...domain.value_objects.measurements import TemperatureValue
from ...domain.entities.hardware_device import HardwareDevice

# Import adapter interface
from ..adapters.interfaces.mcu_adapter import MCUAdapter


class MCUServiceImpl(MCUService):
    """MCU service implementation using MCUAdapter"""
    
    def __init__(self, adapter: MCUAdapter):
        """
        Initialize service with MCU adapter
        
        Args:
            adapter: MCUAdapter implementation
        """
        self._adapter = adapter
        logger.info(f"MCUServiceImpl initialized with {adapter.vendor} adapter")
    
    async def connect(self) -> None:
        """Connect to MCU device via adapter"""
        try:
            await self._adapter.connect()
            logger.info(f"MCU service connected via {self._adapter.vendor} adapter")
            
        except Exception as e:
            logger.error(f"MCU service connection failed: {e}")
            raise  # Re-raise adapter exceptions as-is
    
    async def disconnect(self) -> None:
        """Disconnect from MCU device via adapter"""
        await self._adapter.disconnect()
        logger.info(f"MCU service disconnected via {self._adapter.vendor} adapter")
    
    async def is_connected(self) -> bool:
        """Check if MCU device is connected via adapter"""
        return await self._adapter.is_connected()
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity from adapter"""
        return await self._adapter.get_hardware_device()
    
    # Test Mode Management
    async def enter_test_mode(self, mode: TestMode) -> None:
        """Enter specified test mode via adapter"""
        await self._adapter.enter_test_mode(mode)
        logger.info(f"Entered test mode {mode.name} via adapter")
    
    async def exit_test_mode(self) -> None:
        """Exit current test mode and return to idle via adapter"""
        await self._adapter.exit_test_mode()
        logger.info("Exited test mode via adapter")
    
    async def get_current_test_mode(self) -> Optional[TestMode]:
        """Get current test mode via adapter"""
        return await self._adapter.get_current_test_mode()
    
    # Temperature Control
    async def set_temperature_profile(
        self, 
        upper_temp: TemperatureValue,
        operating_temp: TemperatureValue, 
        cooling_temp: TemperatureValue
    ) -> None:
        """Set complete temperature profile via adapter"""
        await self._adapter.set_temperature_profile(upper_temp, operating_temp, cooling_temp)
        logger.info(f"Set temperature profile via adapter: upper={upper_temp}, operating={operating_temp}, cooling={cooling_temp}")
    
    async def set_operating_temperature(self, temperature: TemperatureValue) -> None:
        """Set operating temperature target via adapter"""
        await self._adapter.set_operating_temperature(temperature)
        logger.info(f"Set operating temperature to {temperature} via adapter")
    
    async def get_current_temperature(self) -> TemperatureValue:
        """Get current temperature reading via adapter"""
        return await self._adapter.get_current_temperature()
    
    async def get_temperature_profile(self) -> Dict[str, TemperatureValue]:
        """Get current temperature profile settings via adapter"""
        return await self._adapter.get_temperature_profile()
    
    # Fan Control
    async def set_fan_speed(self, level: int) -> None:
        """Set fan speed level via adapter"""
        await self._adapter.set_fan_speed(level)
        logger.info(f"Set fan speed to level {level} via adapter")
    
    async def get_fan_speed(self) -> int:
        """Get current fan speed level via adapter"""
        return await self._adapter.get_fan_speed()
    
    # MCU Initialization and Configuration
    async def initialize_mcu(
        self, 
        operating_temp: TemperatureValue,
        standby_temp: TemperatureValue, 
        hold_time_ms: int
    ) -> None:
        """Initialize MCU with operation parameters via adapter"""
        await self._adapter.initialize_mcu(operating_temp, standby_temp, hold_time_ms)
        logger.info(f"MCU initialized via adapter: operating={operating_temp}, standby={standby_temp}, hold_time={hold_time_ms}ms")
    
    # Status and Monitoring
    async def get_mcu_status(self) -> MCUStatus:
        """Get current MCU operational status via adapter"""
        return await self._adapter.get_mcu_status()
    
    async def start_temperature_monitoring(
        self, 
        callback: Callable[[TemperatureValue, MCUStatus], None],
        interval_ms: int = 1000
    ) -> str:
        """Start temperature monitoring with callback via adapter"""
        session_id = await self._adapter.start_temperature_monitoring(callback, interval_ms)
        logger.info(f"Started temperature monitoring session {session_id} via adapter")
        return session_id
    
    async def stop_temperature_monitoring(self, session_id: str) -> None:
        """Stop temperature monitoring session via adapter"""
        await self._adapter.stop_temperature_monitoring(session_id)
        logger.info(f"Stopped temperature monitoring session {session_id} via adapter")
    
    # Safety and Validation
    async def validate_temperature_range(self, temperature: TemperatureValue) -> bool:
        """Validate if temperature is within safe operating range via adapter"""
        return await self._adapter.validate_temperature_range(temperature)
    
    async def emergency_shutdown(self) -> None:
        """Perform emergency shutdown of MCU operations via adapter"""
        await self._adapter.emergency_shutdown()
        logger.warning("Emergency shutdown completed via adapter")
    
    async def reset_mcu(self) -> None:
        """Reset MCU to default state via adapter"""
        await self._adapter.reset_mcu()
        logger.info("MCU reset completed via adapter")
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get MCU device information via adapter"""
        return await self._adapter.get_device_info()
    
    async def run_self_test(self) -> Dict[str, Any]:
        """Run MCU self-test diagnostics via adapter"""
        result = await self._adapter.run_self_test()
        logger.info(f"MCU self-test completed via adapter: {result.get('test_passed', False)}")
        return result