"""
MCU Interface

Interface for MCU (Microcontroller Unit) operations and control.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from domain.enums.mcu_enums import TestMode


class MCUService(ABC):
    """Abstract interface for MCU operations"""

    @abstractmethod
    async def connect(
        self,
        port: str,
        baudrate: int,
        timeout: float,
        bytesize: int,
        stopbits: int,
        parity: Optional[str]
    ) -> None:
        """
        Connect to MCU hardware

        Args:
            port: Serial port (e.g., "COM4")
            baudrate: Baud rate (e.g., 115200)
            timeout: Connection timeout in seconds
            bytesize: Data bits
            stopbits: Stop bits
            parity: Parity setting

        Raises:
            HardwareConnectionError: If connection fails
        """

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
    async def set_temperature(self, target_temp: Optional[float] = None) -> None:
        """
        Set target temperature for the MCU

        Args:
            target_temp: Target temperature in Celsius. None to use default

        Raises:
            HardwareOperationError: If temperature setting fails
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
        Get current temperature reading

        Returns:
            Current temperature in Celsius
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
    async def set_fan_speed(self, speed_percent: Optional[float] = None) -> None:
        """
        Set fan speed percentage

        Args:
            speed_percent: Fan speed (0-100%). None to use default

        Raises:
            HardwareOperationError: If fan speed setting fails
        """
        ...

    @abstractmethod
    async def get_fan_speed(self) -> float:
        """
        Get current fan speed

        Returns:
            Current fan speed percentage (0-100%)
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
