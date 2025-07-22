"""
Serial communication manager implementation.

Provides high-level serial communication interface by orchestrating all components.
This is the main entry point for higher-level code to use serial communication.
"""

import time
from typing import Any, Callable, Dict, Optional

from loguru import logger

from .core.transport import SerialTransport
from .core.buffer import SerialBuffer
from .core.reader import SerialReader
from .features.retry import RetryManager
from .features.health import HealthMonitor
from .features.async_adapter import AsyncAdapter
from .exceptions import SerialCommunicationError, SerialConnectionError


class SerialManager:
    """
    High-level serial communication manager.
    
    Orchestrates all serial communication components to provide a simple,
    reliable interface for higher-level code.
    """
    
    def __init__(self, buffer_size: int = 65536, read_interval: float = 0.01,
                 max_retries: int = 3, retry_base_delay: float = 0.1):
        """
        Initialize serial manager.
        
        Args:
            buffer_size: Data buffer size in bytes
            read_interval: Background reading interval in seconds
            max_retries: Maximum retry attempts for operations
            retry_base_delay: Base delay for retry exponential backoff
        """
        # Create core components
        self._transport = SerialTransport()
        self._buffer = SerialBuffer(max_size=buffer_size)
        self._reader = SerialReader(self._transport, self._buffer, read_interval)
        
        # Create feature components
        self._retry_manager = RetryManager(max_retries, retry_base_delay)
        self._health_monitor = HealthMonitor(self._transport, self._buffer, self._reader)
        self._async_adapter = AsyncAdapter(self._transport, self._buffer, self._reader)
        
        # Manager state
        self._auto_start_reader = True
        self._connection_config: Dict[str, Any] = {}
        
        # Statistics
        self._created_time = time.time()
        self._connection_attempts = 0
        self._successful_connections = 0
        
        logger.info("SerialManager initialized")
    
    def connect(self, port: str, baudrate: int = 9600, timeout: float = 1.0,
                auto_start_reader: bool = True, **kwargs) -> None:
        """
        Connect to serial port with automatic component setup.
        
        Args:
            port: Serial port identifier
            baudrate: Communication baud rate
            timeout: Connection timeout
            auto_start_reader: Whether to automatically start background reader
            **kwargs: Additional serial parameters
        """
        self._connection_attempts += 1
        
        def _connect_operation():
            self._transport.connect(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                **kwargs
            )
            
            # Store configuration for recovery
            self._connection_config = {
                'port': port,
                'baudrate': baudrate,
                'timeout': timeout,
                **kwargs
            }
            
            # Start background reader if requested
            if auto_start_reader:
                self._reader.start_reading()
                self._auto_start_reader = True
            else:
                self._auto_start_reader = False
            
            self._successful_connections += 1
            logger.info(f"SerialManager connected to {port} ({baudrate} baud)")
        
        try:
            self._retry_manager.with_retry(_connect_operation)
        except Exception as e:
            logger.error(f"Failed to connect to {port}: {e}")
            raise SerialConnectionError(f"Connection failed: {e}", port=port)
    
    def disconnect(self) -> None:
        """Disconnect from serial port and stop all components."""
        try:
            # Stop background reader
            if self._reader.is_reading():
                self._reader.stop_reading()
            
            # Disconnect transport
            self._transport.disconnect()
            
            # Clear buffer
            self._buffer.clear()
            
            logger.info("SerialManager disconnected")
        
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            # Don't re-raise disconnect errors
    
    def write(self, data: bytes, use_retry: bool = True) -> int:
        """
        Write data to serial port.
        
        Args:
            data: Data to write
            use_retry: Whether to use retry logic
            
        Returns:
            int: Number of bytes written
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        def _write_operation():
            return self._transport.write(data)
        
        try:
            if use_retry:
                return self._retry_manager.with_retry(_write_operation)
            else:
                return _write_operation()
        
        except Exception as e:
            logger.error(f"Write operation failed: {e}")
            raise SerialCommunicationError(f"Write failed: {e}", operation="write")
    
    def read(self, size: Optional[int] = None, timeout: Optional[float] = None) -> bytes:
        """
        Read data from buffer or transport.
        
        Args:
            size: Number of bytes to read (None = all available)
            timeout: Read timeout in seconds
            
        Returns:
            bytes: Data read
        """
        start_time = time.time()
        
        # First try to get data from buffer
        data = self._buffer.get_data(size)
        
        # If we got enough data or no timeout specified, return immediately
        if data and (size is None or len(data) >= size):
            return data
        
        if timeout is None:
            return data
        
        # Wait for more data with timeout
        needed = size - len(data) if size is not None else 1
        
        while len(data) < needed:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                break
            
            # Small delay to avoid busy waiting
            time.sleep(0.01)
            
            # Check buffer again
            new_data = self._buffer.get_data(needed - len(data))
            data += new_data
        
        return data
    
    def read_until(self, terminator: bytes, max_size: Optional[int] = None,
                   timeout: Optional[float] = None) -> bytes:
        """
        Read data until terminator is found.
        
        Args:
            terminator: Byte sequence to read until
            max_size: Maximum bytes to read
            timeout: Timeout in seconds
            
        Returns:
            bytes: Data including terminator
        """
        if not isinstance(terminator, bytes):
            raise TypeError("Terminator must be bytes")
        
        buffer = b''
        start_time = time.time()
        
        while True:
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    break
            
            # Check max size
            if max_size is not None and len(buffer) >= max_size:
                break
            
            # Read more data
            chunk = self.read(1024, timeout=0.1)
            if not chunk:
                continue
            
            buffer += chunk
            
            # Check for terminator
            if terminator in buffer:
                pos = buffer.find(terminator) + len(terminator)
                result = buffer[:pos]
                
                # Put remaining data back in buffer
                remaining = buffer[pos:]
                if remaining:
                    self._buffer.add_data(remaining)
                
                return result
        
        return buffer
    
    def write_and_read(self, data: bytes, expected_size: Optional[int] = None,
                      timeout: float = 5.0, clear_buffer: bool = True) -> bytes:
        """
        Write data and read response.
        
        Args:
            data: Data to write
            expected_size: Expected response size
            timeout: Response timeout
            clear_buffer: Whether to clear buffer before writing
            
        Returns:
            bytes: Response data
        """
        if clear_buffer:
            self._buffer.clear()
        
        # Write data
        self.write(data)
        
        # Read response
        if expected_size is not None:
            return self.read(expected_size, timeout)
        else:
            # Read all available data within timeout
            return self.read(timeout=timeout)
    
    def is_connected(self) -> bool:
        """Check if serial connection is active."""
        return self._transport.is_connected()
    
    def flush_buffers(self) -> None:
        """Clear all buffers."""
        self._transport.flush_buffers()
        self._buffer.clear()
        logger.debug("All buffers flushed")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return self._health_monitor.get_status()
    
    def auto_recover(self) -> bool:
        """Attempt automatic recovery from connection issues."""
        return self._health_monitor.auto_recover()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            'manager': {
                'created_time': self._created_time,
                'uptime_seconds': time.time() - self._created_time,
                'connection_attempts': self._connection_attempts,
                'successful_connections': self._successful_connections,
                'auto_start_reader': self._auto_start_reader,
                'current_config': self._connection_config.copy()
            },
            'transport': self._transport.get_stats(),
            'buffer': self._buffer.get_stats(),
            'reader': self._reader.get_stats(),
            'retry': self._retry_manager.get_stats(),
            'health': self._health_monitor.get_status()
        }
    
    def configure_components(self, **kwargs) -> None:
        """
        Configure component parameters.
        
        Args:
            buffer_size: New buffer size
            read_interval: New read interval
            max_retries: New max retry attempts
            retry_base_delay: New retry base delay
            health_thresholds: Health monitoring thresholds
        """
        if 'buffer_size' in kwargs:
            self._buffer.resize(kwargs['buffer_size'])
        
        if 'read_interval' in kwargs:
            self._reader.configure_timing(kwargs['read_interval'])
        
        if 'max_retries' in kwargs or 'retry_base_delay' in kwargs:
            max_retries = kwargs.get('max_retries', self._retry_manager._max_retries)
            base_delay = kwargs.get('retry_base_delay', self._retry_manager._base_delay)
            self._retry_manager.configure(max_retries, base_delay)
        
        if 'health_thresholds' in kwargs:
            self._health_monitor.configure_thresholds(**kwargs['health_thresholds'])
        
        logger.info("Component configuration updated")
    
    def set_callbacks(self, data_callback: Optional[Callable[[bytes], None]] = None,
                     error_callback: Optional[Callable[[Exception], None]] = None,
                     health_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                     overflow_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """
        Set various callbacks for events.
        
        Args:
            data_callback: Called when data is received
            error_callback: Called when errors occur
            health_callback: Called when health status changes
            overflow_callback: Called when buffer overflow occurs
        """
        if data_callback is not None:
            self._reader.set_data_callback(data_callback)
        
        if error_callback is not None:
            self._reader.set_error_callback(error_callback)
        
        if health_callback is not None:
            self._health_monitor.set_health_callback(health_callback)
        
        if overflow_callback is not None:
            self._buffer.set_overflow_callback(overflow_callback)
        
        logger.debug("Callbacks configured")
    
    def start_background_reading(self) -> None:
        """Start background reading if not already running."""
        if not self._reader.is_reading():
            if self.is_connected():
                self._reader.start_reading()
                logger.info("Background reading started")
            else:
                raise SerialCommunicationError("Cannot start reading: not connected")
    
    def stop_background_reading(self) -> None:
        """Stop background reading."""
        if self._reader.is_reading():
            self._reader.stop_reading()
            logger.info("Background reading stopped")
    
    @property
    def async_adapter(self) -> AsyncAdapter:
        """Get async adapter for async/await operations."""
        return self._async_adapter
    
    @property
    def retry_manager(self) -> RetryManager:
        """Get retry manager for custom retry operations."""
        return self._retry_manager
    
    @property
    def health_monitor(self) -> HealthMonitor:
        """Get health monitor for detailed health analysis."""
        return self._health_monitor
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()