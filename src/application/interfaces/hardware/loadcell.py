"""
Load Cell Interface

Interface for load cell operations and force measurement.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict

# Local application imports
from domain.value_objects.measurements import ForceValue


class LoadCellService(ABC):
    """Abstract interface for load cell operations"""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to load cell hardware

        All connection parameters are configured via dependency injection
        in the hardware container.

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
    async def read_peak_force(
        self, duration_ms: int = 1000, sampling_interval_ms: int = 200
    ) -> ForceValue:
        """
        Read peak force measurement over a specified duration using continuous sampling

        Args:
            duration_ms: Total sampling duration in milliseconds (default: 1000ms)
            sampling_interval_ms: Interval between samples in milliseconds (default: 200ms)

        Returns:
            ForceValue object containing the peak (maximum absolute) force measured

        Raises:
            HardwareOperationError: If measurement fails
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
