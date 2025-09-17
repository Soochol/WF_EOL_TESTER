"""
Hardware Panel for WF EOL Tester GUI

Panel for manual hardware control and monitoring.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import asyncio
from loguru import logger

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import ConnectionStatus, GUIStateManager


class HardwareControlGroup(QGroupBox):
    """Generic hardware control group widget"""

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """Initialize hardware control group"""
        super().__init__(title, parent)

        # Status indicator
        self.status_label = QLabel("OFFLINE")
        self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")

        # Connect/Disconnect buttons
        self.connect_button = QPushButton("Connect")
        self.connect_button.setProperty("class", "success")
        self.connect_button.setMinimumHeight(35)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setProperty("class", "warning")
        self.disconnect_button.setMinimumHeight(35)
        self.disconnect_button.setEnabled(False)

        # Setup layout
        self.setup_layout()

    def setup_layout(self) -> None:
        """Setup group layout"""
        layout = QVBoxLayout(self)

        # Status row
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addLayout(status_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        layout.addLayout(button_layout)

    def set_status(self, status: ConnectionStatus) -> None:
        """Update status display"""
        if status == ConnectionStatus.CONNECTED:
            self.status_label.setText("ONLINE")
            self.status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        elif status == ConnectionStatus.CONNECTING:
            self.status_label.setText("CONNECTING")
            self.status_label.setStyleSheet("color: #F39C12; font-weight: bold;")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        elif status == ConnectionStatus.ERROR:
            self.status_label.setText("ERROR")
            self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
        else:  # DISCONNECTED
            self.status_label.setText("OFFLINE")
            self.status_label.setStyleSheet("color: #7F8C8D; font-weight: bold;")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)


class HardwarePanel(QWidget):
    """
    Hardware control panel widget

    Provides manual control interface for:
    - Individual hardware component connections
    - Basic hardware operations
    - Hardware status monitoring
    - Manual control commands
    """

    # Signals
    status_message = Signal(str)

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize hardware panel

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager
        self.hardware_facade = container.hardware_service_facade()

        # Hardware control groups
        self.robot_group: Optional[HardwareControlGroup] = None
        self.mcu_group: Optional[HardwareControlGroup] = None
        self.loadcell_group: Optional[HardwareControlGroup] = None
        self.power_group: Optional[HardwareControlGroup] = None
        self.dio_group: Optional[HardwareControlGroup] = None

        # Manual control components
        self.command_input: Optional[QLineEdit] = None
        self.send_command_button: Optional[QPushButton] = None
        self.command_log: Optional[QTextEdit] = None

        # Quick action buttons
        self.emergency_stop_button: Optional[QPushButton] = None
        self.reset_all_button: Optional[QPushButton] = None
        self.home_robot_button: Optional[QPushButton] = None

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()
        self.setup_timers()

        logger.debug("Hardware panel initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # === HARDWARE CONTROL GROUPS ===
        self.robot_group = HardwareControlGroup("Robot Control")
        self.mcu_group = HardwareControlGroup("MCU Control")
        self.loadcell_group = HardwareControlGroup("Load Cell")
        self.power_group = HardwareControlGroup("Power Supply")
        self.dio_group = HardwareControlGroup("Digital I/O")

        # === QUICK ACTIONS SECTION ===
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)

        self.emergency_stop_button = QPushButton("EMERGENCY STOP")
        self.emergency_stop_button.setProperty("class", "danger")
        self.emergency_stop_button.setMinimumHeight(60)
        self.emergency_stop_button.setStyleSheet(
            """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #E74C3C;
                color: white;
                border: 3px solid #C0392B;
            }
            QPushButton:hover {
                background-color: #CD212A;
            }
        """
        )

        self.reset_all_button = QPushButton("Reset All")
        self.reset_all_button.setProperty("class", "warning")
        self.reset_all_button.setMinimumHeight(40)

        self.home_robot_button = QPushButton("Home Robot")
        self.home_robot_button.setProperty("class", "primary")
        self.home_robot_button.setMinimumHeight(40)

        actions_layout.addWidget(self.emergency_stop_button, 2)
        actions_layout.addWidget(self.reset_all_button, 1)
        actions_layout.addWidget(self.home_robot_button, 1)

        # === MANUAL CONTROL SECTION ===
        manual_group = QGroupBox("Manual Command")
        manual_layout = QVBoxLayout(manual_group)

        # Command input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Command:"))

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter manual command...")
        input_layout.addWidget(self.command_input)

        self.send_command_button = QPushButton("Send")
        self.send_command_button.setProperty("class", "primary")
        self.send_command_button.setMinimumHeight(35)
        input_layout.addWidget(self.send_command_button)

        manual_layout.addLayout(input_layout)

        # Command log
        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setMaximumHeight(150)
        self.command_log.setFont(QFont("Consolas", 9))
        self.command_log.setStyleSheet(
            """
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #34495E;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )

        manual_layout.addWidget(self.command_log)

        # Store group references
        self.actions_group = actions_group
        self.manual_group = manual_group

    def setup_layout(self) -> None:
        """Setup widget layout"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Main layout for content
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Hardware control section
        hardware_layout = QGridLayout()
        hardware_layout.setSpacing(16)

        # Add hardware groups in 2x3 grid
        hardware_layout.addWidget(self.robot_group, 0, 0)
        hardware_layout.addWidget(self.mcu_group, 0, 1)
        hardware_layout.addWidget(self.loadcell_group, 1, 0)
        hardware_layout.addWidget(self.power_group, 1, 1)
        hardware_layout.addWidget(self.dio_group, 0, 2)

        # Create hardware widget
        hardware_widget = QWidget()
        hardware_widget.setLayout(hardware_layout)

        main_layout.addWidget(hardware_widget)

        # Quick actions section
        main_layout.addWidget(self.actions_group)

        # Manual control section
        main_layout.addWidget(self.manual_group)

        main_layout.addStretch()

        # Set main layout
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Hardware group connections
        if self.robot_group:
            self.robot_group.connect_button.clicked.connect(lambda: self.connect_hardware("robot"))
            self.robot_group.disconnect_button.clicked.connect(
                lambda: self.disconnect_hardware("robot")
            )

        if self.mcu_group:
            self.mcu_group.connect_button.clicked.connect(lambda: self.connect_hardware("mcu"))
            self.mcu_group.disconnect_button.clicked.connect(
                lambda: self.disconnect_hardware("mcu")
            )

        if self.loadcell_group:
            self.loadcell_group.connect_button.clicked.connect(
                lambda: self.connect_hardware("loadcell")
            )
            self.loadcell_group.disconnect_button.clicked.connect(
                lambda: self.disconnect_hardware("loadcell")
            )

        if self.power_group:
            self.power_group.connect_button.clicked.connect(lambda: self.connect_hardware("power"))
            self.power_group.disconnect_button.clicked.connect(
                lambda: self.disconnect_hardware("power")
            )

        if self.dio_group:
            self.dio_group.connect_button.clicked.connect(lambda: self.connect_hardware("dio"))
            self.dio_group.disconnect_button.clicked.connect(
                lambda: self.disconnect_hardware("dio")
            )

        # Quick action buttons
        if self.emergency_stop_button:
            self.emergency_stop_button.clicked.connect(self.emergency_stop)

        if self.reset_all_button:
            self.reset_all_button.clicked.connect(self.reset_all_hardware)

        if self.home_robot_button:
            self.home_robot_button.clicked.connect(self.home_robot)

        # Manual command
        if self.send_command_button:
            self.send_command_button.clicked.connect(self.send_manual_command)

        if self.command_input:
            self.command_input.returnPressed.connect(self.send_manual_command)

        # State manager signals
        if self.state_manager:
            self.state_manager.hardware_status_changed.connect(self.on_hardware_status_changed)

    def setup_timers(self) -> None:
        """Setup update timers"""
        # Periodic status update
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_hardware_status)
        self.status_timer.start(2000)  # Update every 2 seconds

    def connect_hardware(self, hardware_type: str) -> None:
        """
        Connect specific hardware component

        Args:
            hardware_type: Type of hardware to connect
        """
        try:
            self.add_command_log(f"Connecting {hardware_type}...")

            # This would implement actual hardware connection logic
            # For now, just simulate the connection

            if hardware_type == "robot":
                # Simulate robot connection
                self.add_command_log("Robot connection initiated")
            elif hardware_type == "mcu":
                # Simulate MCU connection
                self.add_command_log("MCU connection initiated")
            elif hardware_type == "loadcell":
                # Simulate load cell connection
                self.add_command_log("Load cell connection initiated")
            elif hardware_type == "power":
                # Simulate power supply connection
                self.add_command_log("Power supply connection initiated")
            elif hardware_type == "dio":
                # Simulate digital I/O connection
                self.add_command_log("Digital I/O connection initiated")

            self.status_message.emit(f"Connecting {hardware_type}...")
            logger.info(f"Hardware connection initiated: {hardware_type}")

        except Exception as e:
            logger.error(f"Failed to connect {hardware_type}: {e}")
            self.add_command_log(f"Connection failed: {e}")
            self.status_message.emit(f"Connection failed: {e}")

    def disconnect_hardware(self, hardware_type: str) -> None:
        """
        Disconnect specific hardware component

        Args:
            hardware_type: Type of hardware to disconnect
        """
        try:
            self.add_command_log(f"Disconnecting {hardware_type}...")

            # This would implement actual hardware disconnection logic

            self.status_message.emit(f"Disconnected {hardware_type}")
            logger.info(f"Hardware disconnected: {hardware_type}")

        except Exception as e:
            logger.error(f"Failed to disconnect {hardware_type}: {e}")
            self.add_command_log(f"Disconnection failed: {e}")
            self.status_message.emit(f"Disconnection failed: {e}")

    def emergency_stop(self) -> None:
        """Execute emergency stop"""
        try:
            self.add_command_log("EMERGENCY STOP ACTIVATED")

            # This would implement actual emergency stop logic
            # Stop all hardware operations

            self.status_message.emit("EMERGENCY STOP ACTIVATED")
            logger.warning("Emergency stop activated from hardware panel")

        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            self.add_command_log(f"Emergency stop failed: {e}")
            self.status_message.emit(f"Emergency stop failed: {e}")

    def reset_all_hardware(self) -> None:
        """Reset all hardware components"""
        try:
            self.add_command_log("Resetting all hardware...")

            # This would implement actual hardware reset logic

            self.status_message.emit("Hardware reset initiated")
            logger.info("All hardware reset initiated")

        except Exception as e:
            logger.error(f"Hardware reset failed: {e}")
            self.add_command_log(f"Reset failed: {e}")
            self.status_message.emit(f"Reset failed: {e}")

    def home_robot(self) -> None:
        """Home robot to origin position"""
        try:
            self.add_command_log("Homing robot...")

            # This would use the robot home use case
            robot_home_use_case = self.container.robot_home_use_case()

            self.status_message.emit("Robot homing initiated")
            logger.info("Robot homing initiated")

        except Exception as e:
            logger.error(f"Robot homing failed: {e}")
            self.add_command_log(f"Robot homing failed: {e}")
            self.status_message.emit(f"Robot homing failed: {e}")

    def send_manual_command(self) -> None:
        """Send manual command"""
        try:
            if not self.command_input:
                return

            command = self.command_input.text().strip()
            if not command:
                return

            self.add_command_log(f"> {command}")

            # This would implement actual command sending logic
            # For now, just echo the command

            self.add_command_log(f"Command sent: {command}")
            self.command_input.clear()

            self.status_message.emit(f"Command sent: {command}")
            logger.info(f"Manual command sent: {command}")

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            self.add_command_log(f"Command failed: {e}")
            self.status_message.emit(f"Command failed: {e}")

    def update_hardware_status(self) -> None:
        """Update hardware status displays"""
        if not self.state_manager:
            return

        hardware_status = self.state_manager.hardware_status

        # Update hardware group status displays
        if self.robot_group:
            self.robot_group.set_status(hardware_status.robot_status)

        if self.mcu_group:
            self.mcu_group.set_status(hardware_status.mcu_status)

        if self.loadcell_group:
            self.loadcell_group.set_status(hardware_status.loadcell_status)

        if self.power_group:
            self.power_group.set_status(hardware_status.power_status)

        if self.dio_group:
            self.dio_group.set_status(hardware_status.digital_io_status)

    def on_hardware_status_changed(self, hardware_status) -> None:
        """Handle hardware status change from state manager"""
        self.update_hardware_status()

    def add_command_log(self, message: str) -> None:
        """
        Add message to command log

        Args:
            message: Message to add
        """
        if self.command_log:
            # Standard library imports
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"

            self.command_log.append(formatted_message)

            # Auto-scroll to bottom
            cursor = self.command_log.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.command_log.setTextCursor(cursor)

    def activate_panel(self) -> None:
        """Called when panel becomes active"""
        # Update hardware status when panel becomes active
        self.update_hardware_status()
        logger.debug("Hardware panel activated")

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        self.emergency_stop()

    def handle_resize(self) -> None:
        """Handle panel resize"""
        # Could adjust layouts based on panel size
        pass

    def refresh_panel(self) -> None:
        """Refresh panel data"""
        self.update_hardware_status()
        self.status_message.emit("Hardware panel refreshed")
