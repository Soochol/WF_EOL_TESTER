"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, Optional

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

    def __init__(self):
        """
        초기화
        """
        # Library information
        self.version: str = "Unknown"

        # Runtime state
        self._is_connected = False
        self._axis_count = 0  # Will be detected during connection
        self._current_position: float = 0.0
        self._servo_state: bool = False
        self._motion_status = MotionStatus.IDLE
        self._error_message = None

        # Connection parameters - will be set during connect
        self.axis_id: int = 0
        self._irq_no: int = 7

        # Software limits - initialized with default values, will be updated from .mot file
        self._software_limits_enabled = False
        self._software_limit_pos: float = 1000.0
        self._software_limit_neg: float = -1000.0

        # Initialize AXL wrapper
        self._axl = AXLWrapper()

        logger.info("AjinextekRobotAdapter initialized")

    async def connect(self, axis_id: int, irq_no: int) -> None:
        """
        하드웨어 연결

        Args:
            axis_id: Axis ID number
            irq_no: IRQ number for connection

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            # Store connection parameters
            self.axis_id = axis_id
            self._irq_no = irq_no

            logger.info(
                "Connecting to AJINEXTEK robot controller (IRQ: %s, Axis: %s)", irq_no, self.axis_id
            )

            # Open AXL library with config value
            result = self._axl.open(irq_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to open AXL library: %s", error_msg)
                raise RobotConnectionError(
                    f"Failed to open AXL library: {error_msg}",
                    "AJINEXTEK",
                    details=f"IRQ: {irq_no}, Error: {result}",
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
                self.version = self._axl.get_lib_version()
                logger.info("AXL Library version: %s", self.version)
            except Exception:
                pass  # Library version is not critical

            # Initialize position tracking and servo state for single axis
            self._current_position = 0.0
            self._servo_state = False

            # Load robot parameters from configuration file for this axis
            await self._load_robot_parameters(axis_id)

            # Motion parameters are now loaded from .prm file via AxmMotLoadParaAll
            logger.info("Motion parameters initialized from .prm file")

            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            logger.info(
                f"AJINEXTEK robot controller connected successfully (IRQ: {irq_no}, Axis: {self.axis_id}, Total Axes: {self._axis_count})"
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
                # Stop motion and turn off servo for this robot's axis
                try:
                    # Stop motion with default deceleration
                    await self.stop_motion(self.axis_id, 1000.0)
                except Exception as e:
                    logger.warning("Failed to stop axis %s during disconnect: %s", self.axis_id, e)

                # Close AXL library connection
                try:
                    result = self._axl.close()
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        logger.warning("AXL library close warning: %s", error_msg)
                except Exception as e:
                    logger.warning("Error closing AXL library: %s", e)

                self._is_connected = False
                self._servo_state = False
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
            axis: Axis number (0-based) - must match this robot instance's axis_id

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            logger.info("Starting homing for axis %s using .mot file parameters", self.axis_id)
            self._motion_status = MotionStatus.HOMING

            # Ensure servo is on
            if not self._servo_state:
                self._set_servo_on()

            # Start homing using parameters already loaded from .mot file
            # The _home_axis method now handles all status monitoring internally
            await self._home_axis()

            # Update position to zero after successful homing
            self._current_position = 0.0

            self._motion_status = MotionStatus.IDLE
            logger.info("Axis %s homing completed successfully", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Homing failed on axis %s: %s", self.axis_id, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Homing failed on axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    # home_all_axes method removed - use individual home_axis() for each axis in separate threads

    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        지정된 축을 절대 위치로 이동

        Args:
            position: 절대 위치 (mm)
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If movement fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        # Use parameters directly
        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info(
                "Moving axis %s to absolute position: %smm at %smm/s", self.axis_id, position, vel
            )

            # Safety check before motion
            current_pos = await self.get_current_position(self.axis_id)
            direction = "positive" if position > current_pos else "negative"
            if not await self.is_axis_safe_to_move(self.axis_id, direction):
                raise RobotMotionError(
                    f"Axis {self.axis_id} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            # Check software limits
            if self._software_limits_enabled:
                if position > self._software_limit_pos or position < self._software_limit_neg:
                    raise RobotMotionError(
                        f"Target position {position}mm exceeds software limits "
                        f"[{self._software_limit_neg}, {self._software_limit_pos}] for axis {self.axis_id}",
                        "AJINEXTEK",
                    )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_state:
                self._set_servo_on()

            # Start absolute position move
            result = self._axl.move_start_pos(self.axis_id, position, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error("Failed to start movement on axis %s: %s", self.axis_id, error_msg)
                raise RobotMotionError(
                    f"Failed to start movement on axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            # Wait for motion to complete
            await self._wait_for_motion_complete(timeout=30.0)

            # Update current position for this axis
            self._current_position = position

            self._motion_status = MotionStatus.IDLE
            logger.info("Axis %s absolute move completed successfully", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Absolute move failed on axis %s: %s", self.axis_id, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Absolute move failed on axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_to_position(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis to absolute position (interface implementation)

        Args:
            position: Target position in mm
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            HardwareOperationError: If movement fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        # Call the more comprehensive move_absolute method
        await self.move_absolute(position, axis_id, velocity, acceleration, deceleration)

    async def move_relative(
        self,
        distance: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis by relative distance (interface implementation)

        Args:
            distance: Distance to move in mm
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            HardwareOperationError: If movement fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        # Get current position for this axis
        current_position = await self.get_current_position(self.axis_id)
        target_position = current_position + distance

        # Use move_to_position to reach target
        await self.move_to_position(target_position, axis_id, velocity, acceleration, deceleration)

    async def get_current_position(self, axis: int) -> float:
        """
        지정된 축의 현재 위치 조회

        Args:
            axis: 축 번호 (0부터 시작) - must match this robot instance's axis_id

        Returns:
            현재 위치 (mm)

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot get position for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            position = self._axl.get_act_pos(self.axis_id)

            # Update cached position
            self._current_position = position

            return position

        except Exception as e:
            logger.warning("Failed to get position for axis %s: %s", self.axis_id, e)
            # Use cached position as fallback
            return self._current_position

    # get_all_positions method removed - use individual get_position() for each axis

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

    async def stop_motion(self, axis_id: int, deceleration: float) -> None:
        """
        지정된 축의 모션 정지

        Args:
            axis_id: Axis ID number
            deceleration: Deceleration value for stopping

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If stop operation fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        try:
            logger.info(
                "Stopping motion on axis %s with deceleration %s mm/s²", self.axis_id, deceleration
            )

            result = self._axl.move_stop(self.axis_id, deceleration)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to stop axis %s: %s", self.axis_id, error_msg)
                raise RobotMotionError(
                    f"Failed to stop axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            # Update motion status - only set to IDLE if all axes are stopped
            # For now, we'll assume this axis is stopped
            logger.info("Axis %s motion stopped successfully", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Unexpected error stopping axis %s: %s", self.axis_id, e)
            raise RobotMotionError(
                f"Unexpected error stopping axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def emergency_stop(self, axis: int) -> None:
        """
        Emergency stop motion immediately for specific axis

        Args:
            axis: Specific axis to stop - must match this robot instance's axis_id

        Raises:
            HardwareException: If emergency stop fails
            ValueError: If axis doesn't match this robot's axis_id
        """

        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot emergency stop axis {axis}"
            )

        try:
            # Stop specific axis
            logger.warning("EMERGENCY STOP activated for axis %d", self.axis_id)

            # Use immediate stop (high deceleration)
            result = self._axl.move_stop(
                self.axis_id, 10000.0
            )  # High deceleration for emergency stop
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to emergency stop axis %d: %s", self.axis_id, error_msg)
                raise HardwareException(
                    "ajinextek_robot",
                    "emergency_stop",
                    {"axis": self.axis_id, "error": error_msg},
                )

            # Turn off servo for safety
            try:
                self._set_servo_off()
                self._servo_state = False
            except Exception as e:
                logger.warning(
                    "Failed to turn off servo %d during emergency stop: %s", self.axis_id, e
                )

            logger.warning("Emergency stop completed for axis %d", self.axis_id)

        except Exception as e:
            logger.error("Emergency stop failed for axis %d: %s", self.axis_id, e)
            raise HardwareException(
                "ajinextek_robot",
                "emergency_stop",
                {"error": f"Emergency stop failed for axis {self.axis_id}: {e}"},
            ) from e

    async def get_position(self, axis: int) -> float:
        """
        Get current position of axis

        Args:
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            Current position in mm

        Raises:
            ValueError: If axis doesn't match this robot's axis_id
        """
        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot get position for axis {axis}"
            )

        return await self.get_current_position(self.axis_id)

    async def is_moving(self, axis: int) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check - must match this robot instance's axis_id

        Returns:
            True if moving, False otherwise

        Raises:
            ValueError: If axis doesn't match this robot's axis_id
        """
        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot check motion for axis {axis}"
            )

        # Check specific axis
        return self._motion_status == MotionStatus.MOVING

    async def set_velocity(self, axis: int, velocity: float) -> None:
        """
        Set default velocity for axis

        Args:
            axis: Axis number - must match this robot instance's axis_id
            velocity: Velocity in mm/s

        Raises:
            HardwareException: If velocity setting fails
            ValueError: If axis doesn't match this robot's axis_id
        """

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot set velocity for axis {axis}"
            )

        if velocity <= 0:
            raise HardwareException(
                "ajinextek_robot",
                "set_velocity",
                {"error": f"Velocity must be positive, got {velocity}"},
            )

        # Set velocity using AXL library function
        result = self._axl.set_max_vel(self.axis_id, velocity)
        if result != AXT_RT_SUCCESS:
            error_msg = get_error_message(result)
            raise RobotMotionError(
                f"Failed to set velocity for axis {self.axis_id}: {error_msg}",
                "AJINEXTEK",
            )
        logger.info("Set velocity to %s mm/s for axis %s", velocity, self.axis_id)

    async def get_velocity(self, axis: int) -> float:
        """
        Get current velocity setting for axis

        Args:
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            Current velocity in mm/s

        Raises:
            ValueError: If axis doesn't match this robot's axis_id
        """
        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot get velocity for axis {axis}"
            )

        try:
            return self._axl.get_max_vel(self.axis_id)
        except Exception as e:
            logger.warning("Failed to get velocity for axis %s: %s", self.axis_id, e)
            return 100.0  # Default fallback

    async def move_velocity(
        self,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Start continuous velocity (jog) motion on this robot's axis

        Args:
            axis_id: Axis ID number
            velocity: Motion velocity (positive/negative for direction)
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If velocity motion fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        # Use parameters directly
        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info("Starting velocity motion on axis %s: %smm/s", self.axis_id, vel)

            # Safety check before motion
            direction = "positive" if vel > 0 else "negative"
            if not await self.is_axis_safe_to_move(self.axis_id, direction):
                raise RobotMotionError(
                    f"Axis {self.axis_id} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_state:
                self._set_servo_on()

            # Start velocity motion
            result = self._axl.move_start_vel(self.axis_id, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(
                    "Failed to start velocity motion on axis %s: %s", self.axis_id, error_msg
                )
                raise RobotMotionError(
                    f"Failed to start velocity motion on axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Velocity motion started successfully on axis %s", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Velocity motion failed on axis %s: %s", self.axis_id, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Velocity motion failed on axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def move_signal_search(
        self,
        search_distance: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Start signal search motion on this robot's axis (move until signal is detected)

        Args:
            search_distance: Maximum search distance in mm
            axis_id: Axis ID number
            velocity: Motion velocity (positive/negative for direction)
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If signal search motion fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        # Use parameters directly
        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info(
                "Starting signal search on axis %s: velocity=%smm/s, distance=%smm",
                self.axis_id,
                vel,
                search_distance,
            )

            # Safety check before motion
            direction = "positive" if vel > 0 else "negative"
            if not await self.is_axis_safe_to_move(self.axis_id, direction):
                raise RobotMotionError(
                    f"Axis {self.axis_id} is not safe to move {direction}",
                    "AJINEXTEK",
                )

            # Check if search distance exceeds software limits
            if self._software_limits_enabled:
                current_pos = await self.get_current_position(self.axis_id)
                target_pos = (
                    current_pos + search_distance if vel > 0 else current_pos - abs(search_distance)
                )

                if target_pos > self._software_limit_pos or target_pos < self._software_limit_neg:
                    raise RobotMotionError(
                        f"Signal search distance {search_distance}mm would exceed software limits "
                        f"[{self._software_limit_neg}, {self._software_limit_pos}] for axis {self.axis_id}",
                        "AJINEXTEK",
                    )

            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_state:
                self._set_servo_on()

            # Start signal search motion
            result = self._axl.move_signal_search(self.axis_id, vel, accel, decel, search_distance)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(
                    "Failed to start signal search on axis %s: %s", self.axis_id, error_msg
                )
                raise RobotMotionError(
                    f"Failed to start signal search on axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Signal search motion started successfully on axis %s", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error("Signal search motion failed on axis %s: %s", self.axis_id, e)
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Signal search motion failed on axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def stop_velocity_motion(self, axis_id: int, deceleration: float) -> None:
        """
        Stop velocity (jog) motion on this robot's axis with specified deceleration

        Args:
            axis_id: Axis ID number
            deceleration: Deceleration value for stopping

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If stop operation fails
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis_id != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot operate on axis {axis_id}"
            )

        self._check_axis(self.axis_id)

        # Use deceleration parameter directly
        decel = deceleration

        try:
            logger.info(
                "Stopping velocity motion on axis %s with deceleration %s mm/s²",
                self.axis_id,
                decel,
            )

            result = self._axl.move_stop(self.axis_id, decel)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(
                    "Failed to stop velocity motion on axis %s: %s", self.axis_id, error_msg
                )
                raise RobotMotionError(
                    f"Failed to stop velocity motion on axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.info("Velocity motion stopped successfully on axis %s", self.axis_id)

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(
                "Unexpected error stopping velocity motion on axis %s: %s", self.axis_id, e
            )
            raise RobotMotionError(
                f"Unexpected error stopping velocity motion on axis {self.axis_id}: {e}",
                "AJINEXTEK",
                details=str(e),
            ) from e

    async def wait_for_completion(
        self,
        axis: int,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Wait for motion to complete on specific axis

        Args:
            axis: Specific axis to wait for (required for thread safety) - must match this robot instance's axis_id
            timeout: Maximum wait time in seconds

        Raises:
            HardwareException: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
            ValueError: If axis doesn't match this robot's axis_id
        """

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot wait for axis {axis}"
            )

        try:
            await self._wait_for_motion_complete(timeout or 30.0)
        except Exception as e:
            raise HardwareException(
                "ajinextek_robot",
                "wait_for_completion",
                {"error": f"Failed to wait for axis {self.axis_id}: {e}"},
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
            Primary axis ID (this robot instance's assigned axis)
        """
        return self.axis_id  # Return this robot instance's assigned axis

    async def check_servo_alarm(self, axis: int) -> bool:
        """
        Check servo alarm status for specified axis

        Args:
            axis: Axis number to check - must match this robot instance's axis_id

        Returns:
            True if alarm is active, False otherwise

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot check servo alarm for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            return self._axl.read_servo_alarm(self.axis_id)
        except Exception as e:
            logger.warning("Failed to read servo alarm for axis %s: %s", self.axis_id, e)
            return False  # Default to no alarm if read fails

    async def check_limit_sensors(self, axis: int) -> Dict[str, bool]:
        """
        Check limit sensor status for specified axis

        Args:
            axis: Axis number to check - must match this robot instance's axis_id

        Returns:
            Dictionary with 'positive_limit' and 'negative_limit' status

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot check limit sensors for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            pos_limit, neg_limit = self._axl.read_limit_status(self.axis_id)
            return {
                "positive_limit": pos_limit,
                "negative_limit": neg_limit,
            }
        except Exception as e:
            logger.warning("Failed to read limit sensors for axis %s: %s", self.axis_id, e)
            return {"positive_limit": False, "negative_limit": False}

    # check_all_servo_alarms method removed - use individual check_servo_alarm() for each axis

    # check_all_limit_sensors method removed - use individual check_limit_sensors() for each axis

    async def is_axis_safe_to_move(self, axis: int, direction: str = "both") -> bool:
        """
        Check if axis is safe to move in specified direction

        Args:
            axis: Axis number to check - must match this robot instance's axis_id
            direction: Movement direction ("positive", "negative", or "both")

        Returns:
            True if safe to move, False otherwise

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number or direction is invalid, or if axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot check safety for axis {axis}"
            )

        self._check_axis(self.axis_id)

        if direction not in ["positive", "negative", "both"]:
            raise ValueError(
                f"Invalid direction: {direction}. Must be 'positive', 'negative', or 'both'"
            )

        # Check servo alarm
        if await self.check_servo_alarm(self.axis_id):
            logger.warning("Axis %s has servo alarm - not safe to move", self.axis_id)
            return False

        # Check limit sensors
        limit_status = await self.check_limit_sensors(self.axis_id)

        if direction == "positive" and limit_status["positive_limit"]:
            logger.warning(
                "Axis %s positive limit is active - not safe to move positive", self.axis_id
            )
            return False
        elif direction == "negative" and limit_status["negative_limit"]:
            logger.warning(
                "Axis %s negative limit is active - not safe to move negative", self.axis_id
            )
            return False
        elif direction == "both" and (
            limit_status["positive_limit"] or limit_status["negative_limit"]
        ):
            logger.warning("Axis %s has active limit sensor - not safe to move", self.axis_id)
            return False

        # Check software limits if enabled
        if self._software_limits_enabled:
            current_pos = await self.get_current_position(self.axis_id)
            if direction in ["positive", "both"] and current_pos >= self._software_limit_pos:
                logger.warning(
                    "Axis %s at positive software limit - not safe to move positive", self.axis_id
                )
                return False
            if direction in ["negative", "both"] and current_pos <= self._software_limit_neg:
                logger.warning(
                    "Axis %s at negative software limit - not safe to move negative", self.axis_id
                )
                return False

        return True

    async def set_software_limits(self, axis: int, pos_limit: float, neg_limit: float) -> None:
        """
        Set software limits for specified axis

        Args:
            axis: Axis number - must match this robot instance's axis_id
            pos_limit: Positive direction limit in mm
            neg_limit: Negative direction limit in mm

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or limits are invalid, or if axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot set software limits for axis {axis}"
            )

        self._check_axis(self.axis_id)

        if neg_limit >= pos_limit:
            raise ValueError(
                f"Negative limit ({neg_limit}) must be less than positive limit ({pos_limit})"
            )

        self._software_limit_pos = pos_limit
        self._software_limit_neg = neg_limit
        logger.info(
            "Software limits set for axis %d: [%.3f, %.3f]", self.axis_id, neg_limit, pos_limit
        )

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
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            Tuple of (negative_limit, positive_limit)

        Raises:
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot get software limits for axis {axis}"
            )

        self._check_axis(self.axis_id)
        return (self._software_limit_neg, self._software_limit_pos)

    async def reset_servo_alarm(self, axis: int) -> bool:
        """
        Reset servo alarm for specified axis

        Args:
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            True if alarm was reset successfully

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot reset servo alarm for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            # Turn servo off and on again to reset alarm
            self._set_servo_off()
            await asyncio.sleep(0.1)  # Small delay
            self._set_servo_on()

            # Check if alarm is cleared
            await asyncio.sleep(0.1)  # Small delay
            alarm_cleared = not await self.check_servo_alarm(self.axis_id)

            if alarm_cleared:
                logger.info("Servo alarm reset successfully for axis %d", self.axis_id)
            else:
                logger.warning("Servo alarm still active after reset for axis %d", self.axis_id)

            return alarm_cleared

        except Exception as e:
            logger.error("Failed to reset servo alarm for axis %d: %s", self.axis_id, e)
            return False

    async def get_detailed_axis_status(self, axis: int) -> Dict[str, Any]:
        """
        Get detailed status for a specific axis

        Args:
            axis: Axis number - must match this robot instance's axis_id

        Returns:
            Detailed status dictionary for the axis

        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid or doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot get detailed status for axis {axis}"
            )

        self._check_axis(self.axis_id)

        status = {
            "axis": self.axis_id,
            "connected": True,
            "servo_on": self._servo_state,
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
                "velocity": 100.0,  # MAXVEL from .prm file
                "acceleration": 1000.0,  # ACCEL from .prm file
                "deceleration": 1000.0,  # DECEL from .prm file
                "unit_per_pulse": 1.0,  # UNITPERPULSE from .prm file
            },
        }

        # Get real-time data
        try:
            status["current_position"] = await self.get_current_position(self.axis_id)
            status["servo_alarm"] = await self.check_servo_alarm(self.axis_id)
            status["limit_sensors"] = await self.check_limit_sensors(self.axis_id)
            status["safe_to_move"] = {
                "positive": await self.is_axis_safe_to_move(self.axis_id, "positive"),
                "negative": await self.is_axis_safe_to_move(self.axis_id, "negative"),
                "both": await self.is_axis_safe_to_move(self.axis_id, "both"),
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

            # Check this robot's assigned axis only
            try:
                axis_status = await self.get_detailed_axis_status(self.axis_id)
                diagnostic["axes"][self.axis_id] = axis_status

                # Check for warnings/errors
                if axis_status.get("servo_alarm", False):
                    diagnostic["errors"].append(f"Axis {self.axis_id}: Servo alarm active")
                    diagnostic["overall_status"] = "ERROR"

                if axis_status.get("limit_sensors", {}).get("positive_limit", False):
                    diagnostic["warnings"].append(
                        f"Axis {self.axis_id}: Positive limit sensor active"
                    )

                if axis_status.get("limit_sensors", {}).get("negative_limit", False):
                    diagnostic["warnings"].append(
                        f"Axis {self.axis_id}: Negative limit sensor active"
                    )

                if not axis_status.get("servo_on", False):
                    diagnostic["warnings"].append(f"Axis {self.axis_id}: Servo is OFF")

            except Exception as e:
                diagnostic["errors"].append(f"Axis {self.axis_id}: Diagnostic failed - {e}")
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
            "servo_state": self._servo_state,
            "default_velocity": 100.0,  # MAXVEL from .prm file
            "default_acceleration": 1000.0,  # ACCEL from .prm file
            "hardware_type": "AJINEXTEK",
            "motion_parameters": {
                "unit_per_pulse": 1.0,  # UNITPERPULSE from .prm
                "pulse_per_unit": 1000,  # PULSEPERMM from .prm
                "pulse_output_method": 0,  # PULSEOUTMETHOD from .prm
                "coordinate_mode": 0,  # Absolute mode from .prm
                "limit_sensor_level": 1,  # LIMITPOSITIVE from .prm
                "software_limits_enabled": False,  # SOFTLIMITUSE from .prm
            },
        }

        if await self.is_connected():
            try:
                # Note: Individual axis information should be retrieved per-axis
                # This status method provides general robot state only
                status["note"] = "Use individual axis methods for detailed per-axis information"

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

    def _set_servo_on(self) -> None:
        """Turn servo on for this robot's axis"""
        self._check_axis(self.axis_id)

        try:
            result = self._axl.servo_on(self.axis_id, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self._servo_state = True
                logger.debug("Servo %s turned ON", self.axis_id)
            else:
                error_msg = get_error_message(result)
                logger.error("Failed to turn on servo %s: %s", self.axis_id, error_msg)
                raise RobotMotionError(
                    f"Failed to turn on servo {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to turn on servo %s: %s", self.axis_id, e)
            raise RobotMotionError(
                f"Failed to turn on servo {self.axis_id}: {e}",
                "AJINEXTEK",
            ) from e

    def _set_servo_off(self) -> None:
        """Turn servo off for this robot's axis"""
        self._check_axis(self.axis_id)

        try:
            result = self._axl.servo_on(self.axis_id, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self._servo_state = False
                logger.debug("Servo %s turned OFF", self.axis_id)
            else:
                error_msg = get_error_message(result)
                logger.error("Failed to turn off servo %s: %s", self.axis_id, error_msg)
                raise RobotMotionError(
                    f"Failed to turn off servo {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to turn off servo %s: %s", self.axis_id, e)
            raise RobotMotionError(
                f"Failed to turn off servo {self.axis_id}: {e}",
                "AJINEXTEK",
            ) from e

    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis

        This method enables servo motor for the specified axis only.
        Should be called before attempting motion operations on the axis.

        Args:
            axis: Axis number to enable servo for - must match this robot instance's axis_id

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo enable operation fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot enable servo for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            logger.info("Enabling servo for axis %s", self.axis_id)

            if not self._servo_state:
                self._set_servo_on()
                logger.debug("Servo enabled for axis %s", self.axis_id)
            else:
                logger.debug("Servo already enabled for axis %s", self.axis_id)

        except Exception as e:
            logger.error("Failed to enable servo for axis %s: %s", self.axis_id, e)
            raise RobotMotionError(
                f"Failed to enable servo for axis {self.axis_id}: {e}",
                "AJINEXTEK",
            ) from e

    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis

        This method disables servo motor for the specified axis.
        Should be called during shutdown or emergency situations.

        Args:
            axis: Axis number to disable servo for - must match this robot instance's axis_id

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If servo disable operation fails
            ValueError: If axis doesn't match this robot's axis_id
        """
        if not await self.is_connected():
            raise RobotConnectionError(
                "AJINEXTEK robot is not connected",
                "AJINEXTEK",
            )

        # Validate that requested axis matches this robot's assigned axis
        if axis != self.axis_id:
            raise ValueError(
                f"This robot instance controls axis {self.axis_id}, cannot disable servo for axis {axis}"
            )

        self._check_axis(self.axis_id)

        try:
            logger.info("Disabling servo for axis %s", self.axis_id)

            if self._servo_state:
                self._set_servo_off()
                logger.debug("Servo disabled for axis %s", self.axis_id)
            else:
                logger.debug("Servo already disabled for axis %s", self.axis_id)

        except Exception as e:
            logger.error("Failed to disable servo for axis %s: %s", self.axis_id, e)
            # Don't raise exception for disable failures during shutdown
            logger.warning("Servo disable failed for axis %s, continuing...", self.axis_id)

    async def _home_axis(self) -> None:
        """
        Perform homing for this robot's axis using parameters from robot_params.mot file

        All homing parameters (ORIGINMODE, ORIGINDIR, ORIGINLEVEL, ORIGINOFFSET,
        ORIGINVEL1, ORIGINVEL2) are already configured in the robot controller
        via AxmMotLoadParaAll. This function follows the AJINEXTEK documentation
        pattern for proper homing with status monitoring.

        Raises:
            RobotMotionError: If homing fails
        """
        self._check_axis(self.axis_id)

        if not self._servo_state:
            raise RobotMotionError(
                f"Servo {self.axis_id} is not ON - cannot perform homing",
                "AJINEXTEK",
            )

        try:
            # Start homing using parameters already loaded from .mot file
            result = self._axl.home_set_start(self.axis_id)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to start homing for axis %s: %s", self.axis_id, error_msg)
                raise RobotMotionError(
                    f"Failed to start homing for axis {self.axis_id}: {error_msg}",
                    "AJINEXTEK",
                )

            logger.debug("Started homing for axis %s using .mot file parameters", self.axis_id)

            # Monitor homing status using AJINEXTEK standard pattern
            while True:
                try:
                    home_result = self._axl.home_get_result(self.axis_id)

                    if home_result == HOME_SUCCESS:
                        logger.info("Homing completed successfully for axis %s", self.axis_id)
                        return

                    elif home_result == HOME_SEARCHING:
                        # Get progress information for logging
                        try:
                            _, step = self._axl.home_get_rate(self.axis_id)
                            logger.debug("Homing axis %s: %d%% complete", self.axis_id, step)
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

                    error_msg = error_messages.get(
                        home_result, f"Unknown homing error: 0x{home_result:02X}"
                    )
                    logger.error(
                        "Homing failed for axis %s: %s (0x%02X)",
                        self.axis_id,
                        error_msg,
                        home_result,
                    )
                    raise RobotMotionError(
                        f"Homing failed for axis {self.axis_id}: {error_msg}",
                        "AJINEXTEK",
                    )

                except Exception as status_error:
                    if isinstance(status_error, RobotMotionError):
                        raise
                    logger.error(
                        "Failed to check homing status for axis %s: %s", self.axis_id, status_error
                    )
                    raise RobotMotionError(
                        f"Failed to check homing status for axis {self.axis_id}: {status_error}",
                        "AJINEXTEK",
                    ) from status_error

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error("Failed to home axis %s: %s", self.axis_id, e)
            raise RobotMotionError(
                f"Failed to home axis {self.axis_id}: {e}",
                "AJINEXTEK",
            ) from e

    async def _wait_for_motion_complete(self, timeout: float = 30.0) -> None:
        """
        Wait for this robot's axis to stop moving

        Args:
            timeout: Maximum wait time in seconds

        Raises:
            RobotMotionError: If axis doesn't stop within timeout or status check fails
        """
        self._check_axis(self.axis_id)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                is_moving = self._axl.read_in_motion(self.axis_id)
                if not is_moving:
                    logger.debug("Axis %s stopped successfully", self.axis_id)
                    return
            except Exception as e:
                logger.error("Failed to check motion status for axis %s: %s", self.axis_id, e)
                raise RobotMotionError(
                    f"Failed to check motion status for axis {self.axis_id}: {e}",
                    "AJINEXTEK",
                ) from e

            await asyncio.sleep(0.01)  # Check every 10ms

        logger.warning("Timeout waiting for axis %s to stop", self.axis_id)
        raise RobotMotionError(
            f"Timeout waiting for axis {self.axis_id} to stop after {timeout} seconds",
            "AJINEXTEK",
        )

    async def _wait_for_homing_complete(self, timeout: float = 30.0) -> None:
        """
        Wait for this robot's axis homing to complete

        Args:
            timeout: Maximum wait time in seconds

        Raises:
            RobotMotionError: If homing doesn't complete within timeout
        """
        # For now, use motion complete check as homing indicator
        # In a real implementation, you might have specific homing status checks
        await self._wait_for_motion_complete(timeout)

    async def _load_robot_parameters(self, axis_id: int) -> None:
        """
        Load robot parameters from AJINEXTEK standard parameter file using AxmMotLoadPara

        Args:
            axis_id: Axis number to load parameters for (this robot's assigned axis)

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

            logger.info(
                "Loading robot parameters from %s using AxmMotLoadPara for axis %d",
                robot_params_file,
                axis_id,
            )

            # Load parameters for specific axis using AJINEXTEK standard function
            result = self._axl.load_para(axis_id, str(robot_params_file))

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error("Failed to load parameters from %s: %s", robot_params_file, error_msg)
                raise RobotConnectionError(
                    f"AxmMotLoadPara failed for axis {axis_id}: {error_msg}",
                    "AJINEXTEK",
                    details=f"File: {robot_params_file}, Axis: {axis_id}, Error: {result}",
                )

            logger.info(
                "Robot parameters loaded successfully from %s for axis %d",
                robot_params_file,
                axis_id,
            )

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
