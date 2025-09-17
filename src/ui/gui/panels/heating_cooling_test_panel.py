"""
Heating Cooling Time Test Panel for WF EOL Tester GUI

Panel for executing heating and cooling time tests with real-time monitoring.
"""

# Standard library imports
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
from application.use_cases.heating_cooling_time_test import (
    HeatingCoolingTimeTestInput,
    HeatingCoolingTimeTestUseCase,
)
from ui.gui.services.gui_state_manager import GUIStateManager, TestStatus


class HeatingCoolingTestWorker(QObject):
    """Worker thread for heating cooling test execution"""

    # Signals
    test_started = Signal()
    test_progress = Signal(int, str)  # progress, message
    test_completed = Signal(object)  # test_result
    test_failed = Signal(str)  # error_message

    def __init__(
        self, use_case: HeatingCoolingTimeTestUseCase, test_input: HeatingCoolingTimeTestInput
    ):
        """
        Initialize test worker

        Args:
            use_case: Heating cooling test use case
            test_input: Test input parameters
        """
        super().__init__()
        self.use_case = use_case
        self.test_input = test_input
        self.is_cancelled = False

    def run_test(self) -> None:
        """Execute the heating cooling test"""
        try:
            self.test_started.emit()
            logger.info("Starting heating cooling time test")

            # Execute test (this would be async in real implementation)
            result = self.use_case.execute(self.test_input)

            if not self.is_cancelled:
                self.test_completed.emit(result)
                logger.info("Heating cooling time test completed successfully")

        except Exception as e:
            if not self.is_cancelled:
                error_msg = f"Heating cooling test failed: {str(e)}"
                logger.error(error_msg)
                self.test_failed.emit(error_msg)

    def cancel_test(self) -> None:
        """Cancel the running test"""
        self.is_cancelled = True
        logger.info("Heating cooling test cancelled")


