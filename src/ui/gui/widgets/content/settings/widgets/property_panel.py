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
from ..core import Colors, ConfigValidator, ConfigValue


class PropertyEditorWidget(QWidget):
    """Property editor for individual configuration values"""

    value_changed = Signal(str, object)  # key, new_value

    def __init__(self, config_value: ConfigValue, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_value = config_value
        self.editor_widget: Optional[QWidget] = None
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

        key_label = QLabel(f"⚙️ {self.config_value.key}")
        key_label.setStyleSheet(
            f"""
            font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 0.5px;
            color: {Colors.TEXT_PRIMARY};
            border: none;
            background-color: transparent;
            padding: 8px 0;
        """
        )
        header_layout.addWidget(key_label)

        header_layout.addStretch()

        # Modern type badge
        type_label = QLabel(f"  {self.config_value.data_type}  ")
        type_label.setStyleSheet(
            f"""
            font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
            color: {Colors.TEXT_MUTED};
            background-color: rgba(33, 150, 243, 0.2);
            border: 1px solid rgba(33, 150, 243, 0.3);
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
        """
        )
        header_layout.addWidget(type_label)

        layout.addLayout(header_layout)

        # Description if available
        if self.config_value.description:
            # Description header
            desc_header = QLabel("📘 Description")
            desc_header.setStyleSheet(
                f"""
                font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
                font-weight: 600;
                font-size: 13px;
                color: {Colors.TEXT_SECONDARY};
                margin-top: 10px;
                margin-bottom: 5px;
                border: none;
                background-color: transparent;
                """
            )
            layout.addWidget(desc_header)

            # Description content
            desc_label = QLabel(self.config_value.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                f"""
                font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
                line-height: 1.6;
                background-color: rgba(33, 150, 243, 0.08);
                border-left: 3px solid rgba(33, 150, 243, 0.5);
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 15px;
                """
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
        self.validation_label.setStyleSheet(
            "font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif; font-size: 12px; letter-spacing: 0.2px; margin-top: 5px; border: none; background-color: transparent;"
        )
        layout.addWidget(self.validation_label)

        # File path info
        if self.config_value.file_path:
            file_label = QLabel(f"File: {os.path.basename(self.config_value.file_path)}")
            file_label.setStyleSheet(
                f"font-family: 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif; color: {Colors.TEXT_DISABLED}; font-size: 12px; letter-spacing: 0.2px; margin-top: 5px; border: none; background-color: transparent;"
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
                f"""
                color: {Colors.SUCCESS};
                background-color: rgba(0, 217, 165, 0.1);
                border-left: 3px solid {Colors.SUCCESS};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                margin-top: 8px;
                """
            )
        else:
            self.validation_label.setText(f"✗ {error_msg}")
            self.validation_label.setStyleSheet(
                f"""
                color: {Colors.ERROR};
                background-color: rgba(244, 67, 54, 0.1);
                border-left: 3px solid {Colors.ERROR};
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                margin-top: 8px;
                """
            )

        # Update editor widget styling based on validation - modern error highlight
        if self.editor_widget:
            if is_valid:
                # Reset to default style
                self.editor_widget.setStyleSheet("")
            else:
                # Modern error styling
                self.editor_widget.setStyleSheet(
                    f"""
                    border: 2px solid {Colors.ERROR};
                    background-color: rgba(244, 67, 54, 0.05);
                    border-radius: 8px;
                    """
                )
