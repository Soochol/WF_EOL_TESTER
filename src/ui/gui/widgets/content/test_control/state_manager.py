"""Test Control State Manager

Manages the state and data for test controls.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal

# Local application imports
from ui.gui.utils.styling import ThemeManager


class TestControlState(QObject):
    """Manages state for test control components"""

    # State change signals
    status_changed = Signal(str, str, object)  # status, icon, progress
    test_sequence_changed = Signal(str)
    serial_number_changed = Signal(str)
    button_state_changed = Signal(str, bool)  # button_name, enabled

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()

        # Current state
        self._current_status = "Ready"
        self._current_icon = "status_ready"
        self._current_progress = 0
        self._current_sequence = "EOL Force Test"
        self._current_serial = "SN123456789"

        # Button states
        self._button_states = {
            "start": True,
            "home": True,
            "pause": True,
            "stop": True,
            "emergency": True,
        }

    @property
    def current_status(self) -> str:
        """Get current test status"""
        return self._current_status

    @property
    def current_icon(self) -> str:
        """Get current status icon"""
        return self._current_icon

    @property
    def current_progress(self) -> int:
        """Get current progress value"""
        return self._current_progress

    @property
    def current_sequence(self) -> str:
        """Get current test sequence"""
        return self._current_sequence

    @property
    def current_serial(self) -> str:
        """Get current serial number"""
        return self._current_serial

    def update_status(
        self, status: str, icon: str = "status_ready", progress: Optional[int] = None
    ) -> None:
        """Update test status"""
        self._current_status = status
        self._current_icon = icon

        if progress is not None:
            self._current_progress = progress

        self.status_changed.emit(status, icon, progress)

    def update_sequence(self, sequence: str) -> None:
        """Update test sequence"""
        if sequence != self._current_sequence:
            self._current_sequence = sequence
            self.test_sequence_changed.emit(sequence)

    def update_serial_number(self, serial: str) -> None:
        """Update serial number"""
        if serial != self._current_serial:
            self._current_serial = serial
            self.serial_number_changed.emit(serial)

    def set_button_enabled(self, button_name: str, enabled: bool) -> None:
        """Set button enabled state"""
        if button_name in self._button_states:
            if self._button_states[button_name] != enabled:
                self._button_states[button_name] = enabled
                self.button_state_changed.emit(button_name, enabled)

    def is_button_enabled(self, button_name: str) -> bool:
        """Check if button is enabled"""
        return self._button_states.get(button_name, True)

    def get_status_style(self, status: str) -> tuple[str, bool]:
        """Get status text style and progress bar mode"""
        status_lower = status.lower()

        if "completed" in status_lower or "success" in status_lower:
            return "color: #00ff00; font-weight: bold;", False  # Green, normal mode
        elif "failed" in status_lower or "error" in status_lower:
            return "color: #ff4444; font-weight: bold;", False  # Red, normal mode
        elif "running" in status_lower or "testing" in status_lower or "executing" in status_lower:
            return "color: #ffaa00; font-weight: bold;", True  # Orange, busy mode
        elif "paused" in status_lower:
            return "color: #4da6ff; font-weight: bold;", False  # Blue, normal mode
        elif "stopped" in status_lower:
            return "color: #ff8800; font-weight: bold;", False  # Orange-red, normal mode
        elif "emergency" in status_lower:
            return "color: #cc0000; font-weight: bold;", False  # Dark red, normal mode
        else:
            return "color: #cccccc; font-weight: bold;", False  # Default gray, normal mode

    def get_progress_bar_style(self, status: str) -> tuple[str, str]:
        """Get progress bar gradient colors and text format"""
        status_lower = status.lower()

        if "completed" in status_lower or "success" in status_lower:
            return "stop: 0 #00ff00, stop: 1 #00cc00", "100%"
        elif "failed" in status_lower or "error" in status_lower:
            return "stop: 0 #ff4444, stop: 1 #cc0000", "Failed"
        elif "running" in status_lower or "testing" in status_lower or "executing" in status_lower:
            return "stop: 0 #2E7D32, stop: 1 #1B5E20", "Progressing..."
        elif "paused" in status_lower:
            return "stop: 0 #4da6ff, stop: 1 #0078d4", "Paused"
        elif "stopped" in status_lower:
            return "stop: 0 #ff8800, stop: 1 #cc6600", "Stopped"
        elif "emergency" in status_lower:
            return "stop: 0 #cc0000, stop: 1 #990000", "Emergency"
        else:
            return "stop: 0 #666666, stop: 1 #404040", "Ready"

    def reset_to_ready(self) -> None:
        """Reset state to ready for new test"""
        self.update_status("Ready", "status_ready", 0)
        # Re-enable all buttons except emergency (always enabled)
        for button in ["start", "home", "pause", "stop"]:
            self.set_button_enabled(button, True)
