"""
Digital Input Interface

Interface for digital input operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from domain.enums.digital_input_enums import (
    LogicLevel,
    PinMode,
)


class DigitalInputService(ABC):
    """Abstract interface for digital input operations"""

    @abstractmethod
    async def initialize(
        self, config: Dict[str, Any]
    ) -> None:
        """
        Initialize the digital input service

        Args:
            config: Configuration dictionary containing initialization parameters
        """
        ...

    @abstractmethod
    async def read_input(self, channel: int) -> bool:
        """
        Read digital input from specified channel

        Args:
            channel: Digital input channel number

        Returns:
            True if input is HIGH, False if LOW
        """
        ...

    @abstractmethod
    async def read_all_inputs(self) -> List[bool]:
        """
        Read all digital inputs

        Returns:
            List of boolean values representing all input states
        """
        ...

    @abstractmethod
    async def get_input_count(self) -> int:
        """
        Get the number of available digital input channels

        Returns:
            Number of digital input channels
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the digital input device"""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if device is connected

        Returns:
            True if connected, False otherwise
        """
        ...
