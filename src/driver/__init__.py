"""
Hardware Driver Module

This module contains hardware drivers for various components.
Drivers are low-level modules that handle direct hardware communication.
"""

from .serial import SerialManager

__all__ = [
    'SerialManager'
]