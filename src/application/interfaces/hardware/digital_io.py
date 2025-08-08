"""
Digital I/O Interface

Interface for digital input and output operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class DigitalIOService(ABC):
    """Abstract interface for digital input and output operations"""

    # ========================================================================
    # Digital Input Methods
    # ========================================================================

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

    # ========================================================================
    # Digital Output Methods
    # ========================================================================

    @abstractmethod
    async def write_output(self, channel: int, level: bool) -> bool:
        """
        Write digital output to specified channel

        Args:
            channel: Digital output channel number
            level: Output logic level (True=HIGH, False=LOW)

        Returns:
            True if write was successful, False otherwise
        """
        ...

    @abstractmethod
    async def read_output(self, channel: int) -> bool:
        """
        Read digital output state from specified channel

        Args:
            channel: Digital output channel number

        Returns:
            True if output is HIGH, False if LOW
        """
        ...

    @abstractmethod
    async def reset_all_outputs(self) -> bool:
        """
        Reset all outputs to LOW

        Returns:
            True if reset was successful, False otherwise
        """
        ...

    # ========================================================================
    # Batch Operations (Optional advanced methods)
    # ========================================================================

    async def read_multiple_inputs(self, channels: List[int]) -> Dict[int, bool]:
        """
        Read multiple digital inputs (default implementation using single reads)

        Args:
            channels: List of input channel numbers

        Returns:
            Dictionary mapping channel numbers to their boolean values
        """
        results = {}
        for channel in channels:
            results[channel] = await self.read_input(channel)
        return results

    async def write_multiple_outputs(self, pin_values: Dict[int, bool]) -> bool:
        """
        Write multiple digital outputs (default implementation using single writes)

        Args:
            pin_values: Dictionary mapping channel numbers to their boolean values

        Returns:
            True if all writes were successful, False otherwise
        """
        success_count = 0
        for channel, level in pin_values.items():
            if await self.write_output(channel, level):
                success_count += 1
        return success_count == len(pin_values)

    async def read_all_outputs(self) -> List[bool]:
        """
        Read all digital outputs (default implementation using single reads)

        Returns:
            List of boolean values representing all output states
        """
        results = []
        # This is a default implementation - subclasses can override for better performance
        # First we need to determine how many output channels there are
        try:
            output_count = await self.get_output_count()
            for channel in range(output_count):
                try:
                    results.append(await self.read_output(channel))
                except Exception:
                    results.append(False)  # Default to False on error
        except Exception:
            # If we can't determine output count, return empty list
            pass
        return results

    async def get_output_count(self) -> int:
        """
        Get the number of available digital output channels

        Returns:
            Number of digital output channels
        """
        # Default implementation - should be overridden by subclasses
        return 0

    # ========================================================================
    # Connection Management
    # ========================================================================

    @abstractmethod
    async def connect(self, irq_no: int = 7) -> None:
        """
        Connect to the digital I/O device
        
        Args:
            irq_no: IRQ number for connection (default: 7)
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the digital I/O device"""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if device is connected

        Returns:
            True if connected, False otherwise
        """
        ...