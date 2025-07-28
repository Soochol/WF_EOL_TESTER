"""
Power Interface

Interface for power supply operations and control.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class PowerService(ABC):
    """Abstract interface for power supply operations"""
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to power supply hardware
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from power supply hardware
        
        Raises:
            HardwareOperationError: If disconnection fails
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
    async def set_voltage(self, voltage: float) -> None:
        """
        Set output voltage
        
        Args:
            voltage: Target voltage in volts
            
        Raises:
            HardwareOperationError: If voltage setting fails
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
    async def set_current_limit(self, current: float) -> None:
        """
        Set current limit
        
        Args:
            current: Current limit in amperes
            
        Raises:
            HardwareOperationError: If current limit setting fails
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
    async def enable_output(self) -> None:
        """
        Enable power output
        
        Raises:
            HardwareOperationError: If output enabling fails
        """
        pass
    
    @abstractmethod
    async def disable_output(self) -> None:
        """
        Disable power output
        
        Raises:
            HardwareOperationError: If output disabling fails
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