"""
Mock Digital Input Service

Mock implementation of digital input hardware service for testing and development.
Simulates digital I/O operations without requiring actual hardware.
"""

import random
from typing import Any, Dict, List

import asyncio

from loguru import logger

from application.interfaces.hardware.digital_io import (
    DigitalIOService,
)
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)


class MockDIO(DigitalIOService):
    """Mock 입력 하드웨어 서비스"""

    def __init__(self, config: Dict[str, Any], irq_no: int = 7):
        """
        초기화

        Args:
            config: 설정 딕셔너리 (HardwareConfiguration의 digital_input 섹션)
            irq_no: IRQ 번호 (기본값: 7)
        """
        # Connection/Hardware defaults (same as Ajinextek for compatibility)
        self._board_number = config.get("board_number", config.get("board_no", 0))
        self._module_position = config.get("module_position", 0)
        self._signal_type = config.get("signal_type", 2)
        self._input_count = config.get("input_count", 8)
        self._irq_no = irq_no

        # Operational defaults
        self._debounce_time_ms = config.get(
            "debounce_time_ms", int(config.get("debounce_time", 0.01) * 1000)
        )
        self._retry_count = config.get("retry_count", 3)
        self._auto_initialize = config.get("auto_initialize", True)

        # Mock-specific defaults (hardcoded)
        self._total_pins = 32
        self._simulate_noise = False
        self._noise_probability = 0.01
        self._response_delay = 0.005
        self._connection_delay = 0.1

        # State initialization
        # Config values are already stored directly above
        self._response_delay_s = self._response_delay
        self._connection_delay_s = self._connection_delay

        # State tracking
        self._is_connected = False
        self._input_states: Dict[int, bool] = {}  # 32 input channels (0-31)
        self._output_states: Dict[int, bool] = {}  # 32 output channels (0-31)

        # Additional attributes for compatibility
        # (already stored directly above)

        # Initialize with default states
        for i in range(32):
            self._input_states[i] = False  # All inputs default to LOW
            self._output_states[i] = False  # All outputs default to LOW

        # Override with config if provided
        initial_input_states = config.get("initial_input_states", {})
        for channel, state in initial_input_states.items():
            if 0 <= channel < 32:
                self._input_states[channel] = bool(state)

        # Statistics for testing
        self._operation_count = 0
        self._read_count = 0
        self._write_count = 0
        self._last_operation_time = 0.0

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

            # Set connected state
            self._is_connected = True
            self._operation_count = 0

            logger.info("Mock DIO hardware connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Mock DIO hardware: {e}")
            raise HardwareConnectionError("mock_dio", str(e)) from e

    async def read_input(self, channel: int) -> bool:
        """
        Read digital input from specified channel

        Args:
            channel: Digital input channel number (0~31, user range)

        Returns:
            True if input is HIGH, False if LOW
        """
        if not await self.is_connected():
            raise ConnectionError("Mock DIO hardware not connected")

        # Validate input channel range
        if not (0 <= channel < 32):
            raise ValueError(f"Input channel {channel} out of range [0-31]")

        # Simulate read delay
        await asyncio.sleep(self._response_delay_s * 0.2)

        # Get current state from input channel
        current_state = self._input_states.get(channel, False)

        # Apply noise simulation if enabled
        if self._simulate_noise and random.random() < self._noise_probability:
            current_state = not current_state
            logger.debug(f"Mock: Noise applied to input channel {channel}")

        self._operation_count += 1
        logger.debug(f"Mock DIO read input channel {channel}: {current_state}")
        return current_state

    async def get_input_count(self) -> int:
        """
        Get the number of available digital input channels

        Returns:
            Number of digital input channels (32)
        """
        return 32  # 실제 하드웨어에 맞춰 INPUT 채널은 32개

    async def get_output_count(self) -> int:
        """
        Get the number of available digital output channels

        Returns:
            Number of digital output channels (32)
        """
        return 32  # 실제 하드웨어에 맞춰 OUTPUT 채널은 32개

    async def read_output(self, channel: int) -> bool:
        """
        Read digital output state from specified channel

        Args:
            channel: Digital output channel number (0~31, user range)

        Returns:
            True if output is HIGH, False if LOW

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If read operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_dio", "DIO hardware not connected")

        # Validate output channel range
        if not (0 <= channel < 32):
            raise HardwareOperationError(
                "mock_dio", "read_output", f"Output channel {channel} out of range [0-31]"
            )

        try:
            # Simulate read delay
            await asyncio.sleep(self._response_delay_s * 0.1)

            # Get current output state from channel
            current_state = self._output_states.get(channel, False)

            self._operation_count += 1
            self._read_count += 1

            logger.debug(f"Mock: Read output channel {channel}: {current_state}")
            return current_state

        except Exception as e:
            logger.error(f"Failed to read output channel {channel}: {e}")
            raise HardwareOperationError("mock_dio", "read_output", str(e)) from e

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
            # Reset all states to default
            for i in range(32):
                self._input_states[i] = False
                self._output_states[i] = False

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

    async def write_output(self, channel: int, level: bool) -> bool:
        """
        Write digital output to specified channel

        Args:
            channel: Digital output channel number (0~31, user range)
            level: Output logic level (True=HIGH, False=LOW)

        Returns:
            True if write was successful, False otherwise

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If write operation fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_dio", "DIO hardware not connected")

        # Validate output channel range
        if not (0 <= channel < 32):
            raise HardwareOperationError(
                "mock_dio", "write_output", f"Output channel {channel} out of range [0-31]"
            )

        try:
            # Simulate write delay
            await asyncio.sleep(self._response_delay_s * 0.1)

            # Store output state directly in channel
            self._output_states[channel] = level

            self._operation_count += 1
            self._write_count += 1

            logger.debug(f"Mock: Write output channel {channel} = {'HIGH' if level else 'LOW'}")
            return True

        except Exception as e:
            logger.error(f"Failed to write output channel {channel}: {e}")
            raise HardwareOperationError("mock_dio", "write_output", str(e)) from e

    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, bool]:
        """
        다중 디지털 입력 읽기

        Args:
            pins: 읽을 핀 번호 리스트

        Returns:
            핀별 bool 값 딕셔너리 (True=HIGH, False=LOW)
        """
        if not pins:
            return {}

        results = {}
        for pin in pins:
            results[pin] = await self.read_input(pin)

        logger.debug(
            "Mock: Read multiple inputs from %d pins",
            len(pins),
        )
        return results

    async def write_multiple_outputs(self, pin_values: Dict[int, bool]) -> bool:
        """
        다중 디지털 출력 쓰기

        Args:
            pin_values: 핀별 출력 레벨 딕셔너리 (True=HIGH, False=LOW)

        Returns:
            True if all writes were successful, False otherwise
        """
        if not pin_values:
            return True

        success_count = 0
        for pin, level in pin_values.items():
            try:
                if await self.write_output(pin, level):
                    success_count += 1
            except Exception as e:
                logger.error(f"Mock: Failed to write pin {pin}: {e}")

        all_successful = success_count == len(pin_values)

        logger.debug(
            f"Mock: Write multiple outputs: {success_count}/{len(pin_values)} pins successful"
        )

        return all_successful

    async def read_all_inputs(self) -> List[bool]:
        """
        Read all digital inputs

        Returns:
            List of boolean values representing all input states (32 channels)
        """
        results = []
        for channel in range(32):
            try:
                results.append(await self.read_input(channel))
            except Exception:
                # If read fails, append False as default
                results.append(False)
        return results

    async def read_all_outputs(self) -> List[bool]:
        """
        Read all digital outputs

        Returns:
            List of boolean values representing all output states (32 channels)
        """
        results = []
        for channel in range(32):
            try:
                results.append(await self.read_output(channel))
            except Exception:
                # If read fails, append False as default
                results.append(False)
        return results

    async def reset_all_outputs(self) -> bool:
        """
        모든 출력을 LOW로 리셋

        Returns:
            True if reset was successful, False otherwise
        """
        try:
            # Reset all 32 output channels to LOW
            reset_values = {channel: False for channel in range(32)}
            success = await self.write_multiple_outputs(reset_values)

            if success:
                logger.info("Mock: All outputs reset to LOW")
            return success

        except Exception as e:
            logger.error(f"Failed to reset all outputs: {e}")
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
            "input_channels": 32,
            "output_channels": 32,
            "simulate_noise": self._simulate_noise,
            "noise_probability": self._noise_probability,
            "response_delay_ms": self._response_delay_s * 1000,
            "statistics": {
                "total_operations": self._operation_count,
                "read_operations": self._read_count,
                "write_operations": self._write_count,
            },
            "current_input_states": {
                f"input_{ch}": state for ch, state in self._input_states.items()
            },
            "current_output_states": {
                f"output_{ch}": state for ch, state in self._output_states.items()
            },
        }

        return status

    # Mock-specific utility methods

    async def set_input_state(self, channel: int, level: bool) -> None:
        """
        Mock용: 입력 채널 상태를 직접 설정 (테스트용)

        Args:
            channel: 입력 채널 번호 (0-31)
            level: 설정할 상태 (True=HIGH, False=LOW)

        Raises:
            HardwareOperationError: If channel setting fails
        """
        if not 0 <= channel < 32:
            raise HardwareOperationError(
                "mock_dio",
                "set_input_state",
                f"Input channel {channel} out of range [0-31]",
            )

        self._input_states[channel] = level
        logger.debug(f"Mock: Set input channel {channel} to {'HIGH' if level else 'LOW'}")

    async def simulate_input_change(self, channel: int) -> None:
        """
        Mock용: 입력 상태를 토글 (테스트용)

        Args:
            channel: 입력 채널 번호 (0-31)

        Raises:
            HardwareOperationError: If toggle operation fails
        """
        current_state = self._input_states.get(channel, False)
        new_state = not current_state
        await self.set_input_state(channel, new_state)

    async def simulate_random_inputs(self, channels: List[int]) -> None:
        """
        Mock용: 지정된 채널들에 랜덤 입력 생성 (테스트용)

        Args:
            channels: 랜덤화할 입력 채널 번호 리스트
        """
        for channel in channels:
            if 0 <= channel < 32:
                random_state = random.random() > 0.5
                await self.set_input_state(channel, random_state)

        logger.debug(
            "Mock: Random inputs generated for %d channels",
            len(channels),
        )
