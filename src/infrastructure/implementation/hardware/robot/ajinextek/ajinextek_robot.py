"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

# 절대 import 사용 (권장)
# src가 Python path에 있을 때 최적의 방법
from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.enums.robot_enums import MotionStatus
from domain.exceptions.hardware_exceptions import (
    HardwareException,
)
from domain.exceptions.robot_exceptions import (
    RobotConnectionError,
    RobotMotionError,
)
from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import (
    AXLWrapper,
)
from infrastructure.implementation.hardware.robot.ajinextek.constants import (
    HOME_ERR_AMP_FAULT,
    HOME_ERR_GNT_RANGE,
    HOME_ERR_NEG_LIMIT,
    HOME_ERR_NOT_DETECT,
    HOME_ERR_POS_LIMIT,
    HOME_ERR_UNKNOWN,
    HOME_ERR_USER_BREAK,
    HOME_ERR_VELOCITY,
    HOME_SEARCHING,
    HOME_SUCCESS,
    SERVO_OFF,
    SERVO_ON,
)
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)


class AjinextekRobot(RobotService):
    """AJINEXTEK 로봇 통합 서비스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 로봇 설정 딕셔너리 (하드웨어 연결 및 모션 파라미터)
        """
        # Store configuration from dict
        self._model = config.get("model", "AJINEXTEK")
        self._irq_no = config.get("irq_no", 7)


        # Runtime state
        self._is_connected = False
        self._axis_count = 0  # Will be detected during connection
        self._current_positions: list[float] = []
        self._servo_states: dict[int, bool] = {}
        self._motion_status = MotionStatus.IDLE
        self._error_message = None

        # Software limits - initialized with default values, will be updated from .mot file
        self._software_limits_enabled = False
        self._software_limit_pos: dict[int, float] = {}
        self._software_limit_neg: dict[int, float] = {}

        # Initialize AXL wrapper
        self._axl = AXLWrapper()

        logger.info("AjinextekRobotAdapter initialized with IRQ %s", self._irq_no)

    async def connect(self) -> None:
        """
        하드웨어 연결

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info("Connecting to AJINEXTEK robot controller (IRQ: %s)", self._irq_no)

            # Open AXL library
            result = self._axl.open(self._irq_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to open AXL library: %s", error_msg)
                raise RobotConnectionError(
                    f"Failed to open AXL library: {error_msg}",
                    "AJINEXTEK",
                    details=f"IRQ: {self._irq_no}, Error: {result}",
                )

            # Get board count for verification
            try:
                board_count = self._axl.get_board_count()
                logger.info("Board count detected: %s", board_count)
            except Exception as e:
                logger.error("Failed to get board count: %s", e)
                raise RobotConnectionError(
                    f"Failed to get board count: {e}",
                    "AJINEXTEK",
                    details=str(e),
                ) from e

            # Get axis count from hardware
            try:
                self._axis_count = self._axl.get_axis_count()
                logger.info("Detected axis count: %s", self._axis_count)
            except Exception as e:
                logger.error("Failed to get axis count: %s", e)
                raise RobotConnectionError(
                    f"Failed to get axis count: {e}",
                    "AJINEXTEK",
                    details=str(e),
                ) from e

            # Get library version for info
            try:
                version = self._axl.get_lib_version()
                logger.info("AXL Library version: %s", version)
            except Exception:
                pass  # Library version is not critical

            # Initialize position tracking and servo states
            self._current_positions = [0.0] * self._axis_count
            for axis in range(self._axis_count):
                self._servo_states[axis] = False

            # Initialize software limits with default values from .mot file
            # These will be populated when software limits are read from controller
            for axis in range(self._axis_count):
                self._software_limit_pos[axis] = 1000.0  # Default positive limit
                self._software_limit_neg[axis] = -1000.0  # Default negative limit

            # Software limits are now managed by robot controller via .mot file

            # Load robot parameters from configuration file
            await self._load_robot_parameters()

            # Motion parameters are now loaded from .prm file via AxmMotLoadParaAll
            logger.info("Motion parameters initialized from .prm file")

            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            logger.info(
                f"AJINEXTEK robot controller connected successfully (IRQ: {self._irq_no}, Axes: {self._axis_count})"
            )

        except Exception as e:
            self._is_connected = False
            if isinstance(e, RobotConnectionError):
                # Re-raise RobotConnectionError as-is to preserve error context
                raise
            else:
                logger.error("Failed to connect to AJINEXTEK robot: %s", e)
                raise RobotConnectionError(
                    f"Robot controller initialization failed: {e}",
                    "AJINEXTEK",
                    details=str(e),
                ) from e

    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제

        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._is_connected:
                # Stop all motion and turn off servos
                for axis in range(self._axis_count):
                    try:
                        await self.stop_motion(axis, 1000.0)  # Default deceleration
                    except Exception as e:
                        logger.warning("Failed to stop axis %s during disconnect: %s", axis, e)

                # Turn off all servos
                for axis in range(self._axis_count):
                    try:
                        self._set_servo_off(axis)
                    except Exception as e:
                        logger.warning("Failed to turn off servo %s: %s", axis, e)

                # Close AXL library connection
                try:
                    result = self._axl.close()
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        logger.warning("AXL library close warning: %s", error_msg)
                except Exception as e:
                    logger.warning("Error closing AXL library: %s", e)

                self._is_connected = False
                self._servo_states = {}
                self._motion_status = MotionStatus.IDLE

                logger.info("AJINEXTEK robot controller disconnected")

        except Exception as e:
            logger.error("Error disconnecting AJINEXTEK robot: %s", e)
            raise HardwareException(
                "ajinextek_robot",
                "disconnect",
                {"error": f"Error disconnecting AJINEXTEK robot: {e}"},
            ) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def home_axis(self, axis: int) -> None:
        """
        Home specified axis using parameters from robot_params.mot file

        All homing parameters (ORIGINMODE, ORIGINDIR, ORIGINLEVEL, ORIGINOFFSET, 
        ORIGINVEL1, ORIGINVEL2) are already configured in the robot controller 
        via AxmMotLoadParaAll from the .mot parameter file.

        Args:
            axis: Axis number (0-based)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            logger.info("Starting homing for axis %s using .mot file parameters", axis)
            self._motion_status = MotionStatus.HOMING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Start homing using parameters already loaded from .mot file
            # The _home_axis method now handles all status monitoring internally
            await self._home_axis(axis)

            # Update position to zero after successful homing
            if axis < len(self._current_positions):
                self._current_positions[axis] = 0.0

            self._motion_status = MotionStatus.IDLE
            logger.info("Axis %s homing completed successfully", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Homing failed on axis %s: %s", axis, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Homing failed on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def home_all_axes(
        self,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> bool:
        """
        모든 축 홈 위치로 이동

        Returns:
            홈 이동 성공 여부

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        try:
            logger.info("Starting homing sequence for all axes")
            self._motion_status = MotionStatus.HOMING

            failed_axes = []

            # Home each axis sequentially using the new single-axis method
            for axis in range(self._axis_count):
                try:
                    await self.home_axis(
                        axis,
                        velocity,
                        acceleration,
                        deceleration,
                    )
                    logger.info("Axis %s homing completed", axis)

                except Exception as e:
                    failed_axes.append((axis, str(e)))
                    logger.error("Failed to home axis %s: %s", axis, e)

            if failed_axes:
                error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
                self._motion_status = MotionStatus.ERROR
                raise RobotMotionError(
                    f"Failed to home {len(failed_axes)} axes: {error_details}",
                    "AJINEXTEK",
                )

            self._motion_status = MotionStatus.IDLE
            logger.info("All axes homing sequence completed successfully")
            return True

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Homing failed: %s", e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Homing failed: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_absolute(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """
        지정된 축을 절대 위치로 이동

        Args:
            axis: 축 번호 (0부터 시작)
            position: 절대 위치 (mm)
            velocity: 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)

        Returns:
            이동 성공 여부

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If movement fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        # Use provided parameters or fall back to reasonable defaults from .prm file
        vel = velocity if velocity is not None else 100.0   # MAXVEL from .prm
        accel = acceleration if acceleration is not None else 1000.0  # ACCEL from .prm  
        decel = deceleration if deceleration is not None else 1000.0  # DECEL from .prm

        try:
            logger.info("Moving axis %s to absolute position: %smm at %smm/s", axis, position, vel)

            # Safety check before motion
            current_pos = await self.get_current_position(axis)
            direction = "positive" if position > current_pos else "negative"
            if not await self.is_axis_safe_to_move(axis, direction):
                raise RobotMotionError(
                    f"Axis {axis} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            # Check software limits
            if self._software_limits_enabled:
                if (
                    position > self._software_limit_pos[axis]
                    or position < self._software_limit_neg[axis]
                ):
                    raise RobotMotionError(
                        f"Target position {position}mm exceeds software limits "
                        f"[{self._software_limit_neg[axis]}, {self._software_limit_pos[axis]}] for axis {axis}",
                        "AJINEXTEK",
                    )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Start absolute position move
            result = self._axl.move_start_pos(axis, position, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error("Failed to start movement on axis %s: %s", axis, error_msg)
                raise RobotMotionError(
                    f"Failed to start movement on axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            # Wait for motion to complete
            await self._wait_for_motion_complete(axis, timeout=30.0)

            # Update current position for this axis
            if axis < len(self._current_positions):
                self._current_positions[axis] = position

            self._motion_status = MotionStatus.IDLE
            logger.info("Axis %s absolute move completed successfully", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Absolute move failed on axis %s: %s", axis, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Absolute move failed on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_to_position(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
    ) -> None:
        """
        Move axis to absolute position (interface implementation)

        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        vel = velocity if velocity is not None else 100.0  # Default velocity from .prm

        # Call the more comprehensive move_absolute method with defaults
        await self.move_absolute(axis, position, vel, 1000.0, 1000.0)  # ACCEL/DECEL from .prm

    async def move_relative(
        self,
        axis: int,
        distance: float,
        velocity: Optional[float] = None,
    ) -> None:
        """
        Move axis by relative distance (interface implementation)

        Args:
            axis: Axis number to move
            distance: Distance to move in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        # Get current position for this axis
        current_position = await self.get_current_position(axis)
        target_position = current_position + distance

        # Use move_to_position to reach target
        await self.move_to_position(axis, target_position, velocity)

    async def get_current_position(self, axis: int) -> float:
        """
        지정된 축의 현재 위치 조회

        Args:
            axis: 축 번호 (0부터 시작)

        Returns:
            현재 위치 (mm)

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            position = self._axl.get_act_pos(axis)

            # Update cached position
            if axis < len(self._current_positions):
                self._current_positions[axis] = position

            return position

        except Exception as e:
            logger.warning("Failed to get position for axis %s: %s", axis, e)
            # Use cached position as fallback
            if axis < len(self._current_positions):
                return self._current_positions[axis]
            return 0.0

    async def get_all_positions(self) -> List[float]:
        """
        모든 축의 현재 위치 조회

        Returns:
            각 축의 현재 위치 (mm)

        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        try:
            positions = []
            for axis in range(self._axis_count):
                position = await self.get_current_position(axis)
                positions.append(position)

            return positions

        except Exception as e:
            logger.error("Failed to get all current positions: %s", e)
            # Return cached positions as fallback
            return self._current_positions.copy()

    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회

        Returns:
            현재 모션 상태
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        return self._motion_status

    async def stop_motion(self, axis: int, deceleration: float) -> None:
        """
        지정된 축의 모션 정지

        Args:
            axis: 정지할 축 번호 (0부터 시작)
            deceleration: 감속도 (mm/s²)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If stop operation fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            logger.info("Stopping motion on axis %s with deceleration %s mm/s²", axis, deceleration)

            result = self._axl.move_stop(axis, deceleration)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to stop axis %s: %s", axis, error_msg)
                raise RobotMotionError(
                    f"Failed to stop axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            # Update motion status - only set to IDLE if all axes are stopped
            # For now, we'll assume this axis is stopped
            logger.info("Axis %s motion stopped successfully", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Unexpected error stopping axis %s: %s", axis, e)
            raise RobotMotionError(
                f"Unexpected error stopping axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def emergency_stop(self) -> None:
        """
        Emergency stop all motion immediately

        Raises:
            HardwareException: If emergency stop fails
        """

        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        try:
            logger.warning("EMERGENCY STOP activated - stopping all axes immediately")

            # Stop all axes with immediate deceleration
            failed_axes = []
            for axis in range(self._axis_count):
                try:
                    # Use immediate stop (high deceleration)
                    result = self._axl.move_stop(
                        axis, 10000.0  # High deceleration for emergency stop
                    )  # 10x normal deceleration
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        failed_axes.append((axis, error_msg))
                        logger.error("Failed to emergency stop axis %d: %s", axis, error_msg)
                    else:
                        logger.debug("Emergency stop sent to axis %d", axis)
                except Exception as e:
                    failed_axes.append((axis, str(e)))
                    logger.error("Exception during emergency stop for axis %d: %s", axis, e)

            # Turn off all servos for additional safety
            for axis in range(self._axis_count):
                try:
                    self._set_servo_off(axis)
                except Exception as e:
                    logger.warning("Failed to turn off servo %d during emergency stop: %s", axis, e)

            self._motion_status = MotionStatus.EMERGENCY_STOP
            self._servo_states = {axis: False for axis in range(self._axis_count)}

            # Report any failures
            if failed_axes:
                failed_list = ", ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
                logger.error("Emergency stop completed with failures: %s", failed_list)
            else:
                logger.warning("Emergency stop completed successfully for all axes")

        except Exception as e:
            logger.error("Emergency stop failed: %s", e)
            raise HardwareException(
                "ajinextek_robot",
                "emergency_stop",
                {"error": f"Emergency stop failed: {e}"},
            ) from e


    async def get_position(self, axis: int) -> float:
        """
        Get current position of axis

        Args:
            axis: Axis number

        Returns:
            Current position in mm
        """
        return await self.get_current_position(axis)

    async def is_moving(self, axis: Optional[int] = None) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check (None checks if any axis is moving)

        Returns:
            True if moving, False otherwise
        """
        if axis is not None:
            # Check specific axis
            return self._motion_status == MotionStatus.MOVING
        # Check if any axis is moving
        return self._motion_status in [
            MotionStatus.MOVING,
            MotionStatus.HOMING,
        ]

    async def set_velocity(self, axis: int, velocity: float) -> None:
        """
        Set default velocity for axis

        Args:
            axis: Axis number
            velocity: Velocity in mm/s

        Raises:
            HardwareException: If velocity setting fails
        """

        if velocity <= 0:
            raise HardwareException(
                "ajinextek_robot",
                "set_velocity",
                {"error": f"Velocity must be positive, got {velocity}"},
            )

        # Set velocity using AXL library function
        result = self._axl.set_max_vel(axis, velocity)
        if result != AXT_RT_SUCCESS:
            error_msg = get_error_message(result)
            raise RobotMotionError(
                f"Failed to set velocity for axis {axis}: {error_msg}",
                "AJINEXTEK",
            )
        logger.info("Set velocity to %s mm/s for axis %s", velocity, axis)

    async def get_velocity(self, axis: int) -> float:
        """
        Get current velocity setting for axis

        Args:
            axis: Axis number

        Returns:
            Current velocity in mm/s
        """
        try:
            return self._axl.get_max_vel(axis)
        except Exception as e:
            logger.warning("Failed to get velocity for axis %s: %s", axis, e)
            return 100.0  # Default fallback

    async def move_velocity(
        self,
        axis: int,
        velocity: float,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """
        Start continuous velocity (jog) motion

        Args:
            axis: Axis number to move
            velocity: Target velocity in mm/s (positive or negative for direction)
            acceleration: Acceleration in mm/s² (optional, uses default if None)
            deceleration: Deceleration in mm/s² (optional, uses default if None)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If velocity motion fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        # Use provided parameters or fall back to defaults from .prm file
        accel = acceleration if acceleration is not None else 1000.0  # ACCEL from .prm
        decel = deceleration if deceleration is not None else 1000.0  # DECEL from .prm

        try:
            logger.info("Starting velocity motion on axis %s: %smm/s", axis, velocity)

            # Safety check before motion
            direction = "positive" if velocity > 0 else "negative"
            if not await self.is_axis_safe_to_move(axis, direction):
                raise RobotMotionError(
                    f"Axis {axis} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Start velocity motion
            result = self._axl.move_start_vel(axis, velocity, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error("Failed to start velocity motion on axis %s: %s", axis, error_msg)
                raise RobotMotionError(
                    f"Failed to start velocity motion on axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Velocity motion started successfully on axis %s", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Velocity motion failed on axis %s: %s", axis, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Velocity motion failed on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_signal_search(
        self,
        axis: int,
        velocity: float,
        search_distance: float,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """
        Start signal search motion (move until signal is detected)

        Args:
            axis: Axis number to move
            velocity: Search velocity in mm/s (positive or negative for direction)
            search_distance: Maximum search distance in mm
            acceleration: Acceleration in mm/s² (optional, uses default if None)
            deceleration: Deceleration in mm/s² (optional, uses default if None)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If signal search motion fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        # Use provided parameters or fall back to defaults from .prm file
        accel = acceleration if acceleration is not None else 1000.0  # ACCEL from .prm
        decel = deceleration if deceleration is not None else 1000.0  # DECEL from .prm

        try:
            logger.info(
                "Starting signal search on axis %s: velocity=%smm/s, distance=%smm",
                axis,
                velocity,
                search_distance,
            )

            # Safety check before motion
            direction = "positive" if velocity > 0 else "negative"
            if not await self.is_axis_safe_to_move(axis, direction):
                raise RobotMotionError(
                    f"Axis {axis} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            # Check if search distance exceeds software limits
            if self._software_limits_enabled:
                current_pos = await self.get_current_position(axis)
                target_pos = (
                    current_pos + search_distance
                    if velocity > 0
                    else current_pos - abs(search_distance)
                )

                if (
                    target_pos > self._software_limit_pos[axis]
                    or target_pos < self._software_limit_neg[axis]
                ):
                    raise RobotMotionError(
                        f"Signal search distance {search_distance}mm would exceed software limits "
                        f"[{self._software_limit_neg[axis]}, {self._software_limit_pos[axis]}] for axis {axis}",
                        "AJINEXTEK",
                    )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Start signal search motion
            result = self._axl.move_signal_search(axis, velocity, accel, decel, search_distance)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error("Failed to start signal search on axis %s: %s", axis, error_msg)
                raise RobotMotionError(
                    f"Failed to start signal search on axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Signal search motion started successfully on axis %s", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Signal search motion failed on axis %s: %s", axis, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Signal search motion failed on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def stop_velocity_motion(self, axis: int, deceleration: Optional[float] = None) -> None:
        """
        Stop velocity (jog) motion with specified deceleration

        Args:
            axis: Axis number to stop
            deceleration: Deceleration in mm/s² (optional, uses default if None)

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If stop operation fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        # Use provided deceleration or fall back to default from .prm file
        decel = deceleration if deceleration is not None else 1000.0  # DECEL from .prm

        try:
            logger.info(
                "Stopping velocity motion on axis %s with deceleration %s mm/s²", axis, decel
            )

            result = self._axl.move_stop(axis, decel)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to stop velocity motion on axis %s: %s", axis, error_msg)
                raise RobotMotionError(
                    f"Failed to stop velocity motion on axis {axis}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Velocity motion stopped successfully on axis %s", axis)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Unexpected error stopping velocity motion on axis %s: %s", axis, e)
            raise RobotMotionError(
                f"Unexpected error stopping velocity motion on axis {axis}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def wait_for_completion(
        self,
        axis: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Wait for motion to complete

        Args:
            axis: Axis to wait for (None waits for all axes)
            timeout: Maximum wait time in seconds

        Raises:
            HardwareException: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
        """

        if axis is not None:
            try:
                await self._wait_for_motion_complete(axis, timeout or 30.0)
            except Exception as e:
                raise HardwareException(
                    "ajinextek_robot",
                    "wait_for_completion",
                    {"error": f"Failed to wait for axis {axis}: {e}"},
                ) from e
        else:
            # Wait for all axes to complete
            try:
                for ax in range(self._axis_count):
                    await self._wait_for_motion_complete(ax, timeout or 30.0)
            except Exception as e:
                raise HardwareException(
                    "ajinextek_robot",
                    "wait_for_completion",
                    {"error": f"Failed to wait for all axes: {e}"},
                ) from e

    async def get_axis_count(self) -> int:
        """
        축 개수 조회

        Returns:
            축 개수
        """
        return self._axis_count

    async def get_primary_axis_id(self) -> int:
        """
        Get the primary axis ID that should be controlled

        Returns:
            Primary axis ID (defaults to 0 for first axis)
        """
        return 0  # Default to first axis

    async def check_servo_alarm(self, axis: int) -> bool:
        """
        Check servo alarm status for specified axis

        Args:
            axis: Axis number to check

        Returns:
            True if alarm is active, False otherwise

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            return self._axl.read_servo_alarm(axis)
        except Exception as e:
            logger.warning("Failed to read servo alarm for axis %s: %s", axis, e)
            return False  # Default to no alarm if read fails

    async def check_limit_sensors(self, axis: int) -> Dict[str, bool]:
        """
        Check limit sensor status for specified axis

        Args:
            axis: Axis number to check

        Returns:
            Dictionary with 'positive_limit' and 'negative_limit' status

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            pos_limit, neg_limit = self._axl.read_limit_status(axis)
            return {
                "positive_limit": pos_limit,
                "negative_limit": neg_limit,
            }
        except Exception as e:
            logger.warning("Failed to read limit sensors for axis %s: %s", axis, e)
            return {"positive_limit": False, "negative_limit": False}

    async def check_all_servo_alarms(self) -> Dict[int, bool]:
        """
        Check servo alarm status for all axes

        Returns:
            Dictionary mapping axis number to alarm status

        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        alarm_status = {}
        for axis in range(self._axis_count):
            try:
                alarm_status[axis] = await self.check_servo_alarm(axis)
            except Exception as e:
                logger.warning("Failed to check servo alarm for axis %s: %s", axis, e)
                alarm_status[axis] = False

        return alarm_status

    async def check_all_limit_sensors(self) -> Dict[int, Dict[str, bool]]:
        """
        Check limit sensor status for all axes

        Returns:
            Dictionary mapping axis number to limit sensor status

        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        limit_status = {}
        for axis in range(self._axis_count):
            try:
                limit_status[axis] = await self.check_limit_sensors(axis)
            except Exception as e:
                logger.warning("Failed to check limit sensors for axis %s: %s", axis, e)
                limit_status[axis] = {"positive_limit": False, "negative_limit": False}

        return limit_status

    async def is_axis_safe_to_move(self, axis: int, direction: str = "both") -> bool:
        """
        Check if axis is safe to move in specified direction

        Args:
            axis: Axis number to check
            direction: Movement direction ("positive", "negative", or "both")

        Returns:
            True if safe to move, False otherwise

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number or direction is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        if direction not in ["positive", "negative", "both"]:
            raise ValueError(
                f"Invalid direction: {direction}. Must be 'positive', 'negative', or 'both'"
            )

        # Check servo alarm
        if await self.check_servo_alarm(axis):
            logger.warning("Axis %s has servo alarm - not safe to move", axis)
            return False

        # Check limit sensors
        limit_status = await self.check_limit_sensors(axis)

        if direction == "positive" and limit_status["positive_limit"]:
            logger.warning("Axis %s positive limit is active - not safe to move positive", axis)
            return False
        elif direction == "negative" and limit_status["negative_limit"]:
            logger.warning("Axis %s negative limit is active - not safe to move negative", axis)
            return False
        elif direction == "both" and (
            limit_status["positive_limit"] or limit_status["negative_limit"]
        ):
            logger.warning("Axis %s has active limit sensor - not safe to move", axis)
            return False

        # Check software limits if enabled
        if self._software_limits_enabled:
            current_pos = await self.get_current_position(axis)
            if direction in ["positive", "both"] and current_pos >= self._software_limit_pos[axis]:
                logger.warning(
                    "Axis %s at positive software limit - not safe to move positive", axis
                )
                return False
            if direction in ["negative", "both"] and current_pos <= self._software_limit_neg[axis]:
                logger.warning(
                    "Axis %s at negative software limit - not safe to move negative", axis
                )
                return False

        return True

    async def set_software_limits(self, axis: int, pos_limit: float, neg_limit: float) -> None:
        """
        Set software limits for specified axis

        Args:
            axis: Axis number
            pos_limit: Positive direction limit in mm
            neg_limit: Negative direction limit in mm

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or limits are invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        if neg_limit >= pos_limit:
            raise ValueError(
                f"Negative limit ({neg_limit}) must be less than positive limit ({pos_limit})"
            )

        self._software_limit_pos[axis] = pos_limit
        self._software_limit_neg[axis] = neg_limit
        logger.info("Software limits set for axis %d: [%.3f, %.3f]", axis, neg_limit, pos_limit)

    async def enable_software_limits(self, enable: bool = True) -> None:
        """
        Enable or disable software limits for all axes

        Args:
            enable: True to enable, False to disable
        """
        self._software_limits_enabled = enable
        logger.info("Software limits %s", "enabled" if enable else "disabled")

    async def get_software_limits(self, axis: int) -> tuple[float, float]:
        """
        Get software limits for specified axis

        Args:
            axis: Axis number

        Returns:
            Tuple of (negative_limit, positive_limit)

        Raises:
            ValueError: If axis number is invalid
        """
        self._check_axis(axis)
        return (self._software_limit_neg[axis], self._software_limit_pos[axis])

    async def reset_servo_alarm(self, axis: int) -> bool:
        """
        Reset servo alarm for specified axis

        Args:
            axis: Axis number

        Returns:
            True if alarm was reset successfully

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            # Turn servo off and on again to reset alarm
            self._set_servo_off(axis)
            await asyncio.sleep(0.1)  # Small delay
            self._set_servo_on(axis)

            # Check if alarm is cleared
            await asyncio.sleep(0.1)  # Small delay
            alarm_cleared = not await self.check_servo_alarm(axis)

            if alarm_cleared:
                logger.info("Servo alarm reset successfully for axis %d", axis)
            else:
                logger.warning("Servo alarm still active after reset for axis %d", axis)

            return alarm_cleared

        except Exception as e:
            logger.error("Failed to reset servo alarm for axis %d: %s", axis, e)
            return False

    async def get_detailed_axis_status(self, axis: int) -> Dict[str, Any]:
        """
        Get detailed status for a specific axis

        Args:
            axis: Axis number

        Returns:
            Detailed status dictionary for the axis

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        status = {
            "axis": axis,
            "connected": True,
            "servo_on": self._servo_states.get(axis, False),
            "current_position": 0.0,
            "servo_alarm": False,
            "limit_sensors": {"positive_limit": False, "negative_limit": False},
            "safe_to_move": {"positive": False, "negative": False, "both": False},
            "coordinate_mode": "absolute",  # Set by .prm file
            "software_limits": {
                "enabled": False,  # Set by .prm file
                "positive": 1000.0,  # Default from .prm
                "negative": -1000.0,  # Default from .prm
            },
            "motion_parameters": {
                "velocity": 100.0,   # MAXVEL from .prm file
                "acceleration": 1000.0,  # ACCEL from .prm file  
                "deceleration": 1000.0,  # DECEL from .prm file
                "unit_per_pulse": 1.0,  # UNITPERPULSE from .prm file
            },
        }

        # Get real-time data
        try:
            status["current_position"] = await self.get_current_position(axis)
            status["servo_alarm"] = await self.check_servo_alarm(axis)
            status["limit_sensors"] = await self.check_limit_sensors(axis)
            status["safe_to_move"] = {
                "positive": await self.is_axis_safe_to_move(axis, "positive"),
                "negative": await self.is_axis_safe_to_move(axis, "negative"),
                "both": await self.is_axis_safe_to_move(axis, "both"),
            }
        except Exception as e:
            status["error"] = str(e)

        return status

    async def run_diagnostic(self) -> Dict[str, Any]:
        """
        Run comprehensive diagnostic check

        Returns:
            Diagnostic results dictionary

        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        diagnostic = {
            "timestamp": time.time(),
            "overall_status": "OK",
            "connection": {"status": "OK", "library_version": None, "board_count": 0},
            "axes": {},
            "servo_alarms": {},
            "limit_sensors": {},
            "motion_status": self._motion_status.value,
            "warnings": [],
            "errors": [],
        }

        try:
            # Test library connection
            try:
                diagnostic["connection"]["library_version"] = self._axl.get_lib_version()
                diagnostic["connection"]["board_count"] = self._axl.get_board_count()
            except Exception as e:
                diagnostic["connection"]["status"] = "ERROR"
                diagnostic["errors"].append(f"Library connection error: {e}")

            # Check each axis
            for axis in range(self._axis_count):
                try:
                    axis_status = await self.get_detailed_axis_status(axis)
                    diagnostic["axes"][axis] = axis_status

                    # Check for warnings/errors
                    if axis_status.get("servo_alarm", False):
                        diagnostic["errors"].append(f"Axis {axis}: Servo alarm active")
                        diagnostic["overall_status"] = "ERROR"

                    if axis_status.get("limit_sensors", {}).get("positive_limit", False):
                        diagnostic["warnings"].append(f"Axis {axis}: Positive limit sensor active")

                    if axis_status.get("limit_sensors", {}).get("negative_limit", False):
                        diagnostic["warnings"].append(f"Axis {axis}: Negative limit sensor active")

                    if not axis_status.get("servo_on", False):
                        diagnostic["warnings"].append(f"Axis {axis}: Servo is OFF")

                except Exception as e:
                    diagnostic["errors"].append(f"Axis {axis}: Diagnostic failed - {e}")
                    diagnostic["overall_status"] = "ERROR"

            # Overall status determination
            if diagnostic["errors"]:
                diagnostic["overall_status"] = "ERROR"
            elif diagnostic["warnings"]:
                diagnostic["overall_status"] = "WARNING"

            logger.info("Diagnostic completed: %s", diagnostic["overall_status"])

        except Exception as e:
            diagnostic["overall_status"] = "ERROR"
            diagnostic["errors"].append(f"Diagnostic failed: {e}")
            logger.error("Diagnostic check failed: %s", e)

        return diagnostic

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "irq_no": self._irq_no,
            "axis_count": self._axis_count,
            "motion_status": self._motion_status.value,
            "servo_states": self._servo_states.copy(),
            "default_velocity": 100.0,   # MAXVEL from .prm file
            "default_acceleration": 1000.0,  # ACCEL from .prm file
            "hardware_type": "AJINEXTEK",
            "motion_parameters": {
                "unit_per_pulse": 1.0,      # UNITPERPULSE from .prm
                "pulse_per_unit": 1000,     # PULSEPERMM from .prm
                "pulse_output_method": 0,   # PULSEOUTMETHOD from .prm
                "coordinate_mode": 0,       # Absolute mode from .prm
                "limit_sensor_level": 1,    # LIMITPOSITIVE from .prm
                "software_limits_enabled": False,  # SOFTLIMITUSE from .prm
            },
        }

        if await self.is_connected():
            try:
                status["current_positions"] = await self.get_all_positions()
                status["servo_alarms"] = await self.check_all_servo_alarms()
                status["limit_sensors"] = await self.check_all_limit_sensors()

                # Add safety status for each axis
                safety_status = {}
                for axis in range(self._axis_count):
                    safety_status[axis] = await self.is_axis_safe_to_move(axis)
                status["safety_status"] = safety_status

                status["last_error"] = None
            except Exception as e:
                status["current_positions"] = None
                status["servo_alarms"] = None
                status["limit_sensors"] = None
                status["safety_status"] = None
                status["last_error"] = str(e)

        return status

    # === Helper Methods ===

    def _check_axis(self, axis_no: int) -> None:
        """Check if axis number is valid"""
        if not self._is_connected:
            raise RobotConnectionError(
                "Robot controller not connected",
                "AJINEXTEK",
            )

        if axis_no < 0 or axis_no >= self._axis_count:
            raise RobotMotionError(
                f"Invalid axis number: {axis_no} (valid: 0-{self._axis_count-1})",
                "AJINEXTEK",
            )

    def _set_servo_on(self, axis_no: int) -> None:
        """Turn servo on for specified axis"""
        self._check_axis(axis_no)

        try:
            result = self._axl.servo_on(axis_no, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = True
                logger.debug("Servo %s turned ON", axis_no)
            else:
                error_msg = get_error_message(result)
                logger.error("Failed to turn on servo %s: %s", axis_no, error_msg)
                raise RobotMotionError(
                    f"Failed to turn on servo {axis_no}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to turn on servo %s: %s", axis_no, e)
            raise RobotMotionError(
                f"Failed to turn on servo {axis_no}: {e}",
                "AJINEXTEK",
            ) from e

    def _set_servo_off(self, axis_no: int) -> None:
        """Turn servo off for specified axis"""
        self._check_axis(axis_no)

        try:
            result = self._axl.servo_on(axis_no, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = False
                logger.debug("Servo %s turned OFF", axis_no)
            else:
                error_msg = get_error_message(result)
                logger.error("Failed to turn off servo %s: %s", axis_no, error_msg)
                raise RobotMotionError(
                    f"Failed to turn off servo {axis_no}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to turn off servo %s: %s", axis_no, e)
            raise RobotMotionError(
                f"Failed to turn off servo {axis_no}: {e}",
                "AJINEXTEK",
            ) from e

    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis

        This method enables servo motor for the specified axis only.
        Should be called before attempting motion operations on the axis.

        Args:
            axis: Axis number to enable servo for

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo enable operation fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            logger.info("Enabling servo for axis %s", axis)

            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)
                logger.debug("Servo enabled for axis %s", axis)
            else:
                logger.debug("Servo already enabled for axis %s", axis)

        except Exception as e:
            logger.error("Failed to enable servo for axis %s: %s", axis, e)
            raise RobotMotionError(
                f"Failed to enable servo for axis {axis}: {e}",
                "AJINEXTEK",
            ) from e

    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis

        This method disables servo motor for the specified axis.
        Should be called during shutdown or emergency situations.

        Args:
            axis: Axis number to disable servo for

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo disable operation fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        self._check_axis(axis)

        try:
            logger.info("Disabling servo for axis %s", axis)

            if self._servo_states.get(axis, False):
                self._set_servo_off(axis)
                logger.debug("Servo disabled for axis %s", axis)
            else:
                logger.debug("Servo already disabled for axis %s", axis)

        except Exception as e:
            logger.error("Failed to disable servo for axis %s: %s", axis, e)
            # Don't raise exception for disable failures during shutdown
            logger.warning("Servo disable failed for axis %s, continuing...", axis)

    async def _home_axis(self, axis_no: int) -> None:
        """
        Perform homing for specified axis using parameters from robot_params.mot file

        All homing parameters (ORIGINMODE, ORIGINDIR, ORIGINLEVEL, ORIGINOFFSET, 
        ORIGINVEL1, ORIGINVEL2) are already configured in the robot controller 
        via AxmMotLoadParaAll. This function follows the AJINEXTEK documentation
        pattern for proper homing with status monitoring.

        Args:
            axis_no: Axis number

        Raises:
            RobotMotionError: If homing fails
        """
        self._check_axis(axis_no)

        if not self._servo_states.get(axis_no, False):
            raise RobotMotionError(
                f"Servo {axis_no} is not ON - cannot perform homing",
                "AJINEXTEK",
            )

        try:
            # Start homing using parameters already loaded from .mot file
            result = self._axl.home_set_start(axis_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to start homing for axis %s: %s", axis_no, error_msg)
                raise RobotMotionError(
                    f"Failed to start homing for axis {axis_no}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.debug("Started homing for axis %s using .mot file parameters", axis_no)

            # Monitor homing status using AJINEXTEK standard pattern
            while True:
                try:
                    home_result = self._axl.home_get_result(axis_no)
                    
                    if home_result == HOME_SUCCESS:
                        logger.info("Homing completed successfully for axis %s", axis_no)
                        return
                    
                    elif home_result == HOME_SEARCHING:
                        # Get progress information for logging
                        try:
                            main_step, step = self._axl.home_get_rate(axis_no)
                            logger.debug("Homing axis %s: %d%% complete", axis_no, step)
                        except Exception:
                            pass  # Progress info is optional
                        
                        # Continue monitoring
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Handle homing errors
                    error_messages = {
                        HOME_ERR_UNKNOWN: "Unknown axis number",
                        HOME_ERR_GNT_RANGE: "Gantry offset out of range", 
                        HOME_ERR_USER_BREAK: "User stopped homing",
                        HOME_ERR_VELOCITY: "Invalid velocity setting",
                        HOME_ERR_AMP_FAULT: "Servo amplifier alarm",
                        HOME_ERR_NEG_LIMIT: "Negative limit sensor detected",
                        HOME_ERR_POS_LIMIT: "Positive limit sensor detected", 
                        HOME_ERR_NOT_DETECT: "Home sensor not detected",
                    }
                    
                    error_msg = error_messages.get(home_result, f"Unknown homing error: 0x{home_result:02X}")
                    logger.error("Homing failed for axis %s: %s (0x%02X)", axis_no, error_msg, home_result)
                    raise RobotMotionError(
                        f"Homing failed for axis {axis_no}: {error_msg}",
                        "AJINEXTEK",
                    )
                    
                except Exception as status_error:
                    if isinstance(status_error, RobotMotionError):
                        raise
                    logger.error("Failed to check homing status for axis %s: %s", axis_no, status_error)
                    raise RobotMotionError(
                        f"Failed to check homing status for axis {axis_no}: {status_error}",
                        "AJINEXTEK",
                    ) from status_error

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to home axis %s: %s", axis_no, e)
            raise RobotMotionError(
                f"Failed to home axis {axis_no}: {e}",
                "AJINEXTEK",
            ) from e

    async def _wait_for_motion_complete(self, axis_no: int, timeout: float = 30.0) -> None:
        """
        Wait for axis to stop moving

        Args:
            axis_no: Axis number
            timeout: Maximum wait time in seconds

        Raises:
            RobotMotionError: If axis doesn't stop within timeout or status check fails
        """
        self._check_axis(axis_no)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                is_moving = self._axl.read_in_motion(axis_no)
                if not is_moving:
                    logger.debug("Axis %s stopped successfully", axis_no)
                    return
            except Exception as e:
                logger.error("Failed to check motion status for axis %s: %s", axis_no, e)
                raise RobotMotionError(
                    f"Failed to check motion status for axis {axis_no}: {e}",
                    "AJINEXTEK",
                ) from e

            await asyncio.sleep(0.01)  # Check every 10ms

        logger.warning("Timeout waiting for axis %s to stop", axis_no)
        raise RobotMotionError(
            f"Timeout waiting for axis {axis_no} to stop after {timeout} seconds",
            "AJINEXTEK",
        )

    async def _wait_for_homing_complete(self, axis_no: int, timeout: float = 30.0) -> None:
        """
        Wait for axis homing to complete

        Args:
            axis_no: Axis number
            timeout: Maximum wait time in seconds

        Raises:
            RobotMotionError: If homing doesn't complete within timeout
        """
        # For now, use motion complete check as homing indicator
        # In a real implementation, you might have specific homing status checks
        await self._wait_for_motion_complete(axis_no, timeout)

    async def _load_robot_parameters(self) -> None:
        """
        Load robot parameters from AJINEXTEK standard parameter file using AxmMotLoadParaAll

        Raises:
            RobotConnectionError: If parameter loading fails
        """
        try:
            robot_params_file = Path("configuration/robot_params.mot")
            
            if not robot_params_file.exists():
                logger.error("Robot parameter file not found: %s", robot_params_file)
                raise RobotConnectionError(
                    f"Required robot parameter file not found: {robot_params_file}",
                    "AJINEXTEK",
                    details=f"Parameter file path: {robot_params_file}",
                )

            logger.info("Loading robot parameters from %s using AxmMotLoadParaAll", robot_params_file)
            
            # Load all parameters using AJINEXTEK standard function
            result = self._axl.load_para_all(str(robot_params_file))
            
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to load parameters from %s: %s", robot_params_file, error_msg)
                raise RobotConnectionError(
                    f"AxmMotLoadParaAll failed: {error_msg}",
                    "AJINEXTEK",
                    details=f"File: {robot_params_file}, Error: {result}",
                )
            
            logger.info("Robot parameters loaded successfully from %s", robot_params_file)

        except RobotConnectionError:
            # Re-raise connection errors to preserve error context
            raise
        except Exception as e:
            logger.error("Failed to load robot parameters: %s", e)
            raise RobotConnectionError(
                f"Robot parameters loading failed: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e


