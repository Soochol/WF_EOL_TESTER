"""
Property editor panel for individual configuration values.

Provides a panel for editing configuration values with appropriate
editor widgets and validation feedback.
"""

# Standard library imports
import os
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

# Local folder imports
from ..core import Colors, ConfigValidator, ConfigValue, Styles


class PropertyEditorWidget(QWidget):
    """Property editor for individual configuration values"""

    value_changed = Signal(str, object)  # key, new_value

    def __init__(self, config_value: ConfigValue, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_value = config_value
        self.editor_widget = None
        self.validator = ConfigValidator()
        self.setup_ui()
        self.validate_current_value()

    def setup_ui(self) -> None:
        """Setup property editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header with key name and type
        header_layout = QHBoxLayout()

        key_label = QLabel(self.config_value.key)
        key_label.setStyleSheet(
            f"""
            font-weight: bold;
            font-size: 14px;
            color: {Colors.TEXT_PRIMARY};
            border: none;
            background-color: transparent;
        """
        )
        header_layout.addWidget(key_label)

        header_layout.addStretch()

        type_label = QLabel(f"({self.config_value.data_type})")
        type_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; border: none; background-color: transparent;")
        header_layout.addWidget(type_label)

        layout.addLayout(header_layout)

        # Description if available
        if self.config_value.description:
            desc_label = QLabel(self.config_value.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; margin-bottom: 10px; border: none; background-color: transparent;"
            )
            layout.addWidget(desc_label)

        # Editor widget will be created by subclasses or factory
        # This is a placeholder for the basic implementation
        self.editor_widget = self._create_basic_editor()
        if self.editor_widget:
            layout.addWidget(self.editor_widget)

        # Validation status
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("font-size: 11px; margin-top: 5px; border: none; background-color: transparent;")
        layout.addWidget(self.validation_label)

        # File path info
        if self.config_value.file_path:
            file_label = QLabel(f"File: {os.path.basename(self.config_value.file_path)}")
            file_label.setStyleSheet(
                f"color: {Colors.TEXT_DISABLED}; font-size: 11px; margin-top: 5px; border: none; background-color: transparent;"
            )
            layout.addWidget(file_label)

        layout.addStretch()

    def _create_basic_editor(self) -> Optional[QWidget]:
        """Create a basic editor widget - to be overridden by specific editors"""
        # This is a placeholder - actual implementation will use editor factory
        # Local folder imports
        from ..widgets.editors import EditorFactory

        return EditorFactory.create_editor(self.config_value, self.emit_value_changed)

    def emit_value_changed(self, new_value) -> None:
        """Emit value changed signal"""
        # For bool values, ensure they are actually bool type
        if self.config_value.data_type == "bool" and not isinstance(new_value, bool):
            new_value = bool(new_value)

        self.config_value.value = new_value
        self.config_value.is_modified = True
        self.validate_current_value()
        self.value_changed.emit(self.config_value.key, new_value)

    def validate_current_value(self) -> None:
        """Validate the current value and update UI"""
        is_valid, error_msg = self.validator.validate(
            self.config_value.key, self.config_value.value
        )

        self.config_value.is_valid = is_valid
        self.config_value.validation_error = error_msg

        if is_valid:
            self.validation_label.setText("✓ Valid")
            self.validation_label.setStyleSheet(
                f"color: {Colors.SUCCESS}; font-size: 11px; margin-top: 5px; border: none; background-color: transparent;"
            )
        else:
            self.validation_label.setText(f"✗ {error_msg}")
            self.validation_label.setStyleSheet(
                f"color: {Colors.ERROR}; font-size: 11px; margin-top: 5px; border: none; background-color: transparent;"
            )

        # Update editor widget styling based on validation
        if self.editor_widget:
            if is_valid:
                self.editor_widget.setStyleSheet("")
            else:
                self.editor_widget.setStyleSheet(
                    f"border: 1px solid {Colors.ERROR}; background-color: #4d2d2d;"
                )
