"""
Load Cell Interface

Interface for load cell operations and force measurement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from domain.value_objects.measurements import ForceValue
from domain.value_objects.hardware_configuration import LoadCellConfig


class LoadCellService(ABC):
    """Abstract interface for load cell operations"""

    @abstractmethod
    async def connect(self, loadcell_config: LoadCellConfig) -> None:
        """
        Connect to load cell hardware

        Args:
            loadcell_config: Load cell connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from load cell hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        raise NotImplementedError

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if load cell is connected

        Returns:
            True if connected, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def zero_calibration(self) -> None:
        """
        Perform zero point calibration

        Raises:
            HardwareOperationError: If calibration fails
        """
        raise NotImplementedError

    @abstractmethod
    async def read_force(self) -> ForceValue:
        """
        Read current force measurement

        Returns:
            ForceValue object containing the measured force
        """
        raise NotImplementedError

    @abstractmethod
    async def read_raw_value(self) -> float:
        """
        Read raw ADC value from load cell

        Returns:
            Raw measurement value
        """
        raise NotImplementedError

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get load cell hardware status

        Returns:
            Dictionary containing status information
        """
        raise NotImplementedError

    @abstractmethod
    async def set_measurement_rate(self, rate_hz: int) -> None:
        """
        Set measurement sampling rate

        Args:
            rate_hz: Sampling rate in Hz

        Raises:
            HardwareOperationError: If rate setting fails
        """
        raise NotImplementedError

    @abstractmethod
    async def get_measurement_rate(self) -> int:
        """
        Get current measurement sampling rate

        Returns:
            Current sampling rate in Hz
        """
        raise NotImplementedError
