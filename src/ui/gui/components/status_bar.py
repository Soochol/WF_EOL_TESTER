"""
Status Bar Widget for WF EOL Tester GUI

Enhanced status bar with hardware status, system information, and messages.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QWidget,
)

from ui.gui.services.gui_state_manager import ConnectionStatus, GUIStateManager


class StatusSection(QWidget):
    """Individual status section widget"""

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """
        Initialize status section

        Args:
            title: Section title
            parent: Parent widget
        """
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(4)

        # Title label
        self.title_label = QLabel(f"{title}:")
        self.title_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        # Value label
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 8))

        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def set_value(self, value: str, color: Optional[str] = None) -> None:
        """
        Set section value with optional color

        Args:
            value: Value to display
            color: Optional text color
        """
        self.value_label.setText(value)

        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        else:
            self.value_label.setStyleSheet("")


class StatusBarWidget(QStatusBar):
    """
    Enhanced status bar for main window

    Displays:
    - Hardware connection status
    - Test execution status
    - System information (CPU, Memory, etc.)
    - Status messages with timeout
    - Connection indicators
    """

    # Signals
    status_clicked = Signal(str)  # status_type

    def __init__(self, state_manager: GUIStateManager, parent: Optional[QWidget] = None):
        """
        Initialize status bar widget

        Args:
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        self.state_manager = state_manager

        # Status sections
        self.hardware_section: Optional[StatusSection] = None
        self.test_section: Optional[StatusSection] = None
        self.system_section: Optional[StatusSection] = None
        self.connection_section: Optional[StatusSection] = None

        # Progress indicator
        self.progress_bar: Optional[QProgressBar] = None

        # Setup UI
        self.setup_ui()
        self.setup_timers()
        self.connect_signals()

        # Initial update
        self.update_all_status()

        logger.debug("Status bar widget initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set status bar properties
        self.setFixedHeight(30)
        self.setSizeGripEnabled(False)

        # Create main widget for custom layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(4, 2, 4, 2)
        main_layout.setSpacing(16)

        # Hardware status section
        self.hardware_section = StatusSection("HW")
        self.hardware_section.setToolTip("Hardware connection status")
        main_layout.addWidget(self.hardware_section)

        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet("color: #BDC3C7;")
        main_layout.addWidget(separator1)

        # Test status section
        self.test_section = StatusSection("TEST")
        self.test_section.setToolTip("Current test status")
        main_layout.addWidget(self.test_section)

        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet("color: #BDC3C7;")
        main_layout.addWidget(separator2)

        # Connection count section
        self.connection_section = StatusSection("CONN")
        self.connection_section.setToolTip("Connected devices count")
        main_layout.addWidget(self.connection_section)

        # Add flexible space
        main_layout.addStretch()

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setStyleSheet("color: #BDC3C7;")
        main_layout.addWidget(separator3)

        # System info section
        self.system_section = StatusSection("SYS")
        self.system_section.setToolTip("System information")
        main_layout.addWidget(self.system_section)

        # Add main widget to status bar
        self.addPermanentWidget(main_widget, 1)

        # Set initial styling
        self.setStyleSheet(
            """
            QStatusBar {
                background-color: #2C3E50;
                color: #ECF0F1;
                border-top: 1px solid #34495E;
            }
            QLabel {
                color: #ECF0F1;
            }
            QProgressBar {
                border: 1px solid #34495E;
                border-radius: 2px;
                background-color: #34495E;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 1px;
            }
        """
        )

    def setup_timers(self) -> None:
        """Setup update timers"""
        # System info update timer
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(5000)  # Update every 5 seconds

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_all_status)
        self.status_timer.start(2000)  # Update every 2 seconds

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        if self.state_manager:
            self.state_manager.hardware_status_changed.connect(self.on_hardware_status_changed)
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.test_progress_changed.connect(self.on_test_progress_changed)

    def on_hardware_status_changed(self, hardware_status) -> None:
        """
        Handle hardware status change

        Args:
            hardware_status: Hardware status object
        """
        self.update_hardware_status(hardware_status)

    def on_test_status_changed(self, status: str) -> None:
        """
        Handle test status change

        Args:
            status: New test status
        """
        self.update_test_status(status)

    def on_test_progress_changed(self, progress: int, message: str) -> None:
        """
        Handle test progress change

        Args:
            progress: Progress percentage
            message: Progress message
        """
        self.update_test_progress(progress, message)

    def update_hardware_status(self, hardware_status) -> None:
        """
        Update hardware status display

        Args:
            hardware_status: Hardware status object
        """
        if not self.hardware_section:
            return

        overall_status = hardware_status.overall_status

        if overall_status == ConnectionStatus.CONNECTED:
            self.hardware_section.set_value("ONLINE", "#27AE60")  # Green
        elif overall_status == ConnectionStatus.CONNECTING:
            self.hardware_section.set_value("CONNECTING", "#F39C12")  # Orange
        elif overall_status == ConnectionStatus.ERROR:
            self.hardware_section.set_value("ERROR", "#E74C3C")  # Red
        else:
            self.hardware_section.set_value("OFFLINE", "#7F8C8D")  # Gray

        # Update connection count
        if self.connection_section:
            connected_count = sum(
                1
                for status in [
                    hardware_status.robot_status,
                    hardware_status.mcu_status,
                    hardware_status.loadcell_status,
                    hardware_status.power_status,
                    hardware_status.digital_io_status,
                ]
                if status == ConnectionStatus.CONNECTED
            )

            self.connection_section.set_value(f"{connected_count}/5")

    def update_test_status(self, status: str) -> None:
        """
        Update test status display

        Args:
            status: Test status string
        """
        if not self.test_section:
            return

        status_upper = status.upper()

        if status == "completed":
            color = "#27AE60"  # Green
        elif status in ["failed", "error"]:
            color = "#E74C3C"  # Red
        elif status == "running":
            color = "#3498DB"  # Blue
        elif status == "cancelled":
            color = "#F39C12"  # Orange
        else:  # idle, ready
            color = "#ECF0F1"  # White

        self.test_section.set_value(status_upper, color)

        # Show/hide progress bar
        if self.progress_bar:
            show_progress = status in ["preparing", "running"]
            self.progress_bar.setVisible(show_progress)

    def update_test_progress(self, progress: int, message: str) -> None:
        """
        Update test progress display

        Args:
            progress: Progress percentage
            message: Progress message
        """
        if self.progress_bar:
            self.progress_bar.setValue(progress)
            if message:
                self.progress_bar.setToolTip(f"{progress}%: {message}")
            else:
                self.progress_bar.setToolTip(f"{progress}%")

    def update_system_info(self) -> None:
        """Update system information display"""
        if not self.system_section:
            return

        try:
            # Get current time for basic system info
            current_time = datetime.now().strftime("%H:%M:%S")
            self.system_section.set_value(current_time)

            # Could be extended to show CPU/Memory usage
            # import psutil
            # cpu_percent = psutil.cpu_percent()
            # memory = psutil.virtual_memory()
            # self.system_section.set_value(f"CPU:{cpu_percent:.0f}% MEM:{memory.percent:.0f}%")

        except Exception as e:
            logger.warning(f"System info update failed: {e}")
            self.system_section.set_value("--")

    def update_all_status(self) -> None:
        """Update all status sections"""
        if self.state_manager:
            # Update from current state
            current_state = self.state_manager.current_state

            # Update hardware status
            self.update_hardware_status(current_state.hardware_status)

            # Update test status
            self.update_test_status(current_state.test_status.value)

            # Update system info
            self.update_system_info()

    def show_message(self, message: str, timeout: int = 2000) -> None:
        """
        Show temporary message in status bar

        Args:
            message: Message to show
            timeout: Timeout in milliseconds
        """
        # Show message in temporary area
        self.showMessage(message, timeout)

    def show_permanent_message(self, message: str) -> None:
        """
        Show permanent message in status bar

        Args:
            message: Permanent message to show
        """
        self.clearMessage()
        self.showMessage(message, 0)  # 0 = permanent

    def clear_message(self) -> None:
        """Clear status message"""
        self.clearMessage()

    def set_progress_visible(self, visible: bool) -> None:
        """
        Set progress bar visibility

        Args:
            visible: Whether progress bar should be visible
        """
        if self.progress_bar:
            self.progress_bar.setVisible(visible)

    def set_progress_value(self, value: int) -> None:
        """
        Set progress bar value

        Args:
            value: Progress value (0-100)
        """
        if self.progress_bar:
            self.progress_bar.setValue(max(0, min(100, value)))

    def get_hardware_status_text(self) -> str:
        """
        Get current hardware status text

        Returns:
            Hardware status text
        """
        if self.hardware_section:
            return self.hardware_section.value_label.text()
        return "--"

    def get_test_status_text(self) -> str:
        """
        Get current test status text

        Returns:
            Test status text
        """
        if self.test_section:
            return self.test_section.value_label.text()
        return "--"

    def highlight_section(self, section_name: str, highlight: bool = True) -> None:
        """
        Highlight a status section

        Args:
            section_name: Name of section to highlight ("hardware", "test", "system", "connection")
            highlight: Whether to highlight
        """
        section_map = {
            "hardware": self.hardware_section,
            "test": self.test_section,
            "system": self.system_section,
            "connection": self.connection_section,
        }

        section = section_map.get(section_name)
        if section:
            if highlight:
                # Add highlight styling
                section.setStyleSheet(
                    """
                    QWidget {
                        background-color: #F39C12;
                        border-radius: 2px;
                        padding: 2px;
                    }
                    QLabel {
                        color: white;
                    }
                """
                )
            else:
                # Remove highlight
                section.setStyleSheet("")
