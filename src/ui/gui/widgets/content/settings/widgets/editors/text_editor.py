"""
Text value editor widget.

Provides line edit and text edit controls for string configuration values.
"""

# Standard library imports
from typing import Any, Callable, Optional, Union

# Third-party imports
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPlainTextEdit, QWidget

# Local folder imports
from ...core import Colors
from .base_editor import BaseEditorWidget


class TextEditorWidget(BaseEditorWidget):
    """Text editor for string values"""

    def __init__(
        self,
        config_value,
        value_changed_callback: Callable[[Any], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(config_value, value_changed_callback, parent)
        self.text_widget: Union[QLineEdit, QPlainTextEdit]

    def setup_ui(self) -> None:
        """Setup text editor UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        value_str = str(self.config_value.value)

        # Use QPlainTextEdit for multi-line text, QLineEdit for single line
        if "\n" in value_str or len(value_str) > 100:
            self.text_widget = QPlainTextEdit()
            self.text_widget.setPlainText(value_str)
            self.text_widget.setMaximumHeight(100)
        else:
            self.text_widget = QLineEdit()
            self.text_widget.setText(value_str)

        # Common styling
        self.text_widget.setStyleSheet(
            f"""
            QLineEdit, QPlainTextEdit {{
                border: 2px solid {Colors.BORDER};
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border-color: {Colors.PRIMARY_ACCENT};
            }}
            QLineEdit:hover, QPlainTextEdit:hover {{
                border-color: {Colors.BORDER_HOVER};
            }}
        """
        )

        layout.addWidget(self.text_widget)

    def connect_signals(self) -> None:
        """Connect text widget signals"""
        if isinstance(self.text_widget, QLineEdit):
            self.text_widget.textChanged.connect(self.on_value_changed)
        else:
            self.text_widget.textChanged.connect(self.on_value_changed)

    def get_value(self) -> str:
        """Get text value"""
        if isinstance(self.text_widget, QLineEdit):
            return self.text_widget.text()
        else:
            return self.text_widget.toPlainText()

    def set_value(self, value: Any) -> None:
        """Set text value"""
        value_str = str(value)
        if isinstance(self.text_widget, QLineEdit):
            self.text_widget.setText(value_str)
        else:
            self.text_widget.setPlainText(value_str)
