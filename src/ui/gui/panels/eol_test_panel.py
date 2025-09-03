"""
EOL Test Panel for WF EOL Tester GUI

Panel for executing end-of-line force tests with real-time progress monitoring.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
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
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from application.containers.application_container import ApplicationContainer
from application.use_cases.eol_force_test import (
    EOLForceTestInput,
    EOLForceTestUseCase,
)
from ui.gui.services.gui_state_manager import GUIStateManager, TestStatus


class EOLTestWorker(QObject):
    """Worker thread for EOL test execution"""

    # Signals
    test_started = Signal()
    test_progress = Signal(int, str)  # progress, message
    test_completed = Signal(object)  # test_result
    test_failed = Signal(str)  # error_message

    def __init__(self, use_case: EOLForceTestUseCase, command: EOLForceTestInput):
        """
        Initialize EOL test worker

        Args:
            use_case: EOL test use case
            command: Test command
        """
        super().__init__()
        self.use_case = use_case
        self.command = command
        self._should_stop = False

    def stop_test(self) -> None:
        """Request test stop"""
        self._should_stop = True

    def run_test(self) -> None:
        """Execute EOL test"""
        try:
            self.test_started.emit()

            # Create event loop for async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Run test
                result = loop.run_until_complete(self.use_case.execute(self.command))

                if not self._should_stop:
                    self.test_completed.emit(result)

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"EOL test execution failed: {e}")
            self.test_failed.emit(str(e))


class EOLTestPanel(QWidget):
    """
    EOL Test panel widget

    Provides interface for:
    - Test parameter configuration
    - Test execution control
    - Real-time progress monitoring
    - Result display and analysis
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
        Initialize EOL test panel

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager

        # Get use case
        self.eol_use_case = container.eol_force_test_use_case()

        # Test execution components
        self.test_worker: Optional[EOLTestWorker] = None
        self.test_thread: Optional[QThread] = None

        # UI components
        # Configuration section
        self.operator_id_input: Optional[QLineEdit] = None
        self.test_mode_combo: Optional[QComboBox] = None
        self.serial_number_input: Optional[QLineEdit] = None

        # Control buttons
        self.start_test_button: Optional[QPushButton] = None
        self.stop_test_button: Optional[QPushButton] = None
        self.reset_button: Optional[QPushButton] = None

        # Progress monitoring
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None
        self.test_log_text: Optional[QTextEdit] = None

        # Results display
        self.results_table: Optional[QTableWidget] = None
        self.summary_label: Optional[QLabel] = None

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()

        # Initialize state
        self.reset_test_ui()

        logger.debug("EOL test panel initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # === CONFIGURATION SECTION ===
        config_group = QGroupBox("Test Configuration")
        config_layout = QGridLayout(config_group)

        # Operator ID
        config_layout.addWidget(QLabel("Operator ID:"), 0, 0)
        self.operator_id_input = QLineEdit()
        self.operator_id_input.setPlaceholderText("Enter operator ID")
        self.operator_id_input.setText("gui_user")
        config_layout.addWidget(self.operator_id_input, 0, 1)

        # Test mode
        config_layout.addWidget(QLabel("Test Mode:"), 1, 0)
        self.test_mode_combo = QComboBox()
        self.test_mode_combo.addItems(["Standard", "Extended", "Debug"])
        config_layout.addWidget(self.test_mode_combo, 1, 1)

        # Serial number
        config_layout.addWidget(QLabel("Serial Number:"), 2, 0)
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setPlaceholderText("Optional serial number")
        config_layout.addWidget(self.serial_number_input, 2, 1)

        # === CONTROL SECTION ===
        control_group = QGroupBox("Test Control")
        control_layout = QHBoxLayout(control_group)

        self.start_test_button = QPushButton("Start EOL Test")
        self.start_test_button.setProperty("class", "success")
        self.start_test_button.setMinimumHeight(50)
        self.start_test_button.setAccessibleName("Start EOL Force Test")

        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.setProperty("class", "danger")
        self.stop_test_button.setMinimumHeight(50)
        self.stop_test_button.setEnabled(False)
        self.stop_test_button.setAccessibleName("Stop Running Test")

        self.reset_button = QPushButton("Reset")
        self.reset_button.setProperty("class", "warning")
        self.reset_button.setMinimumHeight(50)
        self.reset_button.setAccessibleName("Reset Test State")

        control_layout.addWidget(self.start_test_button)
        control_layout.addWidget(self.stop_test_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addStretch()

        # === PROGRESS SECTION ===
        progress_group = QGroupBox("Test Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.status_label = QLabel("Ready to start test")
        self.status_label.setFont(QFont("Arial", 11, QFont.Weight.DemiBold))
        self.status_label.setStyleSheet("color: #2C3E50; padding: 4px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(30)

        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)

        # === TEST LOG SECTION ===
        log_group = QGroupBox("Test Log")
        log_layout = QVBoxLayout(log_group)

        self.test_log_text = QTextEdit()
        self.test_log_text.setReadOnly(True)
        self.test_log_text.setMaximumHeight(200)
        self.test_log_text.setFont(QFont("Consolas", 9))
        self.test_log_text.setStyleSheet(
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

        log_layout.addWidget(self.test_log_text)

        # === RESULTS SECTION ===
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_group)

        self.summary_label = QLabel("No test results available")
        self.summary_label.setFont(QFont("Arial", 10, QFont.Weight.DemiBold))
        self.summary_label.setStyleSheet("color: #7F8C8D; padding: 4px;")

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Step", "Description", "Result", "Value"])
        self.results_table.setMaximumHeight(200)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Set column widths
        self.results_table.setColumnWidth(0, 50)
        self.results_table.setColumnWidth(1, 200)
        self.results_table.setColumnWidth(2, 80)
        self.results_table.setColumnWidth(3, 120)

        results_layout.addWidget(self.summary_label)
        results_layout.addWidget(self.results_table)

        # Store group references
        self.config_group = config_group
        self.control_group = control_group
        self.progress_group = progress_group
        self.log_group = log_group
        self.results_group = results_group

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

        # Top section - Configuration and Control
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.config_group, 2)
        top_layout.addWidget(self.control_group, 1)

        main_layout.addLayout(top_layout)

        # Progress section
        main_layout.addWidget(self.progress_group)

        # Bottom section - Log and Results
        bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        bottom_splitter.addWidget(self.log_group)
        bottom_splitter.addWidget(self.results_group)
        bottom_splitter.setSizes([200, 250])

        main_layout.addWidget(bottom_splitter)

        # Set main layout
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Button signals
        if self.start_test_button:
            self.start_test_button.clicked.connect(self.start_test)

        if self.stop_test_button:
            self.stop_test_button.clicked.connect(self.stop_test)

        if self.reset_button:
            self.reset_button.clicked.connect(self.reset_test)

        # State manager signals
        if self.state_manager:
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.test_progress_changed.connect(self.on_test_progress_changed)

    def start_test(self) -> None:
        """Start EOL test execution"""
        try:
            # Validate inputs
            operator_id = self.operator_id_input.text().strip()
            if not operator_id:
                self.status_message.emit("Operator ID is required")
                return

            # Check if hardware is ready
            hardware_status = self.state_manager.hardware_status
            if hardware_status.overall_status.value != "connected":
                self.status_message.emit("Hardware not ready. Check connections.")
                return

            # Create test command
            command = EOLForceTestInput(
                operator_id=operator_id,
                serial_number=self.serial_number_input.text().strip() or None,
            )

            # Setup worker thread
            self.test_worker = EOLTestWorker(self.eol_use_case, command)
            self.test_thread = QThread()

            # Move worker to thread
            self.test_worker.moveToThread(self.test_thread)

            # Connect worker signals
            self.test_worker.test_started.connect(self.on_test_started)
            self.test_worker.test_progress.connect(self.on_worker_progress)
            self.test_worker.test_completed.connect(self.on_test_completed)
            self.test_worker.test_failed.connect(self.on_test_failed)

            # Connect thread signals
            self.test_thread.started.connect(self.test_worker.run_test)
            self.test_thread.finished.connect(self.test_thread.deleteLater)

            # Start thread
            self.test_thread.start()

            # Update UI
            self.update_ui_for_test_start()

            # Update state manager
            self.state_manager.set_test_status(TestStatus.PREPARING, "Initializing EOL test...")

            logger.info(f"EOL test started - Operator: {operator_id}")

        except Exception as e:
            logger.error(f"Failed to start EOL test: {e}")
            self.status_message.emit(f"Failed to start test: {e}")

    def stop_test(self) -> None:
        """Stop running test"""
        try:
            if self.test_worker:
                self.test_worker.stop_test()

            if self.test_thread and self.test_thread.isRunning():
                self.test_thread.quit()
                self.test_thread.wait(5000)  # Wait up to 5 seconds

            # Update state
            self.state_manager.set_test_status(TestStatus.CANCELLED, "Test stopped by user")

            # Update UI
            self.update_ui_for_test_stop()

            self.add_log_message("Test stopped by user")
            logger.info("EOL test stopped by user")

        except Exception as e:
            logger.error(f"Failed to stop test: {e}")
            self.status_message.emit(f"Failed to stop test: {e}")

    def reset_test(self) -> None:
        """Reset test state"""
        try:
            # Stop any running test
            if self.test_thread and self.test_thread.isRunning():
                self.stop_test()

            # Reset UI
            self.reset_test_ui()

            # Reset state manager
            self.state_manager.reset_test_state()

            self.status_message.emit("Test state reset")
            logger.info("EOL test state reset")

        except Exception as e:
            logger.error(f"Failed to reset test: {e}")
            self.status_message.emit(f"Failed to reset test: {e}")

    def update_ui_for_test_start(self) -> None:
        """Update UI when test starts"""
        if self.start_test_button:
            self.start_test_button.setEnabled(False)

        if self.stop_test_button:
            self.stop_test_button.setEnabled(True)

        if self.reset_button:
            self.reset_button.setEnabled(False)

        # Clear previous results
        if self.results_table:
            self.results_table.setRowCount(0)

        if self.summary_label:
            self.summary_label.setText("Test in progress...")
            self.summary_label.setStyleSheet("color: #3498DB; padding: 4px;")

    def update_ui_for_test_stop(self) -> None:
        """Update UI when test stops"""
        if self.start_test_button:
            self.start_test_button.setEnabled(True)

        if self.stop_test_button:
            self.stop_test_button.setEnabled(False)

        if self.reset_button:
            self.reset_button.setEnabled(True)

    def reset_test_ui(self) -> None:
        """Reset UI to initial state"""
        # Reset buttons
        if self.start_test_button:
            self.start_test_button.setEnabled(True)

        if self.stop_test_button:
            self.stop_test_button.setEnabled(False)

        if self.reset_button:
            self.reset_button.setEnabled(True)

        # Reset progress
        if self.progress_bar:
            self.progress_bar.setValue(0)

        if self.status_label:
            self.status_label.setText("Ready to start test")
            self.status_label.setStyleSheet("color: #2C3E50; padding: 4px;")

        # Clear log
        if self.test_log_text:
            self.test_log_text.clear()
            self.add_log_message("Test log initialized")

        # Clear results
        if self.results_table:
            self.results_table.setRowCount(0)

        if self.summary_label:
            self.summary_label.setText("No test results available")
            self.summary_label.setStyleSheet("color: #7F8C8D; padding: 4px;")

    def on_test_started(self) -> None:
        """Handle test started signal"""
        self.add_log_message("EOL force test started")
        self.state_manager.set_test_status(TestStatus.RUNNING, "EOL test running")

    def on_worker_progress(self, progress: int, message: str) -> None:
        """Handle test progress from worker"""
        self.state_manager.update_test_progress(progress, message)
        self.add_log_message(f"Progress: {progress}% - {message}")

    def on_test_completed(self, result) -> None:
        """Handle test completion"""
        try:
            # Update state manager
            self.state_manager.set_test_result(
                result.__dict__ if hasattr(result, "__dict__") else {}
            )

            # Update UI
            self.update_ui_for_test_stop()
            self.display_test_results(result)

            # Log completion
            status = "PASSED" if result.is_passed else "FAILED"
            duration = (
                result.execution_duration.seconds if hasattr(result, "execution_duration") else 0
            )

            self.add_log_message(f"Test completed: {status} (Duration: {duration:.1f}s)")

            logger.info(f"EOL test completed - Status: {status}")

        except Exception as e:
            logger.error(f"Error handling test completion: {e}")
            self.on_test_failed(str(e))

    def on_test_failed(self, error_message: str) -> None:
        """Handle test failure"""
        self.state_manager.set_test_status(TestStatus.FAILED, f"Test failed: {error_message}")
        self.update_ui_for_test_stop()
        self.add_log_message(f"Test failed: {error_message}")

        # Update summary
        if self.summary_label:
            self.summary_label.setText(f"Test Failed: {error_message}")
            self.summary_label.setStyleSheet("color: #E74C3C; padding: 4px;")

        logger.error(f"EOL test failed: {error_message}")

    def display_test_results(self, result) -> None:
        """
        Display test results in the results table

        Args:
            result: Test result object
        """
        if not self.results_table or not self.summary_label:
            return

        try:
            # Update summary
            status = "PASSED" if result.is_passed else "FAILED"
            color = "#27AE60" if result.is_passed else "#E74C3C"

            duration = (
                result.execution_duration.seconds if hasattr(result, "execution_duration") else 0
            )
            self.summary_label.setText(f"Test {status} - Duration: {duration:.1f}s")
            self.summary_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 4px;")

            # Clear existing results
            self.results_table.setRowCount(0)

            # Add result rows (this would be customized based on actual result structure)
            if hasattr(result, "test_results") and result.test_results:
                for i, step_result in enumerate(result.test_results):
                    self.results_table.insertRow(i)

                    # Extract step information
                    step_name = step_result.get("name", f"Step {i+1}")
                    description = step_result.get("description", "N/A")
                    success = step_result.get("success", False)
                    value = step_result.get("value", step_result.get("response_time_ms", "N/A"))

                    # Create items
                    self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.results_table.setItem(i, 1, QTableWidgetItem(description))
                    self.results_table.setItem(
                        i, 2, QTableWidgetItem("PASS" if success else "FAIL")
                    )
                    self.results_table.setItem(i, 3, QTableWidgetItem(str(value)))

                    # Color code result column
                    result_item = self.results_table.item(i, 2)
                    if success:
                        result_item.setForeground(Qt.GlobalColor.darkGreen)
                    else:
                        result_item.setForeground(Qt.GlobalColor.darkRed)

            else:
                # Add single summary row
                self.results_table.insertRow(0)
                self.results_table.setItem(0, 0, QTableWidgetItem("1"))
                self.results_table.setItem(0, 1, QTableWidgetItem("EOL Force Test"))
                self.results_table.setItem(0, 2, QTableWidgetItem(status))
                self.results_table.setItem(0, 3, QTableWidgetItem(f"{duration:.1f}s"))

        except Exception as e:
            logger.error(f"Failed to display test results: {e}")
            self.summary_label.setText(f"Results display error: {e}")
            self.summary_label.setStyleSheet("color: #E74C3C; padding: 4px;")

    def add_log_message(self, message: str) -> None:
        """
        Add message to test log

        Args:
            message: Message to add
        """
        if self.test_log_text:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            formatted_message = f"[{timestamp}] {message}"

            self.test_log_text.append(formatted_message)

            # Auto-scroll to bottom
            cursor = self.test_log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.test_log_text.setTextCursor(cursor)

    def on_test_status_changed(self, status: str) -> None:
        """Handle test status change from state manager"""
        if self.status_label:
            self.status_label.setText(f"Status: {status.title()}")

            # Update color based on status
            if status == "completed":
                color = "#27AE60"  # Green
            elif status in ["failed", "error"]:
                color = "#E74C3C"  # Red
            elif status == "running":
                color = "#3498DB"  # Blue
            elif status == "cancelled":
                color = "#F39C12"  # Orange
            else:  # idle, ready, preparing
                color = "#2C3E50"  # Dark gray

            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 4px;")

    def on_test_progress_changed(self, progress: int, message: str) -> None:
        """Handle test progress change from state manager"""
        if self.progress_bar:
            self.progress_bar.setValue(progress)

            if message:
                self.progress_bar.setFormat(f"{progress}% - {message}")
            else:
                self.progress_bar.setFormat(f"{progress}%")

    def activate_panel(self) -> None:
        """Called when panel becomes active"""
        # Reset to ready state if idle
        if self.state_manager.test_status == TestStatus.IDLE:
            self.reset_test_ui()

        logger.debug("EOL test panel activated")

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        if self.test_thread and self.test_thread.isRunning():
            self.stop_test()

        self.add_log_message("EMERGENCY STOP ACTIVATED")
        logger.warning("EOL test panel: Emergency stop executed")

    def handle_resize(self) -> None:
        """Handle panel resize"""
        # Could adjust splitter sizes based on panel size
        pass

    def refresh_panel(self) -> None:
        """Refresh panel data"""
        # Could refresh configuration or status if needed
        self.status_message.emit("EOL test panel refreshed")
