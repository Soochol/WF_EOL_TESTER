"""Power Supply Event Handlers

Event handling logic for power supply control operations.
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.power import PowerService

# Local folder imports
from .state_manager import PowerSupplyControlState


class PowerSupplyEventHandlers(QObject):
    """
    Event handlers for power supply control operations.

    Handles all user interactions and delegates to power service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    enable_output_completed = Signal(bool, str)  # success, message
    disable_output_completed = Signal(bool, str)  # success, message
    set_voltage_completed = Signal(bool, str)  # success, message
    set_current_completed = Signal(bool, str)  # success, message
    voltage_read = Signal(float)  # voltage
    current_read = Signal(float)  # current
    measurements_read = Signal(float, float, float)  # voltage, current, power

    def __init__(
        self,
        power_service: PowerService,
        state: PowerSupplyControlState,
        executor_thread=None,  # TestExecutorThread for unified execution
    ):
        super().__init__()
        self.power_service = power_service
        self.state = state
        self.executor_thread = executor_thread

    # Connection operations
    def on_connect_clicked(self) -> None:
        """Handle connect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.connect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Connecting to power supply...")
        self.executor_thread.submit_task("power_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.power_service.connect()
            self.state.set_connected(True)
            self.state.hide_progress()
            self.connect_completed.emit(True, "Power supply connected successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to connect to power supply: {str(e)}"
            logger.error(error_msg)
            self.connect_completed.emit(False, error_msg)

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from power supply...")
        self.executor_thread.submit_task("power_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            await self.power_service.disconnect()
            self.state.set_connected(False)
            self.state.set_output_enabled(False)
            self.state.hide_progress()
            self.disconnect_completed.emit(True, "Power supply disconnected successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to disconnect from power supply: {str(e)}"
            logger.error(error_msg)
            self.disconnect_completed.emit(False, error_msg)

    # Output control operations
    def on_enable_output_clicked(self) -> None:
        """Handle enable output button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.enable_output_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Enabling power output...")
        self.executor_thread.submit_task("power_enable_output", self._async_enable_output())

    async def _async_enable_output(self) -> None:
        """Async enable output operation"""
        try:
            await self.power_service.enable_output()
            self.state.set_output_enabled(True)
            self.state.hide_progress()
            self.enable_output_completed.emit(True, "Power output enabled successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to enable output: {str(e)}"
            logger.error(error_msg)
            self.enable_output_completed.emit(False, error_msg)

    def on_disable_output_clicked(self) -> None:
        """Handle disable output button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disable_output_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disabling power output...")
        self.executor_thread.submit_task("power_disable_output", self._async_disable_output())

    async def _async_disable_output(self) -> None:
        """Async disable output operation"""
        try:
            await self.power_service.disable_output()
            self.state.set_output_enabled(False)
            self.state.hide_progress()
            self.disable_output_completed.emit(True, "Power output disabled successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to disable output: {str(e)}"
            logger.error(error_msg)
            self.disable_output_completed.emit(False, error_msg)

    # Voltage/Current control operations
    def on_set_voltage_clicked(self, voltage: float) -> None:
        """Handle set voltage button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.set_voltage_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting voltage to {voltage}V...")
        self.executor_thread.submit_task(
            "power_set_voltage", self._async_set_voltage(voltage)
        )

    async def _async_set_voltage(self, voltage: float) -> None:
        """Async set voltage operation"""
        try:
            await self.power_service.set_voltage(voltage)
            self.state.hide_progress()
            self.set_voltage_completed.emit(True, f"Voltage set to {voltage}V successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to set voltage: {str(e)}"
            logger.error(error_msg)
            self.set_voltage_completed.emit(False, error_msg)

    def on_set_current_clicked(self, current: float) -> None:
        """Handle set current button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.set_current_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting current limit to {current}A...")
        self.executor_thread.submit_task(
            "power_set_current", self._async_set_current(current)
        )

    async def _async_set_current(self, current: float) -> None:
        """Async set current operation"""
        try:
            await self.power_service.set_current_limit(current)
            self.state.hide_progress()
            self.set_current_completed.emit(True, f"Current limit set to {current}A successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to set current: {str(e)}"
            logger.error(error_msg)
            self.set_current_completed.emit(False, error_msg)

    # Measurement operations
    def on_get_voltage_clicked(self) -> None:
        """Handle get voltage button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task("power_get_voltage", self._async_get_voltage())

    async def _async_get_voltage(self) -> None:
        """Async get voltage operation"""
        try:
            voltage = await self.power_service.get_voltage()
            self.voltage_read.emit(voltage)
        except Exception as e:
            logger.error(f"Failed to read voltage: {e}")
            self.voltage_read.emit(-1.0)

    def on_get_current_clicked(self) -> None:
        """Handle get current button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task("power_get_current", self._async_get_current())

    async def _async_get_current(self) -> None:
        """Async get current operation"""
        try:
            current = await self.power_service.get_current()
            self.current_read.emit(current)
        except Exception as e:
            logger.error(f"Failed to read current: {e}")
            self.current_read.emit(-1.0)

    def on_get_all_measurements_clicked(self) -> None:
        """Handle get all measurements button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task(
            "power_get_all_measurements", self._async_get_all_measurements()
        )

    async def _async_get_all_measurements(self) -> None:
        """Async get all measurements operation"""
        try:
            measurements = await self.power_service.get_all_measurements()
            voltage = measurements.get("voltage", 0.0)
            current = measurements.get("current", 0.0)
            power = measurements.get("power", 0.0)
            self.measurements_read.emit(voltage, current, power)
        except Exception as e:
            logger.error(f"Failed to read measurements: {e}")
            self.measurements_read.emit(-1.0, -1.0, -1.0)
