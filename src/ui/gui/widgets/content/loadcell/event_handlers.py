"""Loadcell Event Handlers

Event handling logic for loadcell control operations.
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.loadcell import LoadCellService

# Local folder imports
from .state_manager import LoadcellControlState


class LoadcellEventHandlers(QObject):
    """
    Event handlers for loadcell control operations.

    Handles all user interactions and delegates to loadcell service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    zero_calibration_completed = Signal(bool, str)  # success, message
    force_read = Signal(float)  # force value
    peak_force_read = Signal(float)  # peak force value
    hold_completed = Signal(bool, str)  # success, message
    hold_release_completed = Signal(bool, str)  # success, message

    def __init__(
        self,
        loadcell_service: LoadCellService,
        state: LoadcellControlState,
        executor_thread=None  # ✅ TestExecutorThread for unified execution
    ):
        super().__init__()
        self.loadcell_service = loadcell_service
        self.state = state
        self.executor_thread = executor_thread  # ✅ Store executor thread

    # Connection operations
    def on_connect_clicked(self) -> None:
        """Handle connect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.connect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Connecting to loadcell...")
        self.executor_thread.submit_task("loadcell_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.loadcell_service.connect()
            self.state.set_connected(True)
            self.connect_completed.emit(True, "Loadcell connected successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Loadcell connect failed: {error_type}: {e}", exc_info=True)
            self.connect_completed.emit(False, f"Connect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from loadcell...")
        self.executor_thread.submit_task("loadcell_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            # Release hold if active
            if self.state.is_held:
                logger.info("Disconnect: Releasing hold first...")
                await self.loadcell_service.hold_release()
                self.state.set_held(False)
                logger.info("Disconnect: Hold released")

            # Disconnect from loadcell
            await self.loadcell_service.disconnect()
            self.state.set_connected(False)
            self.disconnect_completed.emit(True, "Loadcell disconnected")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Loadcell disconnect failed: {error_type}: {e}", exc_info=True)
            self.disconnect_completed.emit(False, f"Disconnect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Calibration operations
    def on_zero_calibration_clicked(self) -> None:
        """Handle zero calibration button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.zero_calibration_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Performing zero calibration...")
        self.executor_thread.submit_task("loadcell_zero_calibration", self._async_zero_calibration())

    async def _async_zero_calibration(self) -> None:
        """Async zero calibration operation"""
        try:
            await self.loadcell_service.zero_calibration()
            self.zero_calibration_completed.emit(True, "Zero calibration completed")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Zero calibration failed: {error_type}: {e}", exc_info=True)
            self.zero_calibration_completed.emit(False, f"Calibration failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Measurement operations
    def on_read_force_clicked(self) -> None:
        """Handle read force button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.state.show_progress("Reading force...")
        self.executor_thread.submit_task("loadcell_read_force", self._async_read_force())

    async def _async_read_force(self) -> None:
        """Async read force operation"""
        try:
            force_value = await self.loadcell_service.read_force()
            self.state.set_force(force_value.value)
            self.force_read.emit(force_value.value)
            self.state.update_status(f"Force: {force_value.value:.3f} kgf", "info")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Read force failed: {error_type}: {e}", exc_info=True)
            self.state.update_status(f"Read force failed: {error_type}: {str(e)}", "error")
        finally:
            self.state.hide_progress()

    def on_read_peak_force_clicked(self, duration_ms: int = 1000, sampling_interval_ms: int = 200) -> None:
        """Handle read peak force button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.state.show_progress(f"Reading peak force ({duration_ms}ms)...")
        self.executor_thread.submit_task(
            "loadcell_read_peak_force",
            self._async_read_peak_force(duration_ms, sampling_interval_ms)
        )

    async def _async_read_peak_force(self, duration_ms: int, sampling_interval_ms: int) -> None:
        """Async read peak force operation"""
        try:
            self.state.set_measurement_in_progress(True)
            peak_force = await self.loadcell_service.read_peak_force(duration_ms, sampling_interval_ms)
            self.state.set_force(peak_force.value)
            self.peak_force_read.emit(peak_force.value)
            self.state.update_status(f"Peak Force: {peak_force.value:.3f} kgf", "info")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Read peak force failed: {error_type}: {e}", exc_info=True)
            self.state.update_status(f"Read peak force failed: {error_type}: {str(e)}", "error")
        finally:
            self.state.set_measurement_in_progress(False)
            self.state.hide_progress()

    # Hold operations
    def on_hold_clicked(self) -> None:
        """Handle hold button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.hold_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Holding measurement...")
        self.executor_thread.submit_task("loadcell_hold", self._async_hold())

    async def _async_hold(self) -> None:
        """Async hold operation"""
        try:
            success = await self.loadcell_service.hold()
            if success:
                self.state.set_held(True)
                self.hold_completed.emit(True, "Measurement held")
            else:
                self.hold_completed.emit(False, "Hold operation failed")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Hold failed: {error_type}: {e}", exc_info=True)
            self.hold_completed.emit(False, f"Hold failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_hold_release_clicked(self) -> None:
        """Handle hold release button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.hold_release_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Releasing hold...")
        self.executor_thread.submit_task("loadcell_hold_release", self._async_hold_release())

    async def _async_hold_release(self) -> None:
        """Async hold release operation"""
        try:
            success = await self.loadcell_service.hold_release()
            if success:
                self.state.set_held(False)
                self.hold_release_completed.emit(True, "Hold released")
            else:
                self.hold_release_completed.emit(False, "Release operation failed")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Hold release failed: {error_type}: {e}", exc_info=True)
            self.hold_release_completed.emit(False, f"Release failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()
