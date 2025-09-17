"""
EOL Test Panel (Qt Designer Version)

Enhanced EOL test panel widget using Qt Designer UI with clean separation
between UI structure and business logic.
"""

# Standard library imports
from pathlib import Path
import sys
import traceback
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
import asyncio
from loguru import logger
import yaml

# Local application imports
# Import existing dependencies
from application.containers.application_container import ApplicationContainer
from application.use_cases.eol_force_test import EOLForceTestCommand
from domain.value_objects.application_config import ApplicationConfig

# Import the generated UI
from ui.gui.panels.eol_test_panel_ui import Ui_EOLTestPanel
from ui.gui.state.gui_state_manager import GUIStateManager, TestStatus


class SerialNumberDialog(QDialog):
    """Modal dialog for serial number input"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Number Input")
        self.setModal(True)
        self.setFixedSize(350, 150)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Label
        label = QLabel("Please enter the serial number:")
        label.setFont(QFont("Arial", 11))
        layout.addWidget(label)

        # Input field
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter serial number...")
        self.serial_input.setMinimumHeight(30)
        self.serial_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.serial_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumHeight(30)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(30)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Focus on input field
        self.serial_input.setFocus()

    def get_serial_number(self) -> Optional[str]:
        """Get entered serial number"""
        text = self.serial_input.text().strip()
        return text if text else None


class EOLTestWorker(QThread):
    """Worker thread for EOL test execution"""

    # Signals
    test_started = Signal()
    test_completed = Signal(object)
    test_failed = Signal(str)
    progress_updated = Signal(int, str)
    log_message = Signal(str)

    def __init__(self, use_case, command):
        super().__init__()
        self.use_case = use_case
        self.command = command
        self._should_stop = False
        self._log_handler_id = None

    def stop_test(self):
        """Request test stop"""
        self._should_stop = True

    def _add_gui_log_handler(self) -> None:
        """Add GUI log handler to capture test logs"""
        if self._log_handler_id is None:
            self._log_handler_id = logger.add(
                self._emit_log_message,
                level="INFO",
                filter=self._should_capture_log,
                catch=False,
            )

    def _remove_gui_log_handler(self) -> None:
        """Remove GUI log handler"""
        if self._log_handler_id is not None:
            try:
                logger.remove(self._log_handler_id)
            except ValueError:
                pass
            self._log_handler_id = None

    def _emit_log_message(self, message) -> None:
        """Emit log message to GUI"""
        try:
            self.log_message.emit(str(message))
        except Exception:
            pass

    def _should_capture_log(self, record) -> bool:
        """Filter logs to capture only INFO level test-related messages"""
        log_level = record.get("level", {}).get("name", "")
        if log_level != "INFO":
            return False

        relevant_modules = [
            "application.use_cases.eol_force_test",
            "application.services.hardware_facade",
            "infrastructure.implementation.hardware",
            "GUI",
        ]
        module_name = record.get("name", "")
        message = record.get("message", "")

        is_relevant_module = any(module in module_name for module in relevant_modules)
        is_test_message = any(
            keyword in message.lower()
            for keyword in ["test", "robot", "power", "measurement", "force", "loadcell", "dio"]
        )

        return is_relevant_module or is_test_message

    def run(self) -> None:
        """Execute EOL test"""
        try:
            self.test_started.emit()
            self._add_gui_log_handler()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(self.use_case.execute(self.command))
                if not self._should_stop:
                    self.test_completed.emit(result)
            finally:
                loop.close()
                self._remove_gui_log_handler()

        except Exception as e:
            logger.error(f"EOL test execution failed: {e}")
            self.test_failed.emit(str(e))
            self._remove_gui_log_handler()


class EOLTestPanel(QWidget):
    """
    EOL Test panel widget using Qt Designer UI

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
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager

        # Setup UI from Qt Designer
        self.ui = Ui_EOLTestPanel()
        self.ui.setupUi(self)

        # Worker thread
        self.worker_thread: Optional[EOLTestWorker] = None

        # Setup scroll area
        self.setup_scroll_area()

        # Connect signals
        self.connect_signals()

        # Initialize state
        self.reset_test_ui()

        logger.debug("EOL test panel initialized with Qt Designer UI")

    def setup_scroll_area(self) -> None:
        """Setup scroll area for the panel"""
        if self.parent():
            scroll_area = QScrollArea(self.parent())
            scroll_area.setWidget(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Button signals
        self.ui.startTestButton.clicked.connect(self.start_test)
        self.ui.stopTestButton.clicked.connect(self.stop_test)
        self.ui.resetButton.clicked.connect(self.reset_test)

        # State manager signals
        if self.state_manager:
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.test_progress_changed.connect(self.on_test_progress_changed)

    def start_test(self) -> None:
        """Start EOL test execution"""
        try:
            # Check hardware status
            hardware_status = self.state_manager.hardware_status
            if hardware_status.overall_status.value != "connected":
                self.status_message.emit("Hardware not ready. Check connections.")
                return

            # Check if serial number popup is required
            try:
                config_path = Path("configuration/application.yaml")
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)
                    app_config = ApplicationConfig.from_dict(config_data)

                    if app_config.gui.require_serial_number_popup:
                        dialog = SerialNumberDialog(self)
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            serial_number = dialog.get_serial_number()
                            if not serial_number:
                                QMessageBox.warning(self, "Warning", "Serial number is required!")
                                return
                        else:
                            return  # User cancelled
                    else:
                        serial_number = None
                else:
                    serial_number = None

            except Exception as e:
                logger.warning(f"Failed to load application config: {e}")
                serial_number = None

            # Create command
            command = EOLForceTestCommand(
                test_id=f"eol_test_{self.state_manager.session_id}",
                force_targets=[10.0, 20.0, 30.0],  # Default values
                serial_number=serial_number,
                operator_id="GUI_User",
            )

            # Create and start worker
            use_case = self.container.eol_force_test_use_case()
            self.worker_thread = EOLTestWorker(use_case, command)

            # Connect worker signals
            self.worker_thread.test_started.connect(self.on_test_started)
            self.worker_thread.test_completed.connect(self.on_test_completed)
            self.worker_thread.test_failed.connect(self.on_test_failed)
            self.worker_thread.progress_updated.connect(self.on_worker_progress)
            self.worker_thread.log_message.connect(self.on_test_log_message)

            # Update UI and start
            self.update_ui_for_test_start()
            self.worker_thread.start()

            logger.info("EOL test started from GUI")

        except Exception as e:
            error_msg = f"Failed to start EOL test: {e}"
            logger.error(error_msg)
            logger.error(f"Stack trace: {traceback.format_exc()}")
            self.status_message.emit(error_msg)

    def stop_test(self) -> None:
        """Stop current test execution"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop_test()
            self.worker_thread.wait(5000)  # Wait up to 5 seconds
            if self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.worker_thread.wait()
            self.worker_thread = None

        self.state_manager.set_test_status(TestStatus.STOPPED, "Test stopped by user")
        self.update_ui_for_test_stop()
        self.add_log_message("Test stopped by user")

        logger.info("EOL test stopped by user")

    def reset_test(self) -> None:
        """Reset test state and UI"""
        self.stop_test()
        self.state_manager.reset_test_state()
        self.reset_test_ui()

        logger.info("EOL test reset")

    def update_ui_for_test_start(self) -> None:
        """Update UI when test starts"""
        self.ui.startTestButton.setEnabled(False)
        self.ui.stopTestButton.setEnabled(True)
        self.ui.resetButton.setEnabled(False)

        # Clear previous results
        self.ui.resultsTable.setRowCount(0)
        self.ui.summaryLabel.setText("Test in progress...")
        self.ui.summaryLabel.setStyleSheet(
            "color: #3498DB; padding: 4px; font-weight: bold; font-size: 11px;"
        )

    def update_ui_for_test_stop(self) -> None:
        """Update UI when test stops"""
        self.ui.startTestButton.setEnabled(True)
        self.ui.stopTestButton.setEnabled(False)
        self.ui.resetButton.setEnabled(True)

    def reset_test_ui(self) -> None:
        """Reset UI to initial state"""
        # Reset buttons
        self.ui.startTestButton.setEnabled(True)
        self.ui.stopTestButton.setEnabled(False)
        self.ui.resetButton.setEnabled(True)

        # Reset progress
        self.ui.progressBar.setValue(0)
        self.ui.statusLabel.setText("Ready to start test")
        self.ui.statusLabel.setStyleSheet("color: #2C3E50; padding: 4px; font-size: 11px;")

        # Clear log
        self.ui.testLogText.clear()
        self.add_log_message("Test log initialized")

        # Clear results
        self.ui.resultsTable.setRowCount(0)
        self.ui.summaryLabel.setText("No test results available")
        self.ui.summaryLabel.setStyleSheet(
            "color: #7F8C8D; padding: 4px; font-weight: bold; font-size: 11px;"
        )

    def add_log_message(self, message: str) -> None:
        """Add message to test log with timestamp"""
        # Standard library imports
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.ui.testLogText.append(formatted_message)

        # Auto-scroll to bottom
        cursor = self.ui.testLogText.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.ui.testLogText.setTextCursor(cursor)

    def display_test_results(self, result) -> None:
        """Display test results in the table"""
        try:
            # Setup table headers
            if hasattr(result, "measurements") and result.measurements:
                headers = ["Measurement", "Value", "Unit", "Status", "Timestamp"]
                self.ui.resultsTable.setColumnCount(len(headers))
                self.ui.resultsTable.setHorizontalHeaderLabels(headers)

                # Add measurement data
                measurements = result.measurements
                self.ui.resultsTable.setRowCount(len(measurements))

                for row, measurement in enumerate(measurements):
                    # Measurement name
                    self.ui.resultsTable.setItem(row, 0, QTableWidgetItem(str(measurement.name)))

                    # Value
                    value_str = (
                        f"{measurement.value:.2f}"
                        if isinstance(measurement.value, (int, float))
                        else str(measurement.value)
                    )
                    self.ui.resultsTable.setItem(row, 1, QTableWidgetItem(value_str))

                    # Unit
                    unit = getattr(measurement, "unit", "N/A")
                    self.ui.resultsTable.setItem(row, 2, QTableWidgetItem(str(unit)))

                    # Status
                    status = "PASS" if getattr(measurement, "is_passed", True) else "FAIL"
                    status_item = QTableWidgetItem(status)
                    if status == "PASS":
                        status_item.setStyleSheet("color: #27AE60; font-weight: bold;")
                    else:
                        status_item.setStyleSheet("color: #E74C3C; font-weight: bold;")
                    self.ui.resultsTable.setItem(row, 3, status_item)

                    # Timestamp
                    timestamp = getattr(measurement, "timestamp", "N/A")
                    if timestamp != "N/A" and hasattr(timestamp, "strftime"):
                        timestamp = timestamp.strftime("%H:%M:%S")
                    self.ui.resultsTable.setItem(row, 4, QTableWidgetItem(str(timestamp)))

                # Resize columns to content
                self.ui.resultsTable.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Error displaying test results: {e}")
            self.add_log_message(f"Error displaying results: {e}")

    # Event handlers
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

            # Update summary
            self.ui.summaryLabel.setText(
                f"Test {status}: {len(getattr(result, 'measurements', []))} measurements"
            )
            if status == "PASSED":
                self.ui.summaryLabel.setStyleSheet(
                    "color: #27AE60; padding: 4px; font-weight: bold; font-size: 11px;"
                )
            else:
                self.ui.summaryLabel.setStyleSheet(
                    "color: #E74C3C; padding: 4px; font-weight: bold; font-size: 11px;"
                )

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
        self.ui.summaryLabel.setText(f"Test Failed: {error_message}")
        self.ui.summaryLabel.setStyleSheet(
            "color: #E74C3C; padding: 4px; font-weight: bold; font-size: 11px;"
        )

    def on_test_status_changed(self, status: TestStatus, message: str) -> None:
        """Handle test status changes from state manager"""
        self.ui.statusLabel.setText(message)

        # Update status label style based on status
        if status == TestStatus.RUNNING:
            self.ui.statusLabel.setStyleSheet("color: #3498DB; padding: 4px; font-size: 11px;")
        elif status == TestStatus.PASSED:
            self.ui.statusLabel.setStyleSheet("color: #27AE60; padding: 4px; font-size: 11px;")
        elif status == TestStatus.FAILED:
            self.ui.statusLabel.setStyleSheet("color: #E74C3C; padding: 4px; font-size: 11px;")
        else:
            self.ui.statusLabel.setStyleSheet("color: #2C3E50; padding: 4px; font-size: 11px;")

    def on_test_progress_changed(self, progress: int, message: str) -> None:
        """Handle test progress changes from state manager"""
        self.ui.progressBar.setValue(progress)
        if message:
            self.ui.statusLabel.setText(message)


# Main execution for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create mock dependencies for testing
    # Local application imports
    from ui.gui.state.gui_state_manager import GUIStateManager

    try:
        container = ApplicationContainer.create()
        state_manager = GUIStateManager()

        panel = EOLTestPanel(container, state_manager)
        panel.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Error: {e}")
        # Standard library imports
        import traceback

        traceback.print_exc()
