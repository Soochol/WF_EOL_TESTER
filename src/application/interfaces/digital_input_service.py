"""
Digital Input Service Interface

Interface for digital input/output hardware control.
Defines methods for GPIO, digital input/output operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum


class PinMode(Enum):
    """GPIO pin modes"""
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    INPUT_PULLDOWN = "input_pulldown"


class LogicLevel(Enum):
    """Logic levels for digital signals"""
    LOW = 0
    HIGH = 1


class DigitalInputService(ABC):
    """디지털 입력 하드웨어 제어 인터페이스"""
    
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
    async def configure_pin(self, pin: int, mode: PinMode) -> bool:
        """
        GPIO 핀 모드 설정
        
        Args:
            pin: 핀 번호
            mode: 핀 모드 (INPUT, OUTPUT 등)
            
        Returns:
            설정 성공 여부
        """
        pass
    
    @abstractmethod
    async def read_digital_input(self, pin: int) -> LogicLevel:
        """
        디지털 입력 읽기
        
        Args:
            pin: 핀 번호
            
        Returns:
            읽은 로직 레벨 (HIGH/LOW)
        """
        pass
    
    @abstractmethod
    async def write_digital_output(self, pin: int, level: LogicLevel) -> bool:
        """
        디지털 출력 쓰기
        
        Args:
            pin: 핀 번호
            level: 출력할 로직 레벨
            
        Returns:
            출력 성공 여부
        """
        pass
    
    @abstractmethod
    async def read_multiple_inputs(self, pins: List[int]) -> Dict[int, LogicLevel]:
        """
        다중 디지털 입력 읽기
        
        Args:
            pins: 읽을 핀 번호 리스트
            
        Returns:
            핀별 로직 레벨 딕셔너리
        """
        pass
    
    @abstractmethod
    async def write_multiple_outputs(self, pin_values: Dict[int, LogicLevel]) -> bool:
        """
        다중 디지털 출력 쓰기
        
        Args:
            pin_values: 핀별 출력 레벨 딕셔너리
            
        Returns:
            출력 성공 여부
        """
        pass
    
    @abstractmethod
    async def read_all_inputs(self) -> Dict[int, LogicLevel]:
        """
        모든 입력 핀 상태 읽기
        
        Returns:
            모든 입력 핀의 로직 레벨 딕셔너리
        """
        pass
    
    @abstractmethod
    async def get_pin_configuration(self) -> Dict[int, PinMode]:
        """
        현재 핀 설정 상태 조회
        
        Returns:
            핀별 설정 모드 딕셔너리
        """
        pass
    
    @abstractmethod
    async def reset_all_outputs(self) -> bool:
        """
        모든 출력을 LOW로 리셋
        
        Returns:
            리셋 성공 여부
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