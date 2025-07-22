"""
Serial buffer management implementation.

Provides thread-safe buffer operations with overflow handling and statistics.
Focuses solely on data buffering and retrieval operations.
"""

import threading
import time
from collections import deque
from typing import Callable, Optional

from loguru import logger

from .interfaces import ISerialBuffer
from ..exceptions import SerialBufferError, SerialExceptionFactory


class SerialBuffer(ISerialBuffer):
    """Thread-safe serial data buffer with overflow handling."""
    
    def __init__(self, max_size: int = 65536):
        """
        Initialize buffer with specified capacity.
        
        Args:
            max_size: Maximum buffer size in bytes (default: 64KB)
        """
        if max_size <= 0:
            raise ValueError("Buffer size must be positive")
        
        self._buffer = deque()
        self._lock = threading.RLock()
        self._max_size = max_size
        self._current_size = 0
        
        # Statistics
        self._bytes_added = 0
        self._bytes_retrieved = 0
        self._overflow_count = 0
        self._overflow_bytes = 0
        self._last_overflow = None
        
        # Callbacks
        self._overflow_callback: Optional[Callable[[int, int], None]] = None
    
    def add_data(self, data: bytes) -> None:
        """
        Add data to buffer with overflow handling.
        
        Args:
            data: Data to add to buffer
            
        Note: Handles overflow by dropping oldest data and calling callback
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        if not data:
            return
        
        with self._lock:
            data_size = len(data)
            self._bytes_added += data_size
            
            # Handle overflow by removing old data
            overflow_bytes = 0
            while self._current_size + data_size > self._max_size and self._buffer:
                old_chunk = self._buffer.popleft()
                old_size = len(old_chunk)
                self._current_size -= old_size
                overflow_bytes += old_size
            
            # If data is larger than entire buffer, truncate it
            if data_size > self._max_size:
                overflow_bytes += data_size - self._max_size
                data = data[-self._max_size:]
                data_size = len(data)
            
            # Add new data
            if data_size > 0:
                self._buffer.append(data)
                self._current_size += data_size
            
            # Handle overflow
            if overflow_bytes > 0:
                self._overflow_count += 1
                self._overflow_bytes += overflow_bytes
                self._last_overflow = time.time()
                
                logger.warning(
                    f"Buffer overflow: dropped {overflow_bytes} bytes "
                    f"(current size: {self._current_size}/{self._max_size})"
                )
                
                # Call overflow callback
                if self._overflow_callback:
                    try:
                        self._overflow_callback(overflow_bytes, self._max_size)
                    except Exception as e:
                        logger.error(f"Error in overflow callback: {e}")
            
            logger.debug(f"Added {data_size} bytes to buffer (total: {self._current_size})")
    
    def get_data(self, size: Optional[int] = None) -> bytes:
        """
        Retrieve data from buffer.
        
        Args:
            size: Number of bytes to retrieve (None = all available)
            
        Returns:
            bytes: Data from buffer
        """
        with self._lock:
            if not self._buffer:
                return b''
            
            if size is None:
                # Return all data
                result = b''.join(self._buffer)
                self._buffer.clear()
                self._current_size = 0
                self._bytes_retrieved += len(result)
                logger.debug(f"Retrieved all {len(result)} bytes from buffer")
                return result
            
            if size <= 0:
                return b''
            
            # Collect data chunks until we have enough
            result_chunks = []
            bytes_collected = 0
            
            while self._buffer and bytes_collected < size:
                chunk = self._buffer[0]
                chunk_size = len(chunk)
                
                if bytes_collected + chunk_size <= size:
                    # Take entire chunk
                    result_chunks.append(self._buffer.popleft())
                    self._current_size -= chunk_size
                    bytes_collected += chunk_size
                else:
                    # Take partial chunk
                    needed = size - bytes_collected
                    result_chunks.append(chunk[:needed])
                    self._buffer[0] = chunk[needed:]
                    self._current_size -= needed
                    bytes_collected += needed
            
            result = b''.join(result_chunks)
            self._bytes_retrieved += len(result)
            
            logger.debug(f"Retrieved {len(result)} bytes from buffer (remaining: {self._current_size})")
            return result
    
    def clear(self) -> None:
        """Clear all data from buffer."""
        with self._lock:
            old_size = self._current_size
            self._buffer.clear()
            self._current_size = 0
            
            if old_size > 0:
                logger.debug(f"Cleared {old_size} bytes from buffer")
    
    def size(self) -> int:
        """
        Get current buffer size.
        
        Returns:
            int: Number of bytes currently in buffer
        """
        with self._lock:
            return self._current_size
    
    def capacity(self) -> int:
        """
        Get buffer capacity.
        
        Returns:
            int: Maximum buffer size
        """
        return self._max_size
    
    def peek(self, size: Optional[int] = None) -> bytes:
        """
        Peek at buffer data without removing it.
        
        Args:
            size: Number of bytes to peek (None = all available)
            
        Returns:
            bytes: Data from buffer (not removed)
        """
        with self._lock:
            if not self._buffer:
                return b''
            
            if size is None:
                # Return all data
                return b''.join(self._buffer)
            
            if size <= 0:
                return b''
            
            # Collect data chunks until we have enough
            result_chunks = []
            bytes_collected = 0
            
            for chunk in self._buffer:
                chunk_size = len(chunk)
                
                if bytes_collected + chunk_size <= size:
                    # Take entire chunk
                    result_chunks.append(chunk)
                    bytes_collected += chunk_size
                else:
                    # Take partial chunk
                    needed = size - bytes_collected
                    result_chunks.append(chunk[:needed])
                    bytes_collected += needed
                    break
            
            return b''.join(result_chunks)
    
    def is_empty(self) -> bool:
        """
        Check if buffer is empty.
        
        Returns:
            bool: True if buffer contains no data
        """
        with self._lock:
            return self._current_size == 0
    
    def is_full(self) -> bool:
        """
        Check if buffer is at capacity.
        
        Returns:
            bool: True if buffer is at maximum capacity
        """
        with self._lock:
            return self._current_size >= self._max_size
    
    def utilization_percent(self) -> float:
        """
        Get buffer utilization percentage.
        
        Returns:
            float: Percentage of buffer capacity in use (0.0-100.0)
        """
        with self._lock:
            return (self._current_size / self._max_size) * 100.0
    
    def set_overflow_callback(self, callback: Optional[Callable[[int, int], None]]) -> None:
        """
        Set callback for buffer overflow events.
        
        Args:
            callback: Function called when overflow occurs (overflow_bytes, buffer_size)
        """
        with self._lock:
            self._overflow_callback = callback
            logger.debug(f"Overflow callback {'set' if callback else 'cleared'}")
    
    def get_stats(self) -> dict:
        """
        Get buffer statistics.
        
        Returns:
            dict: Buffer statistics including usage and overflow info
        """
        with self._lock:
            return {
                'current_size': self._current_size,
                'max_size': self._max_size,
                'utilization_percent': self.utilization_percent(),
                'is_empty': self.is_empty(),
                'is_full': self.is_full(),
                'bytes_added': self._bytes_added,
                'bytes_retrieved': self._bytes_retrieved,
                'overflow_count': self._overflow_count,
                'overflow_bytes': self._overflow_bytes,
                'last_overflow': self._last_overflow,
                'chunks_count': len(self._buffer)
            }
    
    def resize(self, new_size: int) -> None:
        """
        Resize buffer capacity.
        
        Args:
            new_size: New maximum buffer size
            
        Note: If new size is smaller, oldest data may be discarded
        """
        if new_size <= 0:
            raise ValueError("Buffer size must be positive")
        
        with self._lock:
            old_size = self._max_size
            self._max_size = new_size
            
            # If buffer is now too large, trim it
            overflow_bytes = 0
            while self._current_size > self._max_size and self._buffer:
                old_chunk = self._buffer.popleft()
                old_chunk_size = len(old_chunk)
                self._current_size -= old_chunk_size
                overflow_bytes += old_chunk_size
            
            if overflow_bytes > 0:
                self._overflow_count += 1
                self._overflow_bytes += overflow_bytes
                self._last_overflow = time.time()
                
                logger.warning(
                    f"Buffer resize overflow: dropped {overflow_bytes} bytes "
                    f"(new size: {self._current_size}/{self._max_size})"
                )
                
                # Call overflow callback
                if self._overflow_callback:
                    try:
                        self._overflow_callback(overflow_bytes, self._max_size)
                    except Exception as e:
                        logger.error(f"Error in overflow callback during resize: {e}")
            
            logger.info(f"Buffer resized from {old_size} to {new_size} bytes")