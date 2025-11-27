"""
Settings core module.

Contains core data structures, validation logic, and constants
for the settings system.
"""

from .config_file import ConfigFile, ConfigPaths, ConfigValue
from .constants import Colors, EditorTypes, Styles, TreeIcons, UIConstants, ValidationRules
from .validator import ConfigValidator

__all__ = [
    # Data structures
    "ConfigFile",
    "ConfigValue",
    "ConfigPaths",

    # Constants and styling
    "UIConstants",
    "Colors",
    "Styles",
    "ValidationRules",
    "EditorTypes",
    "TreeIcons",

    # Validation
    "ConfigValidator",
]