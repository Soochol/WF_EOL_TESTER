"""MCU State Manager

Centralized state management for MCU control operations.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject, Signal


class MCUControlState(QObject):
    """
    Centralized state manager for MCU control.

    Manages:
    - Connection state
    - Temperature tracking
    - Test mode state
    - Button enable/disable states
    - Status messages
    """

    # State change signals
    connection_changed = Signal(bool)  # is_connected
    temperature_changed = Signal(float)  # temperature in °C
    test_mode_changed = Signal(str)  # test mode text
    button_state_changed = Signal(str, bool)  # button_name, enabled
    status_changed = Signal(str, str)  # status_text, status_type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message

    def __init__(self, enable_buttons_initially: bool = False):
        super().__init__()

        # Connection state
        self._is_connected = False

        # Temperature tracking
        self._current_temperature: Optional[float] = None

        # Test mode state
        self._test_mode = "Normal"

        # Button states
        if enable_buttons_initially:
            # Development mode: all buttons enabled initially for testing
            self._button_states = {
                "connect": True,
                "disconnect": True,
                "read_temp": True,
                "enter_test_mode": True,
                "set_operating_temp": True,
                "set_cooling_temp": True,
                "set_upper_temp": True,
                "set_fan_speed": True,
                "wait_boot": True,
                "start_heating": True,
                "start_cooling": True,
            }
        else:
            # Production mode: only connect button enabled initially
            self._button_states = {
                "connect": True,
                "disconnect": False,
                "read_temp": False,
                "enter_test_mode": False,
                "set_operating_temp": False,
                "set_cooling_temp": False,
                "set_upper_temp": False,
                "set_fan_speed": False,
                "wait_boot": False,
                "start_heating": False,
                "start_cooling": False,
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
                # Connected: enable all control buttons
                self.set_button_enabled("connect", False)
                self.set_button_enabled("disconnect", True)
                self.set_button_enabled("read_temp", True)
                self.set_button_enabled("enter_test_mode", True)
                self.set_button_enabled("set_operating_temp", True)
                self.set_button_enabled("set_cooling_temp", True)
                self.set_button_enabled("set_upper_temp", True)
                self.set_button_enabled("set_fan_speed", True)
                self.set_button_enabled("wait_boot", True)
                self.set_button_enabled("start_heating", True)
                self.set_button_enabled("start_cooling", True)
                self.update_status("MCU connected", "info")
            else:
                # Disconnected: disable all control buttons
                self.set_button_enabled("connect", True)
                self.set_button_enabled("disconnect", False)
                self.set_button_enabled("read_temp", False)
                self.set_button_enabled("enter_test_mode", False)
                self.set_button_enabled("set_operating_temp", False)
                self.set_button_enabled("set_cooling_temp", False)
                self.set_button_enabled("set_upper_temp", False)
                self.set_button_enabled("set_fan_speed", False)
                self.set_button_enabled("wait_boot", False)
                self.set_button_enabled("start_heating", False)
                self.set_button_enabled("start_cooling", False)
                self.update_status("MCU disconnected", "warning")

                # Reset other states
                self._current_temperature = None
                self._test_mode = "Normal"

    # Temperature tracking
    @property
    def current_temperature(self) -> Optional[float]:
        """Get current temperature"""
        return self._current_temperature

    def set_temperature(self, temperature: float) -> None:
        """Update current temperature"""
        self._current_temperature = temperature
        self.temperature_changed.emit(temperature)

    # Test mode state
    @property
    def test_mode(self) -> str:
        """Get test mode"""
        return self._test_mode

    def set_test_mode(self, mode: str) -> None:
        """Update test mode"""
        if self._test_mode != mode:
            self._test_mode = mode
            self.test_mode_changed.emit(mode)

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

    # Reset state
    def reset(self) -> None:
        """Reset all states to initial values"""
        self.set_connected(False)
        self._current_temperature = None
        self._test_mode = "Normal"
