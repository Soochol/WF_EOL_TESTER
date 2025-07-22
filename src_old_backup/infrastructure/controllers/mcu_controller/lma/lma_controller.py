"""
LMA MCU Controller Implementation

This module implements the LMA MCU controller with UART communication.
"""

import time
import struct
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus
from enum import IntEnum


class TestMode(IntEnum):
    """Test mode enumeration"""
    MODE_1 = 1
    MODE_2 = 2
    MODE_3 = 3


class MCUStatus(IntEnum):
    """MCU status enumeration"""
    IDLE = 0
    HEATING = 1
    COOLING = 2
    HOLDING = 3
    ERROR = 4
# Use LMA-specific exceptions instead of generic hardware exceptions
from ..exceptions import LMAError, LMACommunicationError, LMAOperationError, LMAHardwareError
from .....driver.serial import SerialManager
from .....driver.serial.exceptions import SerialConnectionError, SerialCommunicationError, SerialTimeoutError
from .constants import *
from .error_codes import LMAErrorCode, validate_temperature, validate_fan_speed


class LMAController:
    """LMA MCU controller implementation"""

    def __init__(self, port: str, baudrate: int = DEFAULT_BAUDRATE,
                 timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize LMA controller

        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate (default: 9600)
            timeout: Communication timeout in seconds
        """
        self.controller_type = "mcu"
        self.vendor = "lma"
        self.connection_info = port
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # MCU-specific attributes
        self.current_status = MCUStatus.IDLE
        self.status_callback = None

        self.serial_manager = SerialManager()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.retry_count = DEFAULT_RETRY_COUNT

        # Status tracking
        self.current_test_mode: Optional[TestMode] = None
        self.current_temperature: Optional[float] = None
        self.current_fan_speed: Optional[int] = None
        self.temperature_settings: Dict[str, float] = {}


        # Protocol frame buffer
        self.frame_buffer = FrameBuffer()
        self._setup_protocol_constants()
    
    def set_status_callback(self, callback) -> None:
        """Set status update callback"""
        self.status_callback = callback
    
    def _notify_status_change(self, status: MCUStatus, data=None) -> None:
        """Notify status change to callback"""
        self.current_status = status
        if self.status_callback:
            try:
                self.status_callback(status, data or {})
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def connect(self) -> None:
        """Connect to LMA controller (exception-first design)"""
        try:
            self.serial_manager.connect(self.port, baudrate=self.baudrate, timeout=self.timeout)
            self.status = HardwareStatus.CONNECTED
            logger.info(f"Connected to LMA controller at {self.connection_info}")

            # Wait for boot complete message
            try:
                self._wait_for_boot_complete()
            except Exception as e:
                logger.warning(f"Boot complete message not received: {e}")
                # Continue anyway - boot timeout is not a fatal error

        except (SerialConnectionError, SerialCommunicationError) as e:
            logger.error(f"Failed to connect to LMA controller: {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise LMACommunicationError(f"LMA controller connection failed: {e}")
        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            self.status = HardwareStatus.DISCONNECTED
            raise
        except Exception as e:
            logger.error(f"Failed to connect to LMA controller: {e}")
            self.status = HardwareStatus.DISCONNECTED
            raise LMACommunicationError(f"LMA controller connection failed: {e}")

    def disconnect(self) -> None:
        """Disconnect from LMA controller"""
        try:
            self.serial_manager.disconnect()
            self.status = HardwareStatus.DISCONNECTED
            logger.info("Disconnected from LMA controller")
        except Exception as e:
            # Note: Disconnect errors could be suppressed, but we re-raise for debugging
            logger.error(f"Failed to disconnect from LMA controller: {e}")
            self.set_error(f"Disconnect failed: {e}")
            raise LMACommunicationError(f"LMA controller disconnect failed: {e}")

    def is_alive(self) -> bool:
        """Check if connection is alive"""
        return self.serial_manager.is_connected()
    
    def set_error(self, message: str) -> None:
        """Set error status and message"""
        self.status = HardwareStatus.ERROR
        self._error_message = message

    def enter_test_mode(self, mode: TestMode) -> None:
        """Enter specified test mode (exception-first design)"""
        try:
            validate_parameter(mode, TestMode, "test_mode")

            # Map TestMode to protocol value
            mode_value = {
                TestMode.MODE_1: TEST_MODE_1,
                TestMode.MODE_2: TEST_MODE_2,
                TestMode.MODE_3: TEST_MODE_3,
            }[mode]

            self._send_command_and_verify_ack(CMD_ENTER_TEST_MODE, STATUS_TEST_MODE_COMPLETE, mode_value)
            self.current_test_mode = mode
            logger.info(f"Entered test mode {mode}")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error entering test mode: {e}")
            raise LMAOperationError(f"Error entering test mode: {e}")

    def get_test_mode(self) -> Optional[TestMode]:
        """Get current test mode"""
        if self.current_test_mode is None:
            raise LMAOperationError("Test mode not set - must call enter_test_mode() first")
        return self.current_test_mode

    def set_upper_temperature(self, temperature: float) -> None:
        """Set upper temperature limit (exception-first design)"""
        try:
            validate_temperature(temperature)

            # Convert to protocol format (integer * 10)
            temp_value = int(temperature * TEMP_SCALE_FACTOR)

            self._send_command_and_verify_ack(CMD_SET_UPPER_TEMP, STATUS_UPPER_TEMP_OK, temp_value)
            self.temperature_settings['upper'] = temperature
            logger.info(f"Set upper temperature to {temperature}°C")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error setting upper temperature: {e}")
            raise LMAOperationError(f"Error setting upper temperature: {e}")

    def set_operating_temperature(self, temperature: float) -> None:
        """Set operating temperature (exception-first design)"""
        try:
            validate_temperature(temperature)

            temp_value = int(temperature * TEMP_SCALE_FACTOR)

            self._send_command_and_verify_ack(CMD_SET_OPERATING_TEMP, STATUS_OPERATING_TEMP_OK, temp_value)
            self.temperature_settings['operating'] = temperature
            logger.info(f"Set operating temperature to {temperature}°C")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error setting operating temperature: {e}")
            raise LMAOperationError(f"Error setting operating temperature: {e}")

    def set_cooling_temperature(self, temperature: float) -> None:
        """Set cooling temperature"""
        try:
            validate_temperature(temperature)

            temp_value = int(temperature * TEMP_SCALE_FACTOR)

            self._send_command_and_verify_ack(CMD_SET_COOLING_TEMP, STATUS_COOLING_TEMP_OK, temp_value)
            self.temperature_settings['cooling'] = temperature
            logger.info(f"Set cooling temperature to {temperature}°C")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error setting cooling temperature: {e}")
            raise LMAOperationError(f"Error setting cooling temperature: {e}")

    def get_temperature(self) -> float:
        """Get current temperature"""
        try:
            response = self._send_command_with_retry(CMD_REQUEST_TEMP)
            if response.command == STATUS_TEMP_RESPONSE:
                temperature = self._extract_temperature(response.data)
                if temperature is not None:
                    self.current_temperature = temperature
                    return temperature

            logger.error(f"Unexpected response to temperature request: 0x{response.command:02X}")
            raise LMACommunicationError(f"Unexpected response to temperature request: 0x{response.command:02X}")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error getting temperature: {e}")
            raise LMACommunicationError(f"Error getting temperature: {e}")

    def set_fan_speed(self, level: int) -> None:
        """Set fan speed level"""
        try:
            validate_fan_speed(level)

            self._send_command_and_verify_ack(CMD_SET_FAN_SPEED, STATUS_FAN_SPEED_OK, level)
            self.current_fan_speed = level
            logger.info(f"Set fan speed to level {level}")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error setting fan speed: {e}")
            raise LMAOperationError(f"Error setting fan speed: {e}")

    def get_fan_speed(self) -> int:
        """Get current fan speed level"""
        if self.current_fan_speed is None:
            raise LMAOperationError("Fan speed not set - must call set_fan_speed() first")
        return self.current_fan_speed

    def initialize_lma(self, operating_temp: float, standby_temp: float,
                      hold_time_ms: int) -> None:
        """Initialize LMA with parameters"""
        try:
            validate_temperature(operating_temp)
            validate_temperature(standby_temp)

            if hold_time_ms < 0:
                raise LMAOperationError(f"Hold time must be non-negative: {hold_time_ms}")

            # Convert temperatures to protocol format
            operating_value = int(operating_temp * TEMP_SCALE_FACTOR)
            standby_value = int(standby_temp * TEMP_SCALE_FACTOR)

            self._send_command_and_verify_ack(
                CMD_LMA_INIT, STATUS_LMA_INIT_OK,
                operating_value, standby_value, hold_time_ms
            )
            self.temperature_settings['operating'] = operating_temp
            self.temperature_settings['standby'] = standby_temp
            logger.info(f"LMA initialized: operating={operating_temp}°C, "
                       f"standby={standby_temp}°C, hold_time={hold_time_ms}ms")

        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error initializing LMA: {e}")
            raise LMAOperationError(f"Error initializing LMA: {e}")

    def notify_stroke_init_complete(self) -> None:
        """Notify MCU that robot stroke initialization is complete"""
        try:
            self._send_command_and_verify_ack(CMD_STROKE_INIT_COMPLETE, STATUS_STROKE_INIT_OK)
            logger.info("Robot stroke initialization complete notification sent to MCU")
        except LMAError:
            # Re-raise LMA specific errors to preserve error context and debugging info
            raise
        except Exception as e:
            logger.error(f"Error sending stroke initialization complete notification: {e}")
            raise LMAOperationError(f"Error sending stroke initialization complete notification: {e}")

    def get_mcu_status(self) -> MCUStatus:
        """Get current MCU status"""
        return self.current_status

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        try:
            self.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect in context manager: {e}")
        # Return False to propagate any exceptions
        return False


    def _send_command_with_retry(self, command: int, *args, timeout: Optional[float] = None) -> 'ProtocolFrame':
        """Send command with retry logic"""
        if timeout is None:
            timeout = self.timeout

        for attempt in range(self.retry_count):
            try:
                response = self._send_and_wait(command, *args, timeout=timeout)
                if response:
                    return response

                logger.warning(f"Command 0x{command:02X} attempt {attempt + 1} failed")

            except Exception as e:
                logger.error(f"Command 0x{command:02X} attempt {attempt + 1} error: {e}")

            if attempt < self.retry_count - 1:
                time.sleep(0.1)  # Brief delay before retry

        logger.error(f"Command 0x{command:02X} failed after {self.retry_count} attempts")
        raise LMACommunicationError(f"Command 0x{command:02X} failed after {self.retry_count} attempts")

    def _send_command_and_verify_ack(self, command: int, expected_ack: int, *args, timeout: Optional[float] = None) -> None:
        """
        Send command and verify correct ACK response

        Args:
            command: Command byte to send
            expected_ack: Expected ACK response code
            *args: Command arguments
            timeout: Response timeout

        Raises:
            LMACommunicationError: If ACK not received or unexpected response
        """
        if timeout is None:
            timeout = self.timeout

        for attempt in range(self.retry_count):
            try:
                response = self._send_and_wait(command, *args, timeout=timeout)

                if response is None:
                    logger.warning(f"Command 0x{command:02X} attempt {attempt + 1}: No response received")
                elif response.command == expected_ack:
                    logger.debug(f"Command 0x{command:02X} successful: received expected ACK 0x{expected_ack:02X}")
                    return
                else:
                    logger.warning(f"Command 0x{command:02X} attempt {attempt + 1}: "
                                 f"Unexpected response 0x{response.command:02X}, expected 0x{expected_ack:02X}")

            except Exception as e:
                logger.error(f"Command 0x{command:02X} attempt {attempt + 1} error: {e}")

            if attempt < self.retry_count - 1:
                time.sleep(0.1)  # Brief delay before retry

        logger.error(f"Command 0x{command:02X} failed after {self.retry_count} attempts: "
                    f"Expected ACK 0x{expected_ack:02X} not received")
        raise LMACommunicationError(f"Command 0x{command:02X} failed after {self.retry_count} attempts: "
                                  f"Expected ACK 0x{expected_ack:02X} not received")

    def _handle_received_frame(self, frame: 'ProtocolFrame') -> None:
        """Handle received frame from controller"""
        try:
            logger.debug(f"Received frame: CMD=0x{frame.command:02X}, DATA={frame.data.hex()}")

            # Handle status messages
            if frame.command in STATUS_MESSAGES:
                self._handle_status_message(frame)
            else:
                logger.warning(f"Unknown frame received: 0x{frame.command:02X}")

        except Exception as e:
            logger.error(f"Error handling received frame: {e}")

    def _handle_status_message(self, frame: 'ProtocolFrame') -> None:
        """Handle status message from controller"""
        status_msg = STATUS_MESSAGES.get(frame.command, "Unknown status")
        logger.debug(f"Status message: {status_msg}")

        # Update status based on message
        if frame.command == STATUS_TEMP_RISE_START:
            self._notify_status_change(MCUStatus.HEATING)
        elif frame.command == STATUS_TEMP_FALL_START:
            self._notify_status_change(MCUStatus.COOLING)
        elif frame.command in [STATUS_OPERATING_TEMP_REACHED, STATUS_STANDBY_TEMP_REACHED]:
            self._notify_status_change(MCUStatus.HOLDING)
        elif frame.command == STATUS_LMA_INIT_COMPLETE:
            self._notify_status_change(MCUStatus.IDLE)
        elif frame.command == STATUS_TEMP_RESPONSE:
            # Extract temperature from response
            temperature = self._extract_temperature(frame.data)
            if temperature is not None:
                self.current_temperature = temperature
                self._notify_status_change(self.current_status, {"temperature": temperature})

    def _wait_for_boot_complete(self, timeout: float = BOOT_COMPLETE_TIMEOUT) -> None:
        """Wait for boot complete message"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self._wait_for_response(timeout=1.0)
            if response and response.command == STATUS_BOOT_COMPLETE:
                logger.info("Boot complete message received")
                return

        logger.warning("Boot complete message not received within timeout")
        raise LMACommunicationError("Boot complete message not received within timeout")



    # ===================================================================
    # Protocol Frame Handling (Integrated from protocol.py)
    # ===================================================================
    
    def _setup_protocol_constants(self) -> None:
        """Setup protocol constants from constants.py"""
        # Import constants locally to avoid circular imports
        from .constants import (
            STX, ETX, FRAME_STX_SIZE, FRAME_CMD_SIZE, FRAME_LEN_SIZE,
            FRAME_ETX_SIZE, FRAME_OVERHEAD, MAX_DATA_SIZE, MAX_FRAME_SIZE,
            TEMP_SCALE_FACTOR
        )
        self.STX = STX
        self.ETX = ETX
        self.FRAME_STX_SIZE = FRAME_STX_SIZE
        self.FRAME_CMD_SIZE = FRAME_CMD_SIZE
        self.FRAME_LEN_SIZE = FRAME_LEN_SIZE
        self.FRAME_ETX_SIZE = FRAME_ETX_SIZE
        self.FRAME_OVERHEAD = FRAME_OVERHEAD
        self.MAX_DATA_SIZE = MAX_DATA_SIZE
        self.MAX_FRAME_SIZE = MAX_FRAME_SIZE
        self.TEMP_SCALE_FACTOR = TEMP_SCALE_FACTOR
    
    def _build_frame(self, command: int, data: bytes = b'') -> bytes:
        """
        Build protocol frame from command and data
        
        Args:
            command: Command byte
            data: Data payload
            
        Returns:
            bytes: Complete frame
            
        Raises:
            ValueError: If data is too large
        """
        if len(data) > self.MAX_DATA_SIZE:
            raise ValueError(f"Data size {len(data)} exceeds maximum {self.MAX_DATA_SIZE}")
            
        data_length = len(data)
        frame = self.STX + struct.pack('B', command) + struct.pack('B', data_length) + data + self.ETX
        
        logger.debug(f"Built frame: CMD=0x{command:02X}, LEN={data_length}, DATA={data.hex()}")
        return frame
    
    def _build_command_frame(self, command: int, *args) -> bytes:
        """
        Build command frame with integer arguments
        
        Args:
            command: Command byte
            *args: Integer arguments (will be packed as 4-byte integers)
            
        Returns:
            bytes: Complete frame
        """
        data = b''
        for arg in args:
            data += struct.pack('<I', arg)  # Little-endian 32-bit integer
        
        return self._build_frame(command, data)
    
    def _parse_frame(self, frame_data: bytes) -> Optional['ProtocolFrame']:
        """
        Parse protocol frame from bytes
        
        Args:
            frame_data: Raw frame bytes
            
        Returns:
            Optional[ProtocolFrame]: Parsed frame or None if invalid
        """
        if len(frame_data) < self.FRAME_OVERHEAD:
            logger.warning(f"Frame too short: {len(frame_data)} bytes")
            return None
        
        # Check STX
        if frame_data[:self.FRAME_STX_SIZE] != self.STX:
            logger.warning(f"Invalid STX: {frame_data[:self.FRAME_STX_SIZE].hex()}")
            return None
        
        # Check ETX
        if frame_data[-self.FRAME_ETX_SIZE:] != self.ETX:
            logger.warning(f"Invalid ETX: {frame_data[-self.FRAME_ETX_SIZE:].hex()}")
            return None
        
        # Extract command and length
        try:
            command = struct.unpack('B', frame_data[self.FRAME_STX_SIZE:self.FRAME_STX_SIZE + self.FRAME_CMD_SIZE])[0]
            data_length = struct.unpack('B', frame_data[self.FRAME_STX_SIZE + self.FRAME_CMD_SIZE:self.FRAME_STX_SIZE + self.FRAME_CMD_SIZE + self.FRAME_LEN_SIZE])[0]
        except struct.error as e:
            logger.warning(f"Failed to unpack command/length: {e}")
            return None
        
        # Validate frame length
        expected_length = self.FRAME_OVERHEAD + data_length
        if len(frame_data) != expected_length:
            logger.warning(f"Frame length mismatch: expected {expected_length}, got {len(frame_data)}")
            return None
        
        # Extract data
        data_start = self.FRAME_STX_SIZE + self.FRAME_CMD_SIZE + self.FRAME_LEN_SIZE
        data_end = data_start + data_length
        data = frame_data[data_start:data_end]
        
        logger.debug(f"Parsed frame: CMD=0x{command:02X}, LEN={data_length}, DATA={data.hex()}")
        return ProtocolFrame(command=command, data=data)
    
    def _extract_integers(self, data: bytes) -> List[int]:
        """
        Extract integer values from data payload
        
        Args:
            data: Data payload bytes
            
        Returns:
            List[int]: List of extracted integers
        """
        if len(data) % 4 != 0:
            logger.warning(f"Data length {len(data)} is not multiple of 4")
            return []
        
        integers = []
        for i in range(0, len(data), 4):
            try:
                value = struct.unpack('<I', data[i:i+4])[0]  # Little-endian 32-bit
                integers.append(value)
            except struct.error as e:
                logger.warning(f"Failed to unpack integer at offset {i}: {e}")
                break
        
        return integers
    
    def _extract_temperature(self, data: bytes) -> Optional[float]:
        """
        Extract temperature value from data payload
        Temperature is stored as integer * 10 (e.g., 40.5°C = 405)
        
        Args:
            data: Data payload bytes (8 bytes for temperature response)
            
        Returns:
            Optional[float]: Temperature in degrees Celsius or None if invalid
        """
        if len(data) != 8:
            logger.warning(f"Invalid temperature data length: {len(data)}")
            return None
        
        try:
            # Extract two 32-bit integers (temperature data format)
            temp_data = struct.unpack('<II', data)
            # Use first value for temperature (second might be status or checksum)
            temp_raw = temp_data[0]
            temperature = temp_raw / self.TEMP_SCALE_FACTOR  # Convert from scaled integer
            
            logger.debug(f"Extracted temperature: {temperature}°C (raw: {temp_raw})")
            return temperature
        except struct.error as e:
            logger.warning(f"Failed to extract temperature: {e}")
            return None
    
    def _send_frame(self, frame: bytes) -> None:
        """
        Send frame to device
        
        Args:
            frame: Frame bytes to send
            
        Raises:
            LMACommunicationError: If frame send fails
        """
        try:
            self.serial_manager.write(frame)
            logger.debug(f"Sent frame: {frame.hex()}")
        except (SerialCommunicationError, SerialTimeoutError) as e:
            logger.error(f"Failed to send frame: {e}")
            raise LMACommunicationError(f"Failed to send frame: {e}")
    
    def _send_command(self, command: int, *args) -> None:
        """
        Send command with arguments
        
        Args:
            command: Command byte
            *args: Command arguments
            
        Raises:
            LMACommunicationError: If command send fails
        """
        try:
            frame = self._build_command_frame(command, *args)
            self._send_frame(frame)
        except LMACommunicationError:
            raise
        except Exception as e:
            logger.error(f"Failed to build command frame: {e}")
            raise LMACommunicationError(f"Failed to build command frame: {e}")
    
    def _wait_for_response(self, timeout: Optional[float] = None) -> Optional['ProtocolFrame']:
        """
        Wait for response frame
        
        Args:
            timeout: Timeout in seconds (default: use instance timeout)
            
        Returns:
            Optional[ProtocolFrame]: Response frame or None on timeout
        """
        if timeout is None:
            timeout = self.timeout
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Read available data
            data = self.serial_manager.read()
            if data:
                self.frame_buffer.add_data(data)
                
                # Try to extract frame
                frame_data = self.frame_buffer.extract_frame()
                if frame_data:
                    return self._parse_frame(frame_data)
            
            time.sleep(0.01)  # Small delay
        
        logger.warning(f"No response received within {timeout} seconds")
        return None
    
    def _send_and_wait(self, command: int, *args, timeout: Optional[float] = None) -> Optional['ProtocolFrame']:
        """
        Send command and wait for response
        
        Args:
            command: Command byte
            *args: Command arguments
            timeout: Response timeout
            
        Returns:
            Optional[ProtocolFrame]: Response frame or None on timeout
        """
        # Clear buffer
        self.frame_buffer.clear()
        
        # Send command
        self._send_command(command, *args)
        
        # Wait for response
        return self._wait_for_response(timeout)


@dataclass
class ProtocolFrame:
    """Protocol frame data structure"""
    command: int
    data: bytes = b''
    
    def __post_init__(self):
        # Validate on creation
        if len(self.data) > 1024:  # MAX_DATA_SIZE
            raise ValueError(f"Data size {len(self.data)} exceeds maximum 1024")


class FrameBuffer:
    """Buffer for collecting incoming frame data"""
    
    def __init__(self, max_size: int = 1024):
        self.buffer = bytearray()
        self.max_size = max_size
    
    def add_data(self, data: bytes) -> None:
        """Add incoming data to buffer"""
        self.buffer.extend(data)
        
        # Prevent buffer overflow
        if len(self.buffer) > self.max_size:
            # Keep only the last portion of the buffer
            self.buffer = self.buffer[-self.max_size//2:]
            logger.warning("Frame buffer overflow, truncated")
    
    def extract_frame(self) -> Optional[bytes]:
        """
        Extract complete frame from buffer
        
        Returns:
            Optional[bytes]: Complete frame or None if no complete frame found
        """
        STX = b'\xFF\xFF'
        ETX = b'\xFE\xFE'
        FRAME_OVERHEAD = 6  # STX(2) + CMD(1) + LEN(1) + ETX(2)
        
        if len(self.buffer) < FRAME_OVERHEAD:
            return None
        
        # Find STX
        stx_index = self.buffer.find(STX)
        if stx_index == -1:
            # No STX found, clear buffer
            self.buffer.clear()
            return None
        
        # Remove data before STX
        if stx_index > 0:
            self.buffer = self.buffer[stx_index:]
        
        # Check if we have enough data for header
        if len(self.buffer) < 4:  # STX(2) + CMD(1) + LEN(1)
            return None
        
        # Extract data length
        try:
            data_length = self.buffer[3]  # LEN byte
            frame_length = FRAME_OVERHEAD + data_length
        except IndexError:
            return None
        
        # Check if we have complete frame
        if len(self.buffer) < frame_length:
            return None
        
        # Extract frame
        frame_data = bytes(self.buffer[:frame_length])
        self.buffer = self.buffer[frame_length:]
        
        return frame_data
    
    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer.clear()
    
    def __len__(self) -> int:
        """Return buffer length"""
        return len(self.buffer)


def validate_parameter(value: Any, expected_type: type, param_name: str) -> None:
    """Validate parameter type"""
    if not isinstance(value, expected_type):
        raise LMAOperationError(
            f"Parameter {param_name} must be of type {expected_type.__name__}",
            error_code=int(LMAErrorCode.OPERATION_INVALID_PARAMETER)
        )
