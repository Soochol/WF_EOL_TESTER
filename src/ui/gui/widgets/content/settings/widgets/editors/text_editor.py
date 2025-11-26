"""
Text value editor widget.

Provides line edit and text edit controls for string configuration values.
Uses deferred save (Focus Lost) - VS Code style.
"""

# Standard library imports
from typing import Any, Callable, Optional, Union

# Third-party imports
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPlainTextEdit, QWidget

# Local folder imports
from ...core import Colors
from .base_editor import BaseEditorWidget


class TextEditorWidget(BaseEditorWidget):
    """Text editor for string values - saves on focus lost"""

    # Deferred save: commit on focus lost, not on every keystroke
    IMMEDIATE_SAVE = False

    def __init__(
        self,
        config_value,
        value_changed_callback: Callable[[Any], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        self.text_widget: Union[QLineEdit, QPlainTextEdit]
        super().__init__(config_value, value_changed_callback, parent)

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
        """Connect text widget signals for deferred save"""
        # Track changes for pending state
        if isinstance(self.text_widget, QLineEdit):
            self.text_widget.textChanged.connect(self.on_value_changed)
            # Commit on Enter or focus lost
            self.text_widget.editingFinished.connect(self._on_editing_finished)
        else:
            self.text_widget.textChanged.connect(self.on_value_changed)
            # QPlainTextEdit doesn't have editingFinished, use event filter
            self.text_widget.installEventFilter(self)

    def _on_editing_finished(self) -> None:
        """Called when QLineEdit loses focus or Enter is pressed"""
        self.commit_pending_changes()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle focus out event for QPlainTextEdit"""
        if obj == self.text_widget and event.type() == QEvent.Type.FocusOut:
            self.commit_pending_changes()
        return super().eventFilter(obj, event)

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
