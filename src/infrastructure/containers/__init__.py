"""
Dependency Injection Containers

Modern dependency injection containers using dependency-injector library.
Replaces the custom DI implementation with a robust, feature-rich solution.
"""

from .application_container import ApplicationContainer
from .hardware_container import HardwareContainer

__all__ = [
    "ApplicationContainer",
    "HardwareContainer",
]