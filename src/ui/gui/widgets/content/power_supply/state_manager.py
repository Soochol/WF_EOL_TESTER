"""Power Supply State Manager

Manages state and button states for power supply control.
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal


class PowerSupplyControlState(QObject):
    """
    State manager for power supply control widget.

    Manages connection state, output state, and button states.
    Emits signals when state changes occur.
    """

    # State change signals
    connection_changed = Signal(bool)  # connected
    output_changed = Signal(bool)  # enabled
    voltage_changed = Signal(float)  # voltage
    current_changed = Signal(float)  # current
    power_changed = Signal(float)  # power
    status_changed = Signal(str, str)  # message, type (info/warning/error)
    progress_changed = Signal(bool, str)  # visible, message
    button_state_changed = Signal(str, bool)  # button_name, enabled

    def __init__(self):
        super().__init__()
        self._connected = False
        self._output_enabled = False
        self._voltage = 0.0
        self._current = 0.0
        self._power = 0.0

        # Button states
        self._button_states = {
            "connect": True,
            "disconnect": False,
            "enable_output": False,
            "disable_output": False,
            "set_voltage": False,
            "set_current": False,
            "get_voltage": False,
            "get_current": False,
            "get_all_measurements": False,
        }

    # State properties
    @property
    def connected(self) -> bool:
        """Get connection state"""
        return self._connected

    @property
    def output_enabled(self) -> bool:
        """Get output state"""
        return self._output_enabled

    @property
    def voltage(self) -> float:
        """Get voltage"""
        return self._voltage

    @property
    def current(self) -> float:
        """Get current"""
        return self._current

    @property
    def power(self) -> float:
        """Get power"""
        return self._power

    # State update methods
    def set_connected(self, connected: bool) -> None:
        """Update connection state"""
        if self._connected != connected:
            self._connected = connected
            self.connection_changed.emit(connected)
            self._update_button_states()

    def set_output_enabled(self, enabled: bool) -> None:
        """Update output state"""
        if self._output_enabled != enabled:
            self._output_enabled = enabled
            self.output_changed.emit(enabled)
            self._update_button_states()

    def set_voltage(self, voltage: float) -> None:
        """Update voltage"""
        self._voltage = voltage
        self.voltage_changed.emit(voltage)

    def set_current(self, current: float) -> None:
        """Update current"""
        self._current = current
        self.current_changed.emit(current)

    def set_power(self, power: float) -> None:
        """Update power"""
        self._power = power
        self.power_changed.emit(power)

    def update_measurements(self, voltage: float, current: float, power: float) -> None:
        """Update all measurements at once"""
        self.set_voltage(voltage)
        self.set_current(current)
        self.set_power(power)

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

        # Output control buttons
        self._set_button_state("enable_output", self._connected and not self._output_enabled)
        self._set_button_state("disable_output", self._connected and self._output_enabled)

        # Control and measurement buttons
        control_enabled = self._connected
        self._set_button_state("set_voltage", control_enabled)
        self._set_button_state("set_current", control_enabled)
        self._set_button_state("get_voltage", control_enabled)
        self._set_button_state("get_current", control_enabled)
        self._set_button_state("get_all_measurements", control_enabled)

    def _set_button_state(self, button_name: str, enabled: bool) -> None:
        """Update single button state"""
        if button_name in self._button_states:
            if self._button_states[button_name] != enabled:
                self._button_states[button_name] = enabled
                self.button_state_changed.emit(button_name, enabled)

    def get_button_state(self, button_name: str) -> bool:
        """Get button state"""
        return self._button_states.get(button_name, False)
