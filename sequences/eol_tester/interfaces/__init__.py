"""
Hardware service interfaces for standalone EOL Tester sequence.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class TestMode(Enum):
    """MCU test mode."""
    MODE_0 = 0
    MODE_1 = 1
    MODE_2 = 2


@dataclass
class Force:
    """Force measurement value."""
    value: float
    unit: str = "kgf"


# =============================================================================
# Robot Service Interface
# =============================================================================

class RobotService(ABC):
    """Abstract interface for robot operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to robot controller."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from robot controller."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if robot is connected."""
        ...

    @abstractmethod
    async def home_axis(self, axis_id: int) -> None:
        """Home the specified axis."""
        ...

    @abstractmethod
    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """Move to absolute position."""
        ...

    @abstractmethod
    async def get_position(self, axis_id: int) -> float:
        """Get current position."""
        ...

    @abstractmethod
    async def enable_servo(self, axis_id: int) -> None:
        """Enable servo motor."""
        ...


# =============================================================================
# MCU Service Interface
# =============================================================================

class MCUService(ABC):
    """Abstract interface for MCU operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to MCU."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from MCU."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if MCU is connected."""
        ...

    @abstractmethod
    async def get_temperature(self) -> float:
        """Get current temperature."""
        ...

    @abstractmethod
    async def set_operating_temperature(self, temperature: float) -> None:
        """Set operating temperature."""
        ...

    @abstractmethod
    async def set_upper_temperature(self, temperature: float) -> None:
        """Set upper temperature limit."""
        ...

    @abstractmethod
    async def set_fan_speed(self, speed: int) -> None:
        """Set fan speed (0-10)."""
        ...

    @abstractmethod
    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
    ) -> None:
        """Start standby heating sequence."""
        ...

    @abstractmethod
    async def start_standby_cooling(self) -> None:
        """Start standby cooling."""
        ...

    @abstractmethod
    async def wait_boot_complete(self) -> None:
        """Wait for MCU boot complete signal."""
        ...

    @abstractmethod
    async def set_test_mode(self, mode: TestMode) -> None:
        """Set MCU test mode."""
        ...


# =============================================================================
# LoadCell Service Interface
# =============================================================================

class LoadCellService(ABC):
    """Abstract interface for load cell operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to load cell."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from load cell."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if load cell is connected."""
        ...

    @abstractmethod
    async def read_force(self) -> Force:
        """Read current force."""
        ...

    @abstractmethod
    async def read_peak_force(self) -> Force:
        """Read peak force."""
        ...


# =============================================================================
# Power Service Interface
# =============================================================================

class PowerService(ABC):
    """Abstract interface for power supply operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to power supply."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from power supply."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if power supply is connected."""
        ...

    @abstractmethod
    async def set_voltage(self, voltage: float) -> None:
        """Set output voltage."""
        ...

    @abstractmethod
    async def get_voltage(self) -> float:
        """Get current voltage."""
        ...

    @abstractmethod
    async def set_current(self, current: float) -> None:
        """Set output current."""
        ...

    @abstractmethod
    async def get_current(self) -> float:
        """Get current amperage."""
        ...

    @abstractmethod
    async def set_current_limit(self, current: float) -> None:
        """Set current limit."""
        ...

    @abstractmethod
    async def get_current_limit(self) -> float:
        """Get current limit."""
        ...

    @abstractmethod
    async def enable_output(self) -> None:
        """Enable power output."""
        ...

    @abstractmethod
    async def disable_output(self) -> None:
        """Disable power output."""
        ...

    @abstractmethod
    async def is_output_enabled(self) -> bool:
        """Check if output is enabled."""
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get power supply status."""
        ...

    @abstractmethod
    async def get_all_measurements(self) -> Dict[str, float]:
        """Get all measurements (voltage, current, power)."""
        ...


# =============================================================================
# Digital I/O Service Interface
# =============================================================================

class DigitalIOService(ABC):
    """Abstract interface for digital I/O operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to digital I/O device."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from digital I/O device."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if digital I/O is connected."""
        ...

    @abstractmethod
    async def read_input(self, channel: int) -> bool:
        """Read digital input."""
        ...

    @abstractmethod
    async def read_all_inputs(self) -> List[bool]:
        """Read all digital inputs."""
        ...

    @abstractmethod
    async def get_input_count(self) -> int:
        """Get number of input channels."""
        ...

    @abstractmethod
    async def write_output(self, channel: int, level: bool) -> bool:
        """Write digital output."""
        ...

    @abstractmethod
    async def read_output(self, channel: int) -> bool:
        """Read digital output state."""
        ...

    @abstractmethod
    async def reset_all_outputs(self) -> bool:
        """Reset all outputs to LOW."""
        ...

    async def read_multiple_inputs(self, channels: List[int]) -> Dict[int, bool]:
        """Read multiple inputs."""
        results = {}
        for channel in channels:
            results[channel] = await self.read_input(channel)
        return results

    async def write_multiple_outputs(self, pin_values: Dict[int, bool]) -> bool:
        """Write multiple outputs."""
        success_count = 0
        for channel, level in pin_values.items():
            if await self.write_output(channel, level):
                success_count += 1
        return success_count == len(pin_values)

    async def read_all_outputs(self) -> List[bool]:
        """Read all outputs (default implementation)."""
        return []

    async def get_output_count(self) -> int:
        """Get number of output channels."""
        return 0


__all__ = [
    "TestMode",
    "Force",
    "RobotService",
    "MCUService",
    "LoadCellService",
    "PowerService",
    "DigitalIOService",
]
