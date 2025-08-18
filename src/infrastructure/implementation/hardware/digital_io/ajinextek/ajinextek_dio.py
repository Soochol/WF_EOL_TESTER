"""
Ajinextek DIO Input Service

Service implementation for Ajinextek Digital I/O cards.
Provides digital input/output control through AXL library.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from application.interfaces.hardware.digital_io import (
    DigitalIOService,
)
from infrastructure.implementation.hardware.digital_io.ajinextek.constants import (
    MAX_INPUT_CHANNELS,
    MAX_OUTPUT_CHANNELS,
    MODULE_ID_PCI_DB16R,
    MODULE_ID_PCI_DI16R,
    MODULE_ID_PCI_DO16R,
    MODULE_ID_SIO_DB16,
    MODULE_ID_SIO_DI16,
    MODULE_ID_SIO_DO16,
    STATUS_MESSAGES,
)
from infrastructure.implementation.hardware.digital_io.ajinextek.error_codes import (
    AjinextekChannelError,
    AjinextekErrorCode,
    AjinextekHardwareError,
    AjinextekOperationError,
    validate_channel_list,
    validate_pin_values,
)


class AjinextekDIO(DigitalIOService):
    """Ajinextek DIO 카드 통합 서비스"""

    def __init__(self):
        """
        초기화 (기본 Ajinextek 설정 사용)
        """

        # State tracking
        self._is_connected = False

        # AXL library interface (싱글톤 인스턴스 사용)
        from infrastructure.factory import AXLWrapperFactory

        self._axl_lib = AXLWrapperFactory.get_axl_wrapper()
        self._detected_modules: Dict[int, Dict[str, Any]] = {}
        self._module_input_counts: Dict[int, int] = {}
        self._module_output_counts: Dict[int, int] = {}
        self._active_module_no: Optional[int] = None

        # Module role tracking
        self._input_module: Optional[int] = None
        self._output_module: Optional[int] = None

        # runtime parameters
        self._module_count: int = 0
        self._input_count: int = 0
        self._output_count: int = 0

    # ========================================================================
    # Connection & Lifecycle Management
    # ========================================================================

    async def connect(self, irq_no: int = 7) -> None:
        """
        DIO 하드웨어 연결

        Args:
            irq_no: IRQ 번호 (기본값: 7)

        Raises:
            AjinextekHardwareError: 하드웨어 연결 실패
        """
        try:
            logger.info("Connecting to Ajinextek DIO hardware")

            # 중앙화된 연결 관리 사용
            self._axl_lib.connect(irq_no)

            # Check if DIO modules exist
            if not self._axl_lib.is_dio_module():
                raise AjinextekHardwareError(
                    "No DIO modules detected",
                    error_code=int(AjinextekErrorCode.MODULE_NOT_FOUND),
                )
            logger.info("DIO modules detected")

            # Get total module count
            try:
                self._module_count = self._axl_lib.get_dio_module_count()
                logger.info(f"DIO module count: {self._module_count}")
            except Exception as e:
                error_msg = f"Failed to get module count: {e}"
                logger.error(error_msg)
                raise AjinextekHardwareError(
                    error_msg,
                    error_code=int(AjinextekErrorCode.MODULE_NOT_FOUND),
                ) from e

            # Scan all modules to identify input and output modules
            if self._module_count > 0:
                total_inputs = 0
                total_outputs = 0

                for module_no in range(self._module_count):
                    try:
                        module_inputs = self._axl_lib.get_input_count(module_no)
                        module_outputs = self._axl_lib.get_output_count(module_no)

                        logger.info(
                            f"Module {module_no}: Inputs={module_inputs}, Outputs={module_outputs}"
                        )

                        total_inputs += module_inputs
                        total_outputs += module_outputs

                        # Identify module roles
                        if module_inputs > 0:
                            self._input_module = module_no
                            logger.info(f"Input module identified: Module {module_no}")
                        if module_outputs > 0:
                            self._output_module = module_no
                            logger.info(f"Output module identified: Module {module_no}")

                    except Exception as e:
                        logger.warning(f"Failed to get I/O counts for module {module_no}: {e}")

                self._input_count = total_inputs
                self._output_count = total_outputs

                # Set active module (prefer output module if available, otherwise input module)
                self._active_module_no = (
                    self._output_module if self._output_module is not None else self._input_module
                )

                # Fallback if no modules could be scanned
                if total_inputs == 0 and total_outputs == 0:
                    logger.warning("No I/O channels detected, using fallback values")
                    self._input_count = 32  # Match actual hardware spec
                    self._output_count = 32
                    self._input_module = 0
                    self._output_module = 1 if self._module_count > 1 else 0

                logger.info(
                    f"Total I/O channels - Inputs: {self._input_count}, Outputs: {self._output_count}"
                )
                logger.info(
                    f"Module assignment - Input module: {self._input_module}, Output module: {self._output_module}"
                )

            self._is_connected = True
            logger.info(
                f"AJINEXTEK DIO hardware connected successfully (IRQ: {irq_no}, Modules: {self._module_count})"
            )

        except AjinextekHardwareError:
            self._is_connected = False
            raise
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to AJINEXTEK DIO: {e}")
            raise AjinextekHardwareError(
                f"DIO hardware initialization failed: {e}",
                error_code=int(AjinextekErrorCode.HARDWARE_INITIALIZATION_FAILED),
            ) from e

    async def disconnect(self) -> None:
        """
        DIO 하드웨어 연결 해제
        """
        try:
            if self._is_connected:
                # 중앙화된 연결 해제 사용
                self._axl_lib.disconnect()

            self._is_connected = False
            logger.info("AJINEXTEK DIO hardware disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting DIO hardware: {e}")
            raise

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    # ========================================================================
    # Core Public API (Interface Implementation)
    # ========================================================================

    async def read_input(self, channel: int) -> bool:
        """
        Read digital input from specified channel

        Args:
            channel: Digital input channel number

        Returns:
            True if input is HIGH, False if LOW

        Raises:
            AjinextekChannelError: 유효하지 않은 채널
            AjinextekHardwareError: 하드웨어 통신 실패
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        # Check input channel range
        if not (0 <= channel < self._input_count):
            raise AjinextekChannelError(
                f"Input channel {channel} out of range [0, {self._input_count-1}]",
                error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
            )

        try:
            # Read from hardware
            hw_value = await self._read_hardware_input(channel)

            # Return hardware value directly as bool
            result = bool(hw_value)
            return result

        except Exception as e:
            raise AjinextekOperationError(
                f"Failed to read input channel {channel}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def write_output(self, channel: int, level: bool) -> bool:
        """
        Write digital output to specified channel

        Args:
            channel: Digital output channel number
            level: Output logic level (True=HIGH, False=LOW)

        Returns:
            True if write was successful, False otherwise

        Raises:
            AjinextekChannelError: 유효하지 않은 채널
            AjinextekHardwareError: 하드웨어 통신 실패
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        # Check output channel range
        if not (0 <= channel < self._output_count):
            raise AjinextekChannelError(
                f"Output channel {channel} out of range [0, {self._output_count-1}]",
                error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
            )

        try:
            # Convert bool to hardware value
            hw_value = 1 if level else 0

            # Write to hardware
            success = await self._write_hardware_output(channel, hw_value)

            if success:
                return True
            else:
                logger.warning(f"Failed to write output channel {channel}")
                return False

        except Exception as e:
            logger.error(f"Error writing output channel {channel}: {e}")
            raise AjinextekOperationError(
                f"Failed to write output channel {channel}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def get_input_count(self) -> int:
        """
        Get the number of available digital input channels

        Returns:
            Number of digital input channels
        """
        return self._input_count

    async def get_output_count(self) -> int:
        """
        Get the number of available digital output channels

        Returns:
            Number of digital output channels
        """
        return self._output_count

    async def read_output(self, channel: int) -> bool:
        """
        Read digital output state from specified channel

        Args:
            channel: Digital output channel number

        Returns:
            True if output is HIGH, False if LOW

        Raises:
            AjinextekChannelError: Invalid channel
            AjinextekHardwareError: Hardware communication failure
        """
        if not await self.is_connected():
            raise AjinextekHardwareError(
                "DIO hardware not connected",
                error_code=int(AjinextekErrorCode.HARDWARE_NOT_CONNECTED),
            )

        # Check output channel range
        if not (0 <= channel < self._output_count):
            raise AjinextekChannelError(
                f"Output channel {channel} out of range [0, {self._output_count-1}]",
                error_code=int(AjinextekErrorCode.CHANNEL_NOT_CONFIGURED),
            )

        try:
            # Read from hardware
            hw_value = await self._read_hardware_output(channel)

            # Return hardware value directly as bool
            result = bool(hw_value)

            logger.debug(f"Read output channel {channel}: {result}")
            return result

        except Exception as e:
            raise AjinextekOperationError(
                f"Failed to read output channel {channel}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def read_all_inputs(self) -> List[bool]:
        """
        Read all available digital inputs

        Returns:
            List of boolean values representing all input states
        """
        results = []
        for channel in range(await self.get_input_count()):
            try:
                value = await self.read_input(channel)
                results.append(value)
            except Exception as e:
                logger.warning(f"Failed to read input channel {channel}: {e}")
                results.append(False)  # Default to False on error
        return results

    async def read_all_outputs(self) -> List[bool]:
        """
        Read all available digital outputs

        Returns:
            List of boolean values representing all output states
        """
        results = []
        for channel in range(await self.get_output_count()):
            try:
                value = await self.read_output(channel)
                results.append(value)
            except Exception as e:
                logger.warning(f"Failed to read output channel {channel}: {e}")
                results.append(False)  # Default to False on error
        return results

    # ========================================================================
    # Batch Operations
    # ========================================================================

    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, bool]:
        """
        다중 디지털 입력 읽기 (최적화된 배치 작업)

        Args:
            pins: 읽을 핀 번호 리스트

        Returns:
            핀별 bool 값 딕셔너리 (True=HIGH, False=LOW)
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
                                results[pin_index] = bool(value)

                    except Exception as e:
                        logger.warning(
                            f"Batch read failed for pins {start_pin}-{start_pin+count-1}, using individual reads: {e}"
                        )
                        # Fallback to individual pin reads
                        for pin_offset in range(count):
                            pin_index = start_pin + pin_offset
                            if pin_index in pins:
                                try:
                                    results[pin_index] = await self.read_input(pin_index)
                                except Exception:
                                    results[pin_index] = False

                # Read any remaining individual pins not in groups
                for pin in pins:
                    if pin not in results:
                        try:
                            results[pin] = await self.read_input(pin)
                        except Exception:
                            results[pin] = False
            else:
                # Use individual reads for smaller batches or when batch reading is not available
                for pin in pins:
                    results[pin] = await self.read_input(pin)

        except Exception as e:
            logger.error(f"Multiple input read failed: {e}")
            # Fallback to individual reads
            for pin in pins:
                try:
                    results[pin] = await self.read_input(pin)
                except Exception:
                    results[pin] = False

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

    async def write_multiple_outputs(self, pin_values: Dict[int, bool]) -> bool:
        """
        다중 디지털 출력 쓰기 (최적화된 배치 작업)

        Args:
            pin_values: 핀별 출력 레벨 딕셔너리 (True=HIGH, False=LOW)

        Returns:
            출력 성공 여부
        """
        if not pin_values:
            return True

        # Convert bool values to integers for validation
        pin_int_values = {pin: 1 if level else 0 for pin, level in pin_values.items()}
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
                                    batch_values.append(pin_values[pin_index])
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
                                        if await self.write_output(
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
                                    if await self.write_output(pin_index, pin_values[pin_index]):
                                        success_count += 1
                                except Exception:
                                    pass  # Continue with other pins
            else:
                # Use individual writes for smaller batches or when batch writing is not available
                for pin, level in pin_values.items():
                    try:
                        if await self.write_output(pin, level):
                            success_count += 1
                    except Exception:
                        pass  # Continue with other pins

            all_success = success_count == len(pin_values)
            logger.debug(f"Write multiple outputs: {success_count}/{len(pin_values)} successful")
            return all_success

        except Exception as e:
            logger.error(f"Error writing multiple outputs: {e}")
            return False

    async def reset_all_outputs(self) -> bool:
        """
        모든 출력을 LOW로 리셋

        Returns:
            리셋 성공 여부
        """
        if self._output_count == 0:
            return True

        # Reset all output channels to LOW
        reset_values = {channel: False for channel in range(self._output_count)}
        success = await self.write_multiple_outputs(reset_values)

        if success:
            logger.info(STATUS_MESSAGES["all_outputs_reset"])

        return success

    # ========================================================================
    # Status & Information
    # ========================================================================

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "hardware_type": "Ajinextek DIO",
            "module_count": self._module_count,
            "detected_input_count": self._input_count,
            "detected_output_count": self._output_count,
            "input_channels": list(range(self._input_count)),
            "output_channels": list(range(self._output_count)),
        }

        if await self.is_connected():
            try:
                status["hardware_info"] = await self._get_hardware_info()
                status["last_error"] = None
            except Exception as e:
                status["hardware_info"] = None
                status["last_error"] = str(e)

        return status

    # ========================================================================
    # Private Methods (Internal Implementation)
    # ========================================================================

    async def _configure_module(self, module_no: int) -> None:
        """Configure specific DIO module"""
        try:
            # Get module information
            board_no, module_pos, module_id = self._axl_lib.get_module_info(module_no)

            # Get input count
            try:
                self._input_count = self._axl_lib.get_input_count(module_no)
                self._module_input_counts[module_no] = self._input_count
            except Exception as e:
                logger.warning(f"Failed to get input count for module {module_no}: {e}")
                self._module_input_counts[module_no] = 0

            # Get output count
            try:
                self._output_count = self._axl_lib.get_output_count(module_no)
                self._module_output_counts[module_no] = self._output_count
            except Exception as e:
                logger.warning(f"Failed to get output count for module {module_no}: {e}")
                self._module_output_counts[module_no] = 0

            # Get module status
            module_status = self._axl_lib.get_dio_module_status(module_no)

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
            MODULE_ID_SIO_DI16: "SIO-DI16 (16 Input)",
            MODULE_ID_SIO_DO16: "SIO-DO16 (16 Output)",
            MODULE_ID_SIO_DB16: "SIO-DB16 (8 Input/8 Output)",
            MODULE_ID_PCI_DI16R: "PCI-DI16R (16 Input)",
            MODULE_ID_PCI_DO16R: "PCI-DO16R (16 Output)",
            MODULE_ID_PCI_DB16R: "PCI-DB16R (8 Input/8 Output)",
        }
        return module_type_mapping.get(module_id, f"Unknown Module (ID: 0x{module_id:04X})")

    async def _read_hardware_input(self, pin: int) -> int:
        """Read input from hardware"""
        try:
            if self._input_module is None:
                raise AjinextekHardwareError("No input module configured")

            # Read input bit from hardware using input module
            value = self._axl_lib.read_input_bit(self._input_module, pin)
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
            if self._output_module is None:
                raise AjinextekHardwareError("No output module configured")

            # Write output bit to hardware using output module
            self._axl_lib.write_output_bit(self._output_module, pin, bool(value))
            return True

        except Exception as e:
            logger.error(f"Failed to write hardware output pin {pin}: {e}")
            raise AjinextekOperationError(
                f"Hardware output write failed for pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def _read_hardware_output(self, pin: int) -> int:
        """Read output from hardware"""
        try:
            if self._output_module is None:
                raise AjinextekHardwareError("No output module configured")

            # Read output bit from hardware using output module
            value = self._axl_lib.read_output_bit(self._output_module, pin)
            return 1 if value else 0

        except Exception as e:
            logger.error(f"Failed to read hardware output pin {pin}: {e}")
            raise AjinextekOperationError(
                f"Hardware output read failed for pin {pin}: {e}",
                error_code=int(AjinextekErrorCode.OPERATION_TIMEOUT),
            ) from e

    async def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information"""
        try:
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
                "module_count": self._module_count,
                "runtime_input_count": self._input_count,
                "runtime_output_count": self._output_count,
                "supported_operations": ["bit", "byte", "word", "dword"],
            }

        except Exception as e:
            logger.warning(f"Failed to get hardware info: {e}")
            return {
                "error": str(e),
                "active_module_no": self._active_module_no,
                "detected_modules": len(self._detected_modules),
            }
