"""Digital Output State Manager

Manages state and button states for digital output control (output-only).
"""

# Standard library imports
from typing import Dict, List

# Third-party imports
from PySide6.QtCore import QObject, Signal


class DigitalOutputControlState(QObject):
    """
    State manager for digital output control widget (output-only).

    Manages connection state, output states, and button states.
    Emits signals when state changes occur.
    """

    # State change signals
    connection_changed = Signal(bool)  # connected
    output_changed = Signal(int, bool)  # channel, state
    all_outputs_changed = Signal(list)  # all output states
    status_changed = Signal(str, str)  # message, type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message
    button_state_changed = Signal(str, bool)  # button_name, enabled

    def __init__(self):
        super().__init__()
        self._connected = False
        self._output_states: Dict[int, bool] = {}
        self._output_count = 32  # 32 channels for digital output

        # Button states (output-only)
        self._button_states = {
            "connect": True,
            "disconnect": False,
            "write_output": False,
            "read_output": False,
            "reset_all_outputs": False,
        }

    # State properties
    @property
    def connected(self) -> bool:
        """Get connection state"""
        return self._connected

    @property
    def output_count(self) -> int:
        """Get output channel count"""
        return self._output_count

    def get_output_state(self, channel: int) -> bool:
        """Get output state for specific channel"""
        return self._output_states.get(channel, False)

    def get_all_output_states(self) -> List[bool]:
        """Get all output states as list"""
        return [self._output_states.get(i, False) for i in range(self._output_count)]

    # State update methods
    def set_connected(self, connected: bool) -> None:
        """Update connection state"""
        if self._connected != connected:
            self._connected = connected
            self.connection_changed.emit(connected)
            self._update_button_states()

    def set_output_count(self, count: int) -> None:
        """Set output channel count"""
        self._output_count = count

    def set_output_state(self, channel: int, state: bool) -> None:
        """Update output state for specific channel"""
        self._output_states[channel] = state
        self.output_changed.emit(channel, state)

    def set_all_output_states(self, states: List[bool]) -> None:
        """Update all output states"""
        for i, state in enumerate(states):
            self._output_states[i] = state
        self.all_outputs_changed.emit(states)

    # Status and progress
    def show_status(self, message: str, status_type: str = "info") -> None:
        """Show status message"""
        self.status_changed.emit(message, status_type)

    def show_progress(self, message: str) -> None:
        """Show progress indicator"""
        self.progress_changed.emit(True, message)

    def hide_progress(self) -> None:
        """Hide progress indicator"""
        self.progress_changed.emit(False, "")

    # Button state management
    def _update_button_states(self) -> None:
        """Update all button states based on current state"""
        # Connect/Disconnect buttons
        self._set_button_state("connect", not self._connected)
        self._set_button_state("disconnect", self._connected)

        # Output operation buttons (output-only)
        output_enabled = self._connected
        self._set_button_state("write_output", output_enabled)
        self._set_button_state("read_output", output_enabled)
        self._set_button_state("reset_all_outputs", output_enabled)

    def _set_button_state(self, button_name: str, enabled: bool) -> None:
        """Update single button state"""
        if button_name in self._button_states:
            if self._button_states[button_name] != enabled:
                self._button_states[button_name] = enabled
                self.button_state_changed.emit(button_name, enabled)

    def get_button_state(self, button_name: str) -> bool:
        """Get button state"""
        return self._button_states.get(button_name, False)
