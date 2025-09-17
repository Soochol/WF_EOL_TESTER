"""Configuration Package

Provides configuration system for component bindings, environment-specific
configurations, service lifetime management, and interface implementation selection.

Components:
- ComponentConfig: Configuration for component bindings and service lifetimes
- ConfigurationMode: Enumeration for different configuration modes
"""

# Local folder imports
from .component_config import ComponentConfig, ConfigurationMode


__all__ = [
    "ComponentConfig",
    "ConfigurationMode",
]
