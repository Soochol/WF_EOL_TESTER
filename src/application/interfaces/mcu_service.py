"""
MCU Service Interface

Interface for MCU (Microcontroller Unit) hardware control.
Handles temperature control, test modes, and fan management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import IntEnum


class TestMode(IntEnum):
    """Test mode enumeration"""
    MODE_1 = 1
    MODE_2 = 2
    MODE_3 = 3


class MCUStatus(IntEnum):
    """MCU status enumeration"""
    IDLE = 0
    HEATING = 1
    COOLING = 2
    HOLDING = 3
    ERROR = 4


class MCUService(ABC):
    """MCU 제어 인터페이스"""
    
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
    async def set_temperature(self, target_temp: float) -> bool:
        """
        목표 온도 설정
        
        Args:
            target_temp: 목표 온도 (°C)
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 온도 범위
        """
        pass
    
    @abstractmethod
    async def get_temperature(self) -> float:
        """
        현재 온도 측정
        
        Returns:
            현재 온도 (°C)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            RuntimeError: 측정 실패
        """
        pass
    
    @abstractmethod
    async def set_test_mode(self, mode: TestMode) -> bool:
        """
        테스트 모드 설정
        
        Args:
            mode: 테스트 모드
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 모드
        """
        pass
    
    @abstractmethod
    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회
        
        Returns:
            현재 테스트 모드
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        pass
    
    @abstractmethod
    async def set_fan_speed(self, speed_percent: float) -> bool:
        """
        팬 속도 설정
        
        Args:
            speed_percent: 팬 속도 (0-100%)
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 속도 범위
        """
        pass
    
    @abstractmethod
    async def get_fan_speed(self) -> float:
        """
        현재 팬 속도 조회
        
        Returns:
            현재 팬 속도 (0-100%)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
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
    
    @abstractmethod
    async def start_heating(self) -> bool:
        """
        가열 시작
        
        Returns:
            시작 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        pass
    
    @abstractmethod
    async def start_cooling(self) -> bool:
        """
        냉각 시작
        
        Returns:
            시작 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        pass
    
    @abstractmethod
    async def stop_temperature_control(self) -> bool:
        """
        온도 제어 중지
        
        Returns:
            중지 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        pass