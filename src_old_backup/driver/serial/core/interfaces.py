"""
Serial communication component interfaces.

Defines abstract interfaces for all serial communication components
following the Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class ISerialTransport(ABC):
    """Interface for core serial transport layer."""
    
    @abstractmethod
    def connect(self, port: str, **kwargs) -> None:
        """
        Establish connection to serial port.
        
        Args:
            port: Serial port identifier (e.g., '/dev/ttyUSB0', 'COM3')
            **kwargs: Additional connection parameters
            
        Raises:
            SerialConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close serial connection.
        
        Note: Should not raise exceptions - disconnect errors are logged only.
        """
        pass
    
    @abstractmethod
    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read data from serial port.
        
        Args:
            size: Number of bytes to read (None = all available)
            
        Returns:
            bytes: Data read from port
            
        Raises:
            SerialCommunicationError: If read operation fails
        """
        pass
    
    @abstractmethod
    def write(self, data: bytes) -> int:
        """
        Write data to serial port.
        
        Args:
            data: Raw bytes to send
            
        Returns:
            int: Number of bytes written
            
        Raises:
            SerialCommunicationError: If write operation fails
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if transport is connected.
        
        Returns:
            bool: True if connected and operational
        """
        pass
    
    @abstractmethod
    def flush_buffers(self) -> None:
        """Clear all internal transport buffers."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get transport statistics.
        
        Returns:
            Dict containing bytes_sent, bytes_received, etc.
        """
        pass


class ISerialBuffer(ABC):
    """Interface for serial data buffer management."""
    
    @abstractmethod
    def add_data(self, data: bytes) -> None:
        """
        Add data to buffer.
        
        Args:
            data: Data to add to buffer
            
        Note: Should handle overflow gracefully
        """
        pass
    
    @abstractmethod
    def get_data(self, size: Optional[int] = None) -> bytes:
        """
        Retrieve data from buffer.
        
        Args:
            size: Number of bytes to retrieve (None = all available)
            
        Returns:
            bytes: Data from buffer
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data from buffer."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """
        Get current buffer size.
        
        Returns:
            int: Number of bytes currently in buffer
        """
        pass
    
    @abstractmethod
    def capacity(self) -> int:
        """
        Get buffer capacity.
        
        Returns:
            int: Maximum buffer size
        """
        pass


class ISerialReader(ABC):
    """Interface for background serial reading."""
    
    @abstractmethod
    def start_reading(self) -> None:
        """Start background reading thread."""
        pass
    
    @abstractmethod
    def stop_reading(self) -> None:
        """Stop background reading thread."""
        pass
    
    @abstractmethod
    def is_reading(self) -> bool:
        """
        Check if background reading is active.
        
        Returns:
            bool: True if reading thread is running
        """
        pass
    
    @abstractmethod
    def set_data_callback(self, callback: Optional[Callable[[bytes], None]]) -> None:
        """
        Set callback for received data.
        
        Args:
            callback: Function called when data is received
        """
        pass
    
    @abstractmethod
    def set_error_callback(self, callback: Optional[Callable[[Exception], None]]) -> None:
        """
        Set callback for read errors.
        
        Args:
            callback: Function called when read error occurs
        """
        pass


class IRetryManager(ABC):
    """Interface for retry logic management."""
    
    @abstractmethod
    def with_retry(self, operation: Callable[[], Any], **kwargs) -> Any:
        """
        Execute operation with retry logic.
        
        Args:
            operation: Function to execute with retries
            **kwargs: Retry configuration overrides
            
        Returns:
            Result of successful operation
            
        Raises:
            Last exception if all retries fail
        """
        pass
    
    @abstractmethod
    def configure(self, max_retries: int, base_delay: float) -> None:
        """
        Configure retry parameters.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
        """
        pass


class IHealthMonitor(ABC):
    """Interface for connection health monitoring."""
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Dict with health information and recommendations
        """
        pass
    
    @abstractmethod
    def auto_recover(self) -> bool:
        """
        Attempt automatic recovery from connection issues.
        
        Returns:
            bool: True if recovery was successful
        """
        pass
    
    @abstractmethod
    def set_health_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        """
        Set callback for health status changes.
        
        Args:
            callback: Function called when health status changes
        """
        pass


class IAsyncAdapter(ABC):
    """Interface for async/await support."""
    
    @abstractmethod
    async def read_async(self, size: Optional[int] = None) -> bytes:
        """Async-compatible read operation."""
        pass
    
    @abstractmethod
    async def write_async(self, data: bytes) -> int:
        """Async-compatible write operation."""
        pass
    
    @abstractmethod
    async def connect_async(self) -> None:
        """Async-compatible connection."""
        pass
    
    @abstractmethod
    async def disconnect_async(self) -> None:
        """Async-compatible disconnection."""
        pass