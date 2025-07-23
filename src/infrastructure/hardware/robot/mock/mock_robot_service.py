"""
Mock Robot Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Dict, List, Any
from loguru import logger

from application.interfaces.robot_service import RobotService, MotionStatus


class MockRobotService(RobotService):
    """Mock 로봇 서비스 (테스트용)"""
    
    def __init__(
        self,
        axis_count: int = 6,
        max_position: float = 1000.0,
        default_velocity: float = 100.0,
        response_delay: float = 0.1
    ):
        """
        초기화
        
        Args:
            axis_count: 축 개수
            max_position: 최대 위치 (mm)
            default_velocity: 기본 속도 (mm/s)
            response_delay: 응답 지연 시간 (초)
        """
        self._axis_count = axis_count
        self._max_position = max_position
        self._default_velocity = default_velocity
        self._response_delay = response_delay
        
        self._is_connected = False
        self._current_positions = [0.0] * axis_count
        self._motion_status = MotionStatus.IDLE
        self._max_velocity = 1000.0
        
        logger.info(f"MockRobotService initialized with {axis_count} axes")
    
    async def connect(self) -> bool:
        """
        하드웨어 연결 (시뮬레이션)
        
        Returns:
            연결 성공 여부
        """
        logger.info("Connecting to Mock Robot...")
        
        # 연결 지연 시뮬레이션
        await asyncio.sleep(self._response_delay * 2)
        
        # 95% 확률로 성공
        success = random.random() > 0.05
        
        if success:
            self._is_connected = True
            self._motion_status = MotionStatus.IDLE
            logger.info("Mock Robot connected successfully")
        else:
            logger.warning("Mock Robot connection failed")
        
        return success
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제 (시뮬레이션)
        
        Returns:
            연결 해제 성공 여부
        """
        logger.info("Disconnecting Mock Robot...")
        
        await asyncio.sleep(self._response_delay)
        
        self._is_connected = False
        self._motion_status = MotionStatus.IDLE
        self._current_positions = [0.0] * self._axis_count
        
        logger.info("Mock Robot disconnected")
        return True
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def home_all_axes(self) -> bool:
        """
        모든 축 홈 위치로 이동 (시뮬레이션)
        
        Returns:
            홈 이동 성공 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        try:
            logger.info("Starting mock homing sequence")
            self._motion_status = MotionStatus.HOMING
            
            # 홈 이동 시뮬레이션 (2초)
            await asyncio.sleep(2.0)
            
            # 모든 축을 0 위치로 설정
            self._current_positions = [0.0] * self._axis_count
            self._motion_status = MotionStatus.IDLE
            
            logger.info("Mock homing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Mock homing failed: {e}")
            self._motion_status = MotionStatus.ERROR
            return False
    
    async def move_absolute(self, positions: List[float], velocity: float = None) -> bool:
        """
        절대 위치로 이동 (시뮬레이션)
        
        Args:
            positions: 각 축의 절대 위치 (mm)
            velocity: 이동 속도 (mm/s)
            
        Returns:
            이동 성공 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        if len(positions) != self._axis_count:
            raise ValueError(f"Expected {self._axis_count} positions, got {len(positions)}")
        
        # 위치 범위 검증
        for i, pos in enumerate(positions):
            if abs(pos) > self._max_position:
                raise ValueError(f"Position {pos} for axis {i} exceeds limit ±{self._max_position}mm")
        
        vel = velocity or self._default_velocity
        if vel > self._max_velocity:
            raise ValueError(f"Velocity {vel} exceeds maximum {self._max_velocity} mm/s")
        
        try:
            logger.info(f"Mock robot moving to positions: {positions} at {vel} mm/s")
            self._motion_status = MotionStatus.MOVING
            
            # 이동 시간 계산 (가장 먼 축 기준)
            max_distance = max(abs(pos - current) for pos, current in zip(positions, self._current_positions))
            motion_time = max_distance / vel if vel > 0 else 0.1
            
            # 실제 이동 시뮬레이션
            start_positions = self._current_positions.copy()
            steps = max(int(motion_time / 0.1), 1)  # 0.1초마다 위치 업데이트
            
            for step in range(steps):
                await asyncio.sleep(0.1)
                # 선형 보간으로 중간 위치 계산
                progress = (step + 1) / steps
                for i in range(self._axis_count):
                    self._current_positions[i] = start_positions[i] + (positions[i] - start_positions[i]) * progress
            
            self._motion_status = MotionStatus.IDLE
            logger.info("Mock absolute move completed")
            return True
            
        except Exception as e:
            logger.error(f"Mock absolute move failed: {e}")
            self._motion_status = MotionStatus.ERROR
            return False
    
    async def move_relative(self, distances: List[float], velocity: float = None) -> bool:
        """
        상대 위치로 이동 (시뮬레이션)
        
        Args:
            distances: 각 축의 상대 거리 (mm)
            velocity: 이동 속도 (mm/s)
            
        Returns:
            이동 성공 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        if len(distances) != self._axis_count:
            raise ValueError(f"Expected {self._axis_count} distances, got {len(distances)}")
        
        # 목표 위치 계산
        target_positions = [current + distance for current, distance in zip(self._current_positions, distances)]
        
        # 절대 이동으로 구현
        return await self.move_absolute(target_positions, velocity)
    
    async def get_current_position(self) -> List[float]:
        """
        현재 위치 조회 (시뮬레이션)
        
        Returns:
            각 축의 현재 위치 (mm)
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
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
            raise ConnectionError("Mock Robot is not connected")
        
        return self._motion_status
    
    async def stop_motion(self) -> bool:
        """
        모션 정지 (시뮬레이션)
        
        Returns:
            정지 성공 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        try:
            logger.info("Stopping mock robot motion")
            await asyncio.sleep(self._response_delay)
            
            self._motion_status = MotionStatus.IDLE
            logger.info("Mock robot motion stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop mock robot: {e}")
            return False
    
    async def emergency_stop(self) -> bool:
        """
        비상 정지 (시뮬레이션)
        
        Returns:
            비상 정지 실행 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        try:
            logger.warning("MOCK EMERGENCY STOP activated")
            
            # 즉시 정지
            self._motion_status = MotionStatus.EMERGENCY_STOP
            
            return True
            
        except Exception as e:
            logger.error(f"Mock emergency stop failed: {e}")
            return False
    
    async def set_velocity_limit(self, max_velocity: float) -> bool:
        """
        최대 속도 제한 설정 (시뮬레이션)
        
        Args:
            max_velocity: 최대 속도 (mm/s)
            
        Returns:
            설정 성공 여부
        """
        if not self._is_connected:
            raise ConnectionError("Mock Robot is not connected")
        
        if max_velocity <= 0:
            raise ValueError("Max velocity must be positive")
        
        self._max_velocity = max_velocity
        logger.info(f"Mock robot velocity limit set to {max_velocity} mm/s")
        return True
    
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
            'connected': self._is_connected,
            'hardware_type': 'Mock Robot',
            'axis_count': self._axis_count,
            'motion_status': self._motion_status.value,
            'max_position': self._max_position,
            'default_velocity': self._default_velocity,
            'max_velocity': self._max_velocity,
            'response_delay': self._response_delay
        }
        
        if self._is_connected:
            try:
                status['current_positions'] = await self.get_current_position()
                status['last_error'] = None
            except Exception as e:
                status['current_positions'] = None
                status['last_error'] = str(e)
        
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