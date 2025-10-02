"""Modern UI Components for Robot Control

Material Design 3 components adapted from Test Control.
Includes ModernCard, ModernButton, and StatusPill.
"""

# Third-party imports
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider


class ModernCard(QFrame):
    """Glassmorphism card container"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title: str):
        """Setup card UI"""
        self.setStyleSheet(
            """
            ModernCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 12px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                """
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
                background: transparent;
                border: none;
            """
            )
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)


class ModernButton(QPushButton):
    """Material Design 3 button"""

    def __init__(self, text: str, icon_name: str = "", color: str = "primary", parent=None):
        super().__init__(text, parent)
        self.color_type = color
        self.icon_name = icon_name
        self.setup_ui()

    def setup_ui(self):
        """Setup button styling"""
        # Set SVG icon
        if self.icon_name:
            svg_provider = get_svg_icon_provider()
            icon = svg_provider.get_icon(self.icon_name, size=20)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(20, 20))

        # Color schemes
        colors = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #2196F3)",
                "pressed": "#1565C0",
            },
            "success": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00D9A5, stop:1 #00BFA5)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1DE9B6, stop:1 #00D9A5)",
                "pressed": "#00897B",
            },
            "warning": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF9800, stop:1 #F57C00)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFB74D, stop:1 #FF9800)",
                "pressed": "#E65100",
            },
            "danger": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F44336, stop:1 #D32F2F)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF5350, stop:1 #F44336)",
                "pressed": "#B71C1C",
            },
            "secondary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #607D8B, stop:1 #455A64)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #78909C, stop:1 #607D8B)",
                "pressed": "#37474F",
            },
        }

        color_scheme = colors.get(self.color_type, colors["primary"])

        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {color_scheme["bg"]};
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: {color_scheme["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {color_scheme["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: rgba(100, 100, 100, 0.3);
                color: rgba(255, 255, 255, 0.3);
            }}
        """
        )

        self.setCursor(Qt.CursorShape.PointingHandCursor)


class StatusPill(QWidget):
    """Animated status indicator"""

    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.status_text = "Unknown"
        self.status_color = "#cccccc"
        self.setup_ui()

    def setup_ui(self):
        """Setup status pill UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Label (optional)
        if self.label_text:
            label = QLabel(self.label_text)
            label.setStyleSheet(
                """
                font-size: 12px;
                font-weight: 600;
                color: #999999;
            """
            )
            layout.addWidget(label)

        # Status dot
        self.dot_label = QLabel("●")
        self.dot_label.setStyleSheet(f"color: {self.status_color}; font-size: 14px;")
        layout.addWidget(self.dot_label)

        # Status text
        self.text_label = QLabel(self.status_text)
        self.text_label.setStyleSheet(
            """
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
        """
        )
        layout.addWidget(self.text_label)

        layout.addStretch()

        self.update_style()

    def set_status(self, text: str, color: str):
        """Update status"""
        self.status_text = text
        self.status_color = color
        self.text_label.setText(text)
        self.dot_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.update_style()

    def update_style(self):
        """Update pill background"""
        self.setStyleSheet(
            f"""
            StatusPill {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.status_color}20,
                    stop:1 {self.status_color}40);
                border: 1px solid {self.status_color}60;
                border-radius: 20px;
            }}
        """
        )
