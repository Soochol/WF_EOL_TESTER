"""Robot Event Handlers

Event handling logic for robot control operations.
"""

# Third-party imports
from PySide6.QtCore import QObject, Signal
from loguru import logger

# Local application imports
from application.interfaces.hardware.robot import RobotService

# Local folder imports
from .state_manager import RobotControlState


class RobotEventHandlers(QObject):
    """
    Event handlers for robot control operations.

    Handles all user interactions and delegates to robot service.
    Emits signals for async operation results.
    """

    # Async operation result signals
    connect_completed = Signal(bool, str)  # success, message
    disconnect_completed = Signal(bool, str)  # success, message
    servo_on_completed = Signal(bool, str)  # success, message
    servo_off_completed = Signal(bool, str)  # success, message
    home_completed = Signal(bool, str)  # success, message
    move_completed = Signal(bool, str)  # success, message
    position_read = Signal(float)  # position
    stop_completed = Signal(bool, str)  # success, message
    emergency_stop_completed = Signal(bool, str)  # success, message
    load_ratio_read = Signal(float)  # load_ratio
    torque_read = Signal(float)  # torque

    def __init__(
        self,
        robot_service: RobotService,
        state: RobotControlState,
        axis_id: int = 0,
        executor_thread=None  # ✅ TestExecutorThread for unified execution
    ):
        super().__init__()
        self.robot_service = robot_service
        self.state = state
        self.axis_id = axis_id
        self.executor_thread = executor_thread  # ✅ Store executor thread

    # Connection operations
    def on_connect_clicked(self) -> None:
        """Handle connect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available - cannot execute robot operations")
            self.connect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Connecting to robot...")
        self.executor_thread.submit_task("robot_connect", self._async_connect())

    async def _async_connect(self) -> None:
        """Async connect operation"""
        try:
            await self.robot_service.connect()
            self.state.set_connected(True)
            self.connect_completed.emit(True, "Robot connected successfully")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Robot connect failed: {error_type}: {e}", exc_info=True)
            self.connect_completed.emit(False, f"Connect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_disconnect_clicked(self) -> None:
        """Handle disconnect button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.disconnect_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disconnecting from robot...")
        self.executor_thread.submit_task("robot_disconnect", self._async_disconnect())

    async def _async_disconnect(self) -> None:
        """Async disconnect operation with servo off"""
        try:
            # Turn off servo before disconnect if it's on
            if self.state.servo_enabled:
                logger.info("Disconnect: Turning off servo first...")
                await self.robot_service.disable_servo(self.axis_id)
                self.state.set_servo_enabled(False)
                logger.info("Disconnect: Servo disabled")

            # Disconnect from robot
            await self.robot_service.disconnect()
            self.state.set_connected(False)
            self.disconnect_completed.emit(True, "Robot disconnected")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Robot disconnect failed: {error_type}: {e}", exc_info=True)
            self.disconnect_completed.emit(False, f"Disconnect failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Servo operations
    def on_servo_on_clicked(self) -> None:
        """Handle servo on button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.servo_on_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Enabling servo...")
        self.executor_thread.submit_task("robot_servo_on", self._async_servo_on())

    async def _async_servo_on(self) -> None:
        """Async servo on operation"""
        try:
            await self.robot_service.enable_servo(self.axis_id)
            self.state.set_servo_enabled(True)
            self.servo_on_completed.emit(True, "Servo enabled")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Servo on failed: {error_type}: {e}", exc_info=True)
            self.servo_on_completed.emit(False, f"Servo on failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    def on_servo_off_clicked(self) -> None:
        """Handle servo off button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.servo_off_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Disabling servo...")
        self.executor_thread.submit_task("robot_servo_off", self._async_servo_off())

    async def _async_servo_off(self) -> None:
        """Async servo off operation"""
        try:
            await self.robot_service.disable_servo(self.axis_id)
            self.state.set_servo_enabled(False)
            self.servo_off_completed.emit(True, "Servo disabled")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Servo off failed: {error_type}: {e}", exc_info=True)
            self.servo_off_completed.emit(False, f"Servo off failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Motion operations
    def on_home_clicked(self) -> None:
        """Handle home button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.home_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Homing robot...")
        self.executor_thread.submit_task("robot_home", self._async_home())

    async def _async_home(self) -> None:
        """Async home operation"""
        try:
            self.state.set_homing_in_progress(True)  # Disable buttons during homing

            await self.robot_service.home_axis(self.axis_id)
            # Update position after homing
            position = await self.robot_service.get_position(self.axis_id)
            self.state.set_position(position)
            self.home_completed.emit(True, "Homing completed")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Homing failed: {error_type}: {e}", exc_info=True)
            self.home_completed.emit(False, f"Homing failed: {error_type}: {str(e)}")
        finally:
            logger.debug("_async_home finally block - restoring button states")
            self.state.set_homing_in_progress(False)  # Restore buttons after homing
            self.state.hide_progress()
            logger.debug("_async_home finally block - completed")

    def on_move_absolute(
        self,
        position: float,
        velocity: float = 1000.0,
        acceleration: float = 5000.0,
        deceleration: float = 5000.0
    ) -> None:
        """Handle absolute move request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.move_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Moving to {position:.2f} μm...")
        self.executor_thread.submit_task(
            "robot_move_abs",
            self._async_move_absolute(position, velocity, acceleration, deceleration)
        )

    async def _async_move_absolute(
        self,
        position: float,
        velocity: float,
        acceleration: float,
        deceleration: float
    ) -> None:
        """Async absolute move operation"""
        try:
            self.state.set_motion_in_progress(True)  # Disable buttons during motion

            await self.robot_service.move_absolute(
                position=position,
                axis_id=self.axis_id,
                velocity=velocity,
                acceleration=acceleration,
                deceleration=deceleration
            )
            # Update position after move
            new_position = await self.robot_service.get_position(self.axis_id)
            self.state.set_position(new_position)
            self.move_completed.emit(True, f"Moved to {position:.2f} μm")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Absolute move failed: {error_type}: {e}", exc_info=True)
            self.move_completed.emit(False, f"Move failed: {error_type}: {str(e)}")
        finally:
            self.state.set_motion_in_progress(False)  # Restore buttons after motion
            self.state.hide_progress()

    def on_move_relative(
        self,
        distance: float,
        velocity: float = 1000.0,
        acceleration: float = 5000.0,
        deceleration: float = 5000.0
    ) -> None:
        """Handle relative move request"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.move_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress(f"Moving {distance:.2f} μm...")
        self.executor_thread.submit_task(
            "robot_move_rel",
            self._async_move_relative(distance, velocity, acceleration, deceleration)
        )

    async def _async_move_relative(
        self,
        distance: float,
        velocity: float,
        acceleration: float,
        deceleration: float
    ) -> None:
        """Async relative move operation"""
        try:
            self.state.set_motion_in_progress(True)  # Disable buttons during motion

            await self.robot_service.move_relative(
                distance=distance,
                axis_id=self.axis_id,
                velocity=velocity,
                acceleration=acceleration,
                deceleration=deceleration
            )
            # Update position after move
            new_position = await self.robot_service.get_position(self.axis_id)
            self.state.set_position(new_position)
            self.move_completed.emit(True, f"Moved {distance:.2f} μm")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Relative move failed: {error_type}: {e}", exc_info=True)
            self.move_completed.emit(False, f"Move failed: {error_type}: {str(e)}")
        finally:
            self.state.set_motion_in_progress(False)  # Restore buttons after motion
            self.state.hide_progress()

    def on_get_position_clicked(self) -> None:
        """Handle get position button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            return

        self.state.show_progress("Reading position...")
        self.executor_thread.submit_task("robot_get_position", self._async_get_position())

    async def _async_get_position(self) -> None:
        """Async get position operation"""
        try:
            position = await self.robot_service.get_position(self.axis_id)
            self.state.set_position(position)
            self.position_read.emit(position)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Get position failed: {error_type}: {e}", exc_info=True)
            self.state.update_status(f"Get position failed: {error_type}: {str(e)}", "error")
        finally:
            self.state.hide_progress()

    def on_stop_clicked(self) -> None:
        """Handle stop motion button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.stop_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.state.show_progress("Stopping motion...")
        self.executor_thread.submit_task("robot_stop", self._async_stop())

    async def _async_stop(self) -> None:
        """Async stop motion operation"""
        try:
            await self.robot_service.stop_motion(self.axis_id, 5000.0)
            self.stop_completed.emit(True, "Motion stopped")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Stop motion failed: {error_type}: {e}", exc_info=True)
            self.stop_completed.emit(False, f"Stop failed: {error_type}: {str(e)}")
        finally:
            self.state.hide_progress()

    # Emergency operations
    def on_emergency_stop_clicked(self) -> None:
        """Handle emergency stop button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.emergency_stop_completed.emit(False, "System error: Executor thread not initialized")
            return

        self.executor_thread.submit_task("robot_emergency_stop", self._async_emergency_stop())

    async def _async_emergency_stop(self) -> None:
        """Async emergency stop operation with auto-connect and servo off"""
        try:
            # Auto-connect if not connected
            if not self.state.is_connected:
                logger.info("Emergency stop: Auto-connecting to robot...")
                await self.robot_service.connect()
                self.state.set_connected(True)
                logger.info("Emergency stop: Connected successfully")

            # Turn off servo if it's on
            if self.state.servo_enabled:
                logger.info("Emergency stop: Turning off servo...")
                await self.robot_service.disable_servo(self.axis_id)
                logger.info("Emergency stop: Servo disabled")

            # Execute emergency stop
            await self.robot_service.emergency_stop(self.axis_id)

            # Emergency stop: keep connected but set emergency state
            # This allows Servo ON and Home button to be enabled for recovery
            self.state.set_emergency_stopped()
            self.emergency_stop_completed.emit(True, "EMERGENCY STOP ACTIVATED - Servo ON or Home to recover")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Emergency stop failed: {error_type}: {e}", exc_info=True)
            self.emergency_stop_completed.emit(False, f"Emergency stop failed: {error_type}: {str(e)}")

    # Diagnostic operations
    def on_get_load_ratio_clicked(self, ratio_type: int = 0) -> None:
        """Handle get load ratio button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.load_ratio_read.emit(-1.0)
            return

        self.state.show_progress("Reading load ratio...")
        self.executor_thread.submit_task("robot_load_ratio", self._async_get_load_ratio(ratio_type))

    async def _async_get_load_ratio(self, ratio_type: int) -> None:
        """Async get load ratio operation"""
        try:
            load_ratio = await self.robot_service.get_load_ratio(self.axis_id, ratio_type)
            self.load_ratio_read.emit(load_ratio)
            logger.info(f"Load ratio (type {ratio_type}): {load_ratio:.2f}%")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Load ratio read failed: {error_type}: {e}", exc_info=True)
            self.load_ratio_read.emit(-1.0)  # Error indicator
        finally:
            self.state.hide_progress()

    def on_get_torque_clicked(self) -> None:
        """Handle get torque button click"""
        if not self.executor_thread:
            logger.error("TestExecutorThread not available")
            self.torque_read.emit(-1.0)
            return

        self.state.show_progress("Reading torque...")
        self.executor_thread.submit_task("robot_torque", self._async_get_torque())

    async def _async_get_torque(self) -> None:
        """Async get torque operation"""
        try:
            torque = await self.robot_service.get_torque(self.axis_id)
            self.torque_read.emit(torque)
            logger.info(f"Torque: {torque:.2f}")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Torque read failed: {error_type}: {e}", exc_info=True)
            self.torque_read.emit(-1.0)  # Error indicator
        finally:
            self.state.hide_progress()
