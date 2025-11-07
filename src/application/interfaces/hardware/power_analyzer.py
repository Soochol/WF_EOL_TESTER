"""
Power Analyzer Interface

Interface for power analyzer operations (measurement-only).
Power analyzers measure voltage, current, and power but do not control power supply.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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

    # ========================================================================
    # INTEGRATION (ENERGY) MEASUREMENT METHODS
    # ========================================================================
    # These methods provide hardware-based energy integration for accurate
    # cumulative energy measurement (Wh). Supported by WT1800E and similar
    # high-precision power analyzers.
    # ========================================================================

    @abstractmethod
    async def setup_integration(self, mode: str = "normal", timer: int = 3600) -> None:
        """
        Setup integration (energy) measurement parameters

        Args:
            mode: Integration mode - "normal" or "continuous"
            timer: Integration timer in seconds (1-36000, default: 3600 = 1 hour)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If setup fails
        """
        ...

    @abstractmethod
    async def start_integration(self) -> None:
        """
        Start integration (energy) measurement

        Must call setup_integration() first.

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If start fails
        """
        ...

    @abstractmethod
    async def stop_integration(self) -> None:
        """
        Stop integration (energy) measurement

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If stop fails
        """
        ...

    @abstractmethod
    async def reset_integration(self) -> None:
        """
        Reset integration (energy) measurement data to zero

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If reset fails
        """
        ...

    @abstractmethod
    async def get_integration_time(self) -> Dict[str, Any]:
        """
        Get integration measurement time information

        Returns:
            Dictionary containing:
            - 'start_time': Integration start time
            - 'stop_time': Integration stop time
            - 'elapsed_time': Elapsed time in seconds

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        ...

    @abstractmethod
    async def get_integration_state(self) -> str:
        """
        Get current integration state from hardware

        Returns:
            Integration state string: "RESET", "READY", "START", "STOP", "ERROR", "TIMEUP"

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        ...

    @abstractmethod
    async def get_integration_data(self, element: Optional[int] = None) -> Dict[str, float]:
        """
        Get integration (energy) measurement data

        Args:
            element: Measurement element/channel (1-6), None = use default

        Returns:
            Dictionary containing:
            - 'active_energy_wh': Active energy in Wh (WP)
            - 'apparent_energy_vah': Apparent energy in VAh (WS)
            - 'reactive_energy_varh': Reactive energy in varh (WQ)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If query fails
        """
        ...
