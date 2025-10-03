"""
Header Widget

Professional header bar for the WF EOL Tester GUI application.
Contains branding, status information, and control buttons.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class HeaderSectionWidget(QWidget):
    """
    Base class for header sections with consistent styling
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_base_style()

    def setup_base_style(self) -> None:
        """Setup base styling for header sections"""
        self.setStyleSheet(
            """
            HeaderSectionWidget {
                background-color: transparent;
                border: none;
            }
        """
        )


class BrandingSection(HeaderSectionWidget):
    """
    Left section of header containing company logo, product name, and version
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup branding section UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 10, 5)
        layout.setSpacing(10)

        # Product info container
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Product name
        self.product_label = QLabel("WF EOL Tester")
        self.product_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            margin: 0px;
        """
        )
        info_layout.addWidget(self.product_label)

        layout.addLayout(info_layout)
        layout.addStretch()


class StatusSection(HeaderSectionWidget):
    """
    Center section of header containing system status
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.system_status = "Ready"
        self.status_color = "#00ff00"  # Green
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup status section UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)

        # Center the system status
        layout.addStretch()

        # System status
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)

        self.status_icon_label = QLabel("🟢")
        self.status_icon_label.setStyleSheet("font-size: 14px;")
        status_layout.addWidget(self.status_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel(self.system_status)
        self.status_label.setStyleSheet(
            f"""
            font-size: 14px;
            font-weight: bold;
            color: {self.status_color};
            text-align: center;
        """
        )
        status_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(status_layout)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(100, 6)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """
        )
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def create_separator(self) -> QFrame:
        """Create a vertical separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #404040;")
        separator.setFixedWidth(1)
        return separator

    def set_system_status(self, status: str, color: str = "#00ff00", icon: str = "🟢") -> None:
        """Set the system status display"""
        self.system_status = status
        self.status_color = color
        self.status_label.setText(status)
        self.status_label.setStyleSheet(
            f"""
            font-size: 14px;
            font-weight: bold;
            color: {color};
            text-align: center;
        """
        )
        self.status_icon_label.setText(icon)

    def show_progress(self, value: int = 0) -> None:
        """Show progress bar with value"""
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)

    def hide_progress(self) -> None:
        """Hide progress bar"""
        self.progress_bar.setVisible(False)


class ControlSection(HeaderSectionWidget):
    """
    Right section of header containing user info and settings
    """

    # Signals
    notifications_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_name = "Admin"
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup control section UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 15, 5)
        layout.setSpacing(10)

        layout.addStretch()

        # User info
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)

        user_icon_label = QLabel("👤")
        user_icon_label.setStyleSheet("font-size: 14px; color: #0078d4;")
        user_layout.addWidget(user_icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.user_label = QLabel(self.user_name)
        self.user_label.setStyleSheet(
            """
            font-size: 12px;
            color: #cccccc;
            text-align: center;
        """
        )
        user_layout.addWidget(self.user_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(user_layout)

        # Notifications button
        self.notifications_btn = QPushButton("🔔")
        self.notifications_btn.setFixedSize(35, 35)
        self.notifications_btn.setStyleSheet(self.get_icon_button_style())
        self.notifications_btn.setToolTip("Notifications")
        self.notifications_btn.clicked.connect(self.notifications_clicked.emit)
        layout.addWidget(self.notifications_btn)

    def get_icon_button_style(self) -> str:
        """Get styling for icon buttons"""
        return """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 16px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #555555;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """

    def set_user_name(self, name: str) -> None:
        """Set the user name display"""
        self.user_name = name
        self.user_label.setText(name)


class HeaderWidget(QWidget):
    """
    Main header widget containing all header sections
    """

    # Signals
    notifications_requested = Signal()

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
        self.connect_signals()

    def setup_ui(self) -> None:
        """Setup the main header UI"""
        # Set fixed height for header
        self.setFixedHeight(65)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create sections
        self.branding_section = BrandingSection()
        self.status_section = StatusSection()
        self.control_section = ControlSection()

        # Add sections with proportional sizing
        layout.addWidget(self.branding_section, 3)  # 30%
        layout.addWidget(self.status_section, 4)  # 40%
        layout.addWidget(self.control_section, 3)  # 30%

        # Apply header styling
        self.setStyleSheet(self.get_header_style())

    def get_header_style(self) -> str:
        """Get the main header stylesheet"""
        return """
            HeaderWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #404040;
            }
        """

    def connect_signals(self) -> None:
        """Connect internal signals"""
        self.control_section.notifications_clicked.connect(self.notifications_requested.emit)

    def set_system_status(self, status: str, status_type: str = "normal") -> None:
        """Set system status with type-based styling"""
        status_config = {
            "normal": {"color": "#00ff00", "icon": "🟢"},
            "ready": {"color": "#00ff00", "icon": "🟢"},
            "testing": {"color": "#ffaa00", "icon": "🟡"},
            "warning": {"color": "#ffaa00", "icon": "🟡"},
            "error": {"color": "#ff4444", "icon": "🔴"},
            "emergency": {"color": "#ff0000", "icon": "🔴"},
            "homed": {"color": "#00ddff", "icon": "🏠"},
        }

        config = status_config.get(status_type.lower(), status_config["normal"])
        self.status_section.set_system_status(status, config["color"], config["icon"])

        # Update header background based on status
        self.update_header_background(status_type)

    def update_header_background(self, status_type: str) -> None:
        """Update header background color based on status"""
        backgrounds = {
            "normal": "#2d2d2d",
            "ready": "#2d2d2d",
            "testing": "#2d3d4d",  # Blue tint
            "warning": "#4d3d2d",  # Orange tint
            "error": "#4d2d2d",  # Red tint
            "emergency": "#4d2d2d",  # Red tint
            "homed": "#2d4d4d",  # Cyan tint
        }

        bg_color = backgrounds.get(status_type.lower(), backgrounds["normal"])
        self.setStyleSheet(
            f"""
            HeaderWidget {{
                background-color: {bg_color};
                border-bottom: 1px solid #404040;
            }}
        """
        )

    def show_test_progress(self, progress: int) -> None:
        """Show test progress in header"""
        self.status_section.show_progress(progress)

    def hide_test_progress(self) -> None:
        """Hide test progress display"""
        self.status_section.hide_progress()

    def set_user_name(self, name: str) -> None:
        """Set the current user name"""
        self.control_section.set_user_name(name)
