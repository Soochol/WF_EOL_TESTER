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

        # Load application info from configuration
        self.app_name = "WF EOL Tester"
        self.app_version = "1.0.0"
        self._load_app_info_from_config()

        self.setup_ui()

    def _load_app_info_from_config(self) -> None:
        """Load application name and version from configuration file"""
        try:
            # Try to read from container configuration first
            if self.container and hasattr(self.container, "_config_dict"):
                config = self.container._config_dict
                if isinstance(config, dict) and "application" in config:
                    app_config = config["application"]
                    if isinstance(app_config, dict):
                        self.app_name = app_config.get("name", self.app_name)
                        self.app_version = app_config.get("version", self.app_version)
                    return

            # Fallback: read directly from YAML file
            # Standard library imports
            from pathlib import Path

            # Third-party imports
            import yaml

            config_path = Path("configuration/application.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    if config_data and "application" in config_data:
                        self.app_name = config_data["application"].get("name", self.app_name)
                        self.app_version = config_data["application"].get(
                            "version", self.app_version
                        )
        except Exception as e:
            # Use default values if loading fails
            print(f"Failed to load app info from config: {e}")

    def setup_ui(self) -> None:
        """Setup simple about page UI"""
        # Set widget background
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
        """
        )

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

        # Application Title (from configuration)
        title_label = QLabel(self.app_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            """
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
        """
        )
        layout.addWidget(title_label)

        # Version Info (from configuration)
        version_label = QLabel(f"Version {self.app_version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(
            """
            font-size: 18px;
            color: #0078d4;
            margin-bottom: 30px;
        """
        )
        layout.addWidget(version_label)

        # Description
        description_label = QLabel("End-of-Line Testing Application")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet(
            """
            font-size: 16px;
            color: #cccccc;
            margin-bottom: 30px;
        """
        )
        layout.addWidget(description_label)

        # System Information
        system_info = self.get_system_info()
        system_label = QLabel(system_info)
        system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_label.setStyleSheet(
            """
            font-size: 14px;
            color: #888888;
            line-height: 1.5;
            margin-bottom: 30px;
        """
        )
        layout.addWidget(system_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #404040; margin: 20px 0;")
        layout.addWidget(separator)

        # Copyright
        copyright_label = QLabel("© 2024 WF Technologies. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet(
            """
            font-size: 12px;
            color: #666666;
        """
        )
        layout.addWidget(copyright_label)

        # Add stretch to center content
        layout.addStretch()

    def get_system_info(self) -> str:
        """Get basic system information"""
        try:
            python_version = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
            system_info = f"Python {python_version} | {platform.system()} {platform.release()}"
            return system_info
        except Exception:
            return "System information unavailable"
