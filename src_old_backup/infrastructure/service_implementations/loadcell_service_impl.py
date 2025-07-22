"""
LoadCell Service Implementation

Concrete implementation of LoadCellService interface using LoadCellAdapter.
"""

from typing import Dict, Any, List
from loguru import logger

from ...application.interfaces.loadcell_service import LoadCellService
from ...domain.value_objects.measurements import ForceValue
from ...domain.entities.hardware_device import HardwareDevice
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException
)

# Import adapter interface
from ..adapters.interfaces.loadcell_adapter import LoadCellAdapter


class LoadCellServiceImpl(LoadCellService):
    """LoadCell service implementation using LoadCellAdapter"""
    
    def __init__(self, adapter: LoadCellAdapter):
        """
        Initialize service with LoadCell adapter
        
        Args:
            adapter: LoadCellAdapter implementation
        """
        self._adapter = adapter
        logger.info(f"LoadCellServiceImpl initialized with {adapter.vendor} adapter")
    
    async def connect(self) -> None:
        """Connect to loadcell via adapter"""
        try:
            await self._adapter.connect()
            logger.info(f"LoadCell service connected via {self._adapter.vendor} adapter")
            
        except Exception as e:
            logger.error(f"LoadCell service connection failed: {e}")
            raise  # Re-raise adapter exceptions as-is
    
    async def disconnect(self) -> None:
        """Disconnect from loadcell via adapter"""
        await self._adapter.disconnect()
        logger.info(f"LoadCell service disconnected via {self._adapter.vendor} adapter")
    
    async def is_connected(self) -> bool:
        """Check if loadcell is connected via adapter"""
        return await self._adapter.is_connected()
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity from adapter"""
        return await self._adapter.get_hardware_device()
    
    async def read_force_value(self) -> ForceValue:
        """Read current force measurement via adapter"""
        return await self._adapter.read_force_value()
    
    async def read_multiple_samples(self, num_samples: int, interval_ms: float = 100) -> List[ForceValue]:
        """Read multiple force samples via adapter"""
        return await self._adapter.read_multiple_samples(num_samples, interval_ms)
    
    async def get_raw_data(self) -> str:
        """Get raw data string from loadcell via adapter"""
        return await self._adapter.get_raw_data()
    
    async def zero_force(self) -> None:
        """Perform auto-zero operation via adapter"""
        await self._adapter.zero_force()
        logger.info("LoadCell auto-zero completed via adapter")
    
    async def set_hold_enabled(self, enabled: bool) -> None:
        """Enable or disable hold function via adapter"""
        await self._adapter.set_hold_enabled(enabled)
        action = "enabled" if enabled else "disabled"
        logger.info(f"LoadCell hold function {action} via adapter")
    
    async def is_hold_enabled(self) -> bool:
        """Check if hold function is enabled via adapter"""
        return await self._adapter.is_hold_enabled()
    
    async def get_measurement_statistics(self, num_samples: int) -> Dict[str, ForceValue]:
        """Get statistical measurements via adapter"""
        return await self._adapter.get_measurement_statistics(num_samples)
    
    async def execute_force_test(self, test_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive force test via adapter"""
        result = await self._adapter.execute_force_test(test_parameters)
        logger.info(f"Force test completed via adapter: {result.get('test_passed', False)}")
        return result
    
    async def calibrate(self, reference_force: ForceValue) -> None:
        """Perform calibration with known reference force via adapter"""
        await self._adapter.calibrate(reference_force)
        logger.info(f"LoadCell calibration completed via adapter with reference {reference_force}")
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get loadcell device information via adapter"""
        return await self._adapter.get_device_info()
    
    async def get_measurement_range(self) -> Dict[str, ForceValue]:
        """Get measurement range capabilities via adapter"""
        return await self._adapter.get_measurement_range()
    
    async def validate_force_range(self, force: ForceValue) -> bool:
        """Validate if force value is within device measurement range via adapter"""
        return await self._adapter.validate_force_range(force)