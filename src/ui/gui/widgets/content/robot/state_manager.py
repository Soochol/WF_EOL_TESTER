"""Robot State Manager

Centralized state management for robot control operations.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger


class RobotControlState(QObject):
    """
    Centralized state manager for robot control.

    Manages:
    - Connection state
    - Servo state
    - Position tracking
    - Button enable/disable states
    - Status messages
    """

    # State change signals
    connection_changed = Signal(bool)  # is_connected
    servo_changed = Signal(bool)  # is_enabled
    position_changed = Signal(float)  # position in μm
    motion_status_changed = Signal(str)  # motion status text
    button_state_changed = Signal(str, bool)  # button_name, enabled
    status_changed = Signal(str, str)  # status_text, status_type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message

    def __init__(self):
        super().__init__()

        # Connection state
        self._is_connected = False

        # Servo state
        self._servo_enabled = False

        # Position tracking
        self._current_position: Optional[float] = None

        # Motion status
        self._motion_status = "Unknown"

        # Button states
        self._button_states = {
            "connect": True,
            "disconnect": False,
            "servo_on": False,
            "servo_off": False,
            "home": False,
            "move_abs": False,
            "move_rel": False,
            "get_position": False,
            "stop": False,
            "emergency": True,
        }

    # Connection state
    @property
    def is_connected(self) -> bool:
        """Get connection state"""
        return self._is_connected

    def set_connected(self, connected: bool) -> None:
        """Set connection state and update button states"""
        if self._is_connected != connected:
            self._is_connected = connected
            self.connection_changed.emit(connected)

            if connected:
                # Connected: enable control buttons, disable connect
                self.set_button_enabled("connect", False)
                self.set_button_enabled("disconnect", True)
                self.set_button_enabled("servo_on", True)
                self.set_button_enabled("servo_off", False)  # Initially disabled (servo is off)
                self.set_button_enabled("home", False)  # ✅ Disabled until servo is on (home requires servo)
                self.set_button_enabled("move_abs", False)  # Disabled until servo is on
                self.set_button_enabled("move_rel", False)  # Disabled until servo is on
                self.set_button_enabled("get_position", False)  # Disabled initially (enable after home/motion)
                self.set_button_enabled("stop", True)
                self.set_button_enabled("emergency", True)  # Always enabled
                self.update_status("Robot connected - Turn on servo to enable motion", "info")
            else:
                # Disconnected: disable control buttons, enable connect
                self.set_button_enabled("connect", True)
                self.set_button_enabled("disconnect", False)
                self.set_button_enabled("servo_on", False)
                self.set_button_enabled("servo_off", False)
                self.set_button_enabled("home", False)
                self.set_button_enabled("move_abs", False)
                self.set_button_enabled("move_rel", False)
                self.set_button_enabled("get_position", False)
                self.set_button_enabled("stop", False)
                self.set_button_enabled("emergency", True)  # Always enabled
                self.update_status("Robot disconnected", "warning")

                # Reset other states
                self._servo_enabled = False
                self._current_position = None
                self._motion_status = "Unknown"

    # Servo state
    @property
    def servo_enabled(self) -> bool:
        """Get servo state"""
        return self._servo_enabled

    def set_servo_enabled(self, enabled: bool, force_update: bool = False) -> None:
        """Set servo state and update related button states

        Args:
            enabled: Servo enabled state
            force_update: If True, update button states even if servo state hasn't changed
        """
        state_changed = self._servo_enabled != enabled

        if state_changed or force_update:
            if state_changed:
                self._servo_enabled = enabled
                self.servo_changed.emit(enabled)

            if enabled:
                # Servo ON: Enable move buttons, home button, toggle servo buttons
                self.set_button_enabled("servo_on", False)   # Already on
                self.set_button_enabled("servo_off", True)   # Can turn off
                self.set_button_enabled("home", True)        # ✅ Home enabled (requires servo)
                self.set_button_enabled("move_abs", True)    # Movement enabled
                self.set_button_enabled("move_rel", True)    # Movement enabled
                if state_changed or force_update:
                    self.update_status("Servo enabled - Motor active, motion commands available", "info")
            else:
                # Servo OFF: Disable move buttons, home button, toggle servo buttons
                self.set_button_enabled("servo_on", True)    # Can turn on
                self.set_button_enabled("servo_off", False)  # Already off
                self.set_button_enabled("home", False)       # ✅ Home disabled (requires servo)
                self.set_button_enabled("move_abs", False)   # Movement disabled
                self.set_button_enabled("move_rel", False)   # Movement disabled
                if state_changed or force_update:
                    self.update_status("Servo disabled - Turn on servo to enable motion", "warning")

    # Position tracking
    @property
    def current_position(self) -> Optional[float]:
        """Get current position"""
        return self._current_position

    def set_position(self, position: float) -> None:
        """Update current position"""
        self._current_position = position
        self.position_changed.emit(position)

    # Motion status
    @property
    def motion_status(self) -> str:
        """Get motion status"""
        return self._motion_status

    def set_motion_status(self, status: str) -> None:
        """Update motion status"""
        if self._motion_status != status:
            self._motion_status = status
            self.motion_status_changed.emit(status)

    # Button state management
    def set_button_enabled(self, button_name: str, enabled: bool) -> None:
        """Set button enabled state"""
        if button_name in self._button_states:
            if self._button_states[button_name] != enabled:
                self._button_states[button_name] = enabled
                self.button_state_changed.emit(button_name, enabled)

    def get_button_enabled(self, button_name: str) -> bool:
        """Get button enabled state"""
        return self._button_states.get(button_name, False)

    def get_all_button_states(self) -> dict[str, bool]:
        """Get all button states for initial UI setup"""
        return self._button_states.copy()

    # Status updates
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update status message

        Args:
            message: Status message text
            status_type: Type of status (info, warning, error, success)
        """
        self.status_changed.emit(message, status_type)

    # Progress indication
    def show_progress(self, message: str = "Processing...") -> None:
        """Show progress indicator"""
        self.progress_changed.emit(True, message)

    def hide_progress(self) -> None:
        """Hide progress indicator"""
        self.progress_changed.emit(False, "")

    # Emergency state management
    def set_emergency_stopped(self) -> None:
        """Set emergency stopped state - only Servo ON and Emergency buttons enabled"""
        # After emergency stop, servo is off - must turn servo on before homing
        self.set_button_enabled("connect", False)
        self.set_button_enabled("disconnect", True)
        self.set_button_enabled("servo_on", True)   # Enable to turn servo back on
        self.set_button_enabled("servo_off", False)
        self.set_button_enabled("home", False)      # Disable home - must servo on first
        self.set_button_enabled("move_abs", False)
        self.set_button_enabled("move_rel", False)
        self.set_button_enabled("get_position", False)
        self.set_button_enabled("stop", False)
        self.set_button_enabled("emergency", True)  # Always enabled
        # Reset servo state
        self._servo_enabled = False
        self.update_status("Emergency stop activated - Turn Servo ON to recover", "error")

    # Motion state management
    def set_homing_in_progress(self, in_progress: bool) -> None:
        """Set homing in progress state and update button states"""
        if in_progress:
            # Homing in progress: disable most buttons except stop and emergency
            self.set_button_enabled("disconnect", False)
            self.set_button_enabled("servo_on", False)
            self.set_button_enabled("servo_off", False)
            self.set_button_enabled("home", False)
            self.set_button_enabled("move_abs", False)
            self.set_button_enabled("move_rel", False)
            self.set_button_enabled("get_position", False)
            # Stop and Emergency remain enabled
            self.set_button_enabled("stop", True)
            self.set_button_enabled("emergency", True)
        else:
            # Homing completed: restore buttons based on connection and servo state
            if self.is_connected:
                self.set_button_enabled("disconnect", True)
                self.set_button_enabled("get_position", True)
                logger.debug("Homing completed - Get Position button enabled")
                self.set_button_enabled("stop", True)
                self.set_button_enabled("emergency", True)
                # Restore servo-dependent buttons (includes home button)
                # Use force_update=True to restore button states even if servo state hasn't changed
                self.set_servo_enabled(self._servo_enabled, force_update=True)

    def set_motion_in_progress(self, in_progress: bool) -> None:
        """Set motion in progress state and update button states"""
        if in_progress:
            # Motion in progress: disable most buttons except stop and emergency
            self.set_button_enabled("disconnect", False)
            self.set_button_enabled("servo_on", False)
            self.set_button_enabled("servo_off", False)
            self.set_button_enabled("home", False)
            self.set_button_enabled("move_abs", False)
            self.set_button_enabled("move_rel", False)
            self.set_button_enabled("get_position", False)
            # Stop and Emergency remain enabled
            self.set_button_enabled("stop", True)
            self.set_button_enabled("emergency", True)
        else:
            # Motion completed: restore buttons based on connection and servo state
            if self.is_connected:
                self.set_button_enabled("disconnect", True)
                self.set_button_enabled("get_position", True)
                logger.debug("Motion completed - Get Position button enabled")
                self.set_button_enabled("stop", True)
                self.set_button_enabled("emergency", True)
                # Restore servo-dependent buttons (includes home button)
                # Use force_update=True to restore button states even if servo state hasn't changed
                self.set_servo_enabled(self._servo_enabled, force_update=True)

    # Reset state
    def reset(self) -> None:
        """Reset all states to initial values"""
        self.set_connected(False)
        self._servo_enabled = False
        self._current_position = None
        self._motion_status = "Unknown"
