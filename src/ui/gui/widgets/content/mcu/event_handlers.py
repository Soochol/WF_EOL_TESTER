"""MCU Event Handlers

Event handling logic for MCU control operations.
"""

# Standard library imports
import asyncio

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.mcu import MCUService
from domain.enums.mcu_enums import TestMode

# Local folder imports
from .state_manager import MCUControlState


class MCUEventHandlers(QObject):
    """
    Event handlers for MCU control operations.

    Handles all user interactions and delegates to MCU service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    temperature_read = Signal(float)  # temperature
    test_mode_completed = Signal(bool, str)  # success, message
    operating_temp_set = Signal(bool, str)  # success, message
    cooling_temp_set = Signal(bool, str)  # success, message
    upper_temp_set = Signal(bool, str)  # success, message
    fan_speed_set = Signal(bool, str)  # success, message
    boot_wait_completed = Signal(bool, str)  # success, message
    heating_started = Signal()  # heating operation started
    heating_completed = Signal(bool, str)  # success, message
    cooling_started = Signal()  # cooling operation started
    cooling_completed = Signal(bool, str)  # success, message

    def __init__(
        self,
        mcu_service: MCUService,
        state: MCUControlState,
        executor_thread=None,  # ✅ TestExecutorThread for unified execution
    ):
        super().__init__()
        self.mcu_service = mcu_service
        self.state = state
        self.executor_thread = executor_thread  # ✅ Store executor thread

    # Connection operations
    def on_connect_clicked(self) -> None:
        """Handle connect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.connect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Connecting to MCU...")
        self.executor_thread.submit_task("mcu_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.mcu_service.connect()
            self.state.set_connected(True)
            self.connect_completed.emit(True, "MCU connected successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"MCU connect failed: {error_type}: {e}", exc_info=True)
            self.connect_completed.emit(False, f"Connect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from MCU...")
        self.executor_thread.submit_task("mcu_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            await self.mcu_service.disconnect()
            self.state.set_connected(False)
            self.disconnect_completed.emit(True, "MCU disconnected")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"MCU disconnect failed: {error_type}: {e}", exc_info=True)
            self.disconnect_completed.emit(False, f"Disconnect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Temperature operations
    def on_read_temperature_clicked(self) -> None:
        """Handle read temperature button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.state.show_progress("Reading temperature...")
        self.executor_thread.submit_task("mcu_read_temp", self._async_read_temperature())

    async def _async_read_temperature(self) -> None:
        """Async read temperature operation"""
        try:
            temperature = await self.mcu_service.get_temperature()
            self.state.set_temperature(temperature)
            self.temperature_read.emit(temperature)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Read temperature failed: {error_type}: {e}", exc_info=True)
            self.state.update_status(f"Read temperature failed: {error_type}: {str(e)}", "error")
            self.temperature_read.emit(-999.0)  # Error indicator
        finally:
            self.state.hide_progress()

    def on_set_operating_temperature(self, temperature: float) -> None:
        """Handle set operating temperature request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.operating_temp_set.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting operating temperature to {temperature:.1f}°C...")
        self.executor_thread.submit_task("mcu_set_op_temp", self._async_set_operating_temperature(temperature))

    async def _async_set_operating_temperature(self, temperature: float) -> None:
        """Async set operating temperature operation"""
        try:
            await self.mcu_service.set_operating_temperature(temperature)
            self.operating_temp_set.emit(True, f"Operating temperature set to {temperature:.1f}°C")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Set operating temperature failed: {error_type}: {e}", exc_info=True)
            self.operating_temp_set.emit(False, f"Set operating temperature failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_set_cooling_temperature(self, temperature: float) -> None:
        """Handle set cooling temperature request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.cooling_temp_set.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting cooling temperature to {temperature:.1f}°C...")
        self.executor_thread.submit_task("mcu_set_cool_temp", self._async_set_cooling_temperature(temperature))

    async def _async_set_cooling_temperature(self, temperature: float) -> None:
        """Async set cooling temperature operation"""
        try:
            await self.mcu_service.set_cooling_temperature(temperature)
            self.cooling_temp_set.emit(True, f"Cooling temperature set to {temperature:.1f}°C")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Set cooling temperature failed: {error_type}: {e}", exc_info=True)
            self.cooling_temp_set.emit(False, f"Set cooling temperature failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_set_upper_temperature(self, temperature: float) -> None:
        """Handle set upper temperature request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.upper_temp_set.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting upper temperature limit to {temperature:.1f}°C...")
        self.executor_thread.submit_task("mcu_set_upper_temp", self._async_set_upper_temperature(temperature))

    async def _async_set_upper_temperature(self, temperature: float) -> None:
        """Async set upper temperature operation"""
        try:
            await self.mcu_service.set_upper_temperature(temperature)
            self.upper_temp_set.emit(True, f"Upper temperature limit set to {temperature:.1f}°C")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Set upper temperature failed: {error_type}: {e}", exc_info=True)
            self.upper_temp_set.emit(False, f"Set upper temperature failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Test mode operations
    def on_enter_test_mode_clicked(self) -> None:
        """Handle enter test mode button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.test_mode_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Entering test mode...")
        self.executor_thread.submit_task("mcu_test_mode", self._async_enter_test_mode())

    async def _async_enter_test_mode(self) -> None:
        """Async enter test mode operation"""
        try:
            await self.mcu_service.set_test_mode(TestMode.MODE_1)
            self.state.set_test_mode("Test Mode")
            self.test_mode_completed.emit(True, "Entered test mode successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Enter test mode failed: {error_type}: {e}", exc_info=True)
            self.test_mode_completed.emit(False, f"Enter test mode failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Fan control operations
    def on_set_fan_speed(self, fan_speed: int) -> None:
        """Handle set fan speed request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.fan_speed_set.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Setting fan speed to level {fan_speed}...")
        self.executor_thread.submit_task("mcu_fan_speed", self._async_set_fan_speed(fan_speed))

    async def _async_set_fan_speed(self, fan_speed: int) -> None:
        """Async set fan speed operation"""
        try:
            # Convert user input (0-10) to service interface range (1-10)
            if fan_speed == 0:
                service_fan_speed = 1  # Minimum service level
            else:
                service_fan_speed = fan_speed

            await self.mcu_service.set_fan_speed(service_fan_speed)
            self.fan_speed_set.emit(True, f"Fan speed set to level {fan_speed}")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Set fan speed failed: {error_type}: {e}", exc_info=True)
            self.fan_speed_set.emit(False, f"Set fan speed failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Advanced operations
    def on_wait_boot_clicked(self) -> None:
        """Handle wait boot complete button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.boot_wait_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Waiting for MCU boot complete...")
        self.executor_thread.submit_task("mcu_wait_boot", self._async_wait_boot_complete())

    async def _async_wait_boot_complete(self) -> None:
        """Async wait boot complete operation"""
        try:
            if hasattr(self.mcu_service, "wait_boot_complete"):
                await self.mcu_service.wait_boot_complete()
            else:
                await asyncio.sleep(2.0)  # Fallback
            self.boot_wait_completed.emit(True, "Boot complete signal received")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Wait boot complete failed: {error_type}: {e}", exc_info=True)
            self.boot_wait_completed.emit(False, f"Wait boot complete failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_start_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int
    ) -> None:
        """Handle start standby heating request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.heating_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(
            f"Starting heating (op:{operating_temp:.1f}°C, standby:{standby_temp:.1f}°C)..."
        )

        # Emit heating started signal for temperature monitoring
        self.heating_started.emit()

        self.executor_thread.submit_task(
            "mcu_heating",
            self._async_start_heating(operating_temp, standby_temp, hold_time_ms)
        )

    async def _async_start_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int
    ) -> None:
        """Async start standby heating operation"""
        try:
            await self.mcu_service.start_standby_heating(
                operating_temp, standby_temp, hold_time_ms
            )
            self.heating_completed.emit(True, "Standby heating started successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Start heating failed: {error_type}: {e}", exc_info=True)
            self.heating_completed.emit(False, f"Start heating failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_start_cooling_clicked(self) -> None:
        """Handle start standby cooling button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.cooling_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Starting standby cooling...")

        # Emit cooling started signal for temperature monitoring
        self.cooling_started.emit()

        self.executor_thread.submit_task("mcu_cooling", self._async_start_cooling())

    async def _async_start_cooling(self) -> None:
        """Async start standby cooling operation"""
        try:
            await self.mcu_service.start_standby_cooling()
            self.cooling_completed.emit(True, "Standby cooling started successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Start cooling failed: {error_type}: {e}", exc_info=True)
            self.cooling_completed.emit(False, f"Start cooling failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()
