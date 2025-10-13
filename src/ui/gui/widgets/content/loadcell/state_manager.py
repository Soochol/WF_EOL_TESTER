"""Loadcell State Manager

Centralized state management for loadcell control operations.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal


class LoadcellControlState(QObject):
    """
    Centralized state manager for loadcell control.

    Manages:
    - Connection state
    - Force measurement values
    - Hold state
    - Button enable/disable states
    - Status messages
    """

    # State change signals
    connection_changed = Signal(bool)  # is_connected
    force_changed = Signal(float)  # force in kgf (kilogram-force)
    hold_changed = Signal(bool)  # is_held
    button_state_changed = Signal(str, bool)  # button_name, enabled
    status_changed = Signal(str, str)  # status_text, status_type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message

    def __init__(self):
        super().__init__()

        # Connection state
        self._is_connected = False

        # Hold state
        self._is_held = False

        # Force tracking
        self._current_force: Optional[float] = None

        # Button states
        self._button_states = {
            "connect": True,
            "disconnect": False,
            "zero_calibration": False,
            "read_force": False,
            "read_peak_force": False,
            "hold": False,
            "hold_release": False,
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
                self.set_button_enabled("zero_calibration", True)
                self.set_button_enabled("read_force", True)
                self.set_button_enabled("read_peak_force", True)
                self.set_button_enabled("hold", True)
                self.set_button_enabled("hold_release", False)  # Initially disabled
                self.update_status("Loadcell connected", "info")
            else:
                # Disconnected: disable control buttons, enable connect
                self.set_button_enabled("connect", True)
                self.set_button_enabled("disconnect", False)
                self.set_button_enabled("zero_calibration", False)
                self.set_button_enabled("read_force", False)
                self.set_button_enabled("read_peak_force", False)
                self.set_button_enabled("hold", False)
                self.set_button_enabled("hold_release", False)
                self.update_status("Loadcell disconnected", "warning")

                # Reset other states
                self._is_held = False
                self._current_force = None

    # Hold state
    @property
    def is_held(self) -> bool:
        """Get hold state"""
        return self._is_held

    def set_held(self, held: bool) -> None:
        """Set hold state and update related button states"""
        if self._is_held != held:
            self._is_held = held
            self.hold_changed.emit(held)

            if held:
                # Held: Disable hold button, enable release button
                self.set_button_enabled("hold", False)
                self.set_button_enabled("hold_release", True)
                self.update_status("Force measurement held", "info")
            else:
                # Released: Enable hold button, disable release button
                self.set_button_enabled("hold", True)
                self.set_button_enabled("hold_release", False)
                self.update_status("Force measurement released", "info")

    # Force tracking
    @property
    def current_force(self) -> Optional[float]:
        """Get current force"""
        return self._current_force

    def set_force(self, force: float) -> None:
        """Update current force"""
        self._current_force = force
        self.force_changed.emit(force)

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

    # Measurement state management
    def set_measurement_in_progress(self, in_progress: bool) -> None:
        """Set measurement in progress state and update button states"""
        if in_progress:
            # Measurement in progress: disable most buttons
            self.set_button_enabled("disconnect", False)
            self.set_button_enabled("zero_calibration", False)
            self.set_button_enabled("read_force", False)
            self.set_button_enabled("read_peak_force", False)
            self.set_button_enabled("hold", False)
            self.set_button_enabled("hold_release", False)
        else:
            # Measurement completed: restore buttons based on connection state
            if self.is_connected:
                self.set_button_enabled("disconnect", True)
                self.set_button_enabled("zero_calibration", True)
                self.set_button_enabled("read_force", True)
                self.set_button_enabled("read_peak_force", True)
                # Restore hold-dependent buttons
                self.set_held(self._is_held)

    # Reset state
    def reset(self) -> None:
        """Reset all states to initial values"""
        self.set_connected(False)
        self._is_held = False
        self._current_force = None
