"""
Hardware Status Widget

Widget for displaying hardware device status and information.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager, HardwareStatus


class HardwareStatusWidget(QWidget):
    """
    Hardware status widget for displaying device status.

    Shows connection status and current values for all hardware components.
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
        self.connect_signals()
        self.setup_update_timer()

    def setup_ui(self) -> None:
        """Setup the hardware status UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create status group
        self.status_group = QGroupBox("Hardware Status")
        self.status_group.setFont(self._get_group_font())
        main_layout.addWidget(self.status_group)

        # Grid layout for status items
        grid_layout = QGridLayout(self.status_group)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(15, 20, 15, 15)

        # Create status labels
        self.create_status_labels(grid_layout)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

        # Initialize display
        self._update_display()

    def create_status_labels(self, layout: QGridLayout) -> None:
        """Create status labels for each hardware component"""
        row = 0

        # Loadcell
        layout.addWidget(QLabel("Loadcell:"), row, 0)
        self.loadcell_status = QLabel("● Connected")
        self.loadcell_value = QLabel("[12.34 kgf]")
        layout.addWidget(self.loadcell_status, row, 1)
        layout.addWidget(self.loadcell_value, row, 2)
        row += 1

        # MCU
        layout.addWidget(QLabel("MCU:"), row, 0)
        self.mcu_status = QLabel("● Ready")
        self.mcu_port = QLabel("[Port: COM3]")
        layout.addWidget(self.mcu_status, row, 1)
        layout.addWidget(self.mcu_port, row, 2)
        row += 1

        # Power Supply
        layout.addWidget(QLabel("Power Supply:"), row, 0)
        self.power_status = QLabel("● Online")
        self.power_values = QLabel("[24.0V / 5.2A]")
        layout.addWidget(self.power_status, row, 1)
        layout.addWidget(self.power_values, row, 2)
        row += 1

        # Robot
        layout.addWidget(QLabel("Robot:"), row, 0)
        self.robot_status = QLabel("● Homed")
        self.robot_position = QLabel("[X:100 Y:50 Z:25]")
        layout.addWidget(self.robot_status, row, 1)
        layout.addWidget(self.robot_position, row, 2)
        row += 1

        # Digital I/O
        layout.addWidget(QLabel("Digital I/O:"), row, 0)
        self.io_status = QLabel("● Active")
        self.io_channels = QLabel("[8/8 channels]")
        layout.addWidget(self.io_status, row, 1)
        layout.addWidget(self.io_channels, row, 2)

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        self.state_manager.hardware_status_updated.connect(self._on_hardware_status_updated)

    def setup_update_timer(self) -> None:
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(2000)  # Update every 2 seconds

    def _on_hardware_status_updated(self, status: HardwareStatus) -> None:
        """Handle hardware status update"""
        self._update_display(status)

    def _update_display(self, status: Optional[HardwareStatus] = None) -> None:
        """Update the display with current hardware status"""
        if status is None:
            status = self.state_manager.get_hardware_status()

        # Update loadcell
        if status.loadcell_connected:
            self.loadcell_status.setText("🟢 Connected")
            self.loadcell_value.setText(f"[{status.loadcell_value:.2f} kgf]")
        else:
            self.loadcell_status.setText("🔴 Disconnected")
            self.loadcell_value.setText("[-- kgf]")

        # Update MCU
        if status.mcu_connected:
            self.mcu_status.setText("🟢 Ready")
            self.mcu_port.setText(f"[Port: {status.mcu_port}]")
        else:
            self.mcu_status.setText("🔴 Offline")
            self.mcu_port.setText("[Port: --]")

        # Update Power Supply
        if status.power_connected:
            self.power_status.setText("🟢 Online")
            self.power_values.setText(
                f"[{status.power_voltage:.1f}V / {status.power_current:.1f}A]"
            )
        else:
            self.power_status.setText("🔴 Offline")
            self.power_values.setText("[--V / --A]")

        # Update Robot
        if status.robot_connected:
            if status.robot_homed:
                self.robot_status.setText("🟢 Homed")
            else:
                self.robot_status.setText("🟡 Not Homed")
            pos = status.robot_position
            self.robot_position.setText(f"[X:{pos['x']:.0f} Y:{pos['y']:.0f} Z:{pos['z']:.0f}]")
        else:
            self.robot_status.setText("🔴 Disconnected")
            self.robot_position.setText("[X:-- Y:-- Z:--]")

        # Update Digital I/O
        if status.digital_io_connected:
            self.io_status.setText("🟢 Active")
            self.io_channels.setText(
                f"[{status.digital_io_channels}/{status.digital_io_channels} channels]"
            )
        else:
            self.io_status.setText("🔴 Inactive")
            self.io_channels.setText("[0/0 channels]")

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        HardwareStatusWidget {
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
            padding: 2px;
        }
        """
