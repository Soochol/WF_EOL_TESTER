"""
AJINEXTEK Robot Service

Hardware implementation for AJINEXTEK robot controllers using AXL library.
"""

try:
    from .ajinextek_robot import AjinextekRobot
    from .axl_wrapper import AXLWrapper
    from .constants import *
    from .error_codes import *

    _AJINEXTEK_AVAILABLE = True
except ImportError as e:
    import warnings

    warnings.warn(f"AJINEXTEK robot service not available: {e}")
    _AJINEXTEK_AVAILABLE = False

__all__ = []

if _AJINEXTEK_AVAILABLE:
    __all__.extend(["AjinextekRobot", "AXLWrapper"])
