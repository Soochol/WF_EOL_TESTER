"""
Robot Service Interface

Interface for robot hardware control and motion operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class MotionStatus(Enum):
    """Robot motion status enumeration"""
    IDLE = "idle"
    MOVING = "moving" 
    HOMING = "homing"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"


class RobotService(ABC):
    """Robot 하드웨어 제어 인터페이스"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        하드웨어 연결
        
        Returns:
            연결 성공 여부
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제
        
        Returns:
            연결 해제 성공 여부
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        pass
    
    @abstractmethod
    async def home_all_axes(self) -> bool:
        """
        모든 축 홈 위치로 이동
        
        Returns:
            홈 이동 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def move_absolute(self, positions: List[float], velocity: float = 100.0) -> bool:
        """
        절대 위치로 이동
        
        Args:
            positions: 각 축의 절대 위치 (mm)
            velocity: 이동 속도 (mm/s)
            
        Returns:
            이동 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 위치 값
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def move_relative(self, distances: List[float], velocity: float = 100.0) -> bool:
        """
        상대 위치로 이동
        
        Args:
            distances: 각 축의 상대 거리 (mm)
            velocity: 이동 속도 (mm/s)
            
        Returns:
            이동 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 거리 값
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def get_current_position(self) -> List[float]:
        """
        현재 위치 조회
        
        Returns:
            각 축의 현재 위치 (mm)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회
        
        Returns:
            현재 모션 상태
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def stop_motion(self) -> bool:
        """
        모션 정지
        
        Returns:
            정지 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def emergency_stop(self) -> bool:
        """
        비상 정지
        
        Returns:
            비상 정지 실행 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        pass
    
    @abstractmethod
    async def set_velocity_limit(self, max_velocity: float) -> bool:
        """
        최대 속도 제한 설정
        
        Args:
            max_velocity: 최대 속도 (mm/s)
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 속도 값
        """
        pass
    
    @abstractmethod
    async def get_axis_count(self) -> int:
        """
        축 개수 조회
        
        Returns:
            축 개수
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        pass