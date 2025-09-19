"""
EOL Test Panel for WF EOL Tester GUI

Panel for executing end-of-line force tests with real-time progress monitoring.
"""

# Standard library imports
import asyncio
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
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
from loguru import logger
import yaml

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
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(520, 320)

        # Ultra-modern dialog styling with shadows and glassmorphism
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 0.5 #F8FAFC, stop: 1 #EFF6FF);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 16px;
            }
        """
        )

        # Center on parent
        if parent:
            self.move(parent.geometry().center() - self.rect().center())

        self.setup_ui()
        self.serial_number = ""

    def setup_ui(self):
        """Setup modern dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header section with icon and title
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Icon (using Unicode character for now)
        icon_label = QLabel("🏷️")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet(
            """
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #667EEA, stop: 1 #764BA2);
                border-radius: 24px;
                color: white;
            }
        """
        )
        header_layout.addWidget(icon_label)

        # Title and subtitle
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        title_label = QLabel("Serial Number Input")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(
            """
            QLabel {
                color: #0F172A;
                margin: 0;
                padding: 0;
            }
        """
        )

        subtitle_label = QLabel("Please enter the device serial number to continue")
        subtitle_label.setFont(QFont("Inter", 11))
        subtitle_label.setStyleSheet(
            """
            QLabel {
                color: #64748B;
                margin: 0;
                padding: 0;
            }
        """
        )

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addWidget(title_container)
        header_layout.addStretch()

        layout.addWidget(header_widget)

        # Input section with modern styling
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # Serial number label with modern typography
        label = QLabel("Serial Number")
        label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        label.setStyleSheet(
            """
            QLabel {
                color: #374151;
                padding-bottom: 4px;
            }
        """
        )
        input_layout.addWidget(label)

        # Modern input field with enhanced styling
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter device serial number...")
        self.serial_input.setMinimumHeight(48)
        self.serial_input.setFont(QFont("Inter", 12))
        self.serial_input.setStyleSheet(
            """
            QLineEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #FAFBFC);
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 12px;
                color: #111827;
                selection-background-color: #667EEA;
            }
            QLineEdit:focus {
                border: 2px solid #667EEA;
                background: #FFFFFF;
                outline: none;
            }
            QLineEdit:hover {
                border: 2px solid #D1D5DB;
                background: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """
        )
        self.serial_input.textChanged.connect(self.validate_input)
        input_layout.addWidget(self.serial_input)

        layout.addWidget(input_container)

        # Spacer to push buttons down
        layout.addStretch()

        # Modern button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)

        # Cancel button with refined styling
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(44)
        cancel_button.setMinimumWidth(100)
        cancel_button.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        cancel_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #F9FAFB);
                color: #6B7280;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #F3F4F6, stop: 1 #E5E7EB);
                border: 2px solid #D1D5DB;
                color: #374151;
            }
            QPushButton:pressed {
                background: #E5E7EB;
                border: 2px solid #9CA3AF;
            }
        """
        )

        # OK button with premium gradient
        ok_button = QPushButton("Continue")
        ok_button.setMinimumHeight(44)
        ok_button.setMinimumWidth(120)
        ok_button.setFont(QFont("Inter", 11, QFont.Weight.DemiBold))
        ok_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #667EEA, stop: 0.5 #764BA2, stop: 1 #F093FB);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #5B5ACF, stop: 0.5 #6B46C1, stop: 1 #EC4899);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #4F46E5, stop: 0.5 #7C3AED, stop: 1 #BE185D);
            }
            QPushButton:disabled {
                background: #9CA3AF;
                color: #E5E7EB;
            }
        """
        )

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        # Connect buttons
        cancel_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self.accept_dialog)

        # Store references
        self.ok_button = ok_button
        self.cancel_button = cancel_button

        # Initially disable OK button
        ok_button.setEnabled(False)

        layout.addWidget(button_container)

        # Focus on input
        self.serial_input.setFocus()

    def validate_input(self):
        """Validate serial number input"""
        text = self.serial_input.text().strip()
        self.ok_button.setEnabled(len(text) > 0)

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

    def _add_gui_log_handler(self) -> None:
        """Add loguru handler to capture logs for GUI display"""
        if self._log_handler_id is None:
            self._log_handler_id = logger.add(
                self._emit_log_message,
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
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
        """Filter logs to capture all INFO level GUI messages (like CLI)"""
        try:
            # Only capture INFO level logs
            log_level = record.record.get("level", {}).get("name", "")
            if log_level != "INFO":
                return False

            # Capture all GUI logs (to match CLI output)
            module_name = record.record.get("name", "")

            # Show all GUI logs, similar to CLI behavior
            return "GUI" in module_name
        except Exception:
            # If there's any error accessing record attributes, don't capture
            return False

    def run_test(self) -> None:
        """Execute EOL test"""
        try:
            self.test_started.emit()
            self.test_progress.emit(0, "Initializing test...")

            # Create event loop for async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                self.test_progress.emit(10, "Starting EOL force test...")

                # Simulate test progress during execution
                # Start progress monitoring in a separate thread
                def update_progress():
                    progress_steps = [
                        (20, "Initializing hardware..."),
                        (30, "Connecting to loadcell..."),
                        (40, "Setting up robot position..."),
                        (50, "Starting force measurement..."),
                        (60, "Applying test force..."),
                        (70, "Recording measurements..."),
                        (80, "Analyzing results..."),
                    ]

                    for progress, message in progress_steps:
                        if self._should_stop:
                            break
                        time.sleep(0.5)  # Small delay between updates
                        self.test_progress.emit(progress, message)

                # Start progress thread
                progress_thread = threading.Thread(target=update_progress, daemon=True)
                progress_thread.start()

                # Run test
                result = loop.run_until_complete(self.use_case.execute(self.command))

                self.test_progress.emit(90, "Finalizing test results...")

                if not self._should_stop:
                    self.test_progress.emit(100, "Test completed successfully")
                    self.test_completed.emit(result)

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"EOL test execution failed: {e}")
            self.test_progress.emit(0, "Test failed")
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
        # Configuration section - removed (using modal dialog for serial number)

        # Control buttons
        self.start_test_button: Optional[QPushButton] = None
        self.stop_test_button: Optional[QPushButton] = None

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

        # Start capturing GUI logs immediately (commented out temporarily for debugging)
        # self._add_gui_log_handler()

        logger.debug("EOL test panel initialized")

    def __del__(self) -> None:
        """Cleanup when panel is destroyed"""
        try:
            # Stop test thread if running
            if hasattr(self, 'test_thread') and self.test_thread and self.test_thread.isRunning():
                self.test_thread.quit()
                self.test_thread.wait(3000)  # Wait up to 3 seconds for graceful shutdown

            # Remove log handler
            if hasattr(self, '_log_handler_id') and self._log_handler_id is not None:
                logger.remove(self._log_handler_id)
                self._log_handler_id = None
        except Exception:
            pass

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # === CONTROL SECTION ===
        control_group = QGroupBox("Test Control")
        control_group.setStyleSheet(
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
        control_layout = QVBoxLayout(control_group)
        control_layout.setContentsMargins(20, 24, 20, 20)
        control_layout.setSpacing(16)  # Increased spacing for better readability

        self.start_test_button = QPushButton("Start EOL Test")
        self.start_test_button.setProperty("class", "success")
        self.start_test_button.setFixedSize(180, 44)
        self.start_test_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #10B981, stop: 1 #059669);
                color: white;
                border: none;
                border-left: 4px solid #047857;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #34D399, stop: 1 #10B981);
            }
            QPushButton:pressed {
            }
            QPushButton:disabled {
                background: #94A3B8;
                color: #E2E8F0;
                border-left: 4px solid #6B7280;
            }
        """
        )
        self.start_test_button.setAccessibleName("Start EOL Force Test")

        self.stop_test_button = QPushButton("Stop Test")
        self.stop_test_button.setProperty("class", "danger")
        self.stop_test_button.setFixedSize(180, 44)
        self.stop_test_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #EF4444, stop: 1 #DC2626);
                color: white;
                border: none;
                border-left: 4px solid #B91C1C;
                border-radius: 10px;
                font-weight: 600;
                font-size: 13px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #F87171, stop: 1 #EF4444);
            }
            QPushButton:pressed {
            }
            QPushButton:disabled {
                background: #94A3B8;
                color: #E2E8F0;
                border-left: 4px solid #6B7280;
            }
        """
        )
        self.stop_test_button.setEnabled(False)
        self.stop_test_button.setAccessibleName("Stop Running Test")


        # Add top stretch to center buttons vertically
        control_layout.addStretch()

        # Center buttons horizontally within the layout
        control_layout.addWidget(self.start_test_button, 0, Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.stop_test_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Add bottom stretch to center buttons vertically
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
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(16, 20, 16, 16)
        progress_layout.setSpacing(12)

        # Progress GroupBox만 세로 확장 방지
        progress_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed  # 가로: 확장  # 세로: 고정
        )

        self.status_label = QLabel("Ready to start test")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.DemiBold))
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #475569;
                padding: 12px 16px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #F8FAFC, stop: 1 #E2E8F0);
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-weight: 600;
            }
        """
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(40)
        self.progress_bar.setFont(QFont("Arial", 11, QFont.Weight.DemiBold))
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #F8FAFC, stop: 1 #E2E8F0);
                border: 2px solid #CBD5E1;
                border-radius: 10px;
                text-align: center;
                font-weight: 600;
                font-size: 11px;
                color: #374151;
                padding: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #667EEA, stop: 1 #764BA2);
                border-radius: 8px;
                margin: 1px;
            }
            QProgressBar:hover {
                border: 2px solid #94A3B8;
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
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(16, 20, 16, 16)

        self.test_log_text = QTextEdit()
        self.test_log_text.setReadOnly(True)
        self.test_log_text.setMinimumHeight(180)  # 최소 높이만 설정
        self.test_log_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding  # 가로 확장  # 세로 확장
        )
        self.test_log_text.setFont(QFont("JetBrains Mono", 10))
        self.test_log_text.setStyleSheet(
            """
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #1E293B, stop: 1 #334155);
                color: #F1F5F9;
                border: 1px solid #475569;
                border-radius: 10px;
                padding: 16px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                selection-background-color: #667EEA;
                selection-color: white;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background: #475569;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #64748B;
                border-radius: 5px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )

        log_layout.addWidget(self.test_log_text)

        # === RESULTS SECTION ===
        results_group = QGroupBox("Test Results")
        results_group.setStyleSheet(
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
        self.summary_label.setFont(QFont("Arial", 12, QFont.Weight.DemiBold))
        self.summary_label.setStyleSheet(
            """
            QLabel {
                color: #64748B;
                padding: 12px 16px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #F8FAFC, stop: 1 #E2E8F0);
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-weight: 600;
            }
        """
        )

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Step", "Description", "Result", "Value"])
        self.results_table.setMaximumHeight(220)  # 고정 최대 높이
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make table read-only
        self.results_table.setStyleSheet(
            """
            QTableWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #FFFFFF, stop: 1 #FAFBFC);
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                gridline-color: #F1F5F9;
                font-size: 11px;
                selection-background-color: #667EEA;
                selection-color: white;
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
                padding: 12px;
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


        # State manager signals
        if self.state_manager:
            self.state_manager.test_status_changed.connect(self.on_test_status_changed)
            self.state_manager.test_progress_changed.connect(self.on_test_progress_changed)

    def start_test(self) -> None:
        """Start EOL test execution"""
        try:
            # Clean up any previous test resources first
            self._cleanup_test_resources()

            # Check if hardware is ready
            hardware_status = self.state_manager.hardware_status
            if hardware_status.overall_status.value != "connected":
                self.status_message.emit("Hardware not ready. Check connections.")
                return

            # Get application config to check if serial number popup is required
            try:
                # Local application imports
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


    def update_ui_for_test_start(self) -> None:
        """Update UI when test starts"""
        if self.start_test_button:
            self.start_test_button.setEnabled(False)

        if self.stop_test_button:
            self.stop_test_button.setEnabled(True)


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

        # Clean up thread and worker
        self._cleanup_test_resources()

    def _cleanup_test_resources(self) -> None:
        """Clean up test thread and worker resources"""
        try:
            # Clean up thread
            if self.test_thread and self.test_thread.isRunning():
                self.test_thread.quit()
                self.test_thread.wait(3000)  # Wait up to 3 seconds

            # Clear references
            if self.test_thread:
                self.test_thread.deleteLater()
                self.test_thread = None

            if self.test_worker:
                self.test_worker.deleteLater()
                self.test_worker = None

            logger.debug("Test resources cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up test resources: {e}")

    def reset_test_ui(self) -> None:
        """Reset UI to initial state"""
        # Reset buttons
        if self.start_test_button:
            self.start_test_button.setEnabled(True)

        if self.stop_test_button:
            self.stop_test_button.setEnabled(False)


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
                    description = step_result.get("description", step_name)  # Use step_name as fallback
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
                    if result_item is not None:
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
