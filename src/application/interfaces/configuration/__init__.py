"""
Configuration Interfaces

Abstract interfaces for configuration and preference management.
"""

from .configuration import Configuration
from .profile_preference import ProfilePreference

__all__ = [
    'Configuration',
    'ProfilePreference'
]
