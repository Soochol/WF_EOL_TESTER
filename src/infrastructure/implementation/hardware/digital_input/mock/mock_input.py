"""
Mock Digital Input Service

Mock implementation of digital input hardware service for testing and development.
Simulates digital I/O operations without requiring actual hardware.
"""

import random
from typing import Any, Dict, List

import asyncio

from loguru import logger

from application.interfaces.hardware.digital_input import (
    DigitalInputService,
)
from domain.enums.digital_input_enums import (
    LogicLevel,
    PinMode,
)
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)


class MockInput(DigitalInputService):
    """Mock 입력 하드웨어 서비스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리 (HardwareConfiguration의 digital_input 섹션)
        """
        # Connection/Hardware defaults (same as Ajinextek for compatibility)
        self._board_number = config.get("board_number", config.get("board_no", 0))
        self._module_position = config.get("module_position", 0)
        self._signal_type = config.get("signal_type", 2)
        self._input_count = config.get("input_count", 8)

        # Operational defaults
        self._debounce_time_ms = config.get(
            "debounce_time_ms", int(config.get("debounce_time", 0.01) * 1000)
        )
        self._retry_count = config.get("retry_count", 3)
        self._auto_initialize = config.get("auto_initialize", True)

        # Mock-specific defaults
        self._total_pins = config.get("total_pins", 32)
        self._simulate_noise = config.get("simulate_noise", False)
        self._noise_probability = max(0.0, min(1.0, config.get("noise_probability", 0.01)))
        self._response_delay = config.get("response_delay", 0.005)
        self._connection_delay = config.get("connection_delay", 0.1)

        # State initialization
        # Config values are already stored directly above
        self._response_delay_s = self._response_delay
        self._connection_delay_s = self._connection_delay

        # State tracking
        self._is_connected = False
        self._pin_configurations: Dict[int, PinMode] = {}
        self._input_states: Dict[int, LogicLevel] = {}
        self._output_states: Dict[int, LogicLevel] = {}

        # Additional attributes for compatibility
        # (already stored directly above)

        # Initialize input states from config if provided
        initial_input_states = config.get("initial_input_states")
        if initial_input_states:
            self._input_states.update(initial_input_states)

        # Statistics for testing
        self._operation_count = 0
        self._read_count = 0
        self._write_count = 0
        self._last_operation_time = 0.0

    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the digital input service

        Args:
            config: Configuration dictionary containing initialization parameters
        """
        # Apply default + override pattern for configuration
        self._board_number = config.get("board_number", config.get("board_no", self._board_number))
        self._module_position = config.get("module_position", self._module_position)
        self._signal_type = config.get("signal_type", self._signal_type)

        # Operational parameters
        self._debounce_time_ms = config.get(
            "debounce_time_ms",
            int(config.get("debounce_time", self._debounce_time_ms / 1000.0) * 1000),
        )
        self._retry_count = config.get("retry_count", self._retry_count)
        self._auto_initialize = config.get("auto_initialize", self._auto_initialize)

        # Mock-specific parameters
        self._total_pins = config.get("total_pins", self._total_pins)
        self._simulate_noise = config.get("simulate_noise", self._simulate_noise)
        self._noise_probability = max(
            0.0, min(1.0, config.get("noise_probability", self._noise_probability))
        )
        self._response_delay_s = config.get(
            "response_delay", config.get("response_delay_ms", self._response_delay * 1000) / 1000.0
        )
        self._connection_delay_s = config.get("connection_delay", self._connection_delay)

        # Connect the hardware
        await self.connect()

    async def read_input(self, channel: int) -> bool:
        """
        Read digital input from specified channel

        Args:
            channel: Digital input channel number

        Returns:
            True if input is HIGH, False if LOW
        """
        logic_level = await self.read_digital_input(channel)
        return logic_level == LogicLevel.HIGH

    async def get_input_count(self) -> int:
        """
        Get the number of available digital input channels

        Returns:
            Number of digital input channels
        """
        return self._total_pins

    async def connect(self) -> None:
        """
        Mock 하드웨어 연결

        Raises:
            HardwareConnectionError: If connection fails
        """
        try:
            logger.info("Connecting to Mock DIO hardware")

            # Simulate connection delay
            await asyncio.sleep(self._connection_delay_s)

            # Initialize default pin configurations
            await self._initialize_default_pins()

            self._is_connected = True
            self._operation_count = 0

            logger.info("Mock DIO hardware connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Mock DIO hardware: {e}")
            raise HardwareConnectionError("mock_dio", str(e)) from e

    async def disconnect(self) -> None:
        """
        Mock 하드웨어 연결 해제

        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            logger.info("Disconnecting Mock DIO hardware")

            # Reset all outputs before disconnecting
            await self.reset_all_outputs()

            # Simulate disconnection delay
            await asyncio.sleep(self._response_delay_s)

            self._is_connected = False
            self._pin_configurations.clear()
            self._input_states.clear()
            self._output_states.clear()

            logger.info("Mock DIO hardware disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting Mock DIO hardware: {e}")
            raise HardwareOperationError("mock_dio", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def configure_pin(self, pin: int, mode: PinMode) -> None:
        """
        GPIO 핀 모드 설정

        Args:
            pin: 핀 번호
            mode: 핀 모드

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If pin configuration fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_dio", "DIO hardware not connected")

        if not 0 <= pin < self._total_pins:
            raise HardwareOperationError(
                "mock_dio",
                "configure_pin",
                f"Pin {pin} is out of range [0, {self._total_pins-1}]",
            )

        try:
            # Simulate configuration delay
            await asyncio.sleep(self._response_delay_s * 0.1)

            self._pin_configurations[pin] = mode

            # Initialize pin state based on mode
            if mode in [
                PinMode.INPUT,
                PinMode.INPUT_PULLUP,
                PinMode.INPUT_PULLDOWN,
            ]:
                if pin not in self._input_states:
                    # INPUT_PULLUP defaults to HIGH, others to LOW
                    default_level = (
                        LogicLevel.HIGH if mode == PinMode.INPUT_PULLUP else LogicLevel.LOW
                    )
                    self._input_states[pin] = default_level
            elif mode == PinMode.OUTPUT:
                if pin not in self._output_states:
                    self._output_states[pin] = LogicLevel.LOW

            self._operation_count += 1
            logger.debug(f"Mock: Pin {pin} configured as {mode.value}")

        except Exception as e:
            logger.error(f"Failed to configure pin {pin}: {e}")
            raise HardwareOperationError("mock_dio", "configure_pin", str(e)) from e

    async def read_digital_input(self, pin: int) -> LogicLevel:
        """
        디지털 입력 읽기

        Args:
            pin: 핀 번호

        Returns:
            읽은 로직 레벨
        """
        if not await self.is_connected():
            raise ConnectionError("Mock DIO hardware not connected")

        if not 0 <= pin < self._total_pins:
            raise ValueError(f"Pin {pin} is out of range [0, {self._total_pins-1}]")

        # Check if pin is configured as input
        pin_mode = self._pin_configurations.get(pin)
        if pin_mode not in [
            PinMode.INPUT,
            PinMode.INPUT_PULLUP,
            PinMode.INPUT_PULLDOWN,
        ]:
            raise ValueError(f"Pin {pin} is not configured as input (current: {pin_mode})")

        # Simulate read delay
        await asyncio.sleep(self._response_delay_s * 0.2)

        # Get current state
        current_level = self._input_states.get(pin, LogicLevel.LOW)

        # Apply noise simulation if enabled
        if self._simulate_noise and random.random() < self._noise_probability:
            current_level = LogicLevel.HIGH if current_level == LogicLevel.LOW else LogicLevel.LOW
            logger.debug(f"Mock: Noise applied to pin {pin}")

        self._operation_count += 1
        self._read_count += 1

        logger.debug(f"Mock: Read pin {pin} = {current_level.name}")
        return current_level

    async def write_digital_output(self, pin: int, level: LogicLevel) -> None:
        """
        디지털 출력 쓰기

        Args:
            pin: 핀 번호
            level: 출력할 로직 레벨

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If write operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_dio", "DIO hardware not connected")

        if not 0 <= pin < self._total_pins:
            raise HardwareOperationError(
                "mock_dio",
                "write_digital_output",
                f"Pin {pin} is out of range [0, {self._total_pins-1}]",
            )

        # Check if pin is configured as output
        pin_mode = self._pin_configurations.get(pin)
        if pin_mode != PinMode.OUTPUT:
            raise HardwareOperationError(
                "mock_dio",
                "write_digital_output",
                f"Pin {pin} is not configured as output (current: {pin_mode})",
            )

        try:
            # Simulate write delay
            await asyncio.sleep(self._response_delay_s * 0.2)

            # Update output state
            self._output_states[pin] = level

            self._operation_count += 1
            self._write_count += 1

            logger.debug(f"Mock: Write pin {pin} = {level.name}")

        except Exception as e:
            logger.error(f"Failed to write to pin {pin}: {e}")
            raise HardwareOperationError("mock_dio", "write_digital_output", str(e)) from e

    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, LogicLevel]:
        """
        다중 디지털 입력 읽기

        Args:
            pins: 읽을 핀 번호 리스트

        Returns:
            핀별 로직 레벨 딕셔너리
        """
        if not pins:
            return {}

        results = {}
        for pin in pins:
            results[pin] = await self.read_digital_input(pin)

        logger.debug(
            "Mock: Read multiple inputs from %d pins",
            len(pins),
        )
        return results

    async def write_multiple_outputs(self, pin_values: Dict[int, LogicLevel]) -> None:
        """
        다중 디지털 출력 쓰기

        Args:
            pin_values: 핀별 출력 레벨 딕셔너리

        Raises:
            HardwareOperationError: If any write operation fails
        """
        if not pin_values:
            return

        failed_pins = []
        for pin, level in pin_values.items():
            try:
                await self.write_digital_output(pin, level)
            except Exception as e:
                logger.error(f"Mock: Failed to write pin {pin}: {e}")
                failed_pins.append(pin)

        if failed_pins:
            raise HardwareOperationError(
                "mock_dio",
                "write_multiple_outputs",
                f"Failed to write to pins: {failed_pins}",
            )

        logger.debug(
            "Mock: Write multiple outputs: %d pins successful",
            len(pin_values),
        )

    async def read_all_inputs(self) -> List[bool]:
        """
        Read all digital inputs

        Returns:
            List of boolean values representing all input states
        """
        results = []
        for pin in range(self._total_pins):
            # Check if pin is configured as input, if not configure it as input
            if pin not in self._pin_configurations:
                await self.configure_pin(pin, PinMode.INPUT)

            pin_mode = self._pin_configurations.get(pin)
            if pin_mode in [
                PinMode.INPUT,
                PinMode.INPUT_PULLUP,
                PinMode.INPUT_PULLDOWN,
            ]:
                try:
                    logic_level = await self.read_digital_input(pin)
                    results.append(logic_level == LogicLevel.HIGH)
                except Exception:
                    # If read fails, append False as default
                    results.append(False)
            else:
                # For non-input pins, append False
                results.append(False)

        return results

    async def get_pin_configuration(
        self,
    ) -> Dict[int, PinMode]:
        """
        현재 핀 설정 상태 조회

        Returns:
            핀별 설정 모드 딕셔너리
        """
        return self._pin_configurations.copy()

    async def reset_all_outputs(self) -> None:
        """
        모든 출력을 LOW로 리셋

        Raises:
            HardwareOperationError: If reset operation fails
        """
        output_pins = [
            pin for pin, mode in self._pin_configurations.items() if mode == PinMode.OUTPUT
        ]

        if not output_pins:
            return

        try:
            reset_values = {pin: LogicLevel.LOW for pin in output_pins}
            await self.write_multiple_outputs(reset_values)
            logger.info("Mock: All outputs reset to LOW")

        except Exception as e:
            logger.error("Failed to reset all outputs: %s", e)
            raise HardwareOperationError("mock_dio", "reset_all_outputs", str(e)) from e

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "hardware_type": "Mock DIO",
            "total_pins": self._total_pins,
            "configured_pins": len(self._pin_configurations),
            "input_pins": [
                pin
                for pin, mode in self._pin_configurations.items()
                if mode
                in [
                    PinMode.INPUT,
                    PinMode.INPUT_PULLUP,
                    PinMode.INPUT_PULLDOWN,
                ]
            ],
            "output_pins": [
                pin for pin, mode in self._pin_configurations.items() if mode == PinMode.OUTPUT
            ],
            "simulate_noise": self._simulate_noise,
            "noise_probability": self._noise_probability,
            "response_delay_ms": self._response_delay_s * 1000,
            "statistics": {
                "total_operations": self._operation_count,
                "read_operations": self._read_count,
                "write_operations": self._write_count,
            },
            "current_input_states": {pin: level.name for pin, level in self._input_states.items()},
            "current_output_states": {
                pin: level.name for pin, level in self._output_states.items()
            },
        }

        return status

    # Mock-specific utility methods

    async def set_input_state(self, pin: int, level: LogicLevel) -> None:
        """
        Mock용: 입력 핀 상태를 직접 설정 (테스트용)

        Args:
            pin: 핀 번호
            level: 설정할 로직 레벨

        Raises:
            HardwareOperationError: If pin setting fails
        """
        if not 0 <= pin < self._total_pins:
            raise HardwareOperationError(
                "mock_dio",
                "set_input_state",
                f"Pin {pin} is out of range [0, {self._total_pins-1}]",
            )

        pin_mode = self._pin_configurations.get(pin)
        if pin_mode not in [
            PinMode.INPUT,
            PinMode.INPUT_PULLUP,
            PinMode.INPUT_PULLDOWN,
        ]:
            raise HardwareOperationError(
                "mock_dio",
                "set_input_state",
                f"Pin {pin} is not configured as input (current: {pin_mode})",
            )

        self._input_states[pin] = level
        logger.debug(f"Mock: Set input pin {pin} to {level.name}")

    async def simulate_input_change(self, pin: int) -> None:
        """
        Mock용: 입력 상태를 토글 (테스트용)

        Args:
            pin: 핀 번호

        Raises:
            HardwareOperationError: If toggle operation fails
        """
        current_level = self._input_states.get(pin, LogicLevel.LOW)
        new_level = LogicLevel.HIGH if current_level == LogicLevel.LOW else LogicLevel.LOW
        await self.set_input_state(pin, new_level)

    async def simulate_random_inputs(self, pins: List[int]) -> None:
        """
        Mock용: 지정된 핀들에 랜덤 입력 생성 (테스트용)

        Args:
            pins: 랜덤화할 핀 번호 리스트
        """
        for pin in pins:
            random_level = LogicLevel.HIGH if random.random() > 0.5 else LogicLevel.LOW
            await self.set_input_state(pin, random_level)

        logger.debug(
            "Mock: Random inputs generated for %d pins",
            len(pins),
        )

    async def _initialize_default_pins(self) -> None:
        """기본 핀 설정 초기화"""
        # Configure first half as inputs, second half as outputs
        half_pins = self._total_pins // 2

        for pin in range(half_pins):
            await self.configure_pin(pin, PinMode.INPUT)

        for pin in range(half_pins, self._total_pins):
            await self.configure_pin(pin, PinMode.OUTPUT)

        logger.debug(
            "Mock: Initialized %d input pins and %d output pins",
            half_pins,
            half_pins,
        )
