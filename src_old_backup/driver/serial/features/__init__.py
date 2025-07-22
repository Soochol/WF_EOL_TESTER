"""
Feature components for serial communication.

This module contains optional feature components that extend core functionality:
- Retry logic for resilient operations
- Health monitoring for connection diagnostics
- Async adapters for modern Python applications
"""

from .retry import RetryManager
from .health import HealthMonitor
from .async_adapter import AsyncAdapter

__all__ = [
    'RetryManager',
    'HealthMonitor', 
    'AsyncAdapter'
]