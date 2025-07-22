"""
Core serial communication components.

This module contains the essential building blocks for serial communication:
- Interfaces defining component contracts
- Transport layer for low-level communication
- Buffer management for data handling
- Background reading capabilities
"""

from .interfaces import (
    ISerialTransport, ISerialBuffer, ISerialReader,
    IRetryManager, IHealthMonitor, IAsyncAdapter
)
from .transport import SerialTransport
from .buffer import SerialBuffer
from .reader import SerialReader

__all__ = [
    # Interfaces
    'ISerialTransport',
    'ISerialBuffer',
    'ISerialReader',
    'IRetryManager',
    'IHealthMonitor', 
    'IAsyncAdapter',
    
    # Implementations
    'SerialTransport',
    'SerialBuffer',
    'SerialReader'
]