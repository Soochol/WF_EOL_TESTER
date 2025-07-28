"""
Load Cell Interface

Interface for load cell operations and force measurement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from domain.value_objects.measurements import ForceValue


class LoadCellService(ABC):
    """Abstract interface for load cell operations"""
    
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to load cell hardware
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from load cell hardware
        
        Raises:
            HardwareOperationError: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if load cell is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def zero_calibration(self) -> None:
        """
        Perform zero point calibration
        
        Raises:
            HardwareOperationError: If calibration fails
        """
        pass
    
    @abstractmethod
    async def read_force(self) -> ForceValue:
        """
        Read current force measurement
        
        Returns:
            ForceValue object containing the measured force
        """
        pass
    
    @abstractmethod
    async def read_raw_value(self) -> float:
        """
        Read raw ADC value from load cell
        
        Returns:
            Raw measurement value
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get load cell hardware status
        
        Returns:
            Dictionary containing status information
        """
        pass
    
    @abstractmethod
    async def set_measurement_rate(self, rate_hz: int) -> None:
        """
        Set measurement sampling rate
        
        Args:
            rate_hz: Sampling rate in Hz
            
        Raises:
            HardwareOperationError: If rate setting fails
        """
        pass
    
    @abstractmethod
    async def get_measurement_rate(self) -> int:
        """
        Get current measurement sampling rate
        
        Returns:
            Current sampling rate in Hz
        """
        pass