"""
About Widget

Simple single-page about information for WF EOL Tester application.
"""

# Standard library imports
import platform
import sys
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class AboutWidget(QWidget):
    """
    Simple About page for WF EOL Tester application
    """

    def __init__(
        self,
        container: Optional[ApplicationContainer] = None,
        state_manager: Optional[GUIStateManager] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup simple about page UI"""
        # Set widget background
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Application Logo/Icon
        logo_label = QLabel("🔧")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 64px; margin-bottom: 20px;")
        layout.addWidget(logo_label)

        # Application Title
        title_label = QLabel("WF EOL Tester")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Version Info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 18px;
            color: #0078d4;
            margin-bottom: 30px;
        """)
        layout.addWidget(version_label)

        # Description
        description_label = QLabel("End-of-Line Testing Application")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet("""
            font-size: 16px;
            color: #cccccc;
            margin-bottom: 30px;
        """)
        layout.addWidget(description_label)

        # System Information
        system_info = self.get_system_info()
        system_label = QLabel(system_info)
        system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_label.setStyleSheet("""
            font-size: 14px;
            color: #888888;
            line-height: 1.5;
            margin-bottom: 30px;
        """)
        layout.addWidget(system_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #404040; margin: 20px 0;")
        layout.addWidget(separator)

        # Copyright
        copyright_label = QLabel("© 2024 WF Technologies. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            font-size: 12px;
            color: #666666;
        """)
        layout.addWidget(copyright_label)

        # Add stretch to center content
        layout.addStretch()

    def get_system_info(self) -> str:
        """Get basic system information"""
        try:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            system_info = f"Python {python_version} | {platform.system()} {platform.release()}"
            return system_info
        except Exception:
            return "System information unavailable"
