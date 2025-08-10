"""
API route modules
"""

from .config import router as config_router
from .hardware import router as hardware_router
from .status import router as status_router
from .test import router as test_router
from .websocket import router as websocket_router

__all__ = [
    "hardware_router",
    "test_router", 
    "config_router",
    "status_router",
    "websocket_router",
]
