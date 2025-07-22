"""
Core serial transport implementation.

Provides pure serial communication functionality with minimal dependencies.
Focuses solely on connection management and basic I/O operations.
"""

import time
from typing import Any, Dict, Optional

import serial
from loguru import logger

from .interfaces import ISerialTransport
from ..exceptions import (
    SerialConnectionError,
    SerialCommunicationError,
    SerialExceptionFactory
)


class SerialTransport(ISerialTransport):
    """Pure serial transport implementation."""
    
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected_flag = False
        self.port_config: Dict[str, Any] = {}
        
        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_count = 0
        self.last_activity = time.time()
    
    def connect(self, port: str, baudrate: int = 9600, timeout: float = 1.0,
                bytesize: int = 8, parity: str = 'N', stopbits: int = 1,
                xonxoff: bool = False, rtscts: bool = False, dsrdtr: bool = False,
                **kwargs) -> None:
        """Establish connection to serial port."""
        if self.is_connected_flag:
            logger.warning(f'Already connected to {port}')
            return
        
        self.port_config = {
            'port': port,
            'baudrate': baudrate,
            'timeout': timeout,
            'bytesize': bytesize,
            'parity': parity,
            'stopbits': stopbits,
            'xonxoff': xonxoff,
            'rtscts': rtscts,
            'dsrdtr': dsrdtr,
            **kwargs
        }
        
        try:
            self._validate_config()
            
            # Map parity setting
            parity_map = {
                'N': serial.PARITY_NONE,
                'E': serial.PARITY_EVEN,
                'O': serial.PARITY_ODD,
                'M': serial.PARITY_MARK,
                'S': serial.PARITY_SPACE
            }
            
            # Create and open serial port
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity_map[parity],
                stopbits=stopbits,
                timeout=timeout,
                xonxoff=xonxoff,
                rtscts=rtscts,
                dsrdtr=dsrdtr
            )
            
            if not self.serial_port.is_open:
                self.serial_port.open()
            
            if self.serial_port.is_open:
                self.is_connected_flag = True
                self.connection_count += 1
                self.last_activity = time.time()
                logger.info(f'Connected to {port} ({baudrate} baud)')
            else:
                raise SerialExceptionFactory.create_connection_error(
                    port, 'Port failed to open',
                    baudrate=baudrate, timeout=timeout
                )
                
        except serial.SerialException as e:
            self.is_connected_flag = False
            logger.error(f'Serial connection error: {e}')
            raise SerialExceptionFactory.create_connection_error(
                port, str(e),
                baudrate=baudrate, timeout=timeout
            )
        except Exception as e:
            self.is_connected_flag = False
            logger.error(f'Unexpected error during connection: {e}')
            raise SerialConnectionError(
                f'Unexpected error connecting to {port}: {e}',
                port=port
            )
    
    def disconnect(self) -> None:
        """Close serial connection."""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.serial_port = None
            
            self.is_connected_flag = False
            port_name = self.port_config.get('port', 'unknown')
            logger.info(f'Disconnected from {port_name}')
            
        except Exception as e:
            # Disconnect errors are logged but not re-raised
            logger.error(f'Error during disconnect: {e}')
        finally:
            # Ensure state is updated regardless of errors
            self.is_connected_flag = False
            self.serial_port = None
    
    def read(self, size: Optional[int] = None) -> bytes:
        """Read data from serial port."""
        if not self.is_connected_flag or not self.serial_port:
            raise SerialExceptionFactory.create_communication_error(
                self.port_config.get('port', 'unknown'), 'read', 'Not connected to device'
            )
        
        try:
            if size is None:
                # Read all available data
                data = self.serial_port.read(self.serial_port.in_waiting or 1)
            else:
                # Read specific number of bytes
                data = self.serial_port.read(size)
            
            if data:
                self.bytes_received += len(data)
                self.last_activity = time.time()
                logger.debug(f'Received {len(data)} bytes: {data.hex()}')
            
            return data
            
        except serial.SerialException as e:
            logger.error(f'Serial read error: {e}')
            self.is_connected_flag = False
            raise SerialExceptionFactory.create_communication_error(
                self.port_config.get('port', 'unknown'), 'read', str(e)
            )
        except Exception as e:
            logger.error(f'Unexpected error during read: {e}')
            raise SerialCommunicationError(
                f'Unexpected error during read: {e}',
                port=self.port_config.get('port', 'unknown'),
                operation='read'
            )
    
    def write(self, data: bytes) -> int:
        """Write data to serial port."""
        if not self.is_connected_flag or not self.serial_port:
            raise SerialExceptionFactory.create_communication_error(
                self.port_config.get('port', 'unknown'), 'write', 'Not connected to device'
            )
        
        if not isinstance(data, bytes):
            raise SerialExceptionFactory.create_communication_error(
                self.port_config.get('port', 'unknown'), 'write', 'Data must be bytes'
            )
        
        try:
            bytes_written = self.serial_port.write(data)
            self.serial_port.flush()
            
            self.bytes_sent += bytes_written
            self.last_activity = time.time()
            
            logger.debug(f'Sent {bytes_written} bytes: {data.hex()}')
            return bytes_written
            
        except serial.SerialException as e:
            logger.error(f'Serial write error: {e}')
            self.is_connected_flag = False
            raise SerialExceptionFactory.create_communication_error(
                self.port_config.get('port', 'unknown'), 'write', str(e)
            )
        except Exception as e:
            logger.error(f'Unexpected error during write: {e}')
            raise SerialCommunicationError(
                f'Unexpected error during write: {e}',
                port=self.port_config.get('port', 'unknown'),
                operation='write'
            )
    
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        if not self.serial_port:
            return False
        
        try:
            return self.serial_port.is_open and self.is_connected_flag
        except Exception as e:
            logger.error(f'Connection test failed: {e}')
            self.is_connected_flag = False
            return False
    
    def flush_buffers(self) -> None:
        """Clear all transport buffers."""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                logger.debug('Transport buffers flushed')
            except Exception as e:
                logger.warning(f'Failed to flush transport buffers: {e}')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            'port': self.port_config.get('port', 'unknown'),
            'baudrate': self.port_config.get('baudrate', 0),
            'connected': self.is_connected_flag,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'connection_count': self.connection_count,
            'last_activity': self.last_activity,
            'config': self.port_config.copy()
        }
    
    def read_available(self) -> bytes:
        """Read all available data without blocking."""
        if not self.is_connected_flag or not self.serial_port:
            return b''
        
        try:
            available = self.serial_port.in_waiting
            if available > 0:
                return self.read(available)
            return b''
        except Exception:
            return b''
    
    def is_data_available(self) -> bool:
        """Check if data is available to read."""
        if not self.is_connected_flag or not self.serial_port:
            return False
        
        try:
            return self.serial_port.in_waiting > 0
        except Exception:
            return False
    
    def _validate_config(self) -> None:
        """Validate serial configuration parameters."""
        port = self.port_config.get('port', '')
        baudrate = self.port_config.get('baudrate', 0)
        timeout = self.port_config.get('timeout', 0)
        bytesize = self.port_config.get('bytesize', 0)
        parity = self.port_config.get('parity', '')
        stopbits = self.port_config.get('stopbits', 0)
        
        if not isinstance(port, str) or not port:
            raise SerialExceptionFactory.create_configuration_error(
                'port', port, 'Port must be a non-empty string'
            )
        
        if not (300 <= baudrate <= 921600):
            raise SerialExceptionFactory.create_configuration_error(
                'baudrate', baudrate,
                'Baudrate must be between 300 and 921600'
            )
        
        if not (0.1 <= timeout <= 60.0):
            raise SerialExceptionFactory.create_configuration_error(
                'timeout', timeout,
                'Timeout must be between 0.1 and 60.0 seconds'
            )
        
        if bytesize not in [5, 6, 7, 8]:
            raise SerialExceptionFactory.create_configuration_error(
                'bytesize', bytesize, 'Bytesize must be 5, 6, 7, or 8'
            )
        
        if parity not in ['N', 'E', 'O', 'M', 'S']:
            raise SerialExceptionFactory.create_configuration_error(
                'parity', parity,
                'Parity must be N, E, O, M, or S'
            )
        
        if stopbits not in [1, 1.5, 2]:
            raise SerialExceptionFactory.create_configuration_error(
                'stopbits', stopbits, 'Stopbits must be 1, 1.5, or 2'
            )