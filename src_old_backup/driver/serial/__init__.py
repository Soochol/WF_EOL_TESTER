"""
Serial Communication Driver Module

This module provides a component-based serial communication system for hardware communication.
It follows clean architecture principles with separation of concerns and single responsibility.
Located in src/driver/serial/ as a hardware driver component.

The new architecture provides:
- SerialManager: High-level interface for most use cases
- Core components: Transport, Buffer, Reader for specific needs
- Feature components: Retry, Health, AsyncAdapter for optional functionality
- Clean interfaces following SOLID principles
"""

# Main interface for most use cases
from .manager import SerialManager

# Core components for specific needs
from .core import (
    ISerialTransport, ISerialBuffer,
    SerialTransport, SerialBuffer, SerialReader
)

# Feature components for optional functionality
from .features import RetryManager, HealthMonitor, AsyncAdapter

# Exception classes
from .exceptions import (
    SerialDriverError,
    SerialConnectionError,
    SerialCommunicationError,
    SerialTimeoutError,
    SerialBufferError,
    SerialConfigurationError,
    SerialExceptionFactory
)

__all__ = [
    # Main interface
    'SerialManager',
    
    # Core components
    'ISerialTransport',
    'ISerialBuffer', 
    'SerialTransport',
    'SerialBuffer',
    'SerialReader',
    
    # Feature components
    'RetryManager',
    'HealthMonitor',
    'AsyncAdapter',
    
    # Exceptions
    'SerialDriverError',
    'SerialConnectionError',
    'SerialCommunicationError',
    'SerialTimeoutError',
    'SerialBufferError',
    'SerialConfigurationError',
    'SerialExceptionFactory'
]