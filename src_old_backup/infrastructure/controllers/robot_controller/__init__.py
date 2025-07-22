"""
Robot Controller Package

This package provides concrete implementations for different robot controller manufacturers.
Currently supported controllers:
- AJINEXTEK: Motion control using AXL library
"""

# Import specific controllers
try:
    from .ajinextek import AjinextekRobotController
    from .ajinextek import AXLWrapper
    _AJINEXTEK_AVAILABLE = True
except ImportError:
    _AJINEXTEK_AVAILABLE = False

try:
    from .mock.mock_ajinextek_robot_controller import MockAjinextekRobotController
    _MOCK_AVAILABLE = True
except ImportError:
    _MOCK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.extend([
        'AjinextekRobotController',
        'AXLWrapper',
    ])

if _MOCK_AVAILABLE:
    __all__.append('MockAjinextekRobotController')