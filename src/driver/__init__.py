"""
Hardware Driver Module

This module contains hardware drivers for various components.
Drivers are low-level modules that handle direct hardware communication.
"""

# Import drivers conditionally to avoid dependency issues
__all__ = []

try:
    # Local application imports
    from driver.serial import SerialManager

    __all__.append("SerialManager")
except ImportError:
    ...

try:
    # Local application imports
    from driver.tcp import TCPCommunication

    __all__.append("TCPCommunication")
except ImportError:
    ...
