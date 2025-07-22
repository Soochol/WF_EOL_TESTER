"""
Async adapter implementation for serial communication.

Provides async/await support for serial operations using asyncio.
Focuses solely on adapting synchronous operations to async context.
"""

import asyncio
import concurrent.futures
from typing import Optional

from loguru import logger

from ..core.interfaces import IAsyncAdapter, ISerialTransport, ISerialBuffer, ISerialReader


class AsyncAdapter(IAsyncAdapter):
    """Async/await adapter for serial communication components."""
    
    def __init__(self, transport: ISerialTransport, buffer: ISerialBuffer,
                 reader: Optional[ISerialReader] = None, executor: Optional[concurrent.futures.Executor] = None):
        """
        Initialize async adapter.
        
        Args:
            transport: Serial transport to adapt
            buffer: Buffer to adapt
            reader: Optional reader to adapt
            executor: Optional executor for sync operations (default: ThreadPoolExecutor)
        """
        self._transport = transport
        self._buffer = buffer
        self._reader = reader
        self._executor = executor or concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="AsyncSerial")
        self._own_executor = executor is None  # Track if we own the executor
        
        # Async state
        self._connection_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
    
    async def read_async(self, size: Optional[int] = None) -> bytes:
        """
        Async-compatible read operation.
        
        Args:
            size: Number of bytes to read (None = available data from buffer)
            
        Returns:
            bytes: Data read from buffer or transport
        """
        async with self._read_lock:
            try:
                # First try to get data from buffer
                if size is None:
                    # Get all available data from buffer
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(self._executor, self._buffer.get_data)
                    
                    if data:
                        logger.debug(f"Read {len(data)} bytes from buffer (async)")
                        return data
                
                # If no data in buffer or specific size requested, read from transport
                if self._transport.is_connected():
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        self._executor, 
                        self._transport.read, 
                        size
                    )
                    
                    if data:
                        logger.debug(f"Read {len(data)} bytes from transport (async)")
                    
                    return data
                else:
                    logger.warning("Cannot read: transport not connected")
                    return b''
            
            except Exception as e:
                logger.error(f"Async read failed: {e}")
                raise
    
    async def write_async(self, data: bytes) -> int:
        """
        Async-compatible write operation.
        
        Args:
            data: Data to write
            
        Returns:
            int: Number of bytes written
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        async with self._write_lock:
            try:
                if not self._transport.is_connected():
                    raise ConnectionError("Transport not connected")
                
                loop = asyncio.get_event_loop()
                bytes_written = await loop.run_in_executor(
                    self._executor,
                    self._transport.write,
                    data
                )
                
                logger.debug(f"Wrote {bytes_written} bytes (async)")
                return bytes_written
            
            except Exception as e:
                logger.error(f"Async write failed: {e}")
                raise
    
    async def connect_async(self, port: str, **kwargs) -> None:
        """
        Async-compatible connection.
        
        Args:
            port: Serial port to connect to
            **kwargs: Connection parameters
        """
        async with self._connection_lock:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self._executor,
                    self._transport.connect,
                    port,
                    **kwargs
                )
                
                logger.info(f"Connected to {port} (async)")
            
            except Exception as e:
                logger.error(f"Async connect failed: {e}")
                raise
    
    async def disconnect_async(self) -> None:
        """Async-compatible disconnection."""
        async with self._connection_lock:
            try:
                # Stop reader if running
                if self._reader and self._reader.is_reading():
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        self._executor,
                        self._reader.stop_reading
                    )
                
                # Disconnect transport
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self._executor,
                    self._transport.disconnect
                )
                
                logger.info("Disconnected (async)")
            
            except Exception as e:
                logger.error(f"Async disconnect failed: {e}")
                # Don't re-raise disconnect errors
    
    async def read_until_async(self, terminator: bytes, max_size: Optional[int] = None,
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
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    raise asyncio.TimeoutError(f"Read timeout after {timeout}s")
            
            # Check max size
            if max_size is not None and len(buffer) >= max_size:
                break
            
            # Read more data
            chunk = await self.read_async(1024)
            if not chunk:
                await asyncio.sleep(0.01)  # Small delay to avoid busy waiting
                continue
            
            buffer += chunk
            
            # Check for terminator
            if terminator in buffer:
                # Find terminator position
                pos = buffer.find(terminator) + len(terminator)
                result = buffer[:pos]
                
                # Put remaining data back in buffer
                remaining = buffer[pos:]
                if remaining:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        self._executor,
                        self._buffer.add_data,
                        remaining
                    )
                
                logger.debug(f"Read until terminator: {len(result)} bytes")
                return result
        
        logger.debug(f"Read until max size: {len(buffer)} bytes")
        return buffer
    
    async def write_and_wait_async(self, data: bytes, expected_response_size: int,
                                  timeout: Optional[float] = None) -> bytes:
        """
        Write data and wait for response.
        
        Args:
            data: Data to write
            expected_response_size: Expected response size in bytes
            timeout: Timeout in seconds
            
        Returns:
            bytes: Response data
        """
        # Clear buffer before writing
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._buffer.clear)
        
        # Write data
        await self.write_async(data)
        
        # Wait for response
        start_time = asyncio.get_event_loop().time()
        buffer = b''
        
        while len(buffer) < expected_response_size:
            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    raise asyncio.TimeoutError(f"Response timeout after {timeout}s")
            
            # Read more data
            chunk = await self.read_async(expected_response_size - len(buffer))
            if not chunk:
                await asyncio.sleep(0.01)
                continue
            
            buffer += chunk
        
        logger.debug(f"Write and wait: sent {len(data)} bytes, received {len(buffer)} bytes")
        return buffer[:expected_response_size]
    
    async def flush_async(self) -> None:
        """Async buffer flush operation."""
        try:
            loop = asyncio.get_event_loop()
            
            # Flush transport buffers
            if hasattr(self._transport, 'flush_buffers'):
                await loop.run_in_executor(
                    self._executor,
                    self._transport.flush_buffers
                )
            
            # Clear data buffer
            await loop.run_in_executor(
                self._executor,
                self._buffer.clear
            )
            
            logger.debug("Async flush completed")
        
        except Exception as e:
            logger.error(f"Async flush failed: {e}")
            raise
    
    async def get_stats_async(self) -> dict:
        """Get async adapter and component statistics."""
        try:
            loop = asyncio.get_event_loop()
            
            # Get stats from all components
            transport_stats = await loop.run_in_executor(
                self._executor,
                self._transport.get_stats
            )
            
            buffer_stats = await loop.run_in_executor(
                self._executor,
                self._buffer.get_stats
            )
            
            reader_stats = {}
            if self._reader:
                reader_stats = await loop.run_in_executor(
                    self._executor,
                    self._reader.get_stats
                )
            
            return {
                'async_adapter': {
                    'executor_type': type(self._executor).__name__,
                    'own_executor': self._own_executor
                },
                'transport': transport_stats,
                'buffer': buffer_stats,
                'reader': reader_stats
            }
        
        except Exception as e:
            logger.error(f"Get async stats failed: {e}")
            raise
    
    async def wait_for_data_async(self, min_bytes: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Wait for minimum amount of data to be available.
        
        Args:
            min_bytes: Minimum bytes to wait for
            timeout: Timeout in seconds
            
        Returns:
            bool: True if data is available, False on timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check available data
            loop = asyncio.get_event_loop()
            buffer_size = await loop.run_in_executor(
                self._executor,
                self._buffer.size
            )
            
            if buffer_size >= min_bytes:
                return True
            
            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    return False
            
            # Wait a bit before checking again
            await asyncio.sleep(0.01)
    
    def __enter__(self):
        """Sync context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        if self._own_executor:
            self._executor.shutdown(wait=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_async()
        
        if self._own_executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._executor.shutdown, True)