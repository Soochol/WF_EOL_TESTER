"""
Hardware Widget

Hardware management page with device status and controls.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.hardware_status_widget import HardwareStatusWidget


class HardwareWidget(QWidget):
    """
    Hardware widget for device management and control.

    Shows detailed hardware status and provides control options.
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the hardware UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Hardware Status
        self.hardware_status = HardwareStatusWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.hardware_status)

        # Hardware Controls
        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def create_controls_group(self) -> QGroupBox:
        """Create hardware controls group"""
        group = QGroupBox("Device Controls")
        group.setFont(self._get_group_font())
        grid_layout = QGridLayout(group)
        grid_layout.setSpacing(10)

        # Loadcell controls
        grid_layout.addWidget(QLabel("Loadcell:"), 0, 0)
        self.loadcell_connect_btn = QPushButton("Connect")
        self.loadcell_disconnect_btn = QPushButton("Disconnect")
        self.loadcell_calibrate_btn = QPushButton("Calibrate")
        grid_layout.addWidget(self.loadcell_connect_btn, 0, 1)
        grid_layout.addWidget(self.loadcell_disconnect_btn, 0, 2)
        grid_layout.addWidget(self.loadcell_calibrate_btn, 0, 3)

        # MCU controls
        grid_layout.addWidget(QLabel("MCU:"), 1, 0)
        self.mcu_connect_btn = QPushButton("Connect")
        self.mcu_disconnect_btn = QPushButton("Disconnect")
        self.mcu_reset_btn = QPushButton("Reset")
        grid_layout.addWidget(self.mcu_connect_btn, 1, 1)
        grid_layout.addWidget(self.mcu_disconnect_btn, 1, 2)
        grid_layout.addWidget(self.mcu_reset_btn, 1, 3)

        # Power Supply controls
        grid_layout.addWidget(QLabel("Power Supply:"), 2, 0)
        self.power_connect_btn = QPushButton("Connect")
        self.power_disconnect_btn = QPushButton("Disconnect")
        self.power_test_btn = QPushButton("Test Output")
        grid_layout.addWidget(self.power_connect_btn, 2, 1)
        grid_layout.addWidget(self.power_disconnect_btn, 2, 2)
        grid_layout.addWidget(self.power_test_btn, 2, 3)

        # Robot controls
        grid_layout.addWidget(QLabel("Robot:"), 3, 0)
        self.robot_connect_btn = QPushButton("Connect")
        self.robot_disconnect_btn = QPushButton("Disconnect")
        self.robot_home_btn = QPushButton("Home")
        grid_layout.addWidget(self.robot_connect_btn, 3, 1)
        grid_layout.addWidget(self.robot_disconnect_btn, 3, 2)
        grid_layout.addWidget(self.robot_home_btn, 3, 3)

        # Digital I/O controls
        grid_layout.addWidget(QLabel("Digital I/O:"), 4, 0)
        self.io_connect_btn = QPushButton("Connect")
        self.io_disconnect_btn = QPushButton("Disconnect")
        self.io_test_btn = QPushButton("Test Channels")
        grid_layout.addWidget(self.io_connect_btn, 4, 1)
        grid_layout.addWidget(self.io_disconnect_btn, 4, 2)
        grid_layout.addWidget(self.io_test_btn, 4, 3)

        return group

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        HardwareWidget {
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
        """
