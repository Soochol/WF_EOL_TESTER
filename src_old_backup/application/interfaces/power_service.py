"""
Power Service Interface

Defines the contract for power supply control services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ...domain.value_objects.measurements import VoltageValue, CurrentValue
from ...domain.entities.hardware_device import HardwareDevice
from ...domain.enums.hardware_status import HardwareStatus


class PowerService(ABC):
    """Interface for power supply control services"""
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to power supply
        
        Raises:
            BusinessRuleViolationException: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from power supply
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if power supply is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity representing the power supply
        
        Returns:
            HardwareDevice entity with current status and information
        """
        pass
    
    @abstractmethod
    async def set_voltage(self, channel: int, voltage: VoltageValue) -> None:
        """
        Set target voltage for specified channel
        
        Args:
            channel: Channel number (1-based)
            voltage: Target voltage value with units
            
        Raises:
            BusinessRuleViolationException: If operation fails or unsafe
        """
        pass
    
    @abstractmethod
    async def get_voltage_setting(self, channel: int) -> VoltageValue:
        """
        Get voltage setting for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Current voltage setting
            
        Raises:
            BusinessRuleViolationException: If channel invalid or not connected
        """
        pass
    
    @abstractmethod
    async def get_voltage_actual(self, channel: int) -> VoltageValue:
        """
        Get actual output voltage for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Actual output voltage
            
        Raises:
            BusinessRuleViolationException: If measurement fails
        """
        pass
    
    @abstractmethod
    async def set_current_limit(self, channel: int, current: CurrentValue) -> None:
        """
        Set current limit for specified channel
        
        Args:
            channel: Channel number (1-based)  
            current: Current limit value with units
            
        Raises:
            BusinessRuleViolationException: If operation fails or unsafe
        """
        pass
    
    @abstractmethod
    async def get_current_setting(self, channel: int) -> CurrentValue:
        """
        Get current limit setting for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Current limit setting
            
        Raises:
            BusinessRuleViolationException: If channel invalid or not connected
        """
        pass
    
    @abstractmethod
    async def get_current_actual(self, channel: int) -> CurrentValue:
        """
        Get actual output current for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Actual output current
            
        Raises:
            BusinessRuleViolationException: If measurement fails
        """
        pass
    
    @abstractmethod
    async def set_output_enabled(self, channel: int, enabled: bool) -> None:
        """
        Enable or disable output for specified channel
        
        Args:
            channel: Channel number (1-based)
            enabled: True to enable output, False to disable
            
        Raises:
            BusinessRuleViolationException: If operation fails
        """
        pass
    
    @abstractmethod
    async def is_output_enabled(self, channel: int) -> bool:
        """
        Check if output is enabled for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            True if output enabled, False otherwise
            
        Raises:
            BusinessRuleViolationException: If channel invalid or not connected
        """
        pass
    
    @abstractmethod
    async def measure_all(self, channel: int) -> Dict[str, Any]:
        """
        Measure voltage, current, and power for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Dictionary with 'voltage', 'current', and 'power' measurements
            
        Raises:
            BusinessRuleViolationException: If measurement fails
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
            channel: Channel number (1-based)
            ovp_voltage: Over-voltage protection limit (optional)
            ocp_current: Over-current protection limit (optional)
            
        Raises:
            BusinessRuleViolationException: If operation fails
        """
        pass
    
    @abstractmethod
    async def get_protection_status(self, channel: int) -> Dict[str, bool]:
        """
        Get protection status for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Returns:
            Dictionary with protection status flags (ovp_trip, ocp_trip, etc.)
            
        Raises:
            BusinessRuleViolationException: If channel invalid or not connected
        """
        pass
    
    @abstractmethod
    async def clear_protection(self, channel: int) -> None:
        """
        Clear protection faults for specified channel
        
        Args:
            channel: Channel number (1-based)
            
        Raises:
            BusinessRuleViolationException: If operation fails
        """
        pass
    
    @abstractmethod
    async def reset_device(self) -> None:
        """
        Reset power supply to default state
        
        Raises:
            BusinessRuleViolationException: If reset fails
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information (model, firmware, etc.)
        
        Returns:
            Dictionary with device information
            
        Raises:
            BusinessRuleViolationException: If not connected
        """
        pass