"""
Common Styles for Hardware Widgets

Centralized styling definitions for hardware control widgets.
"""

# Third-party imports
from PySide6.QtGui import QFont


class HardwareStyles:
    """Centralized styling for hardware widgets."""

    @staticmethod
    def get_group_font() -> QFont:
        """Get standardized font for group boxes."""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    @staticmethod
    def get_widget_stylesheet() -> str:
        """Get main widget stylesheet."""
        return """
        QWidget {
            background-color: #1e1e1e;
            color: #cccccc;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #404040;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLabel {
            color: #cccccc;
            font-size: 14px;
            font-weight: bold;
        }
        """

    @staticmethod
    def get_button_stylesheet() -> str:
        """Get button-specific stylesheet."""
        return """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: 1px solid #106ebe;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 80px;
            min-height: 30px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
            border: 1px solid #606060;
        }
        """

    @classmethod
    def get_complete_stylesheet(cls) -> str:
        """Get complete stylesheet combining widget and button styles."""
        return cls.get_widget_stylesheet() + cls.get_button_stylesheet()
