"""
Mock Robot Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from loguru import logger

from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.enums.robot_enums import MotionStatus
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)
from domain.value_objects.axis_parameter import AxisParameter


class MockRobot(RobotService):
    """Mock 로봇 서비스 (테스트용)"""

    def __init__(
        self,
        config: Dict[str, Any],
        max_position: float = 1000.0,
        response_delay: float = 0.1,
    ):
        """
        초기화

        Args:
            config: 로봇 설정 딕셔너리 (하드웨어 연결 및 모션 파라미터)
            max_position: 최대 위치 (mm)
            response_delay: 응답 지연 시간 (초)
        """
        # Store configuration from dict
        self._model = config.get("model", "MOCK")
        self._max_position = max_position

        self._response_delay = response_delay

        # Runtime state - will be initialized during connection
        self._is_connected = False
        self._axis_count = 0  # Will be set during connection
        self._current_position: float = 0.0
        self._motion_status = MotionStatus.IDLE
        self._axis_velocity: float = 0.0

        logger.info(f"MockRobotAdapter initialized with {self._axis_count} axes")

    async def connect(self) -> None:
        """
        하드웨어 연결 (시뮬레이션)

        Raises:
            HardwareConnectionError: If connection fails
        """
        logger.info(f"Connecting to Mock Robot (Model: {self._model}, Axes: {self._axis_count})...")

        # 연결 지연 시뮬레이션
        await asyncio.sleep(self._response_delay * 2)

        # 테스트 환경에서는 항상 성공하도록 변경 (원래는 95% 확률)
        success = True  # random.random() > 0.05

        if success:
            self._is_connected = True
            self._motion_status = MotionStatus.IDLE

            # Simulate getting axis count from hardware (mock uses default 6)
            self._axis_count = 6
            logger.info("Mock Robot detected %d axes", self._axis_count)

            # Initialize motion parameters (in real implementation, these would be read from controller files)
            self._velocity = 100.0  # Default velocity from controller
            self._acceleration = 100.0  # Default acceleration from controller
            self._deceleration = 100.0  # Default deceleration from controller
            self._max_velocity = 1000.0  # Max velocity from controller
            self._homing_velocity = 10.0  # Homing velocity from controller
            self._homing_acceleration = 100.0  # Homing acceleration from controller
            self._homing_deceleration = 100.0  # Homing deceleration from controller

            # Initialize position tracking and velocity for single axis control
            self._current_position = 0.0
            self._axis_velocity = self._velocity
            logger.info("Mock Robot connected successfully")
        else:
            logger.warning("Mock Robot connection failed")
            raise HardwareConnectionError("mock_robot", "Simulated connection failure")

    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제 (시뮬레이션)

        Raises:
            HardwareOperationError: If disconnection fails
        """
        logger.info("Disconnecting Mock Robot...")

        await asyncio.sleep(self._response_delay)

        self._is_connected = False
        self._motion_status = MotionStatus.IDLE
        self._current_position = 0.0

        logger.info("Mock Robot disconnected")

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def move_to_position(
        self,
        position: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        단일 축을 절대 위치로 이동 (시뮬레이션)

        Args:
            position: 목표 위치 (mm)
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_param.axis < 0 or axis_param.axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Invalid axis {axis_param.axis}",
            )

        if abs(position) > self._max_position:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Position {position} exceeds limit ±{self._max_position}mm",
            )

        vel = axis_param.velocity
        if vel > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s",
            )

        try:
            logger.info(f"Mock robot moving axis {axis_param.axis} to position {position} at {vel} mm/s")
            self._motion_status = MotionStatus.MOVING

            # 이동 시간 계산
            distance = abs(position - self._current_position)
            motion_time = distance / vel if vel > 0 else 0.1

            # 이동 시뮬레이션
            start_position = self._current_position
            steps = max(int(motion_time / 0.1), 1)

            for step in range(steps):
                await asyncio.sleep(0.1)
                progress = (step + 1) / steps
                self._current_position = start_position + (position - start_position) * progress

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock axis {axis_param.axis} move completed")

        except Exception as e:
            logger.error(f"Mock axis {axis_param.axis} move failed: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "move_to_position", str(e)) from e

    async def move_relative_single(
        self,
        axis: int,
        distance: float,
        velocity: float,
    ) -> None:
        """
        단일 축을 상대 위치로 이동 (시뮬레이션)

        Args:
            axis: 축 번호
            distance: 이동 거리 (mm)
            velocity: 이동 속도 (mm/s)

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_relative_single",
                f"Invalid axis {axis}",
            )

        # 목표 위치 계산
        target_position = self._current_position + distance

        # 절대 이동으로 구현
        await self.move_to_position(axis, target_position, velocity)

    async def get_position(self, axis: int) -> float:
        """
        단일 축의 현재 위치 조회 (시뮬레이션)

        Args:
            axis: 축 번호

        Returns:
            현재 위치 (mm)
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "get_position",
                f"Invalid axis {axis}",
            )

        # 작은 노이즈 추가로 실제 하드웨어 시뮬레이션
        noise = random.uniform(-0.01, 0.01)  # ±0.01mm 노이즈
        return self._current_position + noise

    async def move_absolute(
        self,
        position: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            position: Target position in mm
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_param.axis < 0 or axis_param.axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Invalid axis {axis_param.axis}",
            )

        if abs(position) > self._max_position:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Position {position} exceeds limit ±{self._max_position}mm",
            )

        # Use provided values directly
        vel = axis_param.velocity
        acc = axis_param.acceleration
        dec = axis_param.deceleration

        if vel > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s",
            )

        try:
            logger.info(
                f"Moving mock robot axis {axis_param.axis} to position {position}mm "
                f"(vel: {vel}mm/s, acc: {acc}mm/s², dec: {dec}mm/s²)"
            )

            self._motion_status = MotionStatus.MOVING

            # Calculate motion time
            distance = abs(position - self._current_position)
            motion_time = distance / vel if vel > 0 else 0.1

            # Simulate motion with steps
            start_position = self._current_position
            steps = max(int(motion_time / 0.1), 1)

            for step in range(steps):
                await asyncio.sleep(0.1)
                progress = (step + 1) / steps
                self._current_position = start_position + (position - start_position) * progress

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock robot axis {axis_param.axis} moved to position {position}mm")

        except Exception as e:
            logger.error(f"Failed to move mock robot axis {axis_param.axis} to position {position}mm: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "move_absolute", str(e)) from e

    async def move_relative(
        self,
        distance: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        Move axis by relative distance

        Args:
            distance: Distance to move in mm
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_param.axis < 0 or axis_param.axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_relative",
                f"Invalid axis {axis_param.axis}",
            )

        # Calculate target position
        target_position = self._current_position + distance

        # Use absolute move to reach target
        await self.move_absolute(target_position, axis_param)

    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회

        Returns:
            현재 모션 상태
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        return self._motion_status

    async def stop_motion(self, axis_param: AxisParameter) -> None:
        """
        지정된 축의 모션 정지 (시뮬레이션)

        Args:
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)
                       deceleration 값이 사용됨

        Raises:
            HardwareOperationError: If stop operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis_param.axis < 0 or axis_param.axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "stop_motion",
                f"Invalid axis {axis_param.axis}",
            )

        try:
            logger.info(
                f"Stopping mock robot motion on axis {axis_param.axis} with deceleration {axis_param.deceleration} mm/s²"
            )

            await asyncio.sleep(self._response_delay)

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock robot axis {axis_param.axis} motion stopped")

        except Exception as e:
            logger.error(f"Failed to stop mock robot axis {axis_param.axis}: {e}")
            raise HardwareOperationError("mock_robot", "stop_motion", str(e)) from e

    async def emergency_stop(self, axis: int) -> None:
        """
        비상 정지 (시뮬레이션)

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
            logger.warning(f"MOCK EMERGENCY STOP activated for axis {axis}")

            # 즉시 정지
            self._motion_status = MotionStatus.EMERGENCY_STOP

        except Exception as e:
            logger.error(f"Mock emergency stop failed for axis {axis}: {e}")
            raise HardwareOperationError("mock_robot", "emergency_stop", str(e)) from e

    async def is_moving(self, axis: int) -> bool:
        """
        축이 현재 이동 중인지 확인

        Args:
            axis: 확인할 축

        Returns:
            이동 중이면 True, 아니면 False
        """
        if not self._is_connected:
            return False

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "is_moving",
                f"Invalid axis {axis}",
            )

        return self._motion_status == MotionStatus.MOVING

    async def set_velocity(self, axis: int, velocity: float) -> None:
        """
        축의 기본 속도 설정

        Args:
            axis: 축 번호
            velocity: 속도 (mm/s)

        Raises:
            HardwareOperationError: If velocity setting fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "set_velocity",
                f"Invalid axis {axis}",
            )

        if velocity <= 0:
            raise HardwareOperationError(
                "mock_robot",
                "set_velocity",
                "Velocity must be positive",
            )

        if velocity > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "set_velocity",
                f"Velocity {velocity} exceeds maximum {self._max_velocity} mm/s",
            )

        self._axis_velocity = velocity
        logger.info(f"Mock robot axis {axis} velocity set to {velocity} mm/s")

    async def get_velocity(self, axis: int) -> float:
        """
        축의 현재 속도 설정 조회

        Args:
            axis: 축 번호

        Returns:
            현재 속도 (mm/s)
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "get_velocity",
                f"Invalid axis {axis}",
            )

        return self._axis_velocity

    async def wait_for_completion(
        self,
        axis: int,
        timeout: Optional[float] = None,
    ) -> None:
        """
        모션 완료 대기

        Args:
            axis: 대기할 축 (None이면 모든 축)
            timeout: 최대 대기 시간 (초)

        Raises:
            HardwareOperationError: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "wait_for_completion",
                f"Invalid axis {axis}",
            )

        start_time = asyncio.get_event_loop().time()

        while self._motion_status == MotionStatus.MOVING:
            if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError(f"Motion did not complete within {timeout} seconds")

            await asyncio.sleep(0.1)

        if self._motion_status == MotionStatus.ERROR:
            raise HardwareOperationError(
                "mock_robot",
                "wait_for_completion",
                "Motion ended with error",
            )

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

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": self._is_connected,
            "hardware_type": "Mock Robot",
            "axis_count": self._axis_count,
            "motion_status": self._motion_status.value,
            "max_position": self._max_position,
            "default_velocity": self._velocity,
            "max_velocity": self._max_velocity,
            "response_delay": self._response_delay,
        }

        if self._is_connected:
            try:
                # Get current position for single axis control
                pos = await self.get_position(0)  # Use primary axis (axis 0)
                status["current_position"] = pos
                status["last_error"] = None
            except Exception as e:
                status["current_position"] = None
                status["last_error"] = str(e)

        return status

    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis (Mock implementation)

        This method simulates enabling servo motor for the specified axis.
        In mock mode, this is a no-op operation that logs the action.

        Args:
            axis: Axis number to enable servo for

        Raises:
            HardwareOperationError: If robot is not connected or invalid axis
        """
        if not self._is_connected:
            raise HardwareOperationError("mock_robot", "enable_servo", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "enable_servo",
                f"Invalid axis {axis}. Valid range: 0-{self._axis_count-1}",
            )

        try:
            logger.info("Mock robot: Enabling servo for axis %d", axis)

            # Simulate servo enable delay
            await asyncio.sleep(self._response_delay)

            logger.debug("Mock robot: Servo enabled successfully for axis %d", axis)
        except Exception as e:
            raise HardwareOperationError("mock_robot", "enable_servo", str(e)) from e

    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis (Mock implementation)

        This method simulates disabling servo motor for the specified axis.
        In mock mode, this is a no-op operation that logs the action.

        Args:
            axis: Axis number to disable servo for

        Raises:
            HardwareOperationError: If robot is not connected or invalid axis
        """
        if not self._is_connected:
            raise HardwareOperationError("mock_robot", "disable_servo", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "disable_servo",
                f"Invalid axis {axis}. Valid range: 0-{self._axis_count-1}",
            )

        try:
            logger.info("Mock robot: Disabling servo for axis %d", axis)

            # Simulate servo disable delay
            await asyncio.sleep(self._response_delay)

            logger.debug("Mock robot: Servo disabled successfully for axis %d", axis)
        except Exception as e:
            logger.error("Mock robot: Failed to disable servo for axis %d: %s", axis, e)
            # Don't raise exception for disable failures during shutdown

    async def home_axis(self, axis: int) -> None:
        """
        Home a single axis (Mock implementation)

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
                f"Invalid axis {axis}. Valid range: 0-{self._axis_count-1}",
            )

        try:
            # Use default homing parameters
            vel = self._homing_velocity
            acc = self._homing_acceleration
            dec = self._homing_deceleration

            logger.info(
                f"Mock robot: Homing axis {axis} (vel: {vel}mm/s, acc: {acc}mm/s², dec: {dec}mm/s²)"
            )

            self._motion_status = MotionStatus.MOVING

            # Simulate homing motion - move to zero position
            homing_time = abs(self._current_position) / vel if vel > 0 else 1.0
            steps = max(int(homing_time / 0.1), 1)

            start_position = self._current_position
            for step in range(steps):
                await asyncio.sleep(0.1)
                progress = (step + 1) / steps
                self._current_position = start_position * (1 - progress)

            # Set to exactly zero after homing
            self._current_position = 0.0
            self._motion_status = MotionStatus.IDLE

            logger.info(f"Mock robot: Axis {axis} homed successfully")

        except Exception as e:
            logger.error(f"Mock robot: Failed to home axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "home_axis", str(e)) from e

    # Mock-specific utility methods

    def set_position_directly(self, position: float) -> None:
        """
        Mock용: 위치를 직접 설정 (테스트용)

        Args:
            position: 설정할 위치 값
        """
        self._current_position = position
        logger.debug(f"Mock robot position set directly to: {position}")

    def simulate_error(self, error_type: str = "general") -> None:
        """
        Mock용: 에러 상황 시뮬레이션 (테스트용)

        Args:
            error_type: 에러 타입 ("general", "emergency", "connection")
        """
        if error_type == "emergency":
            self._motion_status = MotionStatus.EMERGENCY_STOP
        elif error_type == "connection":
            self._is_connected = False
        else:
            self._motion_status = MotionStatus.ERROR

        logger.debug(f"Mock robot error simulated: {error_type}")
