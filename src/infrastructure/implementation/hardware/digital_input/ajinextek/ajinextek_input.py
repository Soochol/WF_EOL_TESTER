"""
Ajinextek DIO Input Service

Service implementation for Ajinextek Digital I/O cards.
Provides digital input/output control through AXL library.
"""

from typing import Any, Dict, List, Optional

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
from infrastructure.implementation.hardware.digital_input.ajinextek.constants import (
    COMMAND_DESCRIPTIONS,
    DEFAULT_BOARD_NUMBER,
    DEFAULT_CONFIG,
    DEFAULT_DEBOUNCE_TIME_MS,
    DEFAULT_MODULE_POSITION,
    DEFAULT_RETRY_COUNT,
    LOGIC_HIGH,
    LOGIC_LOW,
    MAX_INPUT_CHANNELS,
    MAX_OUTPUT_CHANNELS,
    PIN_MODE_INPUT,
    PIN_MODE_INPUT_PULLDOWN,
    PIN_MODE_INPUT_PULLUP,
    PIN_MODE_OUTPUT,
    STATUS_MESSAGES,
)
from infrastructure.implementation.hardware.digital_input.ajinextek.error_codes import (
    AjinextekChannelError,
    AjinextekConfigurationError,
    AjinextekDIOError,
    AjinextekErrorCode,
    AjinextekHardwareError,
    AjinextekOperationError,
    create_hardware_error,
    validate_board_number,
    validate_channel_list,
    validate_channel_number,
    validate_module_position,
    validate_pin_values,
)


