"""
Power Interface

Interface for power supply operations and control.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PowerService(ABC):
    """Abstract interface for power supply operations"""

    @abstractmethod
    async def connect(
        self,
        host: str,
        port: int,
        timeout: float,
        channel: int
    ) -> None:
        """
        Connect to power supply hardware

        Args:
            host: IP address or hostname
            port: TCP port number
            timeout: Connection timeout in seconds
            channel: Power channel number

        Raises:
            HardwareConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from power supply hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if power supply is connected

        Returns:
            True if connected, False otherwise
        """
        ...

    @abstractmethod
    async def set_voltage(self, voltage: float) -> None:
        """
        Set output voltage

        Args:
            voltage: Target voltage in volts

        Raises:
            HardwareOperationError: If voltage setting fails
        """
        ...

    @abstractmethod
    async def get_voltage(self) -> float:
        """
        Get current output voltage

        Returns:
            Current voltage in volts
        """
        ...

    @abstractmethod
    async def set_current_limit(self, current: float) -> None:
        """
        Set current limit

        Args:
            current: Current limit in amperes

        Raises:
            HardwareOperationError: If current limit setting fails
        """
        ...

    @abstractmethod
    async def get_current_limit(self) -> float:
        """
        Get current limit setting

        Returns:
            Current limit in amperes
        """
        ...

    @abstractmethod
    async def get_current(self) -> float:
        """
        Get current output current

        Returns:
            Current in amperes
        """
        ...

    @abstractmethod
    async def set_current(self, current: float) -> None:
        """
        Set output current

        Args:
            current: Current in amperes

        Raises:
            HardwareOperationError: If current setting fails
        """
        ...

    @abstractmethod
    async def enable_output(self) -> None:
        """
        Enable power output

        Raises:
            HardwareOperationError: If output enabling fails
        """
        ...

    @abstractmethod
    async def disable_output(self) -> None:
        """
        Disable power output

        Raises:
            HardwareOperationError: If output disabling fails
        """
        ...

    @abstractmethod
    async def is_output_enabled(self) -> bool:
        """
        Check if power output is enabled

        Returns:
            True if output is enabled, False otherwise
        """
        ...

    @abstractmethod
    async def get_device_identity(self) -> Optional[str]:
        """
        Get device identification string

        Returns:
            Device identification string from *IDN? command, or None if not available
        """
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get power supply status

        Returns:
            Dictionary containing status information
        """
