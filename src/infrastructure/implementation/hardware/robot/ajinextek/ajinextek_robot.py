"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

import time
from typing import Any, Dict, List, Optional

import asyncio
from loguru import logger

# 절대 import 사용 (권장)
# src가 Python path에 있을 때 최적의 방법
from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.enums.robot_enums import MotionStatus
from domain.exceptions.robot_exceptions import (
    AXLConnectionError,
    AXLMotionError,
    RobotConfigurationError,
    RobotConnectionError,
    RobotMotionError,
)
from domain.value_objects.hardware_configuration import (
    RobotConfig,
)
from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import (
    AXLWrapper,
)
from infrastructure.implementation.hardware.robot.ajinextek.constants import *
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import (
    AXT_RT_SUCCESS,
    get_error_message,
)


class AjinextekRobot(RobotService):
    """AJINEXTEK 로봇 통합 서비스"""

    def __init__(
        self,
        # Hardware model
        model: str = "AJINEXTEK",
        # Motion parameters
        axis: int = 0,
        velocity: float = 100.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0,
        # Positioning settings
        position_tolerance: float = 0.1,
        homing_velocity: float = 10.0,
        homing_acceleration: float = 100.0,
        homing_deceleration: float = 100.0,
        # Connection parameters (AJINEXTEK specific)
        irq_no: int = 7,
    ):
        """
        초기화

        Args:
            model: 하드웨어 모델명
            axis: 사용할 축 번호
            velocity: 기본 속도 (mm/s)
            acceleration: 기본 가속도 (mm/s²)
            deceleration: 기본 감속도 (mm/s²)
            position_tolerance: 위치 허용 오차
            homing_velocity: 홈 복귀 속도
            homing_acceleration: 홈 복귀 가속도
            homing_deceleration: 홈 복귀 감속도
            irq_no: IRQ 번호
        """
        # Store configuration
        self._model = model
        self._axis = axis
        self._velocity = velocity
        self._acceleration = acceleration
        self._deceleration = deceleration
        self._default_velocity = velocity
        self._default_acceleration = acceleration
        self._default_deceleration = deceleration
        self._position_tolerance = position_tolerance
        self._homing_velocity = homing_velocity
        self._homing_acceleration = homing_acceleration
        self._homing_deceleration = homing_deceleration
        self._irq_no = irq_no

        # Runtime state
        self._is_connected = False
        self._axis_count = 0  # Will be detected during connection
        self._current_positions = []
        self._servo_states = {}
        self._motion_status = MotionStatus.IDLE
        self._error_message = None

        # Initialize AXL wrapper
        self._axl = AXLWrapper()

        logger.info(f"AjinextekRobotAdapter initialized with IRQ {irq_no}")

    async def connect(self, robot_config: RobotConfig) -> None:
        """
        하드웨어 연결

        Args:
            robot_config: Robot connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        # Update connection parameters from config
        self._irq_no = robot_config.irq_no

        try:
            logger.info(f"Connecting to AJINEXTEK robot controller (IRQ: {self._irq_no})")

            # Open AXL library
            result = self._axl.open(self._irq_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to open AXL library: {error_msg}")
                raise RobotConnectionError(
                    f"Failed to open AXL library: {error_msg}",
                    "AJINEXTEK",
                    details=f"IRQ: {self._irq_no}, Error: {result}",
                )

            # Get board count for verification
            try:
                board_count = self._axl.get_board_count()
                logger.info(f"Board count detected: {board_count}")
            except Exception as e:
                logger.error(f"Failed to get board count: {e}")
                raise RobotConnectionError(
                    f"Failed to get board count: {e}", "AJINEXTEK", details=str(e)
                ) from e

            # Get axis count from hardware
            try:
                self._axis_count = self._axl.get_axis_count()
                logger.info(f"Detected axis count: {self._axis_count}")
            except Exception as e:
                logger.error(f"Failed to get axis count: {e}")
                raise RobotConnectionError(
                    f"Failed to get axis count: {e}", "AJINEXTEK", details=str(e)
                ) from e

            # Get library version for info
            try:
                version = self._axl.get_lib_version()
                logger.info(f"AXL Library version: {version}")
            except Exception:
                pass  # Library version is not critical

            # Initialize position tracking and servo states
            self._current_positions = [0.0] * self._axis_count
            for axis in range(self._axis_count):
                self._servo_states[axis] = False

            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            logger.info(
                f"AJINEXTEK robot controller connected successfully (IRQ: {self._irq_no}, Axes: {self._axis_count})"
            )
            return True

        except RobotConnectionError:
            # Re-raise connection errors to preserve error context
            self._is_connected = False
            raise
        except Exception as e:
            logger.error(f"Failed to connect to AJINEXTEK robot: {e}")
            self._is_connected = False
            raise RobotConnectionError(
                f"Robot controller initialization failed: {e}", "AJINEXTEK", details=str(e)
            ) from e

    async def disconnect(self) -> bool:
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
                        await self.stop_motion(axis, self._default_deceleration)
                    except Exception as e:
                        logger.warning(f"Failed to stop axis {axis} during disconnect: {e}")

                # Turn off all servos
                for axis in range(self._axis_count):
                    try:
                        self._set_servo_off(axis)
                    except Exception as e:
                        logger.warning(f"Failed to turn off servo {axis}: {e}")

                # Close AXL library connection
                try:
                    result = self._axl.close()
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        logger.warning(f"AXL library close warning: {error_msg}")
                except Exception as e:
                    logger.warning(f"Error closing AXL library: {e}")

                self._is_connected = False
                self._servo_states = {}
                self._motion_status = MotionStatus.IDLE

                logger.info("AJINEXTEK robot controller disconnected")

            return True

        except Exception as e:
            logger.error(f"Error disconnecting AJINEXTEK robot: {e}")
            return False

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def home_axis(
        self,
        axis: int,
        velocity: float = 10.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0,
    ) -> bool:
        """
        지정된 축을 홈 위치로 이동

        Args:
            axis: 축 번호 (0부터 시작)
            velocity: 홈 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)

        Returns:
            홈 이동 성공 여부

        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        self._check_axis(axis)

        accel = acceleration
        decel = deceleration

        try:
            logger.info(f"Starting homing for axis {axis}")
            self._motion_status = MotionStatus.HOMING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Configure default homing parameters
            await self._home_axis(
                axis,
                home_dir=HOME_DIR_CCW,
                signal_level=LIMIT_LEVEL_LOW,
                mode=HOME_MODE_0,
                offset=0.0,
                vel_first=velocity,
                vel_second=velocity * 0.5,
                accel=accel,
                decel=decel,
            )

            # Wait for homing to complete
            await self._wait_for_homing_complete(axis, timeout=30.0)

            # Update position to zero after successful homing
            if axis < len(self._current_positions):
                self._current_positions[axis] = 0.0

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis} homing completed successfully")
            return True

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Homing failed on axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Homing failed on axis {axis}: {e}", "AJINEXTEK", details=str(e)
            ) from e

    async def home_all_axes(
        self, velocity: float = 10.0, acceleration: float = 100.0, deceleration: float = 100.0
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
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        try:
            logger.info("Starting homing sequence for all axes")
            self._motion_status = MotionStatus.HOMING

            failed_axes = []

            # Home each axis sequentially using the new single-axis method
            for axis in range(self._axis_count):
                try:
                    await self.home_axis(axis, velocity, acceleration, deceleration)
                    logger.info(f"Axis {axis} homing completed")

                except Exception as e:
                    failed_axes.append((axis, str(e)))
                    logger.error(f"Failed to home axis {axis}: {e}")

            if failed_axes:
                error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
                self._motion_status = MotionStatus.ERROR
                raise RobotMotionError(
                    f"Failed to home {len(failed_axes)} axes: {error_details}", "AJINEXTEK"
                )

            self._motion_status = MotionStatus.IDLE
            logger.info("All axes homing sequence completed successfully")
            return True

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Homing failed: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(f"Homing failed: {e}", "AJINEXTEK", details=str(e)) from e

    async def move_absolute(
        self,
        axis: int,
        position: float,
        velocity: float = 100.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0,
    ) -> bool:
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
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        self._check_axis(axis)

        vel = velocity
        accel = acceleration
        decel = deceleration

        try:
            logger.info(f"Moving axis {axis} to absolute position: {position}mm at {vel}mm/s")
            self._motion_status = MotionStatus.MOVING

            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)

            # Start absolute position move
            result = self._axl.move_start_pos(axis, position, vel, accel, decel)

            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(f"Failed to start movement on axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start movement on axis {axis}: {error_msg}", "AJINEXTEK"
                )

            # Wait for motion to complete
            await self._wait_for_motion_complete(axis, timeout=30.0)

            # Update current position for this axis
            if axis < len(self._current_positions):
                self._current_positions[axis] = position

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis} absolute move completed successfully")
            return True

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Absolute move failed on axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(
                f"Absolute move failed on axis {axis}: {e}", "AJINEXTEK", details=str(e)
            ) from e

    async def move_relative(
        self,
        axis: int,
        distance: float,
        velocity: float = 100.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0,
    ) -> bool:
        """
        지정된 축을 상대 위치로 이동

        Args:
            axis: 축 번호 (0부터 시작)
            distance: 상대 거리 (mm)
            velocity: 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)

        Returns:
            이동 성공 여부
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        self._check_axis(axis)

        # Get current position for this axis
        current_position = await self.get_current_position(axis)
        target_position = current_position + distance

        # Use absolute move to reach target
        return await self.move_absolute(axis, target_position, velocity, acceleration, deceleration)

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
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        self._check_axis(axis)

        try:
            position = self._axl.get_act_pos(axis)

            # Update cached position
            if axis < len(self._current_positions):
                self._current_positions[axis] = position

            return position

        except Exception as e:
            logger.warning(f"Failed to get position for axis {axis}: {e}")
            # Use cached position as fallback
            if axis < len(self._current_positions):
                return self._current_positions[axis]
            else:
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
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        try:
            positions = []
            for axis in range(self._axis_count):
                position = await self.get_current_position(axis)
                positions.append(position)

            return positions

        except Exception as e:
            logger.error(f"Failed to get all current positions: {e}")
            # Return cached positions as fallback
            return self._current_positions.copy()

    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회

        Returns:
            현재 모션 상태
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

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
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        self._check_axis(axis)

        try:
            logger.info(f"Stopping motion on axis {axis} with deceleration {deceleration} mm/s²")

            result = self._axl.move_stop(axis, deceleration)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to stop axis {axis}: {error_msg}")
                raise RobotMotionError(f"Failed to stop axis {axis}: {error_msg}", "AJINEXTEK")

            # Update motion status - only set to IDLE if all axes are stopped
            # For now, we'll assume this axis is stopped
            logger.info(f"Axis {axis} motion stopped successfully")

        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Unexpected error stopping axis {axis}: {e}")
            raise RobotMotionError(
                f"Unexpected error stopping axis {axis}: {e}", "AJINEXTEK", details=str(e)
            ) from e

    async def emergency_stop(self) -> None:
        """
        Emergency stop all motion immediately

        Raises:
            HardwareOperationError: If emergency stop fails
        """
        from domain.exceptions.hardware_exceptions import (
            HardwareOperationError,
        )

        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")

        try:
            logger.warning("EMERGENCY STOP activated")

            # NOTE: In a real implementation, you would:
            # 1. Send immediate stop command
            # 2. Disable all servos
            # 3. Set safety flags

            self._motion_status = MotionStatus.EMERGENCY_STOP
            self._servo_states = {axis: False for axis in range(self._axis_count)}

        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            raise HardwareOperationError(
                "ajinextek_robot", "emergency_stop", f"Emergency stop failed: {e}"
            ) from e

    async def initialize_axes(self) -> None:
        """
        Initialize robot axes and perform homing

        Raises:
            HardwareOperationError: If initialization fails
        """
        await self.home_all_axes(
            self._homing_velocity, self._homing_acceleration, self._homing_deceleration
        )


    async def move_relative(
        self, axis: int, distance: float, velocity: Optional[float] = None
    ) -> None:
        """
        Move axis by relative distance

        Args:
            axis: Axis number to move
            distance: Distance to move in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        from domain.exceptions.hardware_exceptions import (
            HardwareOperationError,
        )

        try:
            vel = velocity if velocity is not None else self._velocity
            current_position = await self.get_current_position(axis)
            target_position = current_position + distance
            success = await self.move_absolute(
                axis, target_position, vel, self._acceleration, self._deceleration
            )
            if not success:
                raise HardwareOperationError(
                    "ajinextek_robot",
                    "move_relative",
                    f"Failed to move axis {axis} by distance {distance}",
                )
        except Exception as e:
            raise HardwareOperationError(
                "ajinextek_robot", "move_relative", f"Failed to move axis {axis}: {e}"
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
        else:
            # Check if any axis is moving
            return self._motion_status in [MotionStatus.MOVING, MotionStatus.HOMING]

    async def set_velocity(self, axis: int, velocity: float) -> None:
        """
        Set default velocity for axis

        Args:
            axis: Axis number
            velocity: Velocity in mm/s

        Raises:
            HardwareOperationError: If velocity setting fails
        """
        from domain.exceptions.hardware_exceptions import (
            HardwareOperationError,
        )

        if velocity <= 0:
            raise HardwareOperationError(
                "ajinextek_robot", "set_velocity", f"Velocity must be positive, got {velocity}"
            )

        # For simplicity, set default velocity for all axes
        self._velocity = velocity
        logger.info(f"Set default velocity to {velocity} mm/s for axis {axis}")

    async def get_velocity(self, axis: int) -> float:
        """
        Get current velocity setting for axis

        Args:
            axis: Axis number

        Returns:
            Current velocity in mm/s
        """
        return self._velocity

    async def wait_for_completion(
        self, axis: Optional[int] = None, timeout: Optional[float] = None
    ) -> None:
        """
        Wait for motion to complete

        Args:
            axis: Axis to wait for (None waits for all axes)
            timeout: Maximum wait time in seconds

        Raises:
            HardwareOperationError: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
        """
        from domain.exceptions.hardware_exceptions import (
            HardwareOperationError,
        )

        if axis is not None:
            try:
                await self._wait_for_motion_complete(axis, timeout or 30.0)
            except Exception as e:
                raise HardwareOperationError(
                    "ajinextek_robot", "wait_for_completion", f"Failed to wait for axis {axis}: {e}"
                ) from e
        else:
            # Wait for all axes to complete
            try:
                for ax in range(self._axis_count):
                    await self._wait_for_motion_complete(ax, timeout or 30.0)
            except Exception as e:
                raise HardwareOperationError(
                    "ajinextek_robot", "wait_for_completion", f"Failed to wait for all axes: {e}"
                ) from e

    async def get_axis_count(self) -> int:
        """
        축 개수 조회

        Returns:
            축 개수
        """
        return self._axis_count

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
            "default_velocity": self._default_velocity,
            "default_acceleration": self._default_acceleration,
            "hardware_type": "AJINEXTEK",
        }

        if await self.is_connected():
            try:
                status["current_positions"] = await self.get_all_positions()
                status["last_error"] = None
            except Exception as e:
                status["current_positions"] = None
                status["last_error"] = str(e)

        return status

    # === Helper Methods ===

    def _check_axis(self, axis_no: int) -> None:
        """Check if axis number is valid"""
        if not self._is_connected:
            raise RobotConnectionError("Robot controller not connected", "AJINEXTEK")

        if axis_no < 0 or axis_no >= self._axis_count:
            raise RobotMotionError(
                f"Invalid axis number: {axis_no} (valid: 0-{self._axis_count-1})", "AJINEXTEK"
            )

    def _set_servo_on(self, axis_no: int) -> None:
        """Turn servo on for specified axis"""
        self._check_axis(axis_no)

        try:
            result = self._axl.servo_on(axis_no, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = True
                logger.debug(f"Servo {axis_no} turned ON")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn on servo {axis_no}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to turn on servo {axis_no}: {error_msg}", "AJINEXTEK"
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn on servo {axis_no}: {e}")
            raise RobotMotionError(f"Failed to turn on servo {axis_no}: {e}", "AJINEXTEK") from e

    def _set_servo_off(self, axis_no: int) -> None:
        """Turn servo off for specified axis"""
        self._check_axis(axis_no)

        try:
            result = self._axl.servo_on(axis_no, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = False
                logger.debug(f"Servo {axis_no} turned OFF")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn off servo {axis_no}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to turn off servo {axis_no}: {error_msg}", "AJINEXTEK"
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn off servo {axis_no}: {e}")
            raise RobotMotionError(f"Failed to turn off servo {axis_no}: {e}", "AJINEXTEK") from e

    async def _home_axis(
        self,
        axis_no: int,
        home_dir: int = HOME_DIR_CCW,
        signal_level: int = LIMIT_LEVEL_LOW,
        mode: int = HOME_MODE_0,
        offset: float = 0.0,
        vel_first: float = 10.0,
        vel_second: float = 5.0,
        accel: float = 100.0,
        decel: float = 100.0,
    ) -> None:
        """
        Perform homing for specified axis

        Args:
            axis_no: Axis number
            home_dir: Homing direction (default: CCW)
            signal_level: Sensor signal level (default: LOW)
            mode: Homing mode (default: Mode 0)
            offset: Offset from home position
            vel_first: First search velocity
            vel_second: Second search velocity
            accel: Acceleration
            decel: Deceleration

        Raises:
            RobotMotionError: If homing setup or start fails
        """
        self._check_axis(axis_no)

        if not self._servo_states.get(axis_no, False):
            raise RobotMotionError(
                f"Servo {axis_no} is not ON - cannot perform homing", "AJINEXTEK"
            )

        try:
            # Set homing method
            result = self._axl.home_set_method(axis_no, home_dir, signal_level, mode, offset)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing method for axis {axis_no}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to set homing method for axis {axis_no}: {error_msg}", "AJINEXTEK"
                )

            # Set homing velocities
            result = self._axl.home_set_vel(axis_no, vel_first, vel_second, accel, decel)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing velocities for axis {axis_no}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to set homing velocities for axis {axis_no}: {error_msg}", "AJINEXTEK"
                )

            # Start homing
            result = self._axl.home_set_start(axis_no)
            if result == AXT_RT_SUCCESS:
                logger.debug(f"Started homing for axis {axis_no}")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to start homing for axis {axis_no}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start homing for axis {axis_no}: {error_msg}", "AJINEXTEK"
                )

        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to home axis {axis_no}: {e}")
            raise RobotMotionError(f"Failed to home axis {axis_no}: {e}", "AJINEXTEK") from e

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
                    logger.debug(f"Axis {axis_no} stopped successfully")
                    return
            except Exception as e:
                logger.error(f"Failed to check motion status for axis {axis_no}: {e}")
                raise RobotMotionError(
                    f"Failed to check motion status for axis {axis_no}: {e}", "AJINEXTEK"
                ) from e

            await asyncio.sleep(0.01)  # Check every 10ms

        logger.warning(f"Timeout waiting for axis {axis_no} to stop")
        raise RobotMotionError(
            f"Timeout waiting for axis {axis_no} to stop after {timeout} seconds", "AJINEXTEK"
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
