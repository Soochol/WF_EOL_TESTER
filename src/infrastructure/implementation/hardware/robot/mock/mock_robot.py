"""
Mock Robot Service

Mock implementation for testing and development without real hardware.
"""

import random
from typing import Any, Dict, List, Optional

import asyncio
from loguru import logger

from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.enums.robot_enums import MotionStatus
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)


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
        self._axis_count = config.get("axis_count", 6)
        self._max_position = max_position

        # Motion parameters with defaults
        self._velocity = config.get("default_velocity", 100.0)
        self._acceleration = config.get("default_acceleration", 100.0)
        self._deceleration = config.get("default_deceleration", 100.0)
        self._position_tolerance = config.get("position_tolerance", 0.1)
        self._homing_velocity = config.get("homing_velocity", 10.0)
        self._homing_acceleration = config.get("homing_acceleration", 100.0)
        self._homing_deceleration = config.get("homing_deceleration", 100.0)
        self._response_delay = response_delay

        self._is_connected = False
        self._current_positions = [0.0] * self._axis_count
        self._motion_status = MotionStatus.IDLE
        self._max_velocity = 1000.0
        self._axis_velocities = [self._velocity] * self._axis_count

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
        self._current_positions = [0.0] * self._axis_count

        logger.info("Mock Robot disconnected")

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def initialize_axes(self) -> None:
        """
        축 초기화 및 홈 위치로 이동 (시뮬레이션)

        Raises:
            HardwareOperationError: If initialization fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        try:
            logger.info("Starting mock axis initialization")
            self._motion_status = MotionStatus.HOMING

            # 홈 이동 시뮬레이션 (2초)
            await asyncio.sleep(2.0)

            # 모든 축을 0 위치로 설정
            self._current_positions = [0.0] * self._axis_count
            self._motion_status = MotionStatus.IDLE

            logger.info("Mock axis initialization completed successfully")

        except Exception as e:
            logger.error(f"Mock axis initialization failed: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "initialize_axes", str(e)) from e

    async def move_to_position(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
    ) -> None:
        """
        단일 축을 절대 위치로 이동 (시뮬레이션)

        Args:
            axis: 축 번호
            position: 목표 위치 (mm)
            velocity: 이동 속도 (mm/s)

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Invalid axis {axis}",
            )

        if abs(position) > self._max_position:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Position {position} exceeds limit ±{self._max_position}mm",
            )

        vel = velocity or self._velocity
        if vel > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "move_to_position",
                f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s",
            )

        try:
            logger.info(f"Mock robot moving axis {axis} to position {position} at {vel} mm/s")
            self._motion_status = MotionStatus.MOVING

            # 이동 시간 계산
            distance = abs(position - self._current_positions[axis])
            motion_time = distance / vel if vel > 0 else 0.1

            # 이동 시뮬레이션
            start_position = self._current_positions[axis]
            steps = max(int(motion_time / 0.1), 1)

            for step in range(steps):
                await asyncio.sleep(0.1)
                progress = (step + 1) / steps
                self._current_positions[axis] = (
                    start_position + (position - start_position) * progress
                )

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock axis {axis} move completed")

        except Exception as e:
            logger.error(f"Mock axis {axis} move failed: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "move_to_position", str(e)) from e

    async def move_relative_single(
        self,
        axis: int,
        distance: float,
        velocity: Optional[float] = None,
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
        target_position = self._current_positions[axis] + distance

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
        return self._current_positions[axis] + noise

    async def get_all_positions(self) -> List[float]:
        """
        모든 축의 현재 위치 조회 (시뮬레이션)

        Returns:
            각 축의 현재 위치 (mm)
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        # 작은 노이즈 추가로 실제 하드웨어 시뮬레이션
        positions = []
        for pos in self._current_positions:
            noise = random.uniform(-0.01, 0.01)  # ±0.01mm 노이즈
            positions.append(pos + noise)

        return positions

    async def move_absolute(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s
            acceleration: Optional acceleration override in mm/s²
            deceleration: Optional deceleration override in mm/s²

        Raises:
            HardwareOperationError: If movement fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Invalid axis {axis}",
            )

        if abs(position) > self._max_position:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Position {position} exceeds limit ±{self._max_position}mm",
            )

        # Use default values if not provided
        vel = velocity or self._velocity
        acc = acceleration or self._acceleration
        dec = deceleration or self._deceleration

        if vel > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "move_absolute",
                f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s",
            )

        try:
            logger.info(
                f"Moving mock robot axis {axis} to position {position}mm "
                f"(vel: {vel}mm/s, acc: {acc}mm/s², dec: {dec}mm/s²)"
            )

            self._motion_status = MotionStatus.MOVING

            # Calculate motion time
            distance = abs(position - self._current_positions[axis])
            motion_time = distance / vel if vel > 0 else 0.1

            # Simulate motion with steps
            start_position = self._current_positions[axis]
            steps = max(int(motion_time / 0.1), 1)

            for step in range(steps):
                await asyncio.sleep(0.1)
                progress = (step + 1) / steps
                self._current_positions[axis] = (
                    start_position + (position - start_position) * progress
                )

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock robot axis {axis} moved to position {position}mm")

        except Exception as e:
            logger.error(f"Failed to move mock robot axis {axis} to position {position}mm: {e}")
            self._motion_status = MotionStatus.ERROR
            raise HardwareOperationError("mock_robot", "move_absolute", str(e)) from e

    async def move_relative(
        self,
        axis: int,
        distance: float,
        velocity: Optional[float] = None,
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
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "move_relative",
                f"Invalid axis {axis}",
            )

        # Calculate target position
        target_position = self._current_positions[axis] + distance

        # Use absolute move to reach target
        await self.move_absolute(axis, target_position, velocity)

    async def move_absolute_multi(
        self,
        positions: List[float],
        velocity: Optional[float] = None,
    ) -> bool:
        """
        절대 위치로 이동 (다중 축 시뮬레이션)

        Args:
            positions: 각 축의 절대 위치 (mm)
            velocity: 이동 속도 (mm/s)

        Returns:
            이동 성공 여부
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if len(positions) != self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "parameter_validation",
                f"Expected {self._axis_count} positions, got {len(positions)}",
            )

        # 위치 범위 검증
        for i, pos in enumerate(positions):
            if abs(pos) > self._max_position:
                raise HardwareOperationError(
                    "mock_robot",
                    "parameter_validation",
                    f"Position {pos} for axis {i} exceeds limit ±{self._max_position}mm",
                )

        vel = velocity or self._velocity
        if vel > self._max_velocity:
            raise HardwareOperationError(
                "mock_robot",
                "parameter_validation",
                f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s",
            )

        try:
            logger.info(f"Mock robot moving to positions: {positions} at {vel} mm/s")
            self._motion_status = MotionStatus.MOVING

            # 이동 시간 계산 (가장 먼 축 기준)
            max_distance = max(
                abs(pos - current) for pos, current in zip(positions, self._current_positions)
            )
            motion_time = max_distance / vel if vel > 0 else 0.1

            # 실제 이동 시뮬레이션
            start_positions = self._current_positions.copy()
            steps = max(int(motion_time / 0.1), 1)  # 0.1초마다 위치 업데이트

            for step in range(steps):
                await asyncio.sleep(0.1)
                # 선형 보간으로 중간 위치 계산
                progress = (step + 1) / steps
                for i in range(self._axis_count):
                    self._current_positions[i] = (
                        start_positions[i] + (positions[i] - start_positions[i]) * progress
                    )

            self._motion_status = MotionStatus.IDLE
            logger.info("Mock absolute move completed")
            return True

        except Exception as e:
            logger.error(f"Mock absolute move failed: {e}")
            self._motion_status = MotionStatus.ERROR
            return False

    async def move_relative_multi(
        self,
        distances: List[float],
        velocity: Optional[float] = None,
    ) -> bool:
        """
        상대 위치로 이동 (다중 축 시뮬레이션)

        Args:
            distances: 각 축의 상대 거리 (mm)
            velocity: 이동 속도 (mm/s)

        Returns:
            이동 성공 여부
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if len(distances) != self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "parameter_validation",
                f"Expected {self._axis_count} distances, got {len(distances)}",
            )

        # 목표 위치 계산
        target_positions = [
            current + distance for current, distance in zip(self._current_positions, distances)
        ]

        # 절대 이동으로 구현
        return await self.move_absolute_multi(target_positions, velocity)

    async def get_current_position(self) -> List[float]:
        """
        현재 위치 조회 (시뮬레이션)

        Returns:
            각 축의 현재 위치 (mm)
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        # 작은 노이즈 추가로 실제 하드웨어 시뮬레이션
        positions = []
        for pos in self._current_positions:
            noise = random.uniform(-0.01, 0.01)  # ±0.01mm 노이즈
            positions.append(pos + noise)

        return positions

    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회

        Returns:
            현재 모션 상태
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        return self._motion_status

    async def stop_motion(self, axis: int, deceleration: float) -> None:
        """
        지정된 축의 모션 정지 (시뮬레이션)

        Args:
            axis: 정지할 축 번호 (0부터 시작)
            deceleration: 감속도 (mm/s²) - 시뮬레이션에서는 로깅용

        Raises:
            HardwareOperationError: If stop operation fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        if axis < 0 or axis >= self._axis_count:
            raise HardwareOperationError(
                "mock_robot",
                "stop_motion",
                f"Invalid axis {axis}",
            )

        try:
            logger.info(
                f"Stopping mock robot motion on axis {axis} with deceleration {deceleration} mm/s²"
            )

            await asyncio.sleep(self._response_delay)

            self._motion_status = MotionStatus.IDLE
            logger.info(f"Mock robot axis {axis} motion stopped")

        except Exception as e:
            logger.error(f"Failed to stop mock robot axis {axis}: {e}")
            raise HardwareOperationError("mock_robot", "stop_motion", str(e)) from e

    async def emergency_stop(self) -> None:
        """
        비상 정지 (시뮬레이션)

        Raises:
            HardwareOperationError: If emergency stop fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_robot", "Robot is not connected")

        try:
            logger.warning("MOCK EMERGENCY STOP activated")

            # 즉시 정지
            self._motion_status = MotionStatus.EMERGENCY_STOP

        except Exception as e:
            logger.error(f"Mock emergency stop failed: {e}")
            raise HardwareOperationError("mock_robot", "emergency_stop", str(e)) from e

    async def is_moving(self, axis: Optional[int] = None) -> bool:
        """
        축이 현재 이동 중인지 확인

        Args:
            axis: 확인할 축 (None이면 모든 축 확인)

        Returns:
            이동 중이면 True, 아니면 False
        """
        if not self._is_connected:
            return False

        if axis is not None and (axis < 0 or axis >= self._axis_count):
            return False

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

        self._axis_velocities[axis] = velocity
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

        return self._axis_velocities[axis]

    async def wait_for_completion(
        self,
        axis: Optional[int] = None,
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

        if axis is not None and (axis < 0 or axis >= self._axis_count):
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
                status["current_positions"] = await self.get_current_position()
                status["last_error"] = None
            except Exception as e:
                status["current_positions"] = None
                status["last_error"] = str(e)

        return status

    # Mock-specific utility methods

    def set_position_directly(self, positions: List[float]) -> None:
        """
        Mock용: 위치를 직접 설정 (테스트용)

        Args:
            positions: 설정할 위치 리스트
        """
        if len(positions) == self._axis_count:
            self._current_positions = positions.copy()
            logger.debug(f"Mock robot positions set directly to: {positions}")

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
