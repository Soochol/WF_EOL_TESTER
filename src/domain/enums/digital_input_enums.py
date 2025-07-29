"""
Digital Input Related Enumerations

Digital input/output related enums for pin modes and logic levels.
"""

from enum import Enum


class PinMode(Enum):
    """GPIO 핀 모드"""
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    INPUT_PULLDOWN = "input_pulldown"


class LogicLevel(Enum):
    """로직 레벨"""
    LOW = 0
    HIGH = 1
