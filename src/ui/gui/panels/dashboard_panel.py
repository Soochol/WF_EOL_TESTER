"""
Dashboard Panel for WF EOL Tester GUI

System overview panel showing recent tests, system information, and operational status.
"""

# Standard library imports
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Third-party imports
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
import asyncio
from loguru import logger

# Local application imports
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

        # Setup frame - modern card design
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setMinimumSize(QSize(220, 120))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #64748B; font-weight: 600; letter-spacing: 0.5px;")

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #1E293B; font-weight: 700;")

        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        # Apply modern card styling
        self.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #F8FAFC);
                border: 1px solid #E2E8F0;
                border-left: 4px solid {color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FEFEFE, stop: 1 #F1F5F9);
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
        self.title_label.setStyleSheet("color: #64748B; font-weight: 600; letter-spacing: 0.5px;")
        self.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #F8FAFC);
                border: 1px solid #E2E8F0;
                border-left: 4px solid {color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FEFEFE, stop: 1 #F1F5F9);
            }}
        """
        )


class DashboardPanel(QWidget):
    """
    Dashboard panel widget

    Provides system overview with:
    - Test status and system uptime cards
    - Recent test results
    - System messages log
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
        self.test_status_card: Optional[StatusCard] = None
        self.uptime_card: Optional[StatusCard] = None

        # Components
        self.system_messages_text: Optional[QTextEdit] = None
        self.recent_tests_table: Optional[QTableWidget] = None

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
        self.test_status_card = StatusCard("Test Status", "IDLE", "#7F8C8D")  # Gray initially

        self.uptime_card = StatusCard("System Uptime", "00:00:00", "#3498DB")  # Blue

        # Create system messages section with modern styling
        messages_group = QGroupBox("System Messages")
        messages_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #334155;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #F8FAFC);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background: transparent;
            }
        """
        )
        messages_layout = QVBoxLayout(messages_group)
        messages_layout.setContentsMargins(16, 20, 16, 16)

        self.system_messages_text = QTextEdit()
        self.system_messages_text.setReadOnly(True)
        self.system_messages_text.setMaximumHeight(180)
        self.system_messages_text.setFont(QFont("JetBrains Mono", 10))
        self.system_messages_text.setStyleSheet(
            """
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #1E293B, stop: 1 #334155);
                color: #F1F5F9;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 12px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                selection-background-color: #667EEA;
                selection-color: white;
            }
            QScrollBar:vertical {
                background: #475569;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #64748B;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """
        )

        messages_layout.addWidget(self.system_messages_text)

        # Create recent tests section with modern styling
        tests_group = QGroupBox("Recent Test Results")
        tests_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #334155;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #F8FAFC);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background: transparent;
            }
        """
        )
        tests_layout = QVBoxLayout(tests_group)
        tests_layout.setContentsMargins(16, 20, 16, 16)

        self.recent_tests_table = QTableWidget()
        self.recent_tests_table.setColumnCount(4)
        self.recent_tests_table.setHorizontalHeaderLabels(
            ["Time", "Test Type", "Status", "Duration"]
        )
        self.recent_tests_table.setMaximumHeight(220)
        self.recent_tests_table.setAlternatingRowColors(True)
        self.recent_tests_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recent_tests_table.setStyleSheet(
            """
            QTableWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #FAFBFC);
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #EEF2FF, stop: 1 #E0E7FF);
                color: #3730A3;
            }
            QTableWidget::item:alternate {
                background: #F8FAFC;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #F8FAFC, stop: 1 #E2E8F0);
                color: #475569;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #CBD5E1;
                font-weight: 600;
                font-size: 11px;
            }
            QScrollBar:vertical {
                background: #F1F5F9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
        """
        )

        # Set column widths
        self.recent_tests_table.setColumnWidth(0, 120)
        self.recent_tests_table.setColumnWidth(1, 150)
        self.recent_tests_table.setColumnWidth(2, 100)
        self.recent_tests_table.setColumnWidth(3, 100)

        tests_layout.addWidget(self.recent_tests_table)

        # Quick actions section removed

        # Store group references
        self.messages_group = messages_group
        self.tests_group = tests_group

    def setup_layout(self) -> None:
        """Setup widget layout"""
        # Create scroll area for entire dashboard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Main layout for content - improved spacing
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(32)

        # Status cards section with modern styling
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(24)
        cards_layout.setContentsMargins(0, 0, 0, 0)

        # Add status cards in 1x2 grid with None checks
        if self.test_status_card:
            cards_layout.addWidget(self.test_status_card, 0, 0)
        if self.uptime_card:
            cards_layout.addWidget(self.uptime_card, 0, 1)

        main_layout.addWidget(cards_widget)

        # Content sections with improved spacing
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(self.messages_group)

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

        # Quick action button signals removed

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
        Handle hardware status change (currently unused after hardware cards removal)

        Args:
            hardware_status: Hardware status object
        """
        # Hardware status display has been removed from dashboard
        # hardware_status is intentionally unused
        _ = hardware_status
        pass

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
        Update hardware status display (currently unused after hardware cards removal)

        Args:
            hardware_status: Hardware status object
        """
        # Hardware status cards have been removed from dashboard
        # Hardware status is now available only through the Hardware panel
        # hardware_status is intentionally unused
        _ = hardware_status
        pass

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

        # Set color based on status - consistent with modern palette
        if status == "completed":
            color = "#10B981"  # Modern green
        elif status in ["failed", "error"]:
            color = "#EF4444"  # Modern red
        elif status == "running":
            color = "#667EEA"  # Modern blue/purple
        elif status == "cancelled":
            color = "#F59E0B"  # Modern amber
        else:  # idle, ready
            color = "#94A3B8"  # Modern gray

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
