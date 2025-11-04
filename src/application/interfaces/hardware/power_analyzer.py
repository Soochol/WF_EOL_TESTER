"""
Power Analyzer Interface

Interface for power analyzer operations (measurement-only).
Power analyzers measure voltage, current, and power but do not control power supply.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Dict


class PowerAnalyzerService(ABC):
    """Abstract interface for power analyzer operations (measurement-only)"""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to power analyzer hardware

        All connection parameters are configured via dependency injection
        in the hardware container.

        Raises:
            HardwareConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from power analyzer hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if power analyzer is connected

        Returns:
            True if connected, False otherwise
        """
        ...

    @abstractmethod
    async def get_measurements(self) -> Dict[str, float]:
        """
        Get all measurements at once (voltage, current, power)

        Returns:
            Dictionary containing:
            - 'voltage': Measured voltage in volts
            - 'current': Measured current in amperes
            - 'power': Measured power in watts

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If measurement fails
        """
        ...

    @abstractmethod
    async def get_device_identity(self) -> str:
        """
        Get device identification string

        Returns:
            Device identification string from *IDN? command

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        ...
