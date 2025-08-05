"""Component Factory Package

Provides factory patterns for creating configured components with dependency
resolution and injection, instance lifecycle management, and interface-based
component creation following the Factory design pattern.

Components:
- ComponentFactory: Factory for creating configured components
- CLIComponentFactory: Specialized factory for CLI components
"""

from .component_factory import ComponentFactory, CLIComponentFactory

__all__ = [
    "ComponentFactory",
    "CLIComponentFactory",
]