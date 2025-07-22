"""
Background serial reading implementation.

Provides thread-safe background reading with callback support and error handling.
Focuses solely on continuous data reading from transport layer.
"""

import threading
import time
from typing import Callable, Optional

from loguru import logger

from .interfaces import ISerialReader, ISerialTransport, ISerialBuffer
from ..exceptions import SerialCommunicationError


class SerialReader(ISerialReader):
    """Background serial reader with callback support."""
    
    def __init__(self, transport: ISerialTransport, buffer: ISerialBuffer, 
                 read_interval: float = 0.01):
        """
        Initialize reader with transport and buffer.
        
        Args:
            transport: Serial transport for reading data
            buffer: Buffer for storing read data
            read_interval: Interval between read attempts in seconds
        """
        self._transport = transport
        self._buffer = buffer
        self._read_interval = max(0.001, read_interval)  # Minimum 1ms
        
        # Threading
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._thread_lock = threading.RLock()
        
        # Callbacks
        self._data_callback: Optional[Callable[[bytes], None]] = None
        self._error_callback: Optional[Callable[[Exception], None]] = None
        
        # Statistics
        self._bytes_read = 0
        self._read_operations = 0
        self._error_count = 0
        self._start_time: Optional[float] = None
        self._last_read_time: Optional[float] = None
    
    def start_reading(self) -> None:
        """Start background reading thread."""
        with self._thread_lock:
            if self._running:
                logger.warning("Reader is already running")
                return
            
            if not self._transport.is_connected():
                raise SerialCommunicationError(
                    "Cannot start reading: transport not connected",
                    operation="start_reading"
                )
            
            self._stop_event.clear()
            self._running = True
            self._start_time = time.time()
            
            self._read_thread = threading.Thread(
                target=self._read_worker,
                name="SerialReader",
                daemon=True
            )
            self._read_thread.start()
            
            logger.info(f"Started background reading (interval: {self._read_interval}s)")
    
    def stop_reading(self) -> None:
        """Stop background reading thread."""
        with self._thread_lock:
            if not self._running:
                logger.debug("Reader is not running")
                return
            
            logger.info("Stopping background reading...")
            self._stop_event.set()
            self._running = False
            
            # Wait for thread to complete
            if self._read_thread and self._read_thread.is_alive():
                self._read_thread.join(timeout=2.0)
                
                if self._read_thread.is_alive():
                    logger.warning("Read thread did not stop cleanly")
                else:
                    logger.info("Background reading stopped")
            
            self._read_thread = None
    
    def is_reading(self) -> bool:
        """
        Check if background reading is active.
        
        Returns:
            bool: True if reading thread is running
        """
        with self._thread_lock:
            return (self._running and 
                    self._read_thread is not None and 
                    self._read_thread.is_alive())
    
    def set_data_callback(self, callback: Optional[Callable[[bytes], None]]) -> None:
        """
        Set callback for received data.
        
        Args:
            callback: Function called when data is received
        """
        with self._thread_lock:
            self._data_callback = callback
            logger.debug(f"Data callback {'set' if callback else 'cleared'}")
    
    def set_error_callback(self, callback: Optional[Callable[[Exception], None]]) -> None:
        """
        Set callback for read errors.
        
        Args:
            callback: Function called when read error occurs
        """
        with self._thread_lock:
            self._error_callback = callback
            logger.debug(f"Error callback {'set' if callback else 'cleared'}")
    
    def configure_timing(self, read_interval: float) -> None:
        """
        Configure read timing parameters.
        
        Args:
            read_interval: Interval between read attempts in seconds
        """
        if read_interval <= 0:
            raise ValueError("Read interval must be positive")
        
        with self._thread_lock:
            old_interval = self._read_interval
            self._read_interval = max(0.001, read_interval)
            
            logger.info(f"Read interval changed from {old_interval}s to {self._read_interval}s")
    
    def get_stats(self) -> dict:
        """
        Get reader statistics.
        
        Returns:
            dict: Reader statistics and performance metrics
        """
        with self._thread_lock:
            current_time = time.time()
            uptime = current_time - self._start_time if self._start_time else 0
            
            # Calculate rates
            read_rate = self._read_operations / uptime if uptime > 0 else 0
            byte_rate = self._bytes_read / uptime if uptime > 0 else 0
            error_rate = self._error_count / uptime if uptime > 0 else 0
            
            return {
                'running': self.is_reading(),
                'uptime_seconds': uptime,
                'read_interval': self._read_interval,
                'bytes_read': self._bytes_read,
                'read_operations': self._read_operations,
                'error_count': self._error_count,
                'last_read_time': self._last_read_time,
                'read_rate_per_second': read_rate,
                'byte_rate_per_second': byte_rate,
                'error_rate_per_second': error_rate,
                'thread_alive': self._read_thread.is_alive() if self._read_thread else False
            }
    
    def _read_worker(self) -> None:
        """
        Background reading worker thread.
        
        Continuously reads data from transport and adds to buffer.
        """
        logger.debug("Read worker thread started")
        
        try:
            while not self._stop_event.is_set():
                try:
                    # Check if transport is still connected
                    if not self._transport.is_connected():
                        logger.warning("Transport disconnected, stopping reader")
                        break
                    
                    # Attempt to read available data
                    if hasattr(self._transport, 'is_data_available'):
                        if not self._transport.is_data_available():
                            self._stop_event.wait(self._read_interval)
                            continue
                    
                    # Read available data
                    if hasattr(self._transport, 'read_available'):
                        data = self._transport.read_available()
                    else:
                        # Fallback to regular read with small size
                        data = self._transport.read(1024)
                    
                    self._read_operations += 1
                    self._last_read_time = time.time()
                    
                    if data:
                        self._bytes_read += len(data)
                        
                        # Add to buffer
                        self._buffer.add_data(data)
                        
                        # Call data callback
                        if self._data_callback:
                            try:
                                self._data_callback(data)
                            except Exception as e:
                                logger.error(f"Error in data callback: {e}")
                        
                        logger.debug(f"Read {len(data)} bytes from transport")
                    
                    # Wait before next read
                    if not self._stop_event.is_set():
                        self._stop_event.wait(self._read_interval)
                
                except Exception as e:
                    self._error_count += 1
                    logger.error(f"Error in read worker: {e}")
                    
                    # Call error callback
                    if self._error_callback:
                        try:
                            self._error_callback(e)
                        except Exception as callback_error:
                            logger.error(f"Error in error callback: {callback_error}")
                    
                    # For connection errors, stop reading
                    if isinstance(e, SerialCommunicationError):
                        logger.warning("Communication error in reader, stopping")
                        break
                    
                    # For other errors, wait and continue
                    if not self._stop_event.is_set():
                        self._stop_event.wait(self._read_interval * 2)
        
        except Exception as e:
            logger.error(f"Fatal error in read worker: {e}")
        
        finally:
            with self._thread_lock:
                self._running = False
            logger.debug("Read worker thread stopped")
    
    def force_read(self, size: Optional[int] = None) -> bytes:
        """
        Force immediate read from transport (bypassing background reading).
        
        Args:
            size: Number of bytes to read
            
        Returns:
            bytes: Data read from transport
            
        Raises:
            SerialCommunicationError: If read fails
        """
        if not self._transport.is_connected():
            raise SerialCommunicationError(
                "Cannot read: transport not connected",
                operation="force_read"
            )
        
        try:
            data = self._transport.read(size)
            
            if data:
                # Update statistics
                with self._thread_lock:
                    self._bytes_read += len(data)
                    self._read_operations += 1
                    self._last_read_time = time.time()
                
                # Add to buffer if not already done by background reader
                if not self.is_reading():
                    self._buffer.add_data(data)
                
                logger.debug(f"Force read {len(data)} bytes")
            
            return data
        
        except Exception as e:
            with self._thread_lock:
                self._error_count += 1
            
            logger.error(f"Force read failed: {e}")
            raise SerialCommunicationError(
                f"Force read failed: {e}",
                operation="force_read"
            )
    
    def __enter__(self):
        """Context manager entry."""
        if self._transport.is_connected():
            self.start_reading()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_reading()