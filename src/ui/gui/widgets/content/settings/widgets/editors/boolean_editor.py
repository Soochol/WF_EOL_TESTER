"""
Boolean value editor widget.

Provides a checkbox editor for boolean configuration values.
"""

from typing import Any

from PySide6.QtWidgets import QCheckBox, QHBoxLayout

from ...core import Colors
from .base_editor import BaseEditorWidget


class BooleanEditorWidget(BaseEditorWidget):
    """Checkbox editor for boolean values"""

    def setup_ui(self) -> None:
        """Setup boolean editor UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(self.config_value.value))
        self.checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: 14px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {Colors.BORDER};
                background-color: {Colors.BACKGROUND_SECONDARY};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {Colors.PRIMARY_ACCENT};
                background-color: {Colors.PRIMARY_ACCENT};
                border-radius: 3px;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTEzLjg1NCA0LjE0NmEuNS41IDAgMCAxIDAgLjcwOGwtOCA4YS41LjUgMCAwIDEtLjcwOCAwbC00LTRhLjUuNSAwIDEgMSAuNzA4LS43MDhMMy41IDExLjc5M2w3LjY0Ni03LjY0N2EuNS41IDAgMCAxIC43MDggMHoiLz48L3N2Zz4=);
            }}
            QCheckBox::indicator:hover {{
                border-color: {Colors.PRIMARY_ACCENT};
            }}
        """
        )

        layout.addWidget(self.checkbox)
        layout.addStretch()

    def connect_signals(self) -> None:
        """Connect checkbox signals"""
        self.checkbox.toggled.connect(self.on_value_changed)

    def get_value(self) -> bool:
        """Get checkbox value"""
        return self.checkbox.isChecked()

    def set_value(self, value: Any) -> None:
        """Set checkbox value"""
        self.checkbox.setChecked(bool(value))