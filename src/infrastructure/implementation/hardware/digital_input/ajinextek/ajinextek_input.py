"""
Ajinextek DIO Input Service

Service implementation for Ajinextek Digital I/O cards.
Provides digital input/output control through AXL library.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from application.interfaces.hardware.digital_input import (
    DigitalInputService,
)
from domain.enums.digital_input_enums import (  # type: ignore[import-untyped]
    LogicLevel,
    PinMode,
)
from infrastructure.implementation.hardware.digital_input.ajinextek.axl_wrapper import (
    AXLDIOWrapper,
)
from infrastructure.implementation.hardware.digital_input.ajinextek.constants import (
    DEFAULT_BOARD_NUMBER,
    DEFAULT_MODULE_POSITION,
    DEFAULT_RETRY_COUNT,
    MAX_INPUT_CHANNELS,
    MAX_OUTPUT_CHANNELS,
    MODULE_ID_PCI_DB64R,
    MODULE_ID_PCI_DI64R,
    MODULE_ID_PCI_DO64R,
    MODULE_ID_SIO_DB32,
    MODULE_ID_SIO_DI32,
    MODULE_ID_SIO_DO32,
    PIN_MODE_INPUT,
    PIN_MODE_INPUT_PULLDOWN,
    PIN_MODE_INPUT_PULLUP,
    PIN_MODE_OUTPUT,
    STATUS_MESSAGES,
)
from infrastructure.implementation.hardware.digital_input.ajinextek.error_codes import (
    AjinextekChannelError,
    AjinextekDIOError,
    AjinextekErrorCode,
    AjinextekHardwareError,
    AjinextekOperationError,
    validate_board_number,
    validate_channel_list,
    validate_channel_number,
    validate_module_position,
    validate_pin_values,
)


class AjinextekInput(DigitalInputService):
    """Ajinextek DIO 카드 통합 서비스"""

    def __init__(self):
        """
        초기화 (기본 Ajinextek 설정 사용)
        """
        # Default connection/hardware parameters
        self._board_number = DEFAULT_BOARD_NUMBER
        self._module_position = DEFAULT_MODULE_POSITION
        self._signal_type = 2  # 24V industrial
        self._input_count = 8

        # Default operational parameters
        self._debounce_time_ms = 10  # 10ms default
        self._retry_count = DEFAULT_RETRY_COUNT
        self._auto_initialize = True

        # Validate parameters
        validate_board_number(self._board_number)
        validate_module_position(self._module_position)

        # State initialization
        # Config values are already stored directly above

        # State tracking
        self._is_connected = False
        self._is_initialized = False
        self._pin_configurations: Dict[int, "PinMode"] = {}
        self._last_input_states: Dict[int, "LogicLevel"] = {}
        self._last_output_states: Dict[int, "LogicLevel"] = {}

        # AXL library interface
        self._axl_lib = None
        self._detected_modules: Dict[int, Dict[str, Any]] = {}
        self._module_input_counts: Dict[int, int] = {}
        self._module_output_counts: Dict[int, int] = {}
        self._active_module_no: Optional[int] = None

        # Interrupt support
        self._interrupt_enabled = False
        self._interrupt_callbacks: Dict[int, Callable[[int, bool], None]] = {}
        self._interrupt_edge_configs: Dict[int, str] = {}

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
        self._debounce_time_ms = config.get(
            "debounce_time_ms",
            int(config.get("debounce_time", self._debounce_time_ms / 1000.0) * 1000),
        )
        self._retry_count = config.get("retry_count", self._retry_count)
        self._auto_initialize = config.get("auto_initialize", self._auto_initialize)

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

    async def connect(self) -> bool:
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

    async def disconnect(self) -> bool:
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

    async def configure_pin(self, pin: int, mode: "PinMode") -> bool:
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

    async def read_digital_input(self, pin: int) -> "LogicLevel":
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
        if pin_mode not in [
            PinMode.INPUT,
            PinMode.INPUT_PULLUP,
            PinMode.INPUT_PULLDOWN,
        ]:
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

    async def write_digital_output(self, pin: int, level: "LogicLevel") -> bool:
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

    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, "LogicLevel"]:
        """
        다중 디지털 입력 읽기 (최적화된 배치 작업)

        Args:
            pins: 읽을 핀 번호 리스트

        Returns:
            핀별 로직 레벨 딕셔너리
        """
        validate_channel_list(pins, MAX_INPUT_CHANNELS)

        if not pins:
            return {}

        results = {}

        try:
            # Use optimized batch reading if available and advantageous
            if self._axl_lib is not None and self._active_module_no is not None and len(pins) >= 8:
                # Try to use batch reading for better performance
                sorted_pins = sorted(pins)

                # Group consecutive pins for batch reading
                pin_groups = self._group_consecutive_pins(sorted_pins)

                for start_pin, count in pin_groups:
                    try:
                        # Use batch read from AXL wrapper
                        batch_values = self._axl_lib.batch_read_inputs(
                            self._active_module_no, start_pin, count
                        )

                        # Map batch results back to individual pins
                        for i, value in enumerate(batch_values):
                            pin_index = start_pin + i
                            if pin_index in pins:
                                results[pin_index] = LogicLevel.HIGH if value else LogicLevel.LOW

                    except Exception as e:
                        logger.warning(
                            f"Batch read failed for pins {start_pin}-{start_pin+count-1}, using individual reads: {e}"
                        )
                        # Fallback to individual pin reads
                        for pin_offset in range(count):
                            pin_index = start_pin + pin_offset
                            if pin_index in pins:
                                try:
                                    results[pin_index] = await self.read_digital_input(pin_index)
                                except Exception:
                                    results[pin_index] = LogicLevel.LOW

                # Read any remaining individual pins not in groups
                for pin in pins:
                    if pin not in results:
                        try:
                            results[pin] = await self.read_digital_input(pin)
                        except Exception:
                            results[pin] = LogicLevel.LOW
            else:
                # Use individual reads for smaller batches or when batch reading is not available
                for pin in pins:
                    results[pin] = await self.read_digital_input(pin)

        except Exception as e:
            logger.error(f"Multiple input read failed: {e}")
            # Fallback to individual reads
            for pin in pins:
                try:
                    results[pin] = await self.read_digital_input(pin)
                except Exception:
                    results[pin] = LogicLevel.LOW

        logger.debug(f"Read multiple inputs: {len(pins)} pins, {len(results)} results")
        return results

    def _group_consecutive_pins(self, sorted_pins: List[int]) -> List[tuple[int, int]]:
        """Group consecutive pins for batch reading optimization"""
        if not sorted_pins:
            return []

        groups = []
        start = sorted_pins[0]
        count = 1

        for i in range(1, len(sorted_pins)):
            if sorted_pins[i] == sorted_pins[i - 1] + 1:
                # Consecutive pin
                count += 1
            else:
                # Gap found, create group
                if count >= 4:  # Only create groups for 4+ consecutive pins
                    groups.append((start, count))
                else:
                    # Add individual pins for small groups
                    for pin_offset in range(count):
                        groups.append((start + pin_offset, 1))

                start = sorted_pins[i]
                count = 1

        # Add the last group
        if count >= 4:
            groups.append((start, count))
        else:
            for pin_offset in range(count):
                groups.append((start + pin_offset, 1))

        return groups

    async def write_multiple_outputs(self, pin_values: Dict[int, "LogicLevel"]) -> bool:
        """
        다중 디지털 출력 쓰기 (최적화된 배치 작업)

        Args:
            pin_values: 핀별 출력 레벨 딕셔너리

        Returns:
            출력 성공 여부
        """
        if not pin_values:
            return True

        # Convert LogicLevel values to integers for validation
        pin_int_values = {
            pin: 1 if level == LogicLevel.HIGH else 0 for pin, level in pin_values.items()
        }
        validate_pin_values(pin_int_values, MAX_OUTPUT_CHANNELS)

        try:
            success_count = 0

            # Use optimized batch writing if available and advantageous
            if (
                self._axl_lib is not None
                and self._active_module_no is not None
                and len(pin_values) >= 8
            ):

                # Convert pin_values to sorted list format for batch writing
                sorted_pins = sorted(pin_values.keys())
                pin_groups = self._group_consecutive_pins(sorted_pins)

                for start_pin, count in pin_groups:
                    if count >= 4:  # Use batch write for groups of 4 or more
                        try:
                            # Prepare values for batch write
                            batch_values = []
                            for pin_offset in range(count):
                                pin_index = start_pin + pin_offset
                                if pin_index in pin_values:
                                    batch_values.append(pin_values[pin_index] == LogicLevel.HIGH)
                                else:
                                    batch_values.append(False)  # Default value

                            # Use batch write from AXL wrapper
                            self._axl_lib.batch_write_outputs(
                                self._active_module_no, start_pin, batch_values
                            )

                            # Count successful writes in this batch
                            for pin_offset in range(count):
                                pin_index = start_pin + pin_offset
                                if pin_index in pin_values:
                                    success_count += 1

                        except Exception as e:
                            logger.warning(
                                f"Batch write failed for pins {start_pin}-{start_pin+count-1}, using individual writes: {e}"
                            )
                            # Fallback to individual pin writes
                            for pin_offset in range(count):
                                pin_index = start_pin + pin_offset
                                if pin_index in pin_values:
                                    try:
                                        if await self.write_digital_output(
                                            pin_index, pin_values[pin_index]
                                        ):
                                            success_count += 1
                                    except Exception:
                                        pass  # Continue with other pins
                    else:
                        # Use individual writes for small groups
                        for pin_offset in range(count):
                            pin_index = start_pin + pin_offset
                            if pin_index in pin_values:
                                try:
                                    if await self.write_digital_output(
                                        pin_index, pin_values[pin_index]
                                    ):
                                        success_count += 1
                                except Exception:
                                    pass  # Continue with other pins
            else:
                # Use individual writes for smaller batches or when batch writing is not available
                for pin, level in pin_values.items():
                    try:
                        if await self.write_digital_output(pin, level):
                            success_count += 1
                    except Exception:
                        pass  # Continue with other pins

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
            if pin_mode in [
                PinMode.INPUT,
                PinMode.INPUT_PULLUP,
                PinMode.INPUT_PULLDOWN,
            ]:
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

    async def get_pin_configuration(
        self,
    ) -> Dict[int, "PinMode"]:
        """
        현재 핀 설정 상태 조회

        Returns:
            핀별 설정 모드 딕셔너리
        """
        return self._pin_configurations.copy()

    async def reset_all_outputs(self) -> bool:
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
        """Load AXL library"""
        try:
            if self._axl_lib is None:
                self._axl_lib = AXLDIOWrapper()
                logger.info("AXL DIO library loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load AXL library: {e}")
            raise AjinextekHardwareError(
                f"Failed to load AXL library: {e}",
                error_code=int(AjinextekErrorCode.LIBRARY_NOT_LOADED),
            ) from e

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
        """Detect and configure DIO modules"""
        try:
            if self._axl_lib is None:
                raise AjinextekHardwareError("AXL library not loaded")

            # Check if DIO modules exist
            if not self._axl_lib.is_dio_module():
                logger.warning("No DIO modules detected in system")
                return False

            # Get total module count
            module_count = self._axl_lib.get_module_count()
            logger.info(f"Detected {module_count} DIO modules")

            # Get specific module number for our board and position
            try:
                self._active_module_no = self._axl_lib.get_module_no(
                    self._board_number, self._module_position
                )
                logger.info(f"Active module number: {self._active_module_no}")
            except Exception as e:
                logger.warning(
                    f"Failed to get module number for board {self._board_number}, position {self._module_position}: {e}"
                )
                # Try to use the first available module
                self._active_module_no = 0

            # Configure detected modules
            for module_no in range(module_count):
                try:
                    await self._configure_module(module_no)
                except Exception as e:
                    logger.warning(f"Failed to configure module {module_no}: {e}")

            return len(self._detected_modules) > 0

        except Exception as e:
            logger.error(f"Module detection failed: {e}")
            raise AjinextekHardwareError(
                f"Module detection failed: {e}",
                error_code=int(AjinextekErrorCode.MODULE_NOT_FOUND),
            ) from e

    async def _configure_module(self, module_no: int) -> None:
        """Configure specific DIO module"""
        try:
            if self._axl_lib is None:
                raise AjinextekHardwareError("AXL library not loaded")

            # Get module information
            board_no, module_pos, module_id = self._axl_lib.get_module_info(module_no)

            # Get input count
            try:
                input_count = self._axl_lib.get_input_count(module_no)
                self._module_input_counts[module_no] = input_count
            except Exception as e:
                logger.warning(f"Failed to get input count for module {module_no}: {e}")
                self._module_input_counts[module_no] = 0

            # Get output count
            try:
                output_count = self._axl_lib.get_output_count(module_no)
                self._module_output_counts[module_no] = output_count
            except Exception as e:
                logger.warning(f"Failed to get output count for module {module_no}: {e}")
                self._module_output_counts[module_no] = 0

            # Get module status
            module_status = self._axl_lib.get_module_status(module_no)

            # Determine module type from module ID
            module_type = self._get_module_type_from_id(module_id)

            # Store module information
            self._detected_modules[module_no] = {
                "board_no": board_no,
                "module_pos": module_pos,
                "module_id": module_id,
                "module_type": module_type,
                "input_count": self._module_input_counts[module_no],
                "output_count": self._module_output_counts[module_no],
                "status": module_status,
            }

            logger.info(
                f"Module {module_no} configured: {module_type}, "
                f"{self._module_input_counts[module_no]} inputs, "
                f"{self._module_output_counts[module_no]} outputs"
            )

        except Exception as e:
            logger.error(f"Failed to configure module {module_no}: {e}")
            raise

    def _get_module_type_from_id(self, module_id: int) -> str:
        """Get module type string from module ID"""
        module_type_mapping = {
            MODULE_ID_SIO_DI32: "SIO-DI32 (32 Input)",
            MODULE_ID_SIO_DO32: "SIO-DO32 (32 Output)",
            MODULE_ID_SIO_DB32: "SIO-DB32 (16 Input/16 Output)",
            MODULE_ID_PCI_DI64R: "PCI-DI64R (64 Input)",
            MODULE_ID_PCI_DO64R: "PCI-DO64R (64 Output)",
            MODULE_ID_PCI_DB64R: "PCI-DB64R (32 Input/32 Output)",
        }
        return module_type_mapping.get(module_id, f"Unknown Module (ID: 0x{module_id:04X})")

    async def _initialize_default_pins(self) -> None:
        """Initialize default pin configurations"""
        # Configure first 16 pins as inputs, next 16 as outputs
        for pin in range(16):
            await self.configure_pin(pin, PinMode.INPUT)
        for pin in range(16, 32):
            await self.configure_pin(pin, PinMode.OUTPUT)

    def _convert_pin_mode(self, mode: "PinMode") -> int:
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
        """Read input from hardware"""
        try:
            if self._axl_lib is None:
                raise AjinextekHardwareError("AXL library not loaded")

            if self._active_module_no is None:
                raise AjinextekHardwareError("No active module configured")

            # Read input bit from hardware
            value = self._axl_lib.read_input_bit(self._active_module_no, pin)
            return 1 if value else 0

        except Exception as e:
            logger.error(f"Failed to read hardware input pin {pin}: {e}")
            raise AjinextekOperationError(
                f"Hardware input read failed for pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def _write_hardware_output(self, pin: int, value: int) -> bool:
        """Write output to hardware"""
        try:
            if self._axl_lib is None:
                raise AjinextekHardwareError("AXL library not loaded")

            if self._active_module_no is None:
                raise AjinextekHardwareError("No active module configured")

            # Write output bit to hardware
            self._axl_lib.write_output_bit(self._active_module_no, pin, bool(value))
            return True

        except Exception as e:
            logger.error(f"Failed to write hardware output pin {pin}: {e}")
            raise AjinextekOperationError(
                f"Hardware output write failed for pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        try:
            if self._axl_lib is None:
                raise AjinextekHardwareError("AXL library not loaded")

            # Collect information about detected modules
            modules_info = []
            total_inputs = 0
            total_outputs = 0

            for module_no, module_data in self._detected_modules.items():
                modules_info.append(
                    {
                        "module_no": module_no,
                        "module_type": module_data["module_type"],
                        "board_no": module_data["board_no"],
                        "module_pos": module_data["module_pos"],
                        "module_id": f"0x{module_data['module_id']:04X}",
                        "input_count": module_data["input_count"],
                        "output_count": module_data["output_count"],
                        "status": f"0x{module_data['status']:04X}",
                    }
                )
                total_inputs += module_data["input_count"]
                total_outputs += module_data["output_count"]

            return {
                "library_name": "AJINEXTEK AXL",
                "active_module_no": self._active_module_no,
                "detected_modules": len(self._detected_modules),
                "modules_info": modules_info,
                "total_inputs": total_inputs,
                "total_outputs": total_outputs,
                "board_number": self._board_number,
                "module_position": self._module_position,
                "signal_type": self._signal_type,
                "supported_operations": ["bit", "byte", "word", "dword"],
            }

        except Exception as e:
            logger.warning(f"Failed to get hardware info: {e}")
            return {
                "error": str(e),
                "active_module_no": self._active_module_no,
                "detected_modules": len(self._detected_modules),
            }

    # === Interrupt Support Methods ===

    async def setup_input_interrupt(
        self, pin: int, edge_mode: str, callback_func: Callable[[int, bool], None]
    ) -> bool:
        """
        Setup interrupt for digital input pin

        Args:
            pin: Pin number to setup interrupt for
            edge_mode: Edge trigger mode ("rising", "falling", "both")
            callback_func: Callback function to call when interrupt occurs

        Returns:
            True if interrupt setup successful

        Raises:
            AjinextekHardwareError: If interrupt setup fails
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        validate_channel_number(pin, MAX_INPUT_CHANNELS)

        if edge_mode not in ["rising", "falling", "both"]:
            raise AjinextekOperationError(
                f"Invalid edge mode: {edge_mode}. Must be 'rising', 'falling', or 'both'",
                error_code=int(AjinextekErrorCode.INVALID_PARAMETER),
            )

        try:
            if self._axl_lib is None or self._active_module_no is None:
                raise AjinextekHardwareError("AXL library or module not available")

            # Configure interrupt edge for the pin
            self._axl_lib.set_interrupt_edge(self._active_module_no, pin, edge_mode, 1)

            # Store callback and configuration
            self._interrupt_callbacks[pin] = callback_func
            self._interrupt_edge_configs[pin] = edge_mode

            # Enable interrupts for the module if not already enabled
            if not self._interrupt_enabled:
                # Setup interrupt callback mechanism
                self._axl_lib.setup_interrupt_callback(
                    self._active_module_no, self._interrupt_handler
                )
                self._axl_lib.enable_module_interrupt(self._active_module_no, True)
                self._interrupt_enabled = True

            logger.info(f"Interrupt setup successful for pin {pin} with {edge_mode} edge")
            return True

        except Exception as e:
            logger.error(f"Failed to setup interrupt for pin {pin}: {e}")
            raise AjinextekOperationError(
                f"Interrupt setup failed for pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.INTERRUPT_HANDLING_ERROR),
            ) from e

    async def remove_input_interrupt(self, pin: int) -> bool:
        """
        Remove interrupt for digital input pin

        Args:
            pin: Pin number to remove interrupt from

        Returns:
            True if interrupt removal successful
        """
        try:
            if pin in self._interrupt_callbacks:
                del self._interrupt_callbacks[pin]

            if pin in self._interrupt_edge_configs:
                del self._interrupt_edge_configs[pin]

            # If no more interrupts are configured, disable module interrupts
            if not self._interrupt_callbacks and self._interrupt_enabled:
                if self._axl_lib is not None and self._active_module_no is not None:
                    self._axl_lib.enable_module_interrupt(self._active_module_no, False)
                self._interrupt_enabled = False

            logger.info(f"Interrupt removed for pin {pin}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove interrupt for pin {pin}: {e}")
            return False

    def _interrupt_handler(self) -> None:
        """
        Internal interrupt handler callback

        This method is called by the AXL library when an interrupt occurs.
        It reads the interrupt status and calls appropriate user callbacks.
        """
        try:
            if self._axl_lib is None or self._active_module_no is None:
                return

            # Read interrupt status to determine which pins triggered
            interrupt_status = self._axl_lib.read_interrupt_status(self._active_module_no)

            # Check each configured interrupt pin
            for pin, callback in self._interrupt_callbacks.items():
                # Check if this pin triggered the interrupt (bit mask check)
                if interrupt_status & (1 << pin):
                    try:
                        # Read current pin state
                        current_state = self._axl_lib.read_input_bit(self._active_module_no, pin)

                        # Call user callback with pin number and state
                        callback(pin, current_state)

                    except Exception as e:
                        logger.error(f"Error in interrupt callback for pin {pin}: {e}")

        except Exception as e:
            logger.error(f"Error in interrupt handler: {e}")

    async def get_interrupt_status(self) -> Dict[str, Any]:
        """
        Get current interrupt configuration and status

        Returns:
            Dictionary containing interrupt status information
        """
        return {
            "interrupt_enabled": self._interrupt_enabled,
            "active_module_no": self._active_module_no,
            "configured_interrupts": {
                pin: {
                    "edge_mode": self._interrupt_edge_configs.get(pin, "unknown"),
                    "callback_configured": bool(callback),
                }
                for pin, callback in self._interrupt_callbacks.items()
            },
            "total_interrupt_pins": len(self._interrupt_callbacks),
        }

    async def enable_all_interrupts(self, enable: bool = True) -> bool:
        """
        Enable or disable all configured interrupts

        Args:
            enable: True to enable, False to disable

        Returns:
            True if operation successful
        """
        try:
            if self._axl_lib is None or self._active_module_no is None:
                raise AjinextekHardwareError("AXL library or module not available")

            self._axl_lib.enable_module_interrupt(self._active_module_no, enable)
            self._interrupt_enabled = enable

            logger.info(f"All interrupts {'enabled' if enable else 'disabled'}")
            return True

        except Exception as e:
            logger.error(f"Failed to {'enable' if enable else 'disable'} interrupts: {e}")
            return False
