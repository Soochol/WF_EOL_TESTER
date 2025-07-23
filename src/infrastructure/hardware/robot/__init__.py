"""
Robot Hardware Implementations

Hardware implementations for robot control systems.
"""

# Import specific implementations
try:
    from infrastructure.hardware.robot.ajinextek import AjinextekRobotService
    _AJINEXTEK_AVAILABLE = True
except ImportError:
    _AJINEXTEK_AVAILABLE = False

try:
    from infrastructure.hardware.robot.mock import MockRobotService
    _MOCK_AVAILABLE = True
except ImportError:
    _MOCK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.append('AjinextekRobotService')

if _MOCK_AVAILABLE:
    __all__.append('MockRobotService')