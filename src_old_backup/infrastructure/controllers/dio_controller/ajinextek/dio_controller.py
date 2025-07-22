"""
AJINEXTEK Digital I/O Controller

Independent digital I/O controller with its own AXL wrapper.
No longer depends on robot controller.
"""

from typing import List, Dict, Any, Optional

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from ..exceptions import (
    AXLDIOError,
    AXLDIOConnectionError,
    AXLDIOInitializationError,
    AXLDIOTimeoutError,
    AXLDIOCommunicationError
)
from .axl_dio_wrapper import AXLDIOWrapper
from ...robot_controller.ajinextek.constants import *
from ...robot_controller.ajinextek.error_codes import AXT_RT_SUCCESS, get_error_message


class AjinextekDIOController:
    """Independent AJINEXTEK Digital I/O controller class"""

    def __init__(self, irq_no: int = 7):
        """
        Initialize AJINEXTEK Digital I/O controller

        Args:
            irq_no: IRQ number for AXL library initialization
        """
        self.controller_type = "dio"
        self.vendor = "ajinextek"
        self.connection_info = f"AXL DIO Module (IRQ: {irq_no})"
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        self.axl = AXLDIOWrapper()
        self.irq_no = irq_no
        self.module_info = {}

    @property
    def is_initialized(self) -> bool:
        """Check if controller is initialized"""
        return self.status == HardwareStatus.CONNECTED

    def set_error(self, message: str) -> None:
        """Set error message and status"""
        self._error_message = message
        self.status = HardwareStatus.ERROR

    def connect(self) -> None:
        """Connect and initialize DIO modules"""
        try:
            # Initialize AXL library
            if not self.axl.is_opened():
                result = self.axl.open(self.irq_no)
                if result != AXT_RT_SUCCESS:
                    error_msg = get_error_message(result)
                    logger.error(f"Failed to open AXL library with IRQ {self.irq_no}: {error_msg} ({result})")
                    raise AXLDIOConnectionError(f"Failed to open AXL library with IRQ {self.irq_no}: {error_msg}", result, "AXLOpen")

            # Get module count
            try:
                self.module_count = self.axl.get_dio_module_count()
            except Exception as e:
                logger.error(f"Failed to get DIO module count: {e}")
                raise AXLDIOInitializationError(f"Failed to get DIO module count: {e}", 0, "AXLGetDIOModuleCount")

            logger.info(f"Found {self.module_count} DIO module(s)")

            # Get info for each module
            for module_no in range(self.module_count):
                try:
                    # Get input count
                    input_count = self.axl.get_input_count(module_no)

                    # Get output count
                    output_count = self.axl.get_output_count(module_no)
                except Exception as e:
                    logger.error(f"Failed to get module {module_no} info: {e}")
                    continue

                self.module_info[module_no] = {
                    'input_count': input_count,
                    'output_count': output_count,
                    'input_bits': input_count,
                    'output_bits': output_count
                }

                logger.info(f"Module {module_no}: {input_count} inputs, {output_count} outputs")

            self.status = HardwareStatus.CONNECTED

        except AXLDIOError as e:
            # Re-raise DIO-specific errors to preserve context
            logger.error(f"DIO initialization failed ({type(e).__name__}): {e}")
            self.status = HardwareStatus.ERROR
            raise
        except Exception as e:
            # Convert generic exceptions to device-specific errors for proper error context
            logger.error(f"DIO initialization failed ({type(e).__name__}): {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise AXLDIOConnectionError(f"DIO controller initialization failed: {e}", 0, "connect")

    def disconnect(self) -> None:
        """Disconnect DIO controller"""
        try:
            if self.axl.is_opened():
                result = self.axl.close()
                if result == AXT_RT_SUCCESS:
                    self.status = HardwareStatus.DISCONNECTED
                    logger.info("DIO controller disconnected successfully")
                else:
                    logger.warning(f"Failed to close AXL library: {result}")
            else:
                self.status = HardwareStatus.DISCONNECTED

        except Exception as e:
            # Note: Disconnect errors could be suppressed, but we re-raise for debugging
            logger.error(f"Failed to disconnect DIO: {e}")
            self.set_error(f"Disconnect failed: {e}")
            raise AXLDIOError(f"DIO controller disconnect failed: {e}", 0, "disconnect")

    def initialize(self) -> None:
        """Initialize the DIO controller (same as connect for AJINEXTEK)"""
        self.connect()

    def is_alive(self) -> bool:
        """Check if DIO controller connection is alive and responsive"""
        if self.status != HardwareStatus.CONNECTED:
            return False

        try:
            # Try to read module count to verify connection
            module_count = self.axl.get_dio_module_count()
            return module_count == self.module_count
        except Exception:
            return False

    def set_output_high(self, module: int, pin: int) -> None:
        """Set output pin to HIGH"""
        self.write_output(module, pin, True)

    def set_output_low(self, module: int, pin: int) -> None:
        """Set output pin to LOW"""
        self.write_output(module, pin, False)

    def set_output(self, module: int, pin: int, value: bool) -> None:
        """Set output pin to specified value"""
        self.write_output(module, pin, value)

    def read_input(self, module: int, pin: int) -> bool:
        """
        Read single input bit

        Args:
            module: Module number
            pin: Bit number (0-based)

        Returns:
            bool: Input state (True=HIGH, False=LOW)

        Raises:
            AXLDIOError: If reading fails
        """
        self._check_module(module)
        self._check_bit(module, pin, is_input=True)

        try:
            # Calculate offset and bit position
            offset, bit_pos = self._calculate_bit_position(pin)

            # Read port
            value = self.axl.read_input_port(module, offset)

            # Extract bit
            return self._extract_bit(value, bit_pos)

        except Exception as e:
            logger.error(f"Failed to read input: {e}")
            raise AXLDIOCommunicationError(f"Failed to read input bit {pin} on module {module}: {e}", 0, "read_input", "read_input_bit")

    def read_output(self, module: int, pin: int) -> bool:
        """
        Read current state of output bit

        Args:
            module: Module number
            pin: Bit number (0-based)

        Returns:
            bool: Output state (True=HIGH, False=LOW)

        Raises:
            AXLDIOError: If reading fails
        """
        self._check_module(module)
        self._check_bit(module, pin, is_input=False)

        try:
            # Calculate offset and bit position
            offset, bit_pos = self._calculate_bit_position(pin)

            # Read port
            value = self.axl.read_output_port(module, offset)

            # Extract bit
            return self._extract_bit(value, bit_pos)

        except Exception as e:
            logger.error(f"Failed to read output: {e}")
            raise AXLDIOCommunicationError(f"Failed to read output bit {pin} on module {module}: {e}", 0, "read_output", "read_output_bit")

    def set_output_port(self, module: int, port: int, value: int) -> None:
        """
        Set entire output port value

        Args:
            module: Module number
            port: Port offset (0 for bits 0-31, 1 for bits 32-63, etc.)
            value: 32-bit port value

        Raises:
            AXLDIOError: If writing fails
        """
        self._check_module(module)

        try:
            result = self.axl.write_output_port(module, port, value)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                raise AXLDIOCommunicationError(f"Failed to write output port {port} on module {module}: {error_msg}", result, "AXLWriteOutputPort", "write_output_port")

        except AXLDIOError:
            raise
        except Exception as e:
            logger.error(f"Failed to write output port: {e}")
            raise AXLDIOCommunicationError(f"Failed to write output port {port} on module {module}: {e}", 0, "set_output_port", "write_output_port")

    def read_input_port(self, module: int, port: int) -> int:
        """
        Read entire input port value

        Args:
            module: Module number
            port: Port offset (0 for bits 0-31, 1 for bits 32-63, etc.)

        Returns:
            int: 32-bit port value

        Raises:
            AXLDIOError: If reading fails
        """
        self._check_module(module)

        try:
            value = self.axl.read_input_port(module, port)
            return value

        except Exception as e:
            logger.error(f"Failed to read input port: {e}")
            raise AXLDIOCommunicationError(f"Failed to read input port {port} on module {module}: {e}", 0, "read_input_port", "read_input_port")

    def get_module_info(self) -> Dict[str, Any]:
        """
        Get information about connected DIO modules

        Returns:
            Dict[str, Any]: Module information dictionary
        """
        return {
            'module_count': self.module_count,
            'modules': self.module_info.copy()
        }

    # Additional convenience methods
    def write_output(self, module_no: int, bit_no: int, state: bool) -> None:
        """
        Write single output bit

        Args:
            module_no: Module number
            bit_no: Bit number (0-based)
            state: Output state (True=HIGH, False=LOW)

        Raises:
            AXLDIOError: If writing fails
        """
        self._check_module(module_no)
        self._check_bit(module_no, bit_no, is_input=False)

        try:
            # Calculate offset and bit position
            offset, bit_pos = self._calculate_bit_position(bit_no)

            # Read current port value
            current_value = self.axl.read_output_port(module_no, offset)

            # Modify bit
            new_value = self._set_bit_value(current_value, bit_pos, state)

            # Write back
            result = self.axl.write_output_port(module_no, offset, new_value)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                raise AXLDIOCommunicationError(f"Failed to write output bit {bit_no} on module {module_no}: {error_msg}", result, "AXLWriteOutputPort", "write_output_bit")

        except AXLDIOError:
            raise
        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            raise AXLDIOCommunicationError(f"Failed to write output bit {bit_no} on module {module_no}: {e}", 0, "write_output", "write_output_bit")

    def toggle_output(self, module_no: int, bit_no: int) -> None:
        """
        Toggle output bit state

        Args:
            module_no: Module number
            bit_no: Bit number (0-based)

        Raises:
            AXLDIOError: If reading or writing fails
        """
        current_state = self.read_output(module_no, bit_no)
        self.write_output(module_no, bit_no, not current_state)

    def read_all_inputs(self, module_no: int) -> List[bool]:
        """
        Read all input bits from module

        Returns:
            List[bool]: List of input states

        Raises:
            AXLDIOError: If reading fails
        """
        self._check_module(module_no)

        info = self.module_info.get(module_no)
        if not info:
            raise AXLDIOError(f"Module {module_no} not found in module info", 0, "read_all_inputs")

        input_count = info['input_count']
        inputs = []

        # Read ports
        for offset in range((input_count + 31) // 32):
            try:
                value = self.axl.read_input_port(module_no, offset)
            except Exception as e:
                logger.error(f"Failed to read input port {offset}: {e}")
                raise AXLDIOCommunicationError(f"Failed to read input port {offset} on module {module_no}: {e}", 0, "read_input_port", "read_all_inputs")

            # Extract bits
            for bit in range(32):
                bit_no = offset * 32 + bit
                if bit_no < input_count:
                    inputs.append(self._extract_bit(value, bit))

        return inputs

    def write_all_outputs(self, module_no: int, states: List[bool]) -> None:
        """
        Write all output bits to module

        Args:
            module_no: Module number
            states: List of output states

        Raises:
            AXLDIOError: If writing fails
        """
        self._check_module(module_no)

        info = self.module_info.get(module_no)
        if not info:
            raise AXLDIOError(f"Module {module_no} not found in module info", 0, "write_all_outputs")

        output_count = info['output_count']
        if len(states) != output_count:
            raise AXLDIOError(f"Invalid state count: {len(states)} (expected {output_count})", 0, "write_all_outputs")

        try:
            # Write ports
            for offset in range((output_count + 31) // 32):
                value = 0

                # Build port value
                for bit in range(32):
                    bit_no = offset * 32 + bit
                    if bit_no < output_count and states[bit_no]:
                        value |= (1 << bit)

                # Write port
                result = self.axl.write_output_port(module_no, offset, value)
                if result != AXT_RT_SUCCESS:
                    error_msg = get_error_message(result)
                    raise AXLDIOCommunicationError(f"Failed to write output port {offset} on module {module_no}: {error_msg}", result, "AXLWriteOutputPort", "write_all_outputs")

        except AXLDIOError:
            raise
        except Exception as e:
            logger.error(f"Failed to write all outputs: {e}")
            raise AXLDIOCommunicationError(f"Failed to write all outputs on module {module_no}: {e}", 0, "write_all_outputs", "write_all_outputs")

    def get_single_module_info(self, module_no: int) -> Dict:
        """Get information for a single module"""
        self._check_module(module_no)

        info = self.module_info.get(module_no)
        if not info:
            raise AXLDIOError(f"Module {module_no} not found in module info", 0, "get_single_module_info")

        return info

    def _check_module(self, module_no: int) -> None:
        """Check if module number is valid and raise exception if not"""
        if not self.is_initialized:
            logger.error("DIO controller not initialized")
            raise AXLDIOInitializationError("DIO controller not initialized", 0, "_check_module")

        if module_no < 0 or module_no >= self.module_count:
            logger.error(f"Invalid module number: {module_no} (valid: 0-{self.module_count-1})")
            raise AXLDIOError(f"Invalid module number: {module_no} (valid: 0-{self.module_count-1})", 0, "_check_module")

    def _check_bit(self, module_no: int, bit_no: int, is_input: bool) -> None:
        """Check if bit number is valid and raise exception if not"""
        info = self.module_info.get(module_no)
        if not info:
            raise AXLDIOError(f"Module {module_no} not found in module info", 0, "_check_bit")

        max_bits = info['input_count'] if is_input else info['output_count']
        if bit_no < 0 or bit_no >= max_bits:
            bit_type = "input" if is_input else "output"
            logger.error(f"Invalid {bit_type} bit: {bit_no} (valid: 0-{max_bits-1})")
            raise AXLDIOError(f"Invalid {bit_type} bit: {bit_no} (valid: 0-{max_bits-1})", 0, "_check_bit")

    def _calculate_bit_position(self, bit_no: int) -> tuple[int, int]:
        """
        Calculate port offset and bit position for a given bit number

        Args:
            bit_no: Bit number (0-based)

        Returns:
            tuple[int, int]: (port_offset, bit_position)
        """
        return bit_no // 32, bit_no % 32

    def _extract_bit(self, value: int, bit_pos: int) -> bool:
        """
        Extract single bit from port value

        Args:
            value: Port value
            bit_pos: Bit position (0-31)

        Returns:
            bool: Bit state (True=HIGH, False=LOW)
        """
        return bool((value >> bit_pos) & 1)

    def _set_bit_value(self, current_value: int, bit_pos: int, state: bool) -> int:
        """
        Set bit in port value

        Args:
            current_value: Current port value
            bit_pos: Bit position (0-31)
            state: Desired bit state (True=HIGH, False=LOW)

        Returns:
            int: New port value with bit set
        """
        if state:
            return current_value | (1 << bit_pos)
        else:
            return current_value & ~(1 << bit_pos)

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        self.disconnect()
        # Return False to propagate any exceptions
        return False


# For backward compatibility
DigitalIO = AjinextekDIOController
