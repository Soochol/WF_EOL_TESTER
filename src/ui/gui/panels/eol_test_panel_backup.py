"""
EOL Test Panel for WF EOL Tester GUI

Panel for executing end-of-line force tests with real-time progress monitoring.
"""

# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
from pathlib import Path

import yaml
from loguru import logger

# Local application imports
from application.containers.application_container import ApplicationContainer
from application.use_cases.eol_force_test import (
    EOLForceTestInput,
    EOLForceTestUseCase,
)
from domain.value_objects.dut_command_info import DUTCommandInfo
from ui.gui.services.gui_state_manager import GUIStateManager, TestStatus


class SerialNumberDialog(QDialog):
    """Modal dialog for serial number input"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Number Input")
        self.setModal(True)
        self.setFixedSize(350, 150)

        # Center on parent
        if parent:
            self.move(parent.geometry().center() - self.rect().center())

        self.setup_ui()
        self.serial_number = ""

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Serial number input
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter serial number...")
        self.serial_input.setMinimumHeight(32)
        self.serial_input.textChanged.connect(self.validate_input)

        form_layout.addRow("Serial Number:", self.serial_input)
        layout.addLayout(form_layout)

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept_dialog)
        self.button_box.rejected.connect(self.reject)

        # Initially disable OK button
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.button_box)

        # Focus on input
        self.serial_input.setFocus()

    def validate_input(self):
        """Validate serial number input"""
        text = self.serial_input.text().strip()
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(len(text) > 0)

    def accept_dialog(self):
        """Accept dialog and save serial number"""
        self.serial_number = self.serial_input.text().strip()
        self.accept()

    def get_serial_number(self) -> str:
        """Get entered serial number"""
        return self.serial_number


class EOLTestWorker(QObject):
    """Worker thread for EOL test execution"""

    # Signals
    test_started = Signal()
    test_progress = Signal(int, str)  # progress, message
    test_completed = Signal(object)  # test_result
    test_failed = Signal(str)  # error_message
    log_message = Signal(str)  # log message for GUI display

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
        self._log_handler_id = None

    def stop_test(self) -> None:
        """Request test stop"""
        self._should_stop = True
        self._remove_gui_log_handler()

    def _add_gui_log_handler(self) -> None:
        """Add loguru handler to capture logs for GUI display"""
        if self._log_handler_id is None:
            self._log_handler_id = logger.add(
                self._emit_log_message,
                level="INFO",
                format="{time:HH:mm:ss.SSS} | {level: <8} | {message}",
                filter=self._should_capture_log,
                catch=False,
            )

    def _remove_gui_log_handler(self) -> None:
        """Remove GUI log handler"""
        if self._log_handler_id is not None:
            try:
                logger.remove(self._log_handler_id)
            except ValueError:
                pass  # Handler already removed
            self._log_handler_id = None

    def _emit_log_message(self, message) -> None:
        """Emit log message to GUI"""
        try:
            self.log_message.emit(str(message))
        except Exception:
            pass  # Ignore errors during GUI emission

    def _should_capture_log(self, record) -> bool:
        """Filter logs to capture only INFO level test-related messages"""
        # Only capture INFO level logs
        log_level = record.get("level", {}).get("name", "")
        if log_level != "INFO":
            return False
        
        # Capture logs from test execution components
        relevant_modules = [
            "application.use_cases.eol_force_test",
            "application.services.hardware_facade",
            "infrastructure.implementation.hardware",
            "GUI",
        ]
        module_name = record.get("name", "")
        message = record.get("message", "")

        # Capture relevant modules or messages containing test info
        is_relevant_module = any(module in module_name for module in relevant_modules)
        is_test_message = any(
            keyword in message.lower()
            for keyword in ["test", "robot", "power", "measurement", "force", "loadcell", "dio"]
        )

        return is_relevant_module or is_test_message

    def run_test(self) -> None:
        """Execute EOL test"""
        try:
            self.test_started.emit()

            # Add GUI log handler to capture test logs
            self._add_gui_log_handler()

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
                # Remove GUI log handler
                self._remove_gui_log_handler()

        except Exception as e:
            logger.error(f"EOL test execution failed: {e}")
            self.test_failed.emit(str(e))
            # Ensure log handler is removed even on error
            self._remove_gui_log_handler()


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
        # Configuration section - removed (using modal dialog for serial number)

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

        # === CONTROL SECTION ===
        control_group = QGroupBox("Test Control")
        control_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """
        )
        control_layout = QVBoxLayout(control_group)
        control_layout.setContentsMargins(16, 20, 16, 16)
        control_layout.setSpacing(8)  # Increased spacing between buttons

        self.start_test_button = QPushButton("Start EOL Test")
        self.start_test_button.setProperty("class", "success")
        self.start_test_button.setFixedHeight(29)
        self.start_test_button.setStyleSheet(
            """
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """
        )
        self.start_test_button.setAccessibleName("Start EOL Force Test")

        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.setProperty("class", "danger")
        self.stop_test_button.setFixedHeight(29)
        self.stop_test_button.setStyleSheet(
            """
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #CD4335;
            }
            QPushButton:pressed {
                background-color: #B03A2E;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """
        )
        self.stop_test_button.setEnabled(False)
        self.stop_test_button.setAccessibleName("Stop Running Test")

        self.reset_button = QPushButton("Reset")
        self.reset_button.setProperty("class", "warning")
        self.reset_button.setFixedHeight(29)
        self.reset_button.setStyleSheet(
            """
            QPushButton {
                background-color: #F39C12;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E67E22;
            }
            QPushButton:pressed {
                background-color: #D35400;
            }
        """
        )
        self.reset_button.setAccessibleName("Reset Test State")

        control_layout.addWidget(self.start_test_button)
        control_layout.addSpacing(8)  # Add explicit spacing between buttons
        control_layout.addWidget(self.stop_test_button)
        control_layout.addSpacing(8)  # Add explicit spacing between buttons
        control_layout.addWidget(self.reset_button)
        control_layout.addStretch()

        # Set Control Group size policy to match Results Group  
        control_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred  # 가로: 확장  # 세로: 선호
        )
        # Remove height restriction to allow natural sizing
        # control_group.setMaximumHeight(220)

        # === PROGRESS SECTION ===
        progress_group = QGroupBox("Test Progress")
        progress_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """
        )
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(16, 20, 16, 16)
        progress_layout.setSpacing(12)

        # Progress GroupBox만 세로 확장 방지
        progress_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed  # 가로: 확장  # 세로: 고정
        )

        self.status_label = QLabel("Ready to start test")
        self.status_label.setFont(QFont("Arial", 11, QFont.Weight.DemiBold))
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #2C3E50;
                padding: 8px;
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
            }
        """
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(32)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 6px;
            }
        """
        )

        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)

        # === TEST LOG SECTION ===
        log_group = QGroupBox("Test Log")
        log_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """
        )
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(16, 20, 16, 16)

        self.test_log_text = QTextEdit()
        self.test_log_text.setReadOnly(True)
        self.test_log_text.setMinimumHeight(150)  # 최소 높이만 설정
        self.test_log_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding  # 가로 확장  # 세로 확장
        )
        self.test_log_text.setFont(QFont("Consolas", 9))
        self.test_log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 2px solid #34495E;
                border-radius: 8px;
                padding: 12px;
                selection-background-color: #3498DB;
            }
        """
        )

        log_layout.addWidget(self.test_log_text)

        # === RESULTS SECTION ===
        results_group = QGroupBox("Test Results")
        results_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """
        )
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(16, 20, 16, 16)
        results_layout.setSpacing(12)

        # Results GroupBox도 세로 확장 방지
        results_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred  # 가로: 확장  # 세로: 선호
        )
        # Remove height restriction to allow natural sizing
        # results_group.setMaximumHeight(220)

        self.summary_label = QLabel("No test results available")
        self.summary_label.setFont(QFont("Arial", 11, QFont.Weight.DemiBold))
        self.summary_label.setStyleSheet(
            """
            QLabel {
                color: #7F8C8D;
                padding: 8px;
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
            }
        """
        )

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Step", "Description", "Result", "Value"])
        self.results_table.setMaximumHeight(200)  # 고정 최대 높이
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #E8E8E8;
                background-color: white;
                alternate-background-color: #F8F9FA;
                selection-background-color: #3498DB;
                border: 2px solid #E8E8E8;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """
        )

        # Optimize column widths for better layout
        self.results_table.setColumnWidth(0, 60)  # Step - slightly wider
        self.results_table.setColumnWidth(1, 180)  # Description - optimized
        self.results_table.setColumnWidth(2, 90)  # Result - slightly wider
        self.results_table.setColumnWidth(3, 140)  # Value - wider for numbers

        results_layout.addWidget(self.summary_label)
        results_layout.addWidget(self.results_table)

        # Store group references
        self.control_group = control_group
        self.progress_group = progress_group
        self.log_group = log_group
        self.results_group = results_group

    def setup_layout(self) -> None:
        """Setup professional widget layout"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Main layout for content with professional spacing
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(20)

        # Top row - Control and Results (side by side, equal size)
        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align both groups to top
        top_row.addWidget(self.control_group, 1)  # Equal ratio
        top_row.addWidget(self.results_group, 1)  # Equal ratio

        # Add top row to main layout
        main_layout.addLayout(top_row, 0)  # 고정 높이 (stretch = 0)

        # Middle row - Progress (full width)
        main_layout.addWidget(self.progress_group, 0)  # 고정 높이 (stretch = 0)

        # Bottom section - Test Log (세로 확장)
        main_layout.addWidget(self.log_group, 1)  # 세로 확장 (stretch = 1)

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
            # Check if hardware is ready
            hardware_status = self.state_manager.hardware_status
            if hardware_status.overall_status.value != "connected":
                self.status_message.emit("Hardware not ready. Check connections.")
                return

            # Get application config to check if serial number popup is required
            try:
                from domain.value_objects.application_config import ApplicationConfig

                config_path = Path("configuration/application.yaml")
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)
                    app_config = ApplicationConfig.from_dict(config_data)
                    require_popup = app_config.gui.require_serial_number_popup
                else:
                    require_popup = True  # Default to showing popup
            except Exception as e:
                logger.warning(f"Failed to load app config: {e}, using default")
                require_popup = True  # Default to showing popup

            # Get serial number from popup if required, otherwise use default
            serial_number = "GUI_SN"  # Default value
            if require_popup:
                dialog = SerialNumberDialog(self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    serial_number = dialog.get_serial_number()
                else:
                    # User cancelled the dialog
                    return

            # Create test command with default values
            dut_info = DUTCommandInfo(
                dut_id="GUI_DUT",
                model_number="GUI_MODEL",
                serial_number=serial_number,
                manufacturer="WF",
            )

            command = EOLForceTestInput(
                dut_info=dut_info,
                operator_id="DEFAULT_OPERATOR",  # Use fixed operator ID
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
            self.test_worker.log_message.connect(self.on_test_log_message)

            # Connect thread signals
            self.test_thread.started.connect(self.test_worker.run_test)
            self.test_thread.finished.connect(self.test_thread.deleteLater)

            # Start thread
            self.test_thread.start()

            # Update UI
            self.update_ui_for_test_start()

            # Update state manager
            self.state_manager.set_test_status(TestStatus.PREPARING, "Initializing EOL test...")

            logger.info(f"EOL test started - Serial Number: {serial_number}")

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

    def on_test_log_message(self, message: str) -> None:
        """Handle log message from test worker"""
        # Remove timestamp from loguru message if it exists (we add our own)
        clean_message = message.strip()
        if clean_message:
            self.add_log_message(clean_message)

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
