"""
Hardware Facade Package

Contains the unified HardwareServiceFacade that integrates all hardware functionality.
All hardware operations are coordinated through the facade for simplicity and maintainability.
"""

from .hardware_service_facade import HardwareServiceFacade

__all__ = ["HardwareServiceFacade"]