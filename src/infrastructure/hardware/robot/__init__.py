"""
Robot Hardware Implementations

Hardware implementations for robot control systems.
"""

# Import specific implementations
try:
    from infrastructure.hardware.robot.ajinextek import AjinextekRobotAdapter
    _AJINEXTEK_AVAILABLE = True
except ImportError:
    _AJINEXTEK_AVAILABLE = False

try:
    from infrastructure.hardware.robot.mock import MockRobotAdapter
    _MOCK_AVAILABLE = True
except ImportError:
    _MOCK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.append('AjinextekRobotAdapter')

if _MOCK_AVAILABLE:
    __all__.append('MockRobotAdapter')