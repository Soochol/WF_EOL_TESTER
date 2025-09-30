"""
Editor factory for creating appropriate editor widgets.

Provides factory methods to create the correct editor widget
based on configuration value type and constraints.
"""

# Standard library imports
from typing import Any, Callable, Optional

# Third-party imports
from PySide6.QtWidgets import QWidget

# Local folder imports
from ...core import ConfigValue
from .base_editor import BaseEditorWidget
from .boolean_editor import BooleanEditorWidget
from .combo_editor import ComboEditorWidget
from .numeric_editor import NumericEditorWidget
from .text_editor import TextEditorWidget


class EditorFactory:
    """Factory for creating configuration value editors"""

    @staticmethod
    def create_editor(
        config_value: ConfigValue,
        value_changed_callback: Callable[[Any], None],
        parent: Optional[QWidget] = None,
    ) -> Optional[BaseEditorWidget]:
        """
        Create appropriate editor widget for configuration value.

        Args:
            config_value: Configuration value to edit
            value_changed_callback: Callback for value changes
            parent: Parent widget

        Returns:
            Editor widget or None if no suitable editor found
        """
        # Check for allowed values first (combo box)
        if config_value.allowed_values and len(config_value.allowed_values) > 1:
            return ComboEditorWidget(config_value, value_changed_callback, parent)

        # Type-specific editors
        data_type = config_value.data_type.lower()

        if data_type == "bool":
            return BooleanEditorWidget(config_value, value_changed_callback, parent)
        elif data_type in ("int", "float"):
            return NumericEditorWidget(config_value, value_changed_callback, parent)
        elif data_type == "str":
            return TextEditorWidget(config_value, value_changed_callback, parent)

        # Fallback to text editor for unknown types
        return TextEditorWidget(config_value, value_changed_callback, parent)

    @staticmethod
    def get_editor_type(config_value: ConfigValue) -> str:
        """
        Get the editor type name for a configuration value.

        Args:
            config_value: Configuration value

        Returns:
            Editor type name
        """
        if config_value.allowed_values and len(config_value.allowed_values) > 1:
            return "combo"

        data_type = config_value.data_type.lower()
        if data_type == "bool":
            return "boolean"
        elif data_type in ("int", "float"):
            return "numeric"
        elif data_type == "str":
            return "text"

        return "text"  # fallback
