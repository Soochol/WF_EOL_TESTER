"""
Dashboard Panel for WF EOL Tester GUI

System overview panel showing hardware status, recent tests, and system information.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import (
    ConnectionStatus,
    GUIStateManager,
    TestStatus,
)


class StatusCard(QFrame):
    """Status card widget for dashboard metrics"""

    def __init__(
        self, title: str, value: str = "0", color: str = "#3498DB", parent: Optional[QWidget] = None
    ):
        """
        Initialize status card

        Args:
            title: Card title
            value: Card value
            color: Card accent color
            parent: Parent widget
        """
        super().__init__(parent)

        self.title = title
        self.color = color

        # Setup frame
        self.setFrameStyle(QFrame.Shape.Box)
        self.setMinimumSize(QSize(200, 100))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #2C3E50;")

        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        # Apply card styling
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid #E8E8E8;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """
        )

    def set_value(self, value: str) -> None:
        """
        Update card value

        Args:
            value: New value to display
        """
        self.value_label.setText(str(value))

    def set_color(self, color: str) -> None:
        """
        Update card color

        Args:
            color: New accent color
        """
        self.color = color
        self.title_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid #E8E8E8;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """
        )


class DashboardPanel(QWidget):
    """
    Dashboard panel widget

    Provides system overview with:
    - Hardware connection status cards
    - Recent test results
    - System messages log
    - Quick action buttons
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
        Initialize dashboard panel

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager

        # Status cards
        self.hardware_status_card: Optional[StatusCard] = None
        self.test_status_card: Optional[StatusCard] = None
        self.connection_count_card: Optional[StatusCard] = None
        self.uptime_card: Optional[StatusCard] = None

        # Components
        self.system_messages_text: Optional[QTextEdit] = None
        self.recent_tests_table: Optional[QTableWidget] = None
        self.refresh_button: Optional[QPushButton] = None
        self.quick_test_button: Optional[QPushButton] = None

        # State tracking
        self.start_time = datetime.now()

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()
        self.setup_timers()

        # Initial data load
        self.refresh_panel()

        logger.debug("Dashboard panel initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create status cards
        self.hardware_status_card = StatusCard(
            "Hardware Status", "Checking...", "#E74C3C"  # Red initially
        )

        self.test_status_card = StatusCard("Test Status", "IDLE", "#7F8C8D")  # Gray initially

        self.connection_count_card = StatusCard(
            "Connected Devices", "0/5", "#F39C12"  # Orange initially
        )

        self.uptime_card = StatusCard("System Uptime", "00:00:00", "#3498DB")  # Blue

        # Create system messages section
        messages_group = QGroupBox("System Messages")
        messages_layout = QVBoxLayout(messages_group)

        self.system_messages_text = QTextEdit()
        self.system_messages_text.setReadOnly(True)
        self.system_messages_text.setMaximumHeight(150)
        self.system_messages_text.setFont(QFont("Consolas", 9))
        self.system_messages_text.setStyleSheet(
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

        messages_layout.addWidget(self.system_messages_text)

        # Create recent tests section
        tests_group = QGroupBox("Recent Test Results")
        tests_layout = QVBoxLayout(tests_group)

        self.recent_tests_table = QTableWidget()
        self.recent_tests_table.setColumnCount(4)
        self.recent_tests_table.setHorizontalHeaderLabels(
            ["Time", "Test Type", "Status", "Duration"]
        )
        self.recent_tests_table.setMaximumHeight(200)
        self.recent_tests_table.setAlternatingRowColors(True)
        self.recent_tests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set column widths
        self.recent_tests_table.setColumnWidth(0, 120)
        self.recent_tests_table.setColumnWidth(1, 150)
        self.recent_tests_table.setColumnWidth(2, 100)
        self.recent_tests_table.setColumnWidth(3, 100)

        tests_layout.addWidget(self.recent_tests_table)

        # Create quick actions section
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)

        self.refresh_button = QPushButton("Refresh Status")
        self.refresh_button.setProperty("class", "primary")
        self.refresh_button.setMinimumHeight(44)
        self.refresh_button.setAccessibleName("Refresh Dashboard Status")

        self.quick_test_button = QPushButton("Quick MCU Test")
        self.quick_test_button.setProperty("class", "success")
        self.quick_test_button.setMinimumHeight(44)
        self.quick_test_button.setAccessibleName("Start Quick MCU Test")

        actions_layout.addWidget(self.refresh_button)
        actions_layout.addWidget(self.quick_test_button)
        actions_layout.addStretch()

        # Store group references
        self.messages_group = messages_group
        self.tests_group = tests_group
        self.actions_group = actions_group

    def setup_layout(self) -> None:
        """Setup widget layout"""
        # Create scroll area for entire dashboard
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

        # Status cards section
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(16)

        # Add status cards in 2x2 grid
        cards_layout.addWidget(self.hardware_status_card, 0, 0)
        cards_layout.addWidget(self.test_status_card, 0, 1)
        cards_layout.addWidget(self.connection_count_card, 1, 0)
        cards_layout.addWidget(self.uptime_card, 1, 1)

        main_layout.addWidget(cards_widget)

        # Content sections
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.messages_group)
        left_column.addWidget(self.actions_group)

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(self.tests_group)

        # Create column widgets
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)

        content_layout.addWidget(left_widget, 1)
        content_layout.addWidget(right_widget, 1)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

        # Set main layout
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # State manager signals
        if self.state_manager:
            self.state_manager.hardware_status_changed.connect(self.on_hardware_status_changed)
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.system_message_added.connect(self.on_system_message_added)

        # Button signals
        if self.refresh_button:
            self.refresh_button.clicked.connect(self.refresh_panel)

        if self.quick_test_button:
            self.quick_test_button.clicked.connect(self.start_quick_test)

    def setup_timers(self) -> None:
        """Setup update timers"""
        # Uptime update timer
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)  # Update every second

        # Data refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def on_hardware_status_changed(self, hardware_status) -> None:
        """
        Handle hardware status change

        Args:
            hardware_status: Hardware status object
        """
        self.update_hardware_status_display(hardware_status)

    def on_test_status_changed(self, status: str) -> None:
        """
        Handle test status change

        Args:
            status: New test status
        """
        self.update_test_status_display(status)

    def on_system_message_added(self, message: str) -> None:
        """
        Handle new system message

        Args:
            message: New system message
        """
        if self.system_messages_text:
            # Add message to text widget
            self.system_messages_text.append(message)

            # Auto-scroll to bottom
            cursor = self.system_messages_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.system_messages_text.setTextCursor(cursor)

    def update_hardware_status_display(self, hardware_status) -> None:
        """
        Update hardware status card

        Args:
            hardware_status: Hardware status object
        """
        if not self.hardware_status_card or not self.connection_count_card:
            return

        overall_status = hardware_status.overall_status

        # Update hardware status card
        if overall_status == ConnectionStatus.CONNECTED:
            self.hardware_status_card.set_value("ONLINE")
            self.hardware_status_card.set_color("#27AE60")  # Green
        elif overall_status == ConnectionStatus.CONNECTING:
            self.hardware_status_card.set_value("CONNECTING")
            self.hardware_status_card.set_color("#F39C12")  # Orange
        elif overall_status == ConnectionStatus.ERROR:
            self.hardware_status_card.set_value("ERROR")
            self.hardware_status_card.set_color("#E74C3C")  # Red
        else:
            self.hardware_status_card.set_value("OFFLINE")
            self.hardware_status_card.set_color("#7F8C8D")  # Gray

        # Update connection count card
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

        self.connection_count_card.set_value(f"{connected_count}/5")

        # Set color based on connection ratio
        if connected_count == 5:
            self.connection_count_card.set_color("#27AE60")  # Green
        elif connected_count >= 3:
            self.connection_count_card.set_color("#F39C12")  # Orange
        else:
            self.connection_count_card.set_color("#E74C3C")  # Red

    def update_test_status_display(self, status: str) -> None:
        """
        Update test status card

        Args:
            status: Test status string
        """
        if not self.test_status_card:
            return

        status_upper = status.upper()
        self.test_status_card.set_value(status_upper)

        # Set color based on status
        if status == "completed":
            color = "#27AE60"  # Green
        elif status in ["failed", "error"]:
            color = "#E74C3C"  # Red
        elif status == "running":
            color = "#3498DB"  # Blue
        elif status == "cancelled":
            color = "#F39C12"  # Orange
        else:  # idle, ready
            color = "#7F8C8D"  # Gray

        self.test_status_card.set_color(color)

    def update_uptime(self) -> None:
        """Update system uptime display"""
        if not self.uptime_card:
            return

        uptime = datetime.now() - self.start_time

        # Format uptime as HH:MM:SS
        total_seconds = int(uptime.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.uptime_card.set_value(uptime_str)

    def refresh_data(self) -> None:
        """Refresh dashboard data"""
        # Update recent test results
        self.load_recent_tests()

        # Update system messages
        self.load_system_messages()

    def load_recent_tests(self) -> None:
        """Load recent test results into table"""
        if not self.recent_tests_table:
            return

        try:
            # Clear existing rows
            self.recent_tests_table.setRowCount(0)

            # This would normally load from the repository
            # For now, add some sample data
            sample_tests = [
                ["14:30:15", "EOL Force Test", "PASSED", "45.2s"],
                ["14:25:33", "MCU Test", "PASSED", "8.1s"],
                ["14:20:12", "EOL Force Test", "FAILED", "12.5s"],
                ["14:15:44", "MCU Test", "PASSED", "7.9s"],
            ]

            for i, test_data in enumerate(sample_tests):
                self.recent_tests_table.insertRow(i)

                for j, value in enumerate(test_data):
                    item = QTableWidgetItem(str(value))

                    # Color code status column
                    if j == 2:  # Status column
                        if value == "PASSED":
                            item.setForeground(QPalette().brush(QPalette.ColorRole.BrightText))
                            item.setBackground(QPalette().brush(QPalette.ColorRole.Dark))
                        elif value == "FAILED":
                            item.setForeground(QPalette().brush(QPalette.ColorRole.BrightText))
                            item.setBackground(QPalette().brush(QPalette.ColorRole.Dark))

                    self.recent_tests_table.setItem(i, j, item)

        except Exception as e:
            logger.error(f"Failed to load recent tests: {e}")

    def load_system_messages(self) -> None:
        """Load recent system messages"""
        if not self.system_messages_text or not self.state_manager:
            return

        try:
            # Get recent messages from state manager
            recent_messages = self.state_manager.get_system_messages(20)

            # Clear and reload messages
            self.system_messages_text.clear()

            for message in recent_messages:
                self.system_messages_text.append(message)

            # Scroll to bottom
            cursor = self.system_messages_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.system_messages_text.setTextCursor(cursor)

        except Exception as e:
            logger.error(f"Failed to load system messages: {e}")

    def start_quick_test(self) -> None:
        """Start quick MCU test"""
        try:
            # Navigate to MCU test panel and start test
            if self.state_manager:
                self.state_manager.navigate_to_panel("mcu_test")
                self.status_message.emit("Navigating to MCU test panel")

        except Exception as e:
            logger.error(f"Quick test start failed: {e}")
            self.status_message.emit(f"Quick test failed: {e}")

    def refresh_panel(self) -> None:
        """Refresh all panel data"""
        try:
            # Force immediate status update (in a safer way)
            if self.state_manager:
                # Use QTimer to trigger status update safely
                QTimer.singleShot(100, self.state_manager._update_hardware_status)

            # Refresh data
            self.refresh_data()

            self.status_message.emit("Dashboard refreshed")
            logger.info("Dashboard panel refreshed")

        except Exception as e:
            logger.error(f"Dashboard refresh failed: {e}")
            self.status_message.emit(f"Refresh failed: {e}")

    def activate_panel(self) -> None:
        """Called when panel becomes active"""
        # Refresh data when panel becomes active
        self.refresh_data()
        logger.debug("Dashboard panel activated")

    def handle_resize(self) -> None:
        """Handle panel resize"""
        # Could adjust layouts based on size if needed
        pass

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        # Dashboard doesn't need specific emergency stop handling
        # but could display emergency status
        self.status_message.emit("Emergency stop activated")
        logger.info("Dashboard: Emergency stop acknowledged")
