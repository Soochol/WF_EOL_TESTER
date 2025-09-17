"""
AJINEXTEK Robot Service

Hardware implementation for AJINEXTEK robot controllers using AXL library.
"""

try:
    # Local application imports
    from infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
        AjinextekRobot,
    )
    from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import AXLWrapper
    from infrastructure.implementation.hardware.robot.ajinextek.constants import *
    from infrastructure.implementation.hardware.robot.ajinextek.error_codes import *

    _AJINEXTEK_AVAILABLE = True
except ImportError as e:
    # Standard library imports
    import warnings

    warnings.warn(f"AJINEXTEK robot service not available: {e}")
    _AJINEXTEK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.extend(["AjinextekRobot", "AXLWrapper"])
