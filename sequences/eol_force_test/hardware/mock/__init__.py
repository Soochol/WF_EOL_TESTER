"""
Mock hardware implementations for standalone EOL Tester sequence.
These implementations simulate hardware behavior for testing and development.
"""

import asyncio
import random
from typing import Any, Dict, List

from loguru import logger

from ...interfaces import (
    RobotService,
    MCUService,
    LoadCellService,
    PowerService,
    DigitalIOService,
    Force,
    TestMode,
)


class MockRobotService(RobotService):
    """Mock robot service for testing."""

    def __init__(self):
        self._connected = False
        self._position = 0.0
        self._homed = False
        self._servo_enabled = False

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info("MockRobot: Connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = False
        logger.info("MockRobot: Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def home_axis(self, axis_id: int) -> None:
        await asyncio.sleep(0.5)
        self._position = 0.0
        self._homed = True
        logger.info(f"MockRobot: Axis {axis_id} homed")

    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        # Simulate movement time based on distance
        distance = abs(position - self._position)
        move_time = min(distance / velocity, 2.0)  # Cap at 2 seconds
        await asyncio.sleep(move_time)
        self._position = position
        logger.debug(f"MockRobot: Moved to {position}um")

    async def get_position(self, axis_id: int) -> float:
        return self._position

    async def enable_servo(self, axis_id: int) -> None:
        await asyncio.sleep(0.1)
        self._servo_enabled = True
        logger.info(f"MockRobot: Servo {axis_id} enabled")


class MockMCUService(MCUService):
    """Mock MCU service for testing."""

    def __init__(self):
        self._connected = False
        self._temperature = 25.0
        self._target_temperature = 25.0
        self._fan_speed = 0
        self._test_mode = TestMode.MODE_0

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info("MockMCU: Connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = False
        logger.info("MockMCU: Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def get_temperature(self) -> float:
        # Simulate temperature approaching target
        diff = self._target_temperature - self._temperature
        if abs(diff) > 0.5:
            self._temperature += diff * 0.3
        else:
            self._temperature = self._target_temperature
        return self._temperature + random.uniform(-0.2, 0.2)

    async def set_operating_temperature(self, temperature: float) -> None:
        self._target_temperature = temperature
        await asyncio.sleep(0.1)
        logger.info(f"MockMCU: Operating temperature set to {temperature}C")

    async def set_upper_temperature(self, temperature: float) -> None:
        await asyncio.sleep(0.05)
        logger.info(f"MockMCU: Upper temperature set to {temperature}C")

    async def set_fan_speed(self, speed: int) -> None:
        self._fan_speed = speed
        await asyncio.sleep(0.05)
        logger.info(f"MockMCU: Fan speed set to {speed}")

    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
    ) -> None:
        self._target_temperature = operating_temp
        await asyncio.sleep(0.1)
        logger.info(f"MockMCU: Standby heating started (op: {operating_temp}C, standby: {standby_temp}C)")

    async def start_standby_cooling(self) -> None:
        self._target_temperature = 38.0  # Default standby
        await asyncio.sleep(0.1)
        logger.info("MockMCU: Standby cooling started")

    async def wait_boot_complete(self) -> None:
        await asyncio.sleep(0.5)
        logger.info("MockMCU: Boot complete signal received")

    async def set_test_mode(self, mode: TestMode) -> None:
        self._test_mode = mode
        await asyncio.sleep(0.05)
        logger.info(f"MockMCU: Test mode set to {mode}")


class MockLoadCellService(LoadCellService):
    """Mock load cell service for testing."""

    def __init__(self):
        self._connected = False
        self._base_force = 5.0  # Base force in kgf

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info("MockLoadCell: Connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = False
        logger.info("MockLoadCell: Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def read_force(self) -> Force:
        # Simulate force with some noise
        force_value = self._base_force + random.uniform(-0.1, 0.1)
        return Force(value=force_value, unit="kgf")

    async def read_peak_force(self) -> Force:
        # Simulate peak force slightly higher than current
        force_value = self._base_force + random.uniform(0.5, 2.0)
        return Force(value=force_value, unit="kgf")


class MockPowerService(PowerService):
    """Mock power supply service for testing."""

    def __init__(self):
        self._connected = False
        self._voltage = 0.0
        self._current = 0.0
        self._current_limit = 30.0
        self._output_enabled = False

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info("MockPower: Connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = False
        logger.info("MockPower: Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def set_voltage(self, voltage: float) -> None:
        self._voltage = voltage
        await asyncio.sleep(0.05)
        logger.info(f"MockPower: Voltage set to {voltage}V")

    async def get_voltage(self) -> float:
        return self._voltage

    async def set_current(self, current: float) -> None:
        self._current = current
        await asyncio.sleep(0.05)
        logger.info(f"MockPower: Current set to {current}A")

    async def get_current(self) -> float:
        return self._current if self._output_enabled else 0.0

    async def set_current_limit(self, current: float) -> None:
        self._current_limit = current
        await asyncio.sleep(0.05)
        logger.info(f"MockPower: Current limit set to {current}A")

    async def get_current_limit(self) -> float:
        return self._current_limit

    async def enable_output(self) -> None:
        self._output_enabled = True
        await asyncio.sleep(0.1)
        logger.info("MockPower: Output enabled")

    async def disable_output(self) -> None:
        self._output_enabled = False
        await asyncio.sleep(0.1)
        logger.info("MockPower: Output disabled")

    async def is_output_enabled(self) -> bool:
        return self._output_enabled

    async def get_status(self) -> Dict[str, Any]:
        return {
            "voltage": self._voltage,
            "current": self._current,
            "current_limit": self._current_limit,
            "output_enabled": self._output_enabled,
        }

    async def get_all_measurements(self) -> Dict[str, float]:
        current = self._current if self._output_enabled else 0.0
        return {
            "voltage": self._voltage,
            "current": current,
            "power": self._voltage * current,
        }


class MockDigitalIOService(DigitalIOService):
    """Mock digital I/O service for testing."""

    def __init__(self, input_count: int = 16, output_count: int = 16):
        self._connected = False
        self._input_count = input_count
        self._output_count = output_count
        self._inputs = [False] * input_count
        self._outputs = [False] * output_count

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        logger.info("MockDigitalIO: Connected")

    async def disconnect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = False
        logger.info("MockDigitalIO: Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def read_input(self, channel: int) -> bool:
        if 0 <= channel < self._input_count:
            return self._inputs[channel]
        return False

    async def read_all_inputs(self) -> List[bool]:
        return list(self._inputs)

    async def get_input_count(self) -> int:
        return self._input_count

    async def write_output(self, channel: int, value: bool) -> bool:
        if 0 <= channel < self._output_count:
            self._outputs[channel] = value
            logger.debug(f"MockDigitalIO: Output {channel} = {value}")
            return True
        return False

    async def read_output(self, channel: int) -> bool:
        if 0 <= channel < self._output_count:
            return self._outputs[channel]
        return False

    async def reset_all_outputs(self) -> bool:
        self._outputs = [False] * self._output_count
        logger.info("MockDigitalIO: All outputs reset")
        return True

    async def read_all_outputs(self) -> List[bool]:
        return list(self._outputs)

    async def get_output_count(self) -> int:
        return self._output_count

    # Utility method to simulate input signals
    def set_input(self, channel: int, level: bool) -> None:
        """Set input state for simulation purposes."""
        if 0 <= channel < self._input_count:
            self._inputs[channel] = level


# Aliases for factory compatibility
MockLoadCell = MockLoadCellService
MockMCU = MockMCUService
MockPower = MockPowerService
MockRobot = MockRobotService
MockDigitalIO = MockDigitalIOService


__all__ = [
    # Original names
    "MockRobotService",
    "MockMCUService",
    "MockLoadCellService",
    "MockPowerService",
    "MockDigitalIOService",
    # Short aliases
    "MockLoadCell",
    "MockMCU",
    "MockPower",
    "MockRobot",
    "MockDigitalIO",
]