class HeatingCoolingTestPanel(QWidget):
    """
    Heating Cooling Time Test panel widget

    Provides interface for:
    - Test parameter configuration
    - Test execution controls
    - Real-time progress monitoring
    - Test results display
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
        Initialize heating cooling test panel

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager
        self.use_case = container.heating_cooling_time_test_use_case()

        # Test execution components
        self.test_worker: Optional[HeatingCoolingTestWorker] = None
        self.test_thread: Optional[QThread] = None

        # UI Components
        self.start_test_button: Optional[QPushButton] = None
        self.stop_test_button: Optional[QPushButton] = None
        self.test_progress_bar: Optional[QProgressBar] = None
        self.test_status_label: Optional[QLabel] = None
        self.test_log: Optional[QTextEdit] = None
        self.results_table: Optional[QTableWidget] = None

        # Test parameters
        self.heating_temp_input: Optional[QSpinBox] = None
        self.cooling_temp_input: Optional[QSpinBox] = None
        self.test_duration_input: Optional[QSpinBox] = None
        self.cycle_count_input: Optional[QSpinBox] = None

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()
        self.setup_timers()

        logger.debug("Heating cooling test panel initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # === TEST PARAMETERS SECTION ===
        params_group = QGroupBox("Test Parameters")

        # Temperature settings
        self.heating_temp_input = QSpinBox()
        self.heating_temp_input.setRange(20, 150)
        self.heating_temp_input.setValue(80)
        self.heating_temp_input.setSuffix(" °C")

        self.cooling_temp_input = QSpinBox()
        self.cooling_temp_input.setRange(-20, 50)
        self.cooling_temp_input.setValue(10)
        self.cooling_temp_input.setSuffix(" °C")

        # Test duration and cycles
        self.test_duration_input = QSpinBox()
        self.test_duration_input.setRange(1, 3600)
        self.test_duration_input.setValue(60)
        self.test_duration_input.setSuffix(" sec")

        self.cycle_count_input = QSpinBox()
        self.cycle_count_input.setRange(1, 100)
        self.cycle_count_input.setValue(5)

        # === CONTROL SECTION ===
        control_group = QGroupBox("Test Control")

        self.start_test_button = QPushButton("Start Heating Cooling Test")
        self.start_test_button.setProperty("class", "success")
        self.start_test_button.setMinimumHeight(50)
        self.start_test_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.setProperty("class", "danger")
        self.stop_test_button.setMinimumHeight(50)
        self.stop_test_button.setEnabled(False)

        # === STATUS SECTION ===
        status_group = QGroupBox("Test Status")

        self.test_status_label = QLabel("Ready to start")
        self.test_status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.test_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.test_progress_bar = QProgressBar()
        self.test_progress_bar.setVisible(False)
        self.test_progress_bar.setTextVisible(True)

        # === LOG SECTION ===
        log_group = QGroupBox("Test Log")

        self.test_log = QTextEdit()
        self.test_log.setReadOnly(True)
        self.test_log.setMaximumHeight(200)
        self.test_log.setFont(QFont("Consolas", 9))
        self.test_log.setStyleSheet(
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

        # === RESULTS SECTION ===
        results_group = QGroupBox("Test Results")

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(
            ["Cycle", "Heating Time", "Cooling Time", "Status"]
        )
        self.results_table.setMaximumHeight(200)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Store group references
        self.params_group = params_group
        self.control_group = control_group
        self.status_group = status_group
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

        # Parameters section layout
        params_layout = QGridLayout(self.params_group)
        params_layout.addWidget(QLabel("Heating Temperature:"), 0, 0)
        params_layout.addWidget(self.heating_temp_input, 0, 1)
        params_layout.addWidget(QLabel("Cooling Temperature:"), 0, 2)
        params_layout.addWidget(self.cooling_temp_input, 0, 3)
        params_layout.addWidget(QLabel("Duration per Phase:"), 1, 0)
        params_layout.addWidget(self.test_duration_input, 1, 1)
        params_layout.addWidget(QLabel("Number of Cycles:"), 1, 2)
        params_layout.addWidget(self.cycle_count_input, 1, 3)

        # Control section layout
        control_layout = QHBoxLayout(self.control_group)
        control_layout.addWidget(self.start_test_button)
        control_layout.addWidget(self.stop_test_button)
        control_layout.addStretch()

        # Status section layout
        status_layout = QVBoxLayout(self.status_group)
        status_layout.addWidget(self.test_status_label)
        status_layout.addWidget(self.test_progress_bar)

        # Log section layout
        log_layout = QVBoxLayout(self.log_group)
        log_layout.addWidget(self.test_log)

        # Results section layout
        results_layout = QVBoxLayout(self.results_group)
        results_layout.addWidget(self.results_table)

        # Add sections to main layout
        main_layout.addWidget(self.params_group)
        main_layout.addWidget(self.control_group)
        main_layout.addWidget(self.status_group)

        # Bottom sections in horizontal layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.log_group, 1)
        bottom_layout.addWidget(self.results_group, 1)
        main_layout.addLayout(bottom_layout)

        main_layout.addStretch()

        # Set main layout
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Control button signals
        if self.start_test_button:
            self.start_test_button.clicked.connect(self.start_test)

        if self.stop_test_button:
            self.stop_test_button.clicked.connect(self.stop_test)

        # State manager signals
        if self.state_manager:
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)

    def setup_timers(self) -> None:
        """Setup update timers"""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second

    def start_test(self) -> None:
        """Start heating cooling time test"""
        try:
            self.add_log("Preparing heating cooling time test...")

            # Create test input
            test_input = HeatingCoolingTimeTestInput(
                heating_temperature=self.heating_temp_input.value(),
                cooling_temperature=self.cooling_temp_input.value(),
                duration_per_phase=self.test_duration_input.value(),
                number_of_cycles=self.cycle_count_input.value(),
            )

            # Create worker and thread
            self.test_worker = HeatingCoolingTestWorker(self.use_case, test_input)
            self.test_thread = QThread()
            self.test_worker.moveToThread(self.test_thread)

            # Connect worker signals
            self.test_worker.test_started.connect(self.on_test_started)
            self.test_worker.test_progress.connect(self.on_test_progress)
            self.test_worker.test_completed.connect(self.on_test_completed)
            self.test_worker.test_failed.connect(self.on_test_failed)

            # Connect thread signals
            self.test_thread.started.connect(self.test_worker.run_test)
            self.test_thread.finished.connect(self.cleanup_test_thread)

            # Start test
            self.test_thread.start()

            # Update UI state
            self.start_test_button.setEnabled(False)
            self.stop_test_button.setEnabled(True)

            self.status_message.emit("Heating cooling test started")
            logger.info("Heating cooling time test initiated")

        except Exception as e:
            logger.error(f"Failed to start heating cooling test: {e}")
            self.add_log(f"Test start failed: {e}")
            self.status_message.emit(f"Test start failed: {e}")

    def stop_test(self) -> None:
        """Stop the running test"""
        try:
            if self.test_worker:
                self.test_worker.cancel_test()

            if self.test_thread and self.test_thread.isRunning():
                self.test_thread.quit()
                self.test_thread.wait(5000)  # Wait up to 5 seconds

            self.cleanup_test_thread()
            self.add_log("Test stopped by user")
            self.status_message.emit("Test stopped")
            logger.info("Heating cooling test stopped by user")

        except Exception as e:
            logger.error(f"Failed to stop test: {e}")
            self.add_log(f"Failed to stop test: {e}")

    def on_test_started(self) -> None:
        """Handle test started signal"""
        self.test_status_label.setText("Running...")
        self.test_status_label.setStyleSheet("color: #3498DB; font-weight: bold;")
        self.test_progress_bar.setVisible(True)
        self.test_progress_bar.setValue(0)
        self.clear_results()
        self.add_log("Heating cooling time test started")

    def on_test_progress(self, progress: int, message: str) -> None:
        """Handle test progress update"""
        self.test_progress_bar.setValue(progress)
        self.add_log(f"Progress: {message} ({progress}%)")

    def on_test_completed(self, result) -> None:
        """Handle test completion"""
        self.test_status_label.setText("Completed")
        self.test_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        self.test_progress_bar.setValue(100)

        self.display_results(result)
        self.add_log("Test completed successfully")
        self.cleanup_test_thread()

        self.status_message.emit("Heating cooling test completed")

    def on_test_failed(self, error_message: str) -> None:
        """Handle test failure"""
        self.test_status_label.setText("Failed")
        self.test_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        self.test_progress_bar.setVisible(False)

        self.add_log(f"Test failed: {error_message}")
        self.cleanup_test_thread()

        self.status_message.emit(f"Test failed: {error_message}")

    def cleanup_test_thread(self) -> None:
        """Clean up test thread and worker"""
        if self.test_thread:
            self.test_thread.quit()
            self.test_thread.wait()
            self.test_thread = None

        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None

        # Reset UI state
        self.start_test_button.setEnabled(True)
        self.stop_test_button.setEnabled(False)

    def display_results(self, result) -> None:
        """Display test results in table"""
        if not result or not hasattr(result, "cycle_results"):
            return

        self.results_table.setRowCount(len(result.cycle_results))

        for i, cycle_result in enumerate(result.cycle_results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{cycle_result.heating_time:.1f}s"))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{cycle_result.cooling_time:.1f}s"))
            self.results_table.setItem(
                i, 3, QTableWidgetItem("PASS" if cycle_result.passed else "FAIL")
            )

    def clear_results(self) -> None:
        """Clear results table"""
        self.results_table.setRowCount(0)

    def add_log(self, message: str) -> None:
        """Add message to test log"""
        if self.test_log:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.test_log.append(formatted_message)

            # Auto-scroll to bottom
            cursor = self.test_log.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.test_log.setTextCursor(cursor)

    def on_test_status_changed(self, status: str) -> None:
        """Handle test status change from state manager"""
        # Update UI based on global test status if needed
        pass

    def update_status(self) -> None:
        """Update panel status (called by timer)"""
        # Periodic status updates if needed
        pass

    def activate_panel(self) -> None:
        """Called when panel becomes active"""
        logger.debug("Heating cooling test panel activated")

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        if self.test_thread and self.test_thread.isRunning():
            self.stop_test()
        self.status_message.emit("Emergency stop - Heating cooling test terminated")
        logger.warning("Emergency stop: Heating cooling test terminated")

    def handle_resize(self) -> None:
        """Handle panel resize"""
        # Could adjust layouts based on panel size
        pass
