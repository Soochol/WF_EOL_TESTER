"""Reusable information card component"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class InfoCard(QFrame):
    """Reusable information card component"""

    def __init__(self, title: str, content: str, icon: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui(title, content, icon)

    def setup_ui(self, title: str, content: str, icon: str) -> None:
        """Setup the card UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(
            """
            InfoCard {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            InfoCard:hover {
                border-color: #0078d4;
                background-color: #333333;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title with icon
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            title_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # Content
        content_label = QLabel(content)
        content_label.setStyleSheet(
            """
            color: #cccccc;
            font-size: 14px;
            line-height: 1.4;
        """
        )
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
