"""Test Control Event Handlers

Handles all events and user interactions for test controls.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QComboBox, QLineEdit

# Local folder imports
from .state_manager import TestControlState


class TestControlEventHandlers(QObject):
    """Handles events for test control components"""

    # Signals for main widget to connect to
    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()

    def __init__(self, state_manager: TestControlState, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.state_manager = state_manager

    def handle_start_test_clicked(self) -> None:
        """Handle START TEST button click"""
        # Update state to running
        self.state_manager.update_status("Test Starting...", "play", 0)

        # Disable start button during test
        self.state_manager.set_button_enabled("start", False)
        self.state_manager.set_button_enabled("home", False)

        # Emit signal
        self.test_started.emit()

    def handle_stop_test_clicked(self) -> None:
        """Handle STOP button click"""
        # Update state to stopped
        self.state_manager.update_status("Test Stopped", "stop", 0)

        # Re-enable controls
        self.state_manager.set_button_enabled("start", True)
        self.state_manager.set_button_enabled("home", True)

        # Emit signal
        self.test_stopped.emit()

    def handle_pause_test_clicked(self) -> None:
        """Handle PAUSE button click"""
        # Update state to paused
        self.state_manager.update_status("Test Paused", "pause")

        # Emit signal
        self.test_paused.emit()

    def handle_home_button_clicked(self) -> None:
        """Handle HOME button click with debug logging"""
        # Third-party imports
        from loguru import logger

        logger.info("🏠 HOME button clicked in TestControlWidget")
        logger.debug("Emitting robot_home_requested signal...")

        # Update state
        self.state_manager.update_status("Robot Homing...", "dashboard", 0)

        # Disable home button during homing
        self.state_manager.set_button_enabled("home", False)

        # Emit signal
        self.robot_home_requested.emit()
        logger.debug("robot_home_requested signal emitted successfully")

    def handle_emergency_stop_clicked(self) -> None:
        """Handle EMERGENCY STOP button click"""
        # Update state to emergency
        self.state_manager.update_status("EMERGENCY STOP ACTIVATED", "emergency", 0)

        # Disable start button (requires homing)
        self.state_manager.set_button_enabled("start", False)

        # Emit signal
        self.emergency_stop_requested.emit()

    def handle_sequence_changed(self, combo_box: QComboBox) -> None:
        """Handle test sequence selection change"""
        sequence = combo_box.currentText()
        self.state_manager.update_sequence(sequence)

    def handle_serial_number_changed(self, line_edit: QLineEdit) -> None:
        """Handle serial number change"""
        serial = line_edit.text()
        self.state_manager.update_serial_number(serial)

    def handle_test_completed(self, success: bool = True) -> None:
        """Handle test completion"""
        if success:
            self.state_manager.update_status("Test Completed Successfully", "status_success", 100)
        else:
            self.state_manager.update_status("Test Failed", "status_error", 0)

        # Re-enable controls
        self.state_manager.set_button_enabled("start", True)
        self.state_manager.set_button_enabled("home", True)

    def handle_robot_homing_completed(self, success: bool = True) -> None:
        """Handle robot homing completion"""
        if success:
            self.state_manager.update_status("Robot Homing Completed", "status_success", 100)
            # Re-enable start button after successful homing
            self.state_manager.set_button_enabled("start", True)
        else:
            self.state_manager.update_status("Robot Homing Failed", "status_error", 0)

        # Always re-enable home button
        self.state_manager.set_button_enabled("home", True)

    def handle_test_progress_update(self, progress: int, status_text: Optional[str] = None) -> None:
        """Handle test progress updates"""
        current_status = status_text or self.state_manager.current_status
        self.state_manager.update_status(current_status, self.state_manager.current_icon, progress)
