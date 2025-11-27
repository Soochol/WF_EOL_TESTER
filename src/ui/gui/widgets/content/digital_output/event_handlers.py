"""Digital Output Event Handlers

Event handling logic for digital output control operations (output-only).
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.digital_io import DigitalIOService

# Local folder imports
from .state_manager import DigitalOutputControlState


class DigitalOutputEventHandlers(QObject):
    """
    Event handlers for digital output control operations (output-only).

    Handles all user interactions and delegates to digital I/O service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    output_written = Signal(bool, str)  # success, message
    output_read = Signal(int, bool)  # channel, state
    all_outputs_reset = Signal(bool, str)  # success, message
    channel_count_read = Signal(int)  # output_count

    def __init__(
        self,
        digital_io_service: DigitalIOService,
        state: DigitalOutputControlState,
        executor_thread=None,  # TestExecutorThread for unified execution
    ):
        super().__init__()
        self.digital_io_service = digital_io_service
        self.state = state
        self.executor_thread = executor_thread

    # Connection operations
    def on_connect_clicked(self) -> None:
        """Handle connect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.connect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Connecting to Digital Output...")
        self.executor_thread.submit_task("digital_output_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.digital_io_service.connect()

            # Read output channel count
            try:
                output_count = await self.digital_io_service.get_output_count()
                if output_count > 0:
                    self.state.set_output_count(output_count)
                    self.channel_count_read.emit(output_count)
            except Exception as e:
                logger.warning(f"Failed to read output count: {e}")
                self.state.set_output_count(8)  # Default 8 channels

            self.state.set_connected(True)
            self.state.hide_progress()
            self.connect_completed.emit(True, "Digital Output connected successfully")
        except Exception as e:
            error_type = type(e).__name__
            self.state.hide_progress()
            error_msg = f"Failed to connect to Digital Output: {error_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.connect_completed.emit(False, error_msg)

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from Digital Output...")
        self.executor_thread.submit_task("digital_output_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            await self.digital_io_service.disconnect()
            self.state.set_connected(False)
            self.state.hide_progress()
            self.disconnect_completed.emit(True, "Digital Output disconnected successfully")
        except Exception as e:
            error_type = type(e).__name__
            self.state.hide_progress()
            error_msg = f"Failed to disconnect from Digital Output: {error_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.disconnect_completed.emit(False, error_msg)

    # Output operations
    def on_write_output_clicked(self, channel: int, level: bool) -> None:
        """Handle write output button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.output_written.emit(False, "System error: Executor thread not initialized")
            return

        self.executor_thread.submit_task(
            f"digital_output_write_{channel}", self._async_write_output(channel, level)
        )

    async def _async_write_output(self, channel: int, level: bool) -> None:
        """Async write output operation"""
        try:
            success = await self.digital_io_service.write_output(channel, level)
            if success:
                self.state.set_output_state(channel, level)
                level_str = "HIGH" if level else "LOW"
                self.output_written.emit(True, f"Output {channel} set to {level_str}")
            else:
                self.output_written.emit(False, f"Failed to set output {channel}")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"Failed to write output {channel}: {error_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.output_written.emit(False, error_msg)

    def on_read_output_clicked(self, channel: int) -> None:
        """Handle read output button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task(
            f"digital_output_read_{channel}", self._async_read_output(channel)
        )

    async def _async_read_output(self, channel: int) -> None:
        """Async read output operation"""
        try:
            state = await self.digital_io_service.read_output(channel)
            self.state.set_output_state(channel, state)
            self.output_read.emit(channel, state)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Failed to read output channel {channel}: {error_type}: {e}", exc_info=True)
            self.output_read.emit(channel, False)

    def on_reset_all_outputs_clicked(self) -> None:
        """Handle reset all outputs button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.all_outputs_reset.emit(False, "System error: Executor thread not initialized")
            return

        self.executor_thread.submit_task(
            "digital_output_reset_all", self._async_reset_all_outputs()
        )

    async def _async_reset_all_outputs(self) -> None:
        """Async reset all outputs operation"""
        try:
            success = await self.digital_io_service.reset_all_outputs()
            if success:
                # Update state to all LOW
                for i in range(self.state.output_count):
                    self.state.set_output_state(i, False)
                self.all_outputs_reset.emit(True, "All outputs reset to LOW")
            else:
                self.all_outputs_reset.emit(False, "Failed to reset all outputs")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"Failed to reset all outputs: {error_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.all_outputs_reset.emit(False, error_msg)

    def on_read_all_outputs_clicked(self) -> None:
        """Handle read all outputs button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task(
            "digital_output_read_all", self._async_read_all_outputs()
        )

    async def _async_read_all_outputs(self) -> None:
        """Async read all outputs operation"""
        try:
            states = await self.digital_io_service.read_all_outputs()
            # Update state for all channels
            for i, state in enumerate(states):
                if i < self.state.output_count:
                    self.state.set_output_state(i, state)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Failed to read all outputs: {error_type}: {e}", exc_info=True)
