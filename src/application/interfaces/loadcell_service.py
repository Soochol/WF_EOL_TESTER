"""
LoadCell Service Interface

Interface for LoadCell hardware control and measurement.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LoadCellService(ABC):
    """LoadCell 하드웨어 제어 인터페이스"""
    
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
    async def read_force(self) -> float:
        """
        힘 측정값 읽기
        
        Returns:
            측정된 힘 값 (N)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            HardwareError: 하드웨어 오류
        """
        pass
    
    @abstractmethod
    async def zero(self) -> bool:
        """
        영점 조정
        
        Returns:
            영점 조정 성공 여부
            
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