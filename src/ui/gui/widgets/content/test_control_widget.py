"""
Test Control Widget

Test control page with test parameters and control buttons.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.utils.icon_manager import get_emoji, get_icon, IconSize
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class TestControlWidget(QWidget):
    """
    Test control widget for setting up and running tests.

    Provides test parameter configuration and control buttons.
    """

    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()

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
        """Setup the test control UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Test Sequence Selection
        sequence_group = self.create_sequence_group()
        main_layout.addWidget(sequence_group)

        # Test Parameters
        params_group = self.create_parameters_group()
        main_layout.addWidget(params_group)

        # Control Buttons
        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)

        # Test Status Display
        status_group = self.create_status_group()
        main_layout.addWidget(status_group)

        # Live Test Logs (expanded section)
        logs_group = self.create_logs_group()
        main_layout.addWidget(logs_group, 1)  # Give logs section stretch factor of 1

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def _on_start_test_clicked(self) -> None:
        """Handle START TEST button click"""
        # Emit the test started signal
        self.test_started.emit()

    def _on_home_button_clicked(self) -> None:
        """Handle HOME button click with debug logging"""
        # Third-party imports
        from loguru import logger

        logger.info("🏠 HOME button clicked in TestControlWidget")
        logger.debug("Emitting robot_home_requested signal...")
        # Emit the robot home requested signal
        self.robot_home_requested.emit()
        logger.debug("robot_home_requested signal emitted successfully")

    def create_sequence_group(self) -> QGroupBox:
        """Create test sequence selection group"""
        group = QGroupBox("Test Sequence")
        group.setFont(self._get_group_font())
        layout = QVBoxLayout(group)

        self.sequence_combo = QComboBox()
        self.sequence_combo.addItems(
            [
                "EOL Force Test",
                "Heating Cooling Time Test",
                "Simple MCU Test",
                "Custom Test Sequence",
            ]
        )
        self.sequence_combo.setMinimumHeight(35)
        layout.addWidget(self.sequence_combo)

        return group

    def create_parameters_group(self) -> QGroupBox:
        """Create test parameters group"""
        group = QGroupBox("Test Parameters")
        group.setFont(self._get_group_font())
        layout = QHBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)

        # Serial Number (only parameter remaining)
        layout.addWidget(QLabel("Serial Number:"))
        self.serial_edit = QLineEdit()
        self.serial_edit.setPlaceholderText("Enter serial number...")
        self.serial_edit.setText("SN123456789")
        self.serial_edit.setMinimumHeight(30)
        layout.addWidget(self.serial_edit)

        # Add stretch to center the serial number input
        layout.addStretch()

        return group

    def create_controls_group(self) -> QGroupBox:
        """Create control buttons group"""
        group = QGroupBox("Test Controls")
        group.setFont(self._get_group_font())
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Main control buttons row
        main_controls_layout = QHBoxLayout()
        main_controls_layout.setSpacing(10)

        # START TEST button
        self.start_btn = QPushButton("START TEST")
        start_icon = get_icon("play", IconSize.MEDIUM)
        if not start_icon.isNull():
            self.start_btn.setIcon(start_icon)
        else:
            self.start_btn.setText(f"{get_emoji('play')} START TEST")
        self.start_btn.setMinimumHeight(45)
        self.start_btn.clicked.connect(self._on_start_test_clicked)
        main_controls_layout.addWidget(self.start_btn)

        # HOME button
        self.home_btn = QPushButton("HOME")
        home_icon = get_icon("dashboard", IconSize.MEDIUM)
        if not home_icon.isNull():
            self.home_btn.setIcon(home_icon)
        else:
            self.home_btn.setText(f"{get_emoji('dashboard')} HOME")
        self.home_btn.setMinimumHeight(45)
        self.home_btn.clicked.connect(self._on_home_button_clicked)
        main_controls_layout.addWidget(self.home_btn)

        # PAUSE button
        self.pause_btn = QPushButton("PAUSE")
        pause_icon = get_icon("pause", IconSize.MEDIUM)
        if not pause_icon.isNull():
            self.pause_btn.setIcon(pause_icon)
        else:
            self.pause_btn.setText(f"{get_emoji('pause')} PAUSE")
        self.pause_btn.setMinimumHeight(45)
        self.pause_btn.clicked.connect(self.test_paused.emit)
        main_controls_layout.addWidget(self.pause_btn)

        # STOP button
        self.stop_btn = QPushButton("STOP")
        stop_icon = get_icon("stop", IconSize.MEDIUM)
        if not stop_icon.isNull():
            self.stop_btn.setIcon(stop_icon)
        else:
            self.stop_btn.setText(f"{get_emoji('stop')} STOP")
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.clicked.connect(self.test_stopped.emit)
        main_controls_layout.addWidget(self.stop_btn)

        layout.addLayout(main_controls_layout)

        # Emergency stop button
        self.emergency_btn = QPushButton("EMERGENCY STOP")
        self.emergency_btn.setMinimumHeight(50)
        self.emergency_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #cc0000;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #990000;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #990000;
            }
            QPushButton:pressed {
                background-color: #660000;
            }
        """
        )
        self.emergency_btn.clicked.connect(self.emergency_stop_requested.emit)
        layout.addWidget(self.emergency_btn)

        return group

    def create_status_group(self) -> QGroupBox:
        """Create test status display group"""
        group = QGroupBox("Test Status")
        group.setFont(self._get_group_font())
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)

        # Top row: Status icon and text
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setFont(QFont("", 16))
        self.status_icon.setFixedWidth(30)
        # Set default status
        self._update_status_icon("status_ready")
        top_layout.addWidget(self.status_icon)

        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("", 12, QFont.Weight.Bold))
        top_layout.addWidget(self.status_label)

        # Add stretch to push status to left
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v/%m")
        layout.addWidget(self.progress_bar)

        # Initialize progress bar with default styling
        self._update_progress_bar_style("Ready")

        return group

    def create_logs_group(self) -> QGroupBox:
        """Create live test logs group"""
        group = QGroupBox("Live Test Logs")
        group.setFont(self._get_group_font())
        group.setMinimumHeight(300)  # Set minimum height for expansion
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)

        # Add log viewer widget
        self.log_viewer = LogViewerWidget(self.container, self.state_manager)
        layout.addWidget(self.log_viewer)

        return group

    def update_test_status(
        self, status: str, icon: str = "status_ready", progress: Optional[int] = None
    ) -> None:
        """Update test status display"""
        self.status_label.setText(status)
        self._update_status_icon(icon)

        # Update progress bar if value provided
        if progress is not None:
            self.progress_bar.setValue(progress)

        # Update progress bar style and text based on status
        self._update_progress_bar_style(status)

        # Color coding based on status
        if "completed" in status.lower() or "success" in status.lower():
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")  # Green
            # Switch to normal progress mode and set to 100%
            self.progress_bar.setRange(0, 100)
            if progress is None:
                self.progress_bar.setValue(100)
            # Select all text in serial number field for easy editing of next test
            self.serial_edit.selectAll()
            self.serial_edit.setFocus()
        elif "failed" in status.lower() or "error" in status.lower():
            self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")  # Red
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)
        elif (
            "running" in status.lower()
            or "testing" in status.lower()
            or "executing" in status.lower()
        ):
            self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")  # Orange
            # Switch to busy indicator mode (infinite animation)
            self.progress_bar.setRange(0, 0)
        elif "paused" in status.lower():
            self.status_label.setStyleSheet("color: #4da6ff; font-weight: bold;")  # Blue
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)
        elif "stopped" in status.lower():
            self.status_label.setStyleSheet("color: #ff8800; font-weight: bold;")  # Orange-red
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)
            if progress is None:
                self.progress_bar.setValue(0)
        elif "emergency" in status.lower():
            self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")  # Dark red
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)
            if progress is None:
                self.progress_bar.setValue(0)
        elif "ready" in status.lower():
            self.status_label.setStyleSheet("color: #cccccc; font-weight: bold;")  # Default gray
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)
            if progress is None:
                self.progress_bar.setValue(0)
        else:
            self.status_label.setStyleSheet("color: #cccccc; font-weight: bold;")  # Default gray
            # Switch to normal progress mode
            self.progress_bar.setRange(0, 100)

    def update_test_progress(self, progress: int, status_text: Optional[str] = None) -> None:
        """Update only the progress bar"""
        self.progress_bar.setValue(progress)
        if status_text:
            self.status_label.setText(status_text)

    def disable_start_button(self) -> None:
        """Disable START TEST button (typically after Emergency Stop)"""
        self.start_btn.setEnabled(False)
        self.start_btn.setToolTip("Robot homing required after Emergency Stop")

        # Force immediate visual update
        self.start_btn.repaint()
        self.start_btn.update()

        # Verify the button is actually disabled
        if self.start_btn.isEnabled():
            # If still enabled, try again with more force
            self.start_btn.setEnabled(False)
            self.start_btn.repaint()

    def enable_start_button(self) -> None:
        """Enable START TEST button (typically after successful robot homing)"""
        self.start_btn.setEnabled(True)
        self.start_btn.setToolTip("")

        # Force immediate visual update
        self.start_btn.repaint()
        self.start_btn.update()

    def disable_home_button(self) -> None:
        """Disable HOME button (typically during test execution)"""
        self.home_btn.setEnabled(False)
        self.home_btn.setToolTip("HOME unavailable during test execution")

        # Force immediate visual update
        self.home_btn.repaint()
        self.home_btn.update()

    def enable_home_button(self) -> None:
        """Enable HOME button (typically after test completion)"""
        self.home_btn.setEnabled(True)
        self.home_btn.setToolTip("")

        # Force immediate visual update
        self.home_btn.repaint()
        self.home_btn.update()

    def _update_status_icon(self, icon_name: str) -> None:
        """Update status icon using icon manager"""
        # Try to get icon from icon manager
        icon = get_icon(icon_name, IconSize.SMALL)

        if not icon.isNull():
            # Use QLabel with pixmap for proper icon display
            pixmap = icon.pixmap(16, 16)
            self.status_icon.setPixmap(pixmap)
            self.status_icon.setText("")  # Clear text
        else:
            # Fallback to emoji
            emoji = get_emoji(icon_name)
            if emoji:
                self.status_icon.clear()  # Clear pixmap before setting text
                self.status_icon.setText(emoji)

    def _update_progress_bar_style(self, status: str) -> None:
        """Update progress bar style based on status"""
        # Define color schemes for different states
        if "completed" in status.lower() or "success" in status.lower():
            # Green gradient for success
            gradient_colors = "stop: 0 #00ff00, stop: 1 #00cc00"
            text_format = "100%"
        elif "failed" in status.lower() or "error" in status.lower():
            # Red gradient for failure
            gradient_colors = "stop: 0 #ff4444, stop: 1 #cc0000"
            text_format = "Failed"
        elif (
            "running" in status.lower()
            or "testing" in status.lower()
            or "executing" in status.lower()
        ):
            # Dark green gradient for running
            gradient_colors = "stop: 0 #2E7D32, stop: 1 #1B5E20"
            text_format = "Progressing..."
        elif "paused" in status.lower():
            # Blue gradient for paused
            gradient_colors = "stop: 0 #4da6ff, stop: 1 #0078d4"
            text_format = "Paused"
        elif "stopped" in status.lower():
            # Orange-red gradient for stopped
            gradient_colors = "stop: 0 #ff8800, stop: 1 #cc6600"
            text_format = "Stopped"
        elif "emergency" in status.lower():
            # Dark red gradient for emergency
            gradient_colors = "stop: 0 #cc0000, stop: 1 #990000"
            text_format = "Emergency"
        else:
            # Gray gradient for ready/default
            gradient_colors = "stop: 0 #666666, stop: 1 #404040"
            text_format = "Ready"

        # Apply the new style
        progress_style = f"""
        QProgressBar {{
            border: 1px solid #404040;
            border-radius: 3px;
            background-color: #2d2d2d;
            color: #ffffff;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                {gradient_colors});
            border-radius: 2px;
        }}
        """

        # Update progress bar style and text
        self.progress_bar.setStyleSheet(progress_style)
        self.progress_bar.setFormat(text_format)

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        TestControlWidget {
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
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: 1px solid #106ebe;
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #888888;
        }
        QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
            background-color: #2d2d2d;
            color: #cccccc;
            border: 1px solid #404040;
            border-radius: 3px;
            padding: 5px;
            font-size: 14px;
        }
        QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {
            border-color: #0078d4;
        }
        """
