"""
System Info Widget

Displays system status information in the sidebar.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SystemInfo(QWidget):
    """
    System information widget for the sidebar.

    Displays current system status including connection status,
    temperature, and time.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_update_timer()

    def setup_ui(self) -> None:
        """Setup the system info UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("SYSTEM INFO")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #888888; padding-bottom: 5px;")
        layout.addWidget(title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #404040;")
        layout.addWidget(separator)

        # Status labels
        self.status_label = self.create_info_label("Status: Initializing")
        self.connection_label = self.create_info_label("Connected: 0/5")
        self.temperature_label = self.create_info_label("Temp: --°C")
        self.time_label = self.create_info_label("Time: --:--:--")

        layout.addWidget(self.status_label)
        layout.addWidget(self.connection_label)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.time_label)

        # Add stretch to push content to top
        layout.addStretch()

    def create_info_label(self, text: str) -> QLabel:
        """Create an info label with consistent styling"""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Normal)
        label.setFont(font)
        label.setStyleSheet(
            """
            QLabel {
                color: #cccccc;
                padding: 2px 0px;
                background: transparent;
            }
        """
        )
        label.setWordWrap(True)
        return label

    def setup_update_timer(self) -> None:
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time_display)
        self.update_timer.start(1000)  # Update every second

    def update_time_display(self) -> None:
        """Update the time display"""
        # Standard library imports
        from datetime import datetime

        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"Time: {current_time}")

    def update_system_status(self, status: str) -> None:
        """Update system status"""
        self.status_label.setText(f"Status: {status}")

    def update_connection_status(self, connected: int, total: int) -> None:
        """Update connection status"""
        self.connection_label.setText(f"Connected: {connected}/{total}")

    def update_temperature(self, temperature: float) -> None:
        """Update temperature display"""
        self.temperature_label.setText(f"Temp: {temperature:.1f}°C")
