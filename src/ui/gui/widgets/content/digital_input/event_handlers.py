"""Digital Input Event Handlers

Event handling logic for digital input control operations (input-only).
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.digital_io import DigitalIOService

# Local folder imports
from .state_manager import DigitalInputControlState


class DigitalInputEventHandlers(QObject):
    """
    Event handlers for digital input control operations (input-only).

    Handles all user interactions and delegates to digital I/O service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    input_read = Signal(int, bool, bool)  # channel, raw_state, actual_state (with B-contact logic)
    all_inputs_read = Signal(list)  # all input states
    channel_count_read = Signal(int)  # input_count

    def __init__(
        self,
        digital_io_service: DigitalIOService,
        state: DigitalInputControlState,
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

        self.state.show_progress("Connecting to Digital Input...")
        self.executor_thread.submit_task("digital_input_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.digital_io_service.connect()

            # Read input channel count
            try:
                input_count = await self.digital_io_service.get_input_count()
                if input_count > 0:
                    self.state.set_input_count(input_count)
                    self.channel_count_read.emit(input_count)
            except Exception as e:
                logger.warning(f"Failed to read input count: {e}")
                self.state.set_input_count(32)  # Default 32 channels

            self.state.set_connected(True)
            self.state.hide_progress()
            self.connect_completed.emit(True, "Digital Input connected successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to connect to Digital Input: {str(e)}"
            logger.error(error_msg)
            self.connect_completed.emit(False, error_msg)

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from Digital Input...")
        self.executor_thread.submit_task("digital_input_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation"""
        try:
            await self.digital_io_service.disconnect()
            self.state.set_connected(False)
            self.state.hide_progress()
            self.disconnect_completed.emit(True, "Digital Input disconnected successfully")
        except Exception as e:
            self.state.hide_progress()
            error_msg = f"Failed to disconnect from Digital Input: {str(e)}"
            logger.error(error_msg)
            self.disconnect_completed.emit(False, error_msg)

    # Input operations
    def on_read_input_clicked(self, channel: int) -> None:
        """Handle read input button click for specific channel"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task(
            f"digital_input_read_{channel}", self._async_read_input(channel)
        )

    async def _async_read_input(self, channel: int) -> None:
        """Async read input operation"""
        try:
            raw_state = await self.digital_io_service.read_input(channel)

            # Apply B-contact logic for button channels (8, 9) - inverted logic
            if channel in [8, 9]:  # Button channels with B-contact (normally closed)
                actual_state = not raw_state
            else:
                actual_state = raw_state

            self.state.set_input_state(channel, actual_state)
            self.input_read.emit(channel, raw_state, actual_state)
        except Exception as e:
            logger.error(f"Failed to read input channel {channel}: {e}")
            self.input_read.emit(channel, False, False)

    def on_read_all_inputs_clicked(self) -> None:
        """Handle read all inputs button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.executor_thread.submit_task("digital_input_read_all", self._async_read_all_inputs())

    async def _async_read_all_inputs(self) -> None:
        """Async read all inputs operation"""
        try:
            raw_states = await self.digital_io_service.read_all_inputs()

            # Apply B-contact logic where needed
            actual_states = []
            for channel, raw_state in enumerate(raw_states):
                if channel in [8, 9]:  # B-contact channels
                    actual_state = not raw_state
                else:
                    actual_state = raw_state
                actual_states.append(actual_state)

            self.state.set_all_input_states(actual_states)
            self.all_inputs_read.emit(actual_states)
        except Exception as e:
            logger.error(f"Failed to read all inputs: {e}")
            self.all_inputs_read.emit([False] * self.state.input_count)
