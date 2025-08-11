"""
Mock Robot Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Any, Dict

from loguru import logger

from src.application.interfaces.hardware.robot import (
    RobotService,
)
from src.domain.enums.robot_enums import MotionStatus
from src.domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)


class MockRobot(RobotService):
    """Mock 로봇 서비스 (테스트용)"""

    def __init__(self):
        """
        초기화
        """
        self._is_connected = True  # Mock robot은 항상 연결된 상태로 시작
        self._current_position: float = 0.0
        self._motion_status = MotionStatus.IDLE
        self._axis_velocity: float = 0.0

        # Connection parameters - will be set during connect
        self._axis_id = 0
        self._irq_no = 7

        # Mock-specific settings
        self._model = "MOCK"
        self._max_position = 500000.0  # μm
        self._max_velocity = 100000.0  # μm/s
        self._response_delay = 0.1
        self._axis_count = 6

        logger.info("MockRobot initialized and connected (mock environment)")

    async def connect(self, axis_id: int, irq_no: int) -> None:
        """
        하드웨어 연결 (시뮬레이션)

        Args:
            axis_id: Axis ID number
            irq_no: IRQ number for connection

        Raises:
            HardwareConnectionError: If connection fails
        """
        # Store connection parameters
        self._axis_id = axis_id
        self._irq_no = irq_no

        logger.info(f"Connecting to Mock Robot (IRQ: {irq_no}, Axis: {axis_id})...")

        # 연결 지연 시뮬레이션
        await asyncio.sleep(self._response_delay * 2)

        # 연결 성공 (Mock에서는 항상 성공)
        self._is_connected = True
        logger.info("Mock Robot connected successfully")

    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제 (시뮬레이션)
        """
        logger.info("Disconnecting from Mock Robot...")
        await asyncio.sleep(self._response_delay)
        self._is_connected = False
        logger.info("Mock Robot disconnected")

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def get_position(self, axis: int) -> float:
        """
        현재 위치 조회 (시뮬레이션)

        Args:
            axis: 축 번호

        Returns:
            현재 위치 (μm)

        Raises:
            HardwareConnectionError: If robot is not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        # 작은 노이즈 추가로 실제 하드웨어 시뮬레이션
        noise = random.uniform(-10, 10)  # ±10μm 노이즈
        return self._current_position + noise

    async def get_current_position(self, axis: int) -> float:
        """
        지정된 축의 현재 위치 조회

        Args:
            axis: 축 번호 (0부터 시작)

        Returns:
            현재 위치 (μm)

        Raises:
            HardwareConnectionError: If robot is not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "get_current_position",
                f"Invalid axis {axis}",
            )

        # Same as get_position but with different method name for compatibility
        noise = random.uniform(-10, 10)  # ±10μm 노이즈
        return self._current_position + noise

    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            position: Target position in μm
            axis_id: Axis ID number
            velocity: Motion velocity in μm/s
            acceleration: Motion acceleration in μm/s²
            deceleration: Motion deceleration in μm/s²

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_id < 0 or axis_id >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Invalid axis {axis_id}",
            )

        if abs(position) > self._max_position:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Position {position} exceeds limit ±{self._max_position}μm",
            )

        if velocity > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Velocity {velocity} exceeds maximum {self._max_velocity} μm/s",
            )

        try:
            logger.info(
                f"Moving mock robot axis {axis_id} to position {position}μm "
                f"(vel: {velocity}μm/s, acc: {acceleration}μm/s², dec: {deceleration}μm/s²)"
            )

            self._motion_status = MotionStatus.MOVING

            # Calculate motion time
            distance = abs(position - self._current_position)
            motion_time = distance / velocity if velocity > 0 else 0.1

            # Simulate motion with steps
            start_position = self._current_position
            steps = max(int(motion_time / 0.1), 1)

            for i in range(steps):
                await asyncio.sleep(0.1)
                # Linear interpolation
                progress = (i + 1) / steps
                self._current_position = start_position + (position - start_position) * progress

            # Ensure exact final position
            self._current_position = position
            self._motion_status = MotionStatus.IDLE

            logger.info(f"Mock robot axis {axis_id} reached position {position}μm")

        except Exception as e:
            logger.error(f"Failed to move mock robot axis {axis_id} to position {position}μm: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "move_absolute", str(e)) from e

    async def move_relative(
        self,
        distance: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis by relative distance

        Args:
            distance: Distance to move in μm
            axis_id: Axis ID number
            velocity: Motion velocity in μm/s
            acceleration: Motion acceleration in μm/s²
            deceleration: Motion deceleration in μm/s²

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        target_position = self._current_position + distance
        await self.move_absolute(target_position, axis_id, velocity, acceleration, deceleration)

    async def get_motion_status(self) -> MotionStatus:
        """
        현재 모션 상태 조회 (시뮬레이션)

        Returns:
            현재 모션 상태

        Raises:
            HardwareConnectionError: If robot is not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        return self._motion_status

    async def stop_motion(self, axis_id: int, deceleration: float) -> None:
        """
        지정된 축의 모션 정지 (시뮬레이션)

        Args:
            axis_id: Axis ID number
            deceleration: Deceleration value for stopping

        Raises:
            HardwareOperationError: If stop operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_id < 0 or axis_id >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "stop_motion",
                f"Invalid axis {axis_id}",
            )

        try:
            logger.info(
                f"Stopping motion on mock robot axis {axis_id} with deceleration {deceleration}μm/s²"
            )

            # 시뮬레이션: 즉시 정지
            self._motion_status = MotionStatus.IDLE
            self._axis_velocity = 0.0

            logger.info(f"Mock robot axis {axis_id} stopped at position {self._current_position}μm")

        except Exception as e:
            logger.error(f"Failed to stop mock robot axis {axis_id}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "stop_motion", str(e)) from e

    async def emergency_stop(self, axis: int) -> None:
        """
        Emergency stop motion immediately for specific axis

        Args:
            axis: Specific axis to stop

        Raises:
            HardwareOperationError: If emergency stop fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "emergency_stop",
                f"Invalid axis {axis}",
            )

        try:
            logger.warning(f"Emergency stop triggered on mock robot axis {axis}")

            # Immediate stop - no deceleration
            self._motion_status = MotionStatus.IDLE
            self._axis_velocity = 0.0

            logger.info(
                f"Mock robot axis {axis} emergency stopped at position {self._current_position}μm"
            )

        except Exception as e:
            logger.error(f"Failed to emergency stop mock robot axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "emergency_stop", str(e)) from e

    async def is_moving(self, axis: int) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check

        Returns:
            True if moving, False otherwise
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "is_moving",
                f"Invalid axis {axis}",
            )

        return self._motion_status == MotionStatus.MOVING

    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis

        Args:
            axis: Axis number to enable servo for

        Raises:
            HardwareOperationError: If servo enable operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "enable_servo",
                f"Invalid axis {axis}",
            )

        logger.info(f"Mock robot axis {axis} servo enabled")

    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis

        Args:
            axis: Axis number to disable servo for

        Raises:
            HardwareOperationError: If servo disable operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "disable_servo",
                f"Invalid axis {axis}",
            )

        logger.info(f"Mock robot axis {axis} servo disabled")

    async def get_axis_count(self) -> int:
        """
        Get the number of axes supported by this robot

        Returns:
            Total number of axes
        """
        return self._axis_count

    async def check_servo_alarm(self, axis: int) -> bool:
        """
        Check servo alarm status for specified axis

        Args:
            axis: Axis number to check

        Returns:
            True if alarm is active, False otherwise

        Raises:
            HardwareConnectionError: If robot is not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "check_servo_alarm",
                f"Invalid axis {axis}",
            )

        # Mock: No servo alarms in simulation
        return False

    async def check_limit_sensors(self, axis: int) -> Dict[str, bool]:
        """
        Check limit sensor status for specified axis

        Args:
            axis: Axis number to check

        Returns:
            Dictionary with 'positive_limit' and 'negative_limit' status

        Raises:
            HardwareConnectionError: If robot is not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "check_limit_sensors",
                f"Invalid axis {axis}",
            )

        # Mock: Simulate limit sensors based on current position
        pos_limit = self._current_position >= self._max_position
        neg_limit = self._current_position <= -self._max_position

        return {
            "positive_limit": pos_limit,
            "negative_limit": neg_limit,
        }

    async def home_axis(self, axis: int) -> None:
        """
        Home a single axis

        Args:
            axis: Axis number to home

        Raises:
            HardwareOperationError: If homing operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "home_axis",
                f"Invalid axis {axis}",
            )

        try:
            logger.info(f"Homing mock robot axis {axis}...")

            self._motion_status = MotionStatus.MOVING

            # Simulate homing motion - move to position 0
            await asyncio.sleep(1.0)  # Simulate homing time

            self._current_position = 0.0
            self._motion_status = MotionStatus.IDLE

            logger.info(f"Mock robot axis {axis} homed to position 0.0μm")

        except Exception as e:
            logger.error(f"Failed to home mock robot axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "home_axis", str(e)) from e

    async def get_status(self) -> Dict[str, Any]:
        """
        Get robot status information

        Returns:
            Dictionary containing robot status
        """
        return {
            "model": self._model,
            "type": "Mock Robot",
            "axis_count": self._axis_count,
            "max_position": self._max_position,
            "max_velocity": self._max_velocity,
            "current_position": self._current_position,
            "motion_status": self._motion_status.value,
            "connected": self._is_connected,
            "axis_id": self._axis_id,
            "irq_no": self._irq_no,
        }
