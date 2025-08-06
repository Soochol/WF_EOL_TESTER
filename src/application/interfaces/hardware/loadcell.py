"""
Load Cell Interface

Interface for load cell operations and force measurement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from domain.value_objects.measurements import ForceValue


class LoadCellService(ABC):
    """Abstract interface for load cell operations"""

    @abstractmethod
    async def connect(
        self,
        port: str,
        baudrate: int,
        timeout: float,
        bytesize: int,
        stopbits: int,
        parity: Optional[str],
        indicator_id: int
    ) -> None:
        """
        Connect to load cell hardware

        Args:
            port: Serial port (e.g., "COM3")
            baudrate: Baud rate (e.g., 9600)
            timeout: Connection timeout in seconds
            bytesize: Data bits
            stopbits: Stop bits
            parity: Parity setting
            indicator_id: Indicator device ID

        Raises:
            HardwareConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from load cell hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if load cell is connected

        Returns:
            True if connected, False otherwise
        """
        ...

    @abstractmethod
    async def zero_calibration(self) -> None:
        """
        Perform zero point calibration

        Raises:
            HardwareOperationError: If calibration fails
        """
        ...

    @abstractmethod
    async def read_force(self) -> ForceValue:
        """
        Read current force measurement

        Returns:
            ForceValue object containing the measured force
        """
        ...

    @abstractmethod
    async def read_raw_value(self) -> float:
        """
        Read raw ADC value from load cell

        Returns:
            Raw measurement value
        """
        ...

    @abstractmethod
    async def hold(self) -> bool:
        """
        Hold the current force measurement
        
        Returns:
            True if hold operation was successful, False otherwise
        """
        ...

    @abstractmethod
    async def hold_release(self) -> bool:
        """
        Release the held force measurement
        
        Returns:
            True if release operation was successful, False otherwise
        """
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get load cell hardware status

        Returns:
            Dictionary containing status information
        """
        ...
