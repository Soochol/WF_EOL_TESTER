"""
MCU Interface

Interface for MCU (Microcontroller Unit) operations and control.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from domain.enums.mcu_enums import TestMode, MCUStatus
from domain.value_objects.hardware_configuration import MCUConfig


class MCUService(ABC):
    """Abstract interface for MCU operations"""

    @abstractmethod
    async def connect(self, mcu_config: MCUConfig) -> None:
        """
        Connect to MCU hardware

        Args:
            mcu_config: MCU connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from MCU hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if MCU is connected

        Returns:
            True if connected, False otherwise
        """
        pass

    @abstractmethod
    async def boot_complete(self) -> None:
        """
        Signal MCU that boot process is complete

        Raises:
            HardwareOperationError: If signal sending fails
        """
        pass

    @abstractmethod
    async def send_command(
        self, command: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send command to MCU

        Args:
            command: Command string to send
            data: Optional data payload

        Returns:
            Response from MCU as dictionary
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get MCU status information

        Returns:
            Dictionary containing MCU status
        """
        pass

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset the MCU

        Raises:
            HardwareOperationError: If reset fails
        """
        pass

    @abstractmethod
    async def set_temperature_control(
        self, enabled: bool, target_temp: Optional[float] = None
    ) -> None:
        """
        Enable/disable temperature control

        Args:
            enabled: Whether to enable temperature control
            target_temp: Target temperature in Celsius (if enabling)

        Raises:
            HardwareOperationError: If temperature control setting fails
        """
        pass

    @abstractmethod
    async def get_temperature(self) -> float:
        """
        Get current temperature reading

        Returns:
            Current temperature in Celsius
        """
        pass
