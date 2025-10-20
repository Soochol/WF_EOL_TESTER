"""Test Control Event Handlers

Handles all events and user interactions for test controls.
"""

# Standard library imports
from typing import Optional, TYPE_CHECKING

# Third-party imports
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QComboBox, QLineEdit
from loguru import logger

# Local folder imports
from .state_manager import TestControlState


if TYPE_CHECKING:
    # Local application imports
    from application.interfaces.hardware.robot import RobotService


class TestControlEventHandlers(QObject):
    """Handles events for test control components"""

    # Signals for main widget to connect to
    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()

    def __init__(
        self,
        state_manager: TestControlState,
        robot_service: Optional["RobotService"] = None,
        executor_thread=None,
        axis_id: int = 0,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.state_manager = state_manager
        self.robot_service = robot_service
        self.executor_thread = executor_thread
        self.axis_id = axis_id

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
        """Handle HOME button click - executes actual robot homing operation"""
        logger.info("🏠 HOME button clicked in TestControlWidget")

        # Validate dependencies
        if not self.robot_service:
            logger.error("Robot service not available")
            self.state_manager.update_status("Robot service not initialized", "status_error", 0)
            self.state_manager.set_button_enabled("home", True)
            return

        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.state_manager.update_status("Executor thread not initialized", "status_error", 0)
            self.state_manager.set_button_enabled("home", True)
            return

        # Update state
        self.state_manager.update_status("Robot Homing...", "dashboard", 0)
        self.state_manager.set_button_enabled("home", False)
        self.state_manager.set_button_enabled("start", False)

        # Submit homing task to executor thread
        logger.debug("Submitting robot home task to executor thread...")
        self.executor_thread.submit_task("robot_home", self._async_home())

    async def _async_home(self) -> None:
        """Async home operation with automatic connection and servo on"""
        # Type guard: robot_service should be available at this point
        if not self.robot_service:
            logger.error("Robot service became unavailable during homing")
            self.state_manager.update_status("Robot service error", "status_error", 0)
            self.state_manager.set_button_enabled("home", True)
            return

        try:
            # Step 1: Check and establish connection
            is_connected = await self.robot_service.is_connected()
            if not is_connected:
                logger.info("Robot not connected - connecting automatically...")
                self.state_manager.update_status("Connecting to robot...", "dashboard", 10)
                await self.robot_service.connect()
                logger.info("Robot connected successfully")
                self.state_manager.update_status("Robot connected", "status_success", 30)

            # Step 2: Check and enable servo
            # Note: Always enable servo to ensure it's ready (idempotent operation)
            logger.info("Ensuring servo is enabled...")
            self.state_manager.update_status("Enabling servo...", "dashboard", 50)
            await self.robot_service.enable_servo(self.axis_id)
            logger.info("Servo enabled successfully")
            self.state_manager.update_status("Servo enabled", "status_success", 70)

            # Step 3: Perform homing
            logger.info(f"Starting robot homing for axis {self.axis_id}...")
            self.state_manager.update_status("Homing robot...", "dashboard", 80)
            await self.robot_service.home_axis(self.axis_id)

            # Read position after homing
            position = await self.robot_service.get_position(self.axis_id)
            logger.info(f"Robot homing completed successfully - Position: {position:.2f} μm")

            # Update state
            self.state_manager.update_status("Robot Homing Completed", "status_success", 100)
            self.state_manager.set_button_enabled("start", True)

            # Emit success signal
            self.robot_home_requested.emit()

        except Exception as e:
            logger.error(f"Robot homing failed: {e}", exc_info=True)
            self.state_manager.update_status(f"Robot Homing Failed: {str(e)}", "status_error", 0)

        finally:
            # Always re-enable home button
            logger.debug("Re-enabling home button after homing operation")
            self.state_manager.set_button_enabled("home", True)

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
