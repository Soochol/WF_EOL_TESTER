"""
Power Service Interface

Interface for power supply hardware control.
"""

from abc import ABC, abstractmethod
from typing import Optional


class PowerService(ABC):
    """전원 공급 장치 제어 인터페이스"""
    
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
    async def set_output(self, voltage: float, current: float) -> bool:
        """
        전압과 전류 출력 설정
        
        Args:
            voltage: 출력 전압 (V)
            current: 출력 전류 (A)
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def enable_output(self, enable: bool = True) -> bool:
        """
        출력 활성화/비활성화
        
        Args:
            enable: 활성화 여부
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def measure_output(self) -> tuple[float, float]:
        """
        실제 출력 전압/전류 측정
        
        Returns:
            (전압, 전류) 튜플
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> dict:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        pass