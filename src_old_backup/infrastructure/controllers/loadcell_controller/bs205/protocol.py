"""
BS205 Loadcell Controller Protocol Handler

Handles command building, response parsing, and protocol-specific operations.
"""

import time
from typing import Optional

from loguru import logger

from .constants import *
from .models import LoadcellResponse, ResponseBuffer
from ..exceptions import BS205CommunicationError, BS205OperationError
from .....driver.serial.exceptions import SerialCommunicationError, SerialTimeoutError


class BS205Protocol:
    """BS205 protocol handler for command building and response parsing"""
    
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager
        self.response_buffer = ResponseBuffer()
    
    def build_command(self, indicator_id: int, command: int) -> bytes:
        """
        Build command bytes for loadcell controller
        
        Args:
            indicator_id: Indicator ID (1-255)
            command: Command character (R, Z, H, L)
            
        Returns:
            bytes: Command bytes to send
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not (MIN_INDICATOR_ID <= indicator_id <= MAX_INDICATOR_ID):
            raise ValueError(f"Indicator ID must be between {MIN_INDICATOR_ID} and {MAX_INDICATOR_ID}")
        
        if command not in [CMD_READ_VALUE, CMD_AUTO_ZERO, CMD_HOLD_ON, CMD_HOLD_OFF]:
            raise ValueError(f"Invalid command: {command}")
        
        # Convert indicator ID to ASCII representation
        if indicator_id <= 9:
            # Single digit: use ASCII digit
            id_byte = ord(str(indicator_id))
        elif indicator_id <= 15:
            # Use hex representation for 10-15 (A-F)
            id_byte = ord(hex(indicator_id).upper()[-1])
        else:
            # For IDs > 15, use special encoding
            # According to examples: ID 10 becomes 3A (ASCII ':')
            id_byte = 0x30 + indicator_id  # This might need adjustment based on actual protocol
            if id_byte > 0x7F:  # Keep within ASCII range
                id_byte = 0x30 + (indicator_id % 48)
        
        command_bytes = bytes([id_byte, command])
        
        logger.debug(f"Built command: ID={indicator_id} (0x{id_byte:02X}), CMD={chr(command)} (0x{command:02X})")
        return command_bytes
    
    def send_command(self, indicator_id: int, command: int) -> None:
        """
        Send command to loadcell controller
        
        Args:
            indicator_id: Indicator ID
            command: Command byte (R, Z, H, L)
            
        Raises:
            BS205CommunicationError: If command send fails
        """
        try:
            command_bytes = self.build_command(indicator_id, command)
            self.serial_manager.write(command_bytes)
            
            logger.debug(f"Sent command: ID={indicator_id}, CMD={chr(command)} "
                        f"({command_bytes.hex().upper()})")
            
        except (SerialCommunicationError, SerialTimeoutError) as e:
            logger.error(f"Failed to send command: {e}")
            raise BS205CommunicationError(f"Failed to send command: {e}", indicator_id=indicator_id, command=chr(command))
        except Exception as e:
            logger.error(f"Unexpected error sending command: {e}")
            raise BS205CommunicationError(f"Unexpected error sending command: {e}", indicator_id=indicator_id, command=chr(command))
    
    def send_control_command(self, indicator_id: int, command: int) -> None:
        """
        Send control command (no response expected)
        
        Args:
            indicator_id: Indicator ID
            command: Command byte (Z, H, L)
            
        Raises:
            BS205CommunicationError: If command send fails
        """
        if command == CMD_READ_VALUE:
            logger.error("Use read_value() for read commands")
            raise BS205CommunicationError("Use read_value() for read commands", indicator_id=indicator_id, command=chr(command))
        
        self.send_command(indicator_id, command)
    
    def read_value(self, indicator_id: int, timeout: Optional[float] = None) -> Optional[LoadcellResponse]:
        """
        Read current value from loadcell
        
        Args:
            indicator_id: Indicator ID
            timeout: Response timeout (default: DEFAULT_TIMEOUT)
            
        Returns:
            Optional[LoadcellResponse]: Response data or None if failed
        """
        try:
            if timeout is None:
                timeout = DEFAULT_TIMEOUT
            
            # Clear response buffer
            self.response_buffer.clear()
            
            # Send read command
            self.send_command(indicator_id, CMD_READ_VALUE)
            
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Read available data
                data = self.serial_manager.read()
                if data:
                    self.response_buffer.add_data(data)
                    
                    # Try to extract response
                    response_data = self.response_buffer.extract_response()
                    if response_data:
                        response = self.parse_response(response_data)
                        if response and response.indicator_id == indicator_id:
                            return response
                        elif response:
                            logger.warning(f"Response ID mismatch: expected {indicator_id}, got {response.indicator_id}")
                
                time.sleep(0.01)  # Small delay
            
            logger.warning(f"No response received within {timeout} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error reading value: {e}")
            return None
    
    def parse_response(self, data: bytes) -> Optional[LoadcellResponse]:
        """
        Parse response from loadcell controller
        
        Args:
            data: Response bytes from controller
            
        Returns:
            Optional[LoadcellResponse]: Parsed response or None if invalid
        """
        if len(data) < DATA_LENGTH_MIN:
            logger.warning(f"Response too short: {len(data)} bytes")
            return None
        
        # Check STX and ETX
        if data[0] != STX:
            logger.warning(f"Invalid STX: 0x{data[0]:02X}")
            return None
        
        if data[-1] != ETX:
            logger.warning(f"Invalid ETX: 0x{data[-1]:02X}")
            return None
        
        # Extract payload (between STX and ETX)
        payload = data[1:-1]
        
        try:
            # Convert to ASCII string
            ascii_data = payload.decode('ascii')
            logger.debug(f"Parsing ASCII data: '{ascii_data}'")
            
            # Parse the response
            return self._parse_ascii_response(ascii_data)
            
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode ASCII data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None
    
    def _parse_ascii_response(self, ascii_data: str) -> Optional[LoadcellResponse]:
        """Parse ASCII response data"""
        if len(ascii_data) < 3:  # Minimum: ID + Sign + Digit
            logger.warning(f"ASCII data too short: '{ascii_data}'")
            return None
        
        try:
            # Extract indicator ID (first character or two)
            indicator_id = self._extract_indicator_id(ascii_data)
            if indicator_id is None:
                return None
            
            # Find sign position (+ or -)
            sign_pos = -1
            for i, char in enumerate(ascii_data):
                if char in ['+', '-']:
                    sign_pos = i
                    break
            
            if sign_pos == -1:
                logger.warning(f"No sign found in data: '{ascii_data}'")
                return None
            
            sign = ascii_data[sign_pos]
            value_str = ascii_data[sign_pos + 1:]
            
            # Parse numeric value (handle spaces and decimal point)
            value = self._parse_numeric_value(value_str)
            if value is None:
                return None
            
            # Apply sign
            if sign == '-':
                value = -value
            
            response = LoadcellResponse(
                indicator_id=indicator_id,
                value=value,
                sign=sign,
                raw_data=ascii_data
            )
            
            logger.debug(f"Parsed response: ID={indicator_id}, Value={value}, Sign={sign}")
            return response
            
        except Exception as e:
            logger.error(f"Error parsing ASCII response '{ascii_data}': {e}")
            return None
    
    def _extract_indicator_id(self, ascii_data: str) -> Optional[int]:
        """Extract indicator ID from ASCII data"""
        # Find the position of the sign
        sign_pos = -1
        for i, char in enumerate(ascii_data):
            if char in ['+', '-']:
                sign_pos = i
                break
        
        if sign_pos <= 0:
            logger.warning(f"Invalid sign position in data: '{ascii_data}'")
            return None
        
        id_str = ascii_data[:sign_pos]
        
        try:
            # Handle special ID encodings
            if len(id_str) == 1:
                char = id_str[0]
                if char.isdigit():
                    return int(char)
                elif char == '?':  # Example shows 15 as '?'
                    return 15
                elif char == ':':  # Example shows 10 as ':'
                    return 10
                else:
                    # Other special characters might map to specific IDs
                    ascii_val = ord(char)
                    if ascii_val >= 0x30:  # Starting from '0'
                        return ascii_val - 0x30
                    return ascii_val
            else:
                # Multi-character ID (shouldn't happen in this protocol)
                return int(id_str)
                
        except ValueError as e:
            logger.error(f"Failed to parse indicator ID '{id_str}': {e}")
            return None
    
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """Parse numeric value from string (handle spaces and decimal point)"""
        try:
            # Remove leading/trailing spaces and underscores
            cleaned = value_str.strip().replace('_', ' ')
            
            # Remove extra spaces but preserve decimal point
            # Handle cases like "_ _7487" or "_748.6"
            parts = []
            current_part = ""
            
            for char in cleaned:
                if char == ' ':
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                elif char == '.':
                    current_part += char
                elif char.isdigit():
                    current_part += char
                else:
                    logger.warning(f"Unexpected character in value: '{char}'")
            
            if current_part:
                parts.append(current_part)
            
            # Reconstruct the number
            if not parts:
                logger.warning(f"No numeric parts found in: '{value_str}'")
                return None
            
            # Join parts and handle decimal point
            if len(parts) == 1:
                # Single part, might have decimal point
                value = float(parts[0])
            else:
                # Multiple parts, need to combine
                # Find which part has decimal point
                decimal_part = None
                integer_parts = []
                
                for part in parts:
                    if '.' in part:
                        if decimal_part is not None:
                            logger.warning(f"Multiple decimal points in: '{value_str}'")
                            return None
                        decimal_part = part
                    else:
                        integer_parts.append(part)
                
                if decimal_part:
                    # Combine integer parts and decimal part
                    integer_str = ''.join(integer_parts)
                    if '.' in decimal_part:
                        # Split decimal part
                        dec_int, dec_frac = decimal_part.split('.')
                        full_integer = integer_str + dec_int
                        full_str = full_integer + '.' + dec_frac
                    else:
                        full_str = integer_str + decimal_part
                else:
                    # No decimal point, just combine all parts
                    full_str = ''.join(parts)
                
                value = float(full_str)
            
            # Validate range
            if not (MIN_VALUE <= value <= MAX_VALUE):
                logger.warning(f"Value out of range: {value}")
                return None
            
            return value
            
        except ValueError as e:
            logger.error(f"Failed to parse numeric value '{value_str}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing value '{value_str}': {e}")
            return None