"""
Integration Layer Package

Contains dependency injection configuration and application composition root.
"""

from .dependency_injection import DependencyContainer
from .application_factory import ApplicationFactory

__all__ = [
    'DependencyContainer',
    'ApplicationFactory'
]