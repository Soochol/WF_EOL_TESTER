"""
Simple Serial Communication

Simplified serial communication for hardware devices.
Optimized for request-response patterns like BS205 LoadCell.
"""

import asyncio
from typing import Optional
from loguru import logger

try:
    import serial_asyncio
except ImportError:
    logger.warning("serial_asyncio not available, install with: pip install pyserial-asyncio")
    serial_asyncio = None


class SerialError(Exception):
    """Serial communication error"""
    pass


class SerialConnection:
    """Simple serial connection for async communication"""
    
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Initialize serial connection
        
        Args:
            reader: Async stream reader
            writer: Async stream writer
        """
        self._reader = reader
        self._writer = writer
        self._is_connected = True
    
    @staticmethod
    async def connect(port: str, baudrate: int = 9600, timeout: float = 1.0) -> 'SerialConnection':
        """
        Connect to serial port
        
        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate
            timeout: Connection timeout
            
        Returns:
            SerialConnection instance
            
        Raises:
            SerialError: Connection failed
        """
        if serial_asyncio is None:
            raise SerialError("pyserial-asyncio not installed")
        
        try:
            reader, writer = await asyncio.wait_for(
                serial_asyncio.open_serial_connection(
                    url=port,
                    baudrate=baudrate
                ),
                timeout=timeout
            )
            
            logger.info(f"Serial connected to {port} at {baudrate} baud")
            return SerialConnection(reader, writer)
            
        except asyncio.TimeoutError:
            raise SerialError(f"Connection timeout to {port}")
        except Exception as e:
            raise SerialError(f"Failed to connect to {port}: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from serial port"""
        if self._writer and not self._writer.is_closing():
            self._writer.close()
            await self._writer.wait_closed()
        
        self._is_connected = False
        logger.info("Serial connection closed")
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self._is_connected and not self._writer.is_closing()
    
    async def write(self, data: bytes) -> None:
        """
        Write data to serial port
        
        Args:
            data: Data to write
            
        Raises:
            SerialError: Write failed
        """
        if not self.is_connected():
            raise SerialError("Not connected")
        
        try:
            self._writer.write(data)
            await self._writer.drain()
            
        except Exception as e:
            raise SerialError(f"Write failed: {e}")
    
    async def read_until(self, separator: bytes, timeout: Optional[float] = None) -> bytes:
        """
        Read data until separator is found
        
        Args:
            separator: Byte sequence to read until
            timeout: Read timeout
            
        Returns:
            Data including separator
            
        Raises:
            SerialError: Read failed or timeout
        """
        if not self.is_connected():
            raise SerialError("Not connected")
        
        try:
            if timeout:
                data = await asyncio.wait_for(
                    self._reader.readuntil(separator),
                    timeout=timeout
                )
            else:
                data = await self._reader.readuntil(separator)
            
            return data
            
        except asyncio.TimeoutError:
            raise SerialError("Read timeout")
        except Exception as e:
            raise SerialError(f"Read failed: {e}")
    
    async def read(self, size: int = -1, timeout: Optional[float] = None) -> bytes:
        """
        Read specified number of bytes
        
        Args:
            size: Number of bytes to read (-1 for all available)
            timeout: Read timeout
            
        Returns:
            Data read
            
        Raises:
            SerialError: Read failed or timeout
        """
        if not self.is_connected():
            raise SerialError("Not connected")
        
        try:
            if timeout:
                data = await asyncio.wait_for(
                    self._reader.read(size),
                    timeout=timeout
                )
            else:
                data = await self._reader.read(size)
            
            return data
            
        except asyncio.TimeoutError:
            raise SerialError("Read timeout")
        except Exception as e:
            raise SerialError(f"Read failed: {e}")
    
    async def send_command(self, command: str, terminator: str = '\r', timeout: float = 1.0) -> str:
        """
        Send command and read response (convenience method)
        
        Args:
            command: Command to send
            terminator: Command/response terminator
            timeout: Response timeout
            
        Returns:
            Response string (without terminator)
            
        Raises:
            SerialError: Communication failed
        """
        try:
            # Send command
            command_bytes = f"{command}{terminator}".encode('ascii')
            await self.write(command_bytes)
            
            # Read response
            terminator_bytes = terminator.encode('ascii')
            response_bytes = await self.read_until(terminator_bytes, timeout)
            
            # Decode and strip terminator
            response = response_bytes.decode('ascii').rstrip(terminator)
            
            logger.debug(f"Command: {command} -> Response: {response}")
            return response
            
        except UnicodeDecodeError as e:
            raise SerialError(f"Response decode failed: {e}")
        except Exception as e:
            raise SerialError(f"Command failed: {e}")


class SerialManager:
    """Simple serial manager for creating connections"""
    
    @staticmethod
    async def create_connection(port: str, baudrate: int = 9600, timeout: float = 1.0) -> SerialConnection:
        """
        Create serial connection (convenience method)
        
        Args:
            port: Serial port
            baudrate: Baud rate  
            timeout: Connection timeout
            
        Returns:
            SerialConnection instance
        """
        return await SerialConnection.connect(port, baudrate, timeout)