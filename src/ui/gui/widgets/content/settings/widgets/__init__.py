"""
Settings widgets module.

Provides specialized widget components for the settings interface
including tree view and property editor widgets.
"""

from .property_panel import PropertyEditorWidget
from .tree_widget import SettingsTreeWidget

__all__ = [
    "PropertyEditorWidget",
    "SettingsTreeWidget",
]