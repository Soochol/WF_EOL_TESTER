"""
Power Analyzer Interface

Interface for power analyzer operations (measurement-only).
Power analyzers measure voltage, current, and power but do not control power supply.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Dict, Optional


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

    @abstractmethod
    async def configure_input(
        self,
        voltage_range: Optional[str] = None,
        current_range: Optional[str] = None,
        auto_range: bool = True,
    ) -> None:
        """
        Configure voltage and current input ranges

        Args:
            voltage_range: Voltage range (e.g., "15V", "30V", "60V", "150V", "300V", "600V", "1000V")
            current_range: Current range (e.g., "1A", "2A", "5A", "10A", "20A", "50A")
            auto_range: Enable automatic range adjustment (recommended)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        ...

    @abstractmethod
    async def configure_filter(
        self,
        line_filter: Optional[str] = None,
        frequency_filter: Optional[str] = None,
    ) -> None:
        """
        Configure measurement filters

        Args:
            line_filter: Line filter frequency (e.g., "500HZ", "1KHZ", "10KHZ", "100KHZ")
            frequency_filter: Frequency filter (e.g., "0.5HZ", "1HZ", "10HZ", "100HZ", "1KHZ")

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If configuration fails
        """
        ...
