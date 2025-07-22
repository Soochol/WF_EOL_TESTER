"""
Power Service Implementation

Concrete implementation of PowerService interface using PowerAdapter.
"""

from typing import Dict, Any, Optional
from loguru import logger

from ...application.interfaces.power_service import PowerService
from ...domain.value_objects.measurements import VoltageValue, CurrentValue
from ...domain.entities.hardware_device import HardwareDevice

# Import adapter interface
from ..adapters.interfaces.power_adapter import PowerAdapter


class PowerServiceImpl(PowerService):
    """Power service implementation using PowerAdapter"""
    
    def __init__(self, adapter: PowerAdapter):
        """
        Initialize service with Power adapter
        
        Args:
            adapter: PowerAdapter implementation
        """
        self._adapter = adapter
        logger.info(f"PowerServiceImpl initialized with {adapter.vendor} adapter")
    
    async def connect(self) -> None:
        """Connect to power supply via adapter"""
        try:
            await self._adapter.connect()
            logger.info(f"Power service connected via {self._adapter.vendor} adapter")
            
        except Exception as e:
            logger.error(f"Power service connection failed: {e}")
            raise  # Re-raise adapter exceptions as-is
    
    async def disconnect(self) -> None:
        """Disconnect from power supply via adapter"""
        await self._adapter.disconnect()
        logger.info(f"Power service disconnected via {self._adapter.vendor} adapter")
    
    async def is_connected(self) -> bool:
        """Check if power supply is connected via adapter"""
        return await self._adapter.is_connected()
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity from adapter"""
        return await self._adapter.get_hardware_device()
    
    async def set_voltage(self, channel: int, voltage: VoltageValue) -> None:
        """Set target voltage for specified channel via adapter"""
        await self._adapter.set_voltage(channel, voltage)
        logger.info(f"Set voltage to {voltage} on channel {channel} via adapter")
    
    async def get_voltage_setting(self, channel: int) -> VoltageValue:
        """Get voltage setting for specified channel via adapter"""
        return await self._adapter.get_voltage_setting(channel)
    
    async def get_voltage_actual(self, channel: int) -> VoltageValue:
        """Get actual output voltage for specified channel via adapter"""
        return await self._adapter.get_voltage_actual(channel)
    
    async def set_current_limit(self, channel: int, current: CurrentValue) -> None:
        """Set current limit for specified channel via adapter"""
        await self._adapter.set_current_limit(channel, current)
        logger.info(f"Set current limit to {current} on channel {channel} via adapter")
    
    async def get_current_setting(self, channel: int) -> CurrentValue:
        """Get current limit setting for specified channel via adapter"""
        return await self._adapter.get_current_setting(channel)
    
    async def get_current_actual(self, channel: int) -> CurrentValue:
        """Get actual output current for specified channel via adapter"""
        return await self._adapter.get_current_actual(channel)
    
    async def set_output_enabled(self, channel: int, enabled: bool) -> None:
        """Enable or disable output for specified channel via adapter"""
        await self._adapter.set_output_enabled(channel, enabled)
        action = "enabled" if enabled else "disabled"
        logger.info(f"Output {action} on channel {channel} via adapter")
    
    async def is_output_enabled(self, channel: int) -> bool:
        """Check if output is enabled for specified channel via adapter"""
        return await self._adapter.is_output_enabled(channel)
    
    async def measure_all(self, channel: int) -> Dict[str, Any]:
        """Measure voltage, current, and power for specified channel via adapter"""
        return await self._adapter.measure_all(channel)
    
    async def set_protection_limits(
        self, 
        channel: int, 
        ovp_voltage: Optional[VoltageValue] = None,
        ocp_current: Optional[CurrentValue] = None
    ) -> None:
        """Set protection limits for specified channel via adapter"""
        await self._adapter.set_protection_limits(channel, ovp_voltage, ocp_current)
        if ovp_voltage:
            logger.info(f"Set OVP to {ovp_voltage} on channel {channel} via adapter")
        if ocp_current:
            logger.info(f"Set OCP to {ocp_current} on channel {channel} via adapter")
    
    async def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """Get protection status for specified channel via adapter"""
        return await self._adapter.get_protection_status(channel)
    
    async def clear_protection(self, channel: int) -> None:
        """Clear protection faults for specified channel via adapter"""
        await self._adapter.clear_protection(channel)
        logger.info(f"Cleared protection faults on channel {channel} via adapter")
    
    async def reset_device(self) -> None:
        """Reset power supply to default state via adapter"""
        await self._adapter.reset_device()
        logger.info("Power supply reset completed via adapter")
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get device information via adapter"""
        return await self._adapter.get_device_info()