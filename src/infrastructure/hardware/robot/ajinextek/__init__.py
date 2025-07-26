"""
AJINEXTEK Robot Service

Hardware implementation for AJINEXTEK robot controllers using AXL library.
"""

try:
    from infrastructure.hardware.robot.ajinextek.ajinextek_robot_adapter import AjinextekRobotAdapter
    from infrastructure.hardware.robot.ajinextek.axl_wrapper import AXLWrapper
    from infrastructure.hardware.robot.ajinextek.constants import *
    from infrastructure.hardware.robot.ajinextek.error_codes import *
    _AJINEXTEK_AVAILABLE = True
except ImportError as e:
    import warnings
    warnings.warn(f"AJINEXTEK robot service not available: {e}")
    _AJINEXTEK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.extend(['AjinextekRobotAdapter', 'AXLWrapper'])