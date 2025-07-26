"""
MCU Interface

Interface for MCU (Microcontroller Unit) operations and control.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class MCUService(ABC):
    """Abstract interface for MCU operations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to MCU hardware
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from MCU hardware
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if MCU is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def boot_complete(self) -> bool:
        """
        Signal MCU that boot process is complete
        
        Returns:
            True if signal sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send command to MCU
        
        Args:
            command: Command string to send
            data: Optional data payload
            
        Returns:
            Response from MCU as dictionary
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get MCU status information
        
        Returns:
            Dictionary containing MCU status
        """
        pass
    
    @abstractmethod
    async def reset(self) -> bool:
        """
        Reset the MCU
        
        Returns:
            True if reset successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def set_temperature_control(self, enabled: bool, target_temp: Optional[float] = None) -> bool:
        """
        Enable/disable temperature control
        
        Args:
            enabled: Whether to enable temperature control
            target_temp: Target temperature in Celsius (if enabling)
            
        Returns:
            True if command successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_temperature(self) -> float:
        """
        Get current temperature reading
        
        Returns:
            Current temperature in Celsius
        """
        pass