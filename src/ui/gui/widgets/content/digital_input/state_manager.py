"""Digital Input State Manager

Manages state and button states for digital input control (input-only).
"""

# Standard library imports
from typing import Dict, List

# Third-party imports
from PySide6.QtCore import QObject, Signal


class DigitalInputControlState(QObject):
    """
    State manager for digital input control widget (input-only).

    Manages connection state, input states, and button states.
    Emits signals when state changes occur.
    """

    # State change signals
    connection_changed = Signal(bool)  # connected
    input_changed = Signal(int, bool)  # channel, state
    all_inputs_changed = Signal(list)  # all input states
    status_changed = Signal(str, str)  # message, type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message
    button_state_changed = Signal(str, bool)  # button_name, enabled

    def __init__(self):
        super().__init__()
        self._connected = False
        self._input_states: Dict[int, bool] = {}
        self._input_count = 32  # Default 32 channels

        # Button states (input-only)
        self._button_states = {
            "connect": True,
            "disconnect": False,
            "read_input": False,
            "read_all_inputs": False,
        }

    # State properties
    @property
    def connected(self) -> bool:
        """Get connection state"""
        return self._connected

    @property
    def input_count(self) -> int:
        """Get input channel count"""
        return self._input_count

    def get_input_state(self, channel: int) -> bool:
        """Get input state for specific channel"""
        return self._input_states.get(channel, False)

    def get_all_input_states(self) -> List[bool]:
        """Get all input states as list"""
        return [self._input_states.get(i, False) for i in range(self._input_count)]

    # State update methods
    def set_connected(self, connected: bool) -> None:
        """Update connection state"""
        if self._connected != connected:
            self._connected = connected
            self.connection_changed.emit(connected)
            self._update_button_states()

    def set_input_count(self, count: int) -> None:
        """Set input channel count"""
        self._input_count = count

    def set_input_state(self, channel: int, state: bool) -> None:
        """Update input state for specific channel"""
        self._input_states[channel] = state
        self.input_changed.emit(channel, state)

    def set_all_input_states(self, states: List[bool]) -> None:
        """Update all input states"""
        for i, state in enumerate(states):
            self._input_states[i] = state
        self.all_inputs_changed.emit(states)

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

        # Input operation buttons (input-only)
        input_enabled = self._connected
        self._set_button_state("read_input", input_enabled)
        self._set_button_state("read_all_inputs", input_enabled)

    def _set_button_state(self, button_name: str, enabled: bool) -> None:
        """Update single button state"""
        if button_name in self._button_states:
            if self._button_states[button_name] != enabled:
                self._button_states[button_name] = enabled
                self.button_state_changed.emit(button_name, enabled)

    def get_button_state(self, button_name: str) -> bool:
        """Get button state"""
        return self._button_states.get(button_name, False)
