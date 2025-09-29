"""
UI helper utilities.

Provides common UI operations and helper functions for the settings widget.
"""

# Standard library imports
from typing import Any, Optional

# Third-party imports
from PySide6.QtWidgets import QMessageBox, QWidget

# Local folder imports
from ..core import Colors


class UIHelpers:
    """Utility class for UI operations"""

    @staticmethod
    def show_info_message(parent: QWidget, title: str, message: str) -> None:
        """
        Show an information message box.

        Args:
            parent: Parent widget
            title: Message box title
            message: Message text
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(UIHelpers._get_message_box_style())
        msg_box.exec()

    @staticmethod
    def show_warning_message(parent: QWidget, title: str, message: str) -> None:
        """
        Show a warning message box.

        Args:
            parent: Parent widget
            title: Message box title
            message: Message text
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(UIHelpers._get_message_box_style())
        msg_box.exec()

    @staticmethod
    def show_error_message(parent: QWidget, title: str, message: str) -> None:
        """
        Show an error message box.

        Args:
            parent: Parent widget
            title: Message box title
            message: Message text
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(UIHelpers._get_message_box_style())
        msg_box.exec()

    @staticmethod
    def show_confirmation_dialog(parent: QWidget, title: str, message: str) -> bool:
        """
        Show a confirmation dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message text

        Returns:
            True if user confirmed, False otherwise
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet(UIHelpers._get_message_box_style())

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def format_value_display(value: Any, max_length: int = 50) -> str:
        """
        Format a value for display in UI.

        Args:
            value: Value to format
            max_length: Maximum display length

        Returns:
            Formatted string
        """
        if isinstance(value, bool):
            return "✓" if value else "✗"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if len(value) > max_length:
                return f"{value[:max_length]}..."
            return value
        else:
            str_value = str(value)
            if len(str_value) > max_length:
                return f"{str_value[:max_length]}..."
            return str_value

    @staticmethod
    def get_type_display_name(data_type: str) -> str:
        """
        Get user-friendly display name for data type.

        Args:
            data_type: Data type string

        Returns:
            Display-friendly type name
        """
        type_mapping = {
            "str": "Text",
            "int": "Integer",
            "float": "Number",
            "bool": "Boolean",
            "list": "List",
            "dict": "Object",
        }
        return type_mapping.get(data_type.lower(), data_type.capitalize())

    @staticmethod
    def apply_hover_effect(widget: QWidget, hover_color: Optional[str] = None) -> None:
        """
        Apply hover effect to a widget.

        Args:
            widget: Widget to apply effect to
            hover_color: Color to use on hover
        """
        if hover_color is None:
            hover_color = Colors.BACKGROUND_HOVER

        original_style = widget.styleSheet()
        hover_style = f"{original_style}\nQWidget:hover {{ background-color: {hover_color}; }}"
        widget.setStyleSheet(hover_style)

    @staticmethod
    def center_widget_on_parent(widget: QWidget, parent: QWidget) -> None:
        """
        Center a widget on its parent.

        Args:
            widget: Widget to center
            parent: Parent widget
        """
        parent_geo = parent.geometry()
        widget_geo = widget.geometry()

        x = parent_geo.x() + (parent_geo.width() - widget_geo.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - widget_geo.height()) // 2

        widget.move(x, y)

    @staticmethod
    def _get_message_box_style() -> str:
        """Get consistent styling for message boxes"""
        return f"""
        QMessageBox {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
        }}
        QMessageBox QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: 13px;
        }}
        QMessageBox QPushButton {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            border: 2px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            color: {Colors.TEXT_PRIMARY};
            font-size: 12px;
            min-width: 80px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
            border-color: {Colors.PRIMARY_ACCENT};
        }}
        QMessageBox QPushButton:pressed {{
            background-color: {Colors.PRIMARY_ACCENT};
        }}
        """