class AjinextekInput(DigitalInputService):
    """Ajinextek DIO 카드 통합 서비스"""

    def __init__(
        self,
        board_number: int = DEFAULT_BOARD_NUMBER,
        module_position: int = DEFAULT_MODULE_POSITION,
        signal_type: int = 2,  # 24V industrial
        debounce_time_ms: int = DEFAULT_DEBOUNCE_TIME_MS,
        retry_count: int = DEFAULT_RETRY_COUNT,
        auto_initialize: bool = True,
    ):
        """
        초기화

        Args:
            board_number: DIO 보드 번호
            module_position: 모듈 위치
            signal_type: 신호 타입 (0=TTL, 1=CMOS, 2=24V)
            debounce_time_ms: 디바운스 시간 (밀리초)
            retry_count: 재시도 횟수
            auto_initialize: 자동 초기화 여부
        """
        # Validate parameters
        validate_board_number(board_number)
        validate_module_position(module_position)

        self._board_number = board_number
        self._module_position = module_position
        self._signal_type = signal_type
        self._debounce_time_ms = debounce_time_ms
        self._retry_count = retry_count
        self._auto_initialize = auto_initialize

        # State tracking
        self._is_connected = False
        self._is_initialized = False
        self._pin_configurations: Dict[int, PinMode] = {}
        self._last_input_states: Dict[int, LogicLevel] = {}
        self._last_output_states: Dict[int, LogicLevel] = {}

        # AXL library interface (placeholder - would use ctypes in real implementation)
        self._axl_lib = None

    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the digital input service

        Args:
            config: Configuration dictionary containing initialization parameters
        """
        # Update configuration if provided
        if "board_number" in config:
            self._board_number = config["board_number"]
        if "module_position" in config:
            self._module_position = config["module_position"]
        if "signal_type" in config:
            self._signal_type = config["signal_type"]
        if "debounce_time_ms" in config:
            self._debounce_time_ms = config["debounce_time_ms"]

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
        return MAX_INPUT_CHANNELS

    async def connect(self) -> None:
        """
        DIO 하드웨어 연결

        Returns:
            연결 성공 여부

        Raises:
            AjinextekHardwareError: 하드웨어 연결 실패
        """
        try:
            logger.info(f"Connecting to Ajinextek DIO board {self._board_number}")

            # Load AXL library (placeholder)
            if not await self._load_axl_library():
                raise AjinextekHardwareError(
                    "Failed to load AXL library",
                    error_code=int(AjinextekErrorCode.LIBRARY_NOT_LOADED),
                )

            # Open board connection (placeholder)
            if not await self._open_board():
                raise AjinextekHardwareError(
                    f"Failed to open DIO board {self._board_number}",
                    error_code=int(AjinextekErrorCode.BOARD_NOT_DETECTED),
                )

            # Detect and configure modules (placeholder)
            if not await self._detect_modules():
                raise AjinextekHardwareError(
                    f"Failed to detect modules on board {self._board_number}",
                    error_code=int(AjinextekErrorCode.MODULE_NOT_FOUND),
                )

            # Initialize default pin configurations
            if self._auto_initialize:
                await self._initialize_default_pins()

            self._is_connected = True
            self._is_initialized = True

            logger.info(STATUS_MESSAGES["board_connected"])
            return True

        except AjinextekDIOError:
            raise
        except Exception as e:
            raise AjinextekHardwareError(
                f"Unexpected error connecting to DIO hardware: {e}",
                error_code=int(AjinextekErrorCode.HARDWARE_INITIALIZATION_FAILED),
            ) from e

    async def disconnect(self) -> None:
        """
        DIO 하드웨어 연결 해제

        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._is_connected:
                # Reset all outputs before disconnecting
                await self.reset_all_outputs()

                # Close board connection (placeholder)
                await self._close_board()

                # Unload library (placeholder)
                await self._unload_axl_library()

            self._is_connected = False
            self._is_initialized = False
            self._pin_configurations.clear()
            self._last_input_states.clear()
            self._last_output_states.clear()

            logger.info(STATUS_MESSAGES["board_disconnected"])
            return True

        except Exception as e:
            logger.error(f"Error disconnecting DIO hardware: {e}")
            return False

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected and self._is_initialized

    async def configure_pin(self, pin: int, mode: PinMode) -> None:
        """
        GPIO 핀 모드 설정

        Args:
            pin: 핀 번호
            mode: 핀 모드

        Returns:
            설정 성공 여부

        Raises:
            AjinextekChannelError: 유효하지 않은 채널
            AjinextekHardwareError: 하드웨어 통신 실패
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        validate_channel_number(pin, MAX_INPUT_CHANNELS + MAX_OUTPUT_CHANNELS)

        try:
            # Convert PinMode to hardware-specific values
            hw_mode = self._convert_pin_mode(mode)

            # Configure pin in hardware (placeholder)
            success = await self._configure_hardware_pin(pin, hw_mode)

            if success:
                self._pin_configurations[pin] = mode
                logger.debug(f"Pin {pin} configured as {mode.value}")
                return True
            else:
                raise AjinextekOperationError(
                    f"Failed to configure pin {pin} as {mode.value}",
                    error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
                )

        except AjinextekDIOError:
            raise
        except Exception as e:
            raise AjinextekOperationError(
                f"Unexpected error configuring pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_NOT_SUPPORTED),
            ) from e

    async def read_digital_input(self, pin: int) -> LogicLevel:
        """
        디지털 입력 읽기

        Args:
            pin: 핀 번호

        Returns:
            읽은 로직 레벨

        Raises:
            AjinextekChannelError: 유효하지 않은 채널 또는 설정되지 않은 입력
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        validate_channel_number(pin, MAX_INPUT_CHANNELS)

        # Check if pin is configured as input
        pin_mode = self._pin_configurations.get(pin)
        if pin_mode not in [PinMode.INPUT, PinMode.INPUT_PULLUP, PinMode.INPUT_PULLDOWN]:
            raise AjinextekChannelError(
                f"Pin {pin} is not configured as input (current: {pin_mode})",
                error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
            )

        try:
            # Read from hardware (placeholder)
            hw_value = await self._read_hardware_input(pin)

            # Convert hardware value to LogicLevel
            logic_level = LogicLevel.HIGH if hw_value else LogicLevel.LOW

            # Update state cache
            self._last_input_states[pin] = logic_level

            logger.debug(f"Read pin {pin}: {logic_level.name}")
            return logic_level

        except Exception as e:
            raise AjinextekOperationError(
                f"Failed to read input pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def write_digital_output(self, pin: int, level: LogicLevel) -> None:
        """
        디지털 출력 쓰기

        Args:
            pin: 핀 번호
            level: 출력할 로직 레벨

        Returns:
            출력 성공 여부
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        validate_channel_number(pin, MAX_OUTPUT_CHANNELS)

        # Check if pin is configured as output
        pin_mode = self._pin_configurations.get(pin)
        if pin_mode != PinMode.OUTPUT:
            raise AjinextekChannelError(
                f"Pin {pin} is not configured as output (current: {pin_mode})",
                error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
            )

        try:
            # Convert LogicLevel to hardware value
            hw_value = 1 if level == LogicLevel.HIGH else 0

            # Write to hardware (placeholder)
            success = await self._write_hardware_output(pin, hw_value)

            if success:
                self._last_output_states[pin] = level
                logger.debug(f"Write pin {pin}: {level.name}")
                return True
            else:
                raise AjinextekOperationError(
                    f"Failed to write output pin {pin}",
                    error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
                )

        except AjinextekDIOError:
            raise
        except Exception as e:
            raise AjinextekOperationError(
                f"Failed to write output pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, LogicLevel]:
        """
        다중 디지털 입력 읽기

        Args:
            pins: 읽을 핀 번호 리스트

        Returns:
            핀별 로직 레벨 딕셔너리
        """
        validate_channel_list(pins, MAX_INPUT_CHANNELS)

        results = {}
        for pin in pins:
            results[pin] = await self.read_digital_input(pin)

        logger.debug(f"Read multiple inputs: {len(pins)} pins")
        return results

    async def write_multiple_outputs(self, pin_values: Dict[int, LogicLevel]) -> None:
        """
        다중 디지털 출력 쓰기

        Args:
            pin_values: 핀별 출력 레벨 딕셔너리

        Returns:
            출력 성공 여부
        """
        # Convert LogicLevel values to integers for validation
        pin_int_values = {
            pin: (1 if level == LogicLevel.HIGH else 0) for pin, level in pin_values.items()
        }
        validate_pin_values(pin_int_values, MAX_OUTPUT_CHANNELS)

        try:
            success_count = 0
            for pin, level in pin_values.items():
                if await self.write_digital_output(pin, level):
                    success_count += 1

            all_success = success_count == len(pin_values)
            logger.debug(f"Write multiple outputs: {success_count}/{len(pin_values)} successful")
            return all_success

        except Exception as e:
            logger.error(f"Error writing multiple outputs: {e}")
            return False

    async def read_all_inputs(self) -> List[bool]:
        """
        Read all digital inputs

        Returns:
            List of boolean values representing all input states
        """
        results = []
        for channel in range(MAX_INPUT_CHANNELS):
            # Check if channel is configured as input, if not configure it as input
            if channel not in self._pin_configurations:
                try:
                    await self.configure_pin(channel, PinMode.INPUT)
                except Exception:
                    # If configuration fails, append False as default
                    results.append(False)
                    continue

            pin_mode = self._pin_configurations.get(channel)
            if pin_mode in [PinMode.INPUT, PinMode.INPUT_PULLUP, PinMode.INPUT_PULLDOWN]:
                try:
                    logic_level = await self.read_digital_input(channel)
                    results.append(logic_level == LogicLevel.HIGH)
                except Exception:
                    # If read fails, append False as default
                    results.append(False)
            else:
                # For non-input channels, append False
                results.append(False)

        return results

    async def get_pin_configuration(self) -> Dict[int, PinMode]:
        """
        현재 핀 설정 상태 조회

        Returns:
            핀별 설정 모드 딕셔너리
        """
        return self._pin_configurations.copy()

    async def reset_all_outputs(self) -> None:
        """
        모든 출력을 LOW로 리셋

        Returns:
            리셋 성공 여부
        """
        output_pins = [
            pin for pin, mode in self._pin_configurations.items() if mode == PinMode.OUTPUT
        ]

        if not output_pins:
            return True

        reset_values = {pin: LogicLevel.LOW for pin in output_pins}
        success = await self.write_multiple_outputs(reset_values)

        if success:
            logger.info(STATUS_MESSAGES["all_outputs_reset"])

        return success

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "board_number": self._board_number,
            "module_position": self._module_position,
            "signal_type": self._signal_type,
            "debounce_time_ms": self._debounce_time_ms,
            "hardware_type": "Ajinextek DIO",
            "pin_count": len(self._pin_configurations),
            "input_pins": [
                pin
                for pin, mode in self._pin_configurations.items()
                if mode in [PinMode.INPUT, PinMode.INPUT_PULLUP, PinMode.INPUT_PULLDOWN]
            ],
            "output_pins": [
                pin for pin, mode in self._pin_configurations.items() if mode == PinMode.OUTPUT
            ],
            "last_input_states": {
                pin: level.name for pin, level in self._last_input_states.items()
            },
            "last_output_states": {
                pin: level.name for pin, level in self._last_output_states.items()
            },
        }

        if await self.is_connected():
            try:
                status["hardware_info"] = await self._get_hardware_info()
                status["last_error"] = None
            except Exception as e:
                status["hardware_info"] = None
                status["last_error"] = str(e)

        return status

    # Private helper methods (placeholders for actual AXL library integration)

    async def _load_axl_library(self) -> bool:
        """Load AXL library (placeholder)"""
        # In real implementation, would use ctypes to load AXL.dll
        await asyncio.sleep(0.1)  # Simulate loading time
        return True

    async def _unload_axl_library(self) -> bool:
        """Unload AXL library (placeholder)"""
        await asyncio.sleep(0.05)
        return True

    async def _open_board(self) -> bool:
        """Open DIO board connection (placeholder)"""
        await asyncio.sleep(0.2)  # Simulate board opening
        return True

    async def _close_board(self) -> bool:
        """Close DIO board connection (placeholder)"""
        await asyncio.sleep(0.1)
        return True

    async def _detect_modules(self) -> bool:
        """Detect and configure DIO modules (placeholder)"""
        await asyncio.sleep(0.3)  # Simulate module detection
        return True

    async def _initialize_default_pins(self) -> None:
        """Initialize default pin configurations"""
        # Configure first 16 pins as inputs, next 16 as outputs
        for pin in range(16):
            await self.configure_pin(pin, PinMode.INPUT)
        for pin in range(16, 32):
            await self.configure_pin(pin, PinMode.OUTPUT)

    def _convert_pin_mode(self, mode: PinMode) -> int:
        """Convert PinMode enum to hardware-specific value"""
        mode_mapping = {
            PinMode.INPUT: PIN_MODE_INPUT,
            PinMode.OUTPUT: PIN_MODE_OUTPUT,
            PinMode.INPUT_PULLUP: PIN_MODE_INPUT_PULLUP,
            PinMode.INPUT_PULLDOWN: PIN_MODE_INPUT_PULLDOWN,
        }
        return mode_mapping.get(mode, PIN_MODE_INPUT)

    async def _configure_hardware_pin(self, pin: int, hw_mode: int) -> bool:
        """Configure pin in hardware (placeholder)"""
        await asyncio.sleep(0.01)  # Simulate hardware configuration
        return True

    async def _read_hardware_input(self, pin: int) -> int:
        """Read input from hardware (placeholder)"""
        await asyncio.sleep(0.005)  # Simulate read time
        # Return dummy value (would read from actual hardware)
        return 0

    async def _write_hardware_output(self, pin: int, value: int) -> bool:
        """Write output to hardware (placeholder)"""
        await asyncio.sleep(0.005)  # Simulate write time
        return True

    async def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information (placeholder)"""
        return {
            "board_type": "AX5000 Series",
            "firmware_version": "1.0.0",
            "driver_version": "2.1.5",
            "total_channels": 32,
            "supported_modules": ["DI", "DO", "DIO"],
        }
