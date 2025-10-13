"""
MCU Interface

Interface for MCU (Microcontroller Unit) operations and control.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Local application imports
from domain.enums.mcu_enums import TestMode


class MCUService(ABC):
    """Abstract interface for MCU operations"""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to MCU hardware

        All connection parameters are configured via dependency injection
        in the hardware container.

        Raises:
            HardwareConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from MCU hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if MCU is connected

        Returns:
            True if connected, False otherwise
        """
        ...

    @abstractmethod
    async def wait_boot_complete(self) -> None:
        """
        Wait for MCU boot process to complete

        Raises:
            HardwareOperationError: If boot waiting fails
        """
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get MCU status information

        Returns:
            Dictionary containing MCU status
        """
        ...

    @abstractmethod
    async def set_operating_temperature(self, target_temp: float) -> None:
        """
        Set operating temperature for the MCU

        Args:
            target_temp: Operating temperature in Celsius

        Raises:
            HardwareOperationError: If operating temperature setting fails
        """
        ...

    @abstractmethod
    async def set_upper_temperature(self, upper_temp: float) -> None:
        """
        Set upper temperature limit for the MCU

        Args:
            upper_temp: Upper temperature limit in Celsius

        Raises:
            HardwareOperationError: If upper temperature setting fails
        """
        ...

    @abstractmethod
    async def get_temperature(self) -> float:
        """
        Get current temperature reading (sends MCU command)

        Returns:
            Current temperature in Celsius
        """
        ...

    def get_cached_temperature(self) -> Optional[float]:
        """
        Get last cached temperature without sending MCU command

        This is a lightweight read operation that returns the most recently
        received temperature value without triggering serial communication.
        Useful for GUI updates during heating/cooling operations.

        Returns:
            Last cached temperature in Celsius, or None if no temperature cached
        """
        ...

    @abstractmethod
    async def set_cooling_temperature(self, target_temp: float) -> None:
        """
        Set cooling temperature for the MCU

        Args:
            target_temp: Target cooling temperature in Celsius

        Raises:
            HardwareOperationError: If cooling temperature setting fails
        """
        ...

    @abstractmethod
    async def set_test_mode(self, mode: TestMode) -> None:
        """
        Set test mode for the MCU

        Args:
            mode: Test mode to set

        Raises:
            HardwareOperationError: If test mode setting fails
        """
        ...

    @abstractmethod
    async def get_test_mode(self) -> TestMode:
        """
        Get current test mode

        Returns:
            Current test mode
        """
        ...

    @abstractmethod
    async def set_fan_speed(self, fan_level: int) -> None:
        """
        Set fan speed level

        Args:
            fan_level: Fan speed level (1-10)

        Raises:
            HardwareOperationError: If fan speed setting fails
        """
        ...

    @abstractmethod
    async def get_fan_speed(self) -> int:
        """
        Get current fan speed

        Returns:
            Current fan speed level (1-10)
        """
        ...

    @abstractmethod
    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int = 10000,
    ) -> None:
        """
        Start standby heating mode

        Args:
            operating_temp: Operating temperature in Celsius
            standby_temp: Standby temperature in Celsius
            hold_time_ms: Hold time in milliseconds

        Raises:
            HardwareOperationError: If heating start fails
        """
        ...

    @abstractmethod
    async def start_standby_cooling(self) -> None:
        """
        Start standby cooling mode

        Raises:
            HardwareOperationError: If cooling start fails
        """
        ...

    def clear_timing_history(self) -> None:
        """
        Clear timing history for new test sessions

        This is a non-async method for clearing internal timing data.
        """
        ...

    def get_all_timing_data(self) -> Dict[str, Any]:
        """
        Get all heating/cooling timing data

        Returns:
            Dictionary containing timing data for heating and cooling transitions
        """
        ...
