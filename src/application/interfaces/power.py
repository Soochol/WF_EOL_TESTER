"""
Power Interface

Interface for power supply operations and control.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PowerService(ABC):
    """Abstract interface for power supply operations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to power supply hardware
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from power supply hardware
        
        Returns:
            True if disconnection successful, False otherwise
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
    async def set_voltage(self, voltage: float) -> bool:
        """
        Set output voltage
        
        Args:
            voltage: Target voltage in volts
            
        Returns:
            True if voltage set successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_voltage(self) -> float:
        """
        Get current output voltage
        
        Returns:
            Current voltage in volts
        """
        pass
    
    @abstractmethod
    async def set_current_limit(self, current: float) -> bool:
        """
        Set current limit
        
        Args:
            current: Current limit in amperes
            
        Returns:
            True if limit set successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_current(self) -> float:
        """
        Get current output current
        
        Returns:
            Current in amperes
        """
        pass
    
    @abstractmethod
    async def enable_output(self) -> bool:
        """
        Enable power output
        
        Returns:
            True if output enabled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def disable_output(self) -> bool:
        """
        Disable power output
        
        Returns:
            True if output disabled successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_output_enabled(self) -> bool:
        """
        Check if power output is enabled
        
        Returns:
            True if output is enabled, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get power supply status
        
        Returns:
            Dictionary containing status information
        """
        pass