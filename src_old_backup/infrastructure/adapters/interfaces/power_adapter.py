"""
Power Adapter Interface

Defines the contract for power supply hardware adapters.
Provides business logic abstraction over power supply controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ....domain.value_objects.measurements import VoltageValue, CurrentValue
from ....domain.entities.hardware_device import HardwareDevice
from ..base import HardwareAdapterBase


class PowerAdapter(HardwareAdapterBase):
    """
    Abstract interface for power supply adapters
    
    Provides business logic layer between PowerService and hardware controllers.
    Handles domain object conversion, safety validation, and business rule enforcement.
    """
    
    def __init__(self, vendor: str):
        """
        Initialize power adapter
        
        Args:
            vendor: Power supply vendor name
        """
        super().__init__("power_supply", vendor)
    
    @abstractmethod
    async def set_voltage(self, channel: int, voltage: VoltageValue) -> None:
        """
        Set target voltage for specified channel
        
        Args:
            channel: Channel number
            voltage: Target voltage as domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails or voltage invalid
            HardwareNotReadyException: If device not ready
            UnsafeOperationException: If voltage outside safe limits
        """
        pass
    
    @abstractmethod
    async def get_voltage_setting(self, channel: int) -> VoltageValue:
        """
        Get voltage setting for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            VoltageValue domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_voltage_actual(self, channel: int) -> VoltageValue:
        """
        Get actual output voltage for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            VoltageValue domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def set_current_limit(self, channel: int, current: CurrentValue) -> None:
        """
        Set current limit for specified channel
        
        Args:
            channel: Channel number
            current: Current limit as domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails or current invalid
            HardwareNotReadyException: If device not ready
            UnsafeOperationException: If current outside safe limits
        """
        pass
    
    @abstractmethod
    async def get_current_setting(self, channel: int) -> CurrentValue:
        """
        Get current limit setting for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            CurrentValue domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_current_actual(self, channel: int) -> CurrentValue:
        """
        Get actual output current for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            CurrentValue domain object
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def set_output_enabled(self, channel: int, enabled: bool) -> None:
        """
        Enable or disable output for specified channel
        
        Args:
            channel: Channel number
            enabled: True to enable, False to disable
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def is_output_enabled(self, channel: int) -> bool:
        """
        Check if output is enabled for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            True if enabled, False otherwise
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def measure_all(self, channel: int) -> Dict[str, Any]:
        """
        Measure voltage, current, and power for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            Dictionary with 'voltage', 'current', 'power' measurements
            
        Raises:
            BusinessRuleViolationException: If measurement fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def set_protection_limits(
        self, 
        channel: int, 
        ovp_voltage: Optional[VoltageValue] = None,
        ocp_current: Optional[CurrentValue] = None
    ) -> None:
        """
        Set protection limits for specified channel
        
        Args:
            channel: Channel number
            ovp_voltage: Over-voltage protection limit (optional)
            ocp_current: Over-current protection limit (optional)
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """
        Get protection status for specified channel
        
        Args:
            channel: Channel number
            
        Returns:
            Dictionary with protection status flags
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def clear_protection(self, channel: int) -> None:
        """
        Clear protection faults for specified channel
        
        Args:
            channel: Channel number
            
        Raises:
            BusinessRuleViolationException: If operation fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def reset_device(self) -> None:
        """
        Reset power supply to default state
        
        Raises:
            BusinessRuleViolationException: If reset fails
            HardwareNotReadyException: If device not ready
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information
        
        Returns:
            Device information including model, capabilities, status
            
        Raises:
            BusinessRuleViolationException: If info retrieval fails
            HardwareNotReadyException: If device not ready
        """
        pass