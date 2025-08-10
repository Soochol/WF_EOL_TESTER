"""
Mock Digital I/O Service alias

Alias for MockDIO to maintain consistency with naming conventions.
"""

from .mock_dio import MockDIO

# Create alias for consistency with other mock implementations
MockDigitalIO = MockDIO

__all__ = ["MockDigitalIO"]
