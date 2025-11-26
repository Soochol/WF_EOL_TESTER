"""
Combo box editor widget.

Provides dropdown selection for configuration values with predefined options.
"""

# Standard library imports
from typing import Any

# Third-party imports
from PySide6.QtWidgets import QComboBox, QHBoxLayout

# Local folder imports
from ...core import Colors
from .base_editor import BaseEditorWidget


class ComboEditorWidget(BaseEditorWidget):
    """Combo box editor for values with allowed options - saves immediately on selection"""

    # Immediate save: dropdown selection is applied instantly
    IMMEDIATE_SAVE = True

    def setup_ui(self) -> None:
        """Setup combo box editor UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.combo_box = QComboBox()

        # Add allowed values if available
        if self.config_value.allowed_values:
            for value in self.config_value.allowed_values:
                self.combo_box.addItem(str(value), value)

            # Set current value
            current_text = str(self.config_value.value)
            index = self.combo_box.findText(current_text)
            if index >= 0:
                self.combo_box.setCurrentIndex(index)
        else:
            # If no allowed values, add current value
            self.combo_box.addItem(str(self.config_value.value), self.config_value.value)

        # Styling
        self.combo_box.setStyleSheet(
            f"""
            QComboBox {{
                border: 2px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                min-width: 150px;
            }}
            QComboBox:focus {{
                border-color: {Colors.PRIMARY_ACCENT};
            }}
            QComboBox:hover {{
                border-color: {Colors.BORDER_HOVER};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {Colors.BORDER};
                background-color: {Colors.TERTIARY_BACKGROUND};
            }}
            QComboBox::down-arrow {{
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTEyIDZsLTQgNC00LTQgOCAweiIvPjwvc3ZnPg==);
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                border: 2px solid {Colors.BORDER};
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.PRIMARY_ACCENT};
                outline: none;
            }}
        """
        )

        layout.addWidget(self.combo_box)
        layout.addStretch()

    def connect_signals(self) -> None:
        """Connect combo box signals"""
        self.combo_box.currentTextChanged.connect(self.on_value_changed)

    def get_value(self) -> Any:
        """Get combo box value"""
        return self.combo_box.currentData()

    def set_value(self, value: Any) -> None:
        """Set combo box value"""
        text = str(value)
        index = self.combo_box.findText(text)
        if index >= 0:
            self.combo_box.setCurrentIndex(index)
