"""
Mock Power Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Dict, Any
from loguru import logger

from application.interfaces.power_service import PowerService


class MockPowerService(PowerService):
    """Mock 전원 공급 장치 서비스 (테스트용)"""
    
    def __init__(
        self,
        max_voltage: float = 30.0,
        max_current: float = 5.0,
        voltage_accuracy: float = 0.01,
        current_accuracy: float = 0.001,
        connection_delay: float = 0.2
    ):
        """
        초기화
        
        Args:
            max_voltage: 최대 전압 (V)
            max_current: 최대 전류 (A)
            voltage_accuracy: 전압 정확도 (V)
            current_accuracy: 전류 정확도 (A)
            connection_delay: 연결 지연시간 (초)
        """
        self._max_voltage = max_voltage
        self._max_current = max_current
        self._voltage_accuracy = voltage_accuracy
        self._current_accuracy = current_accuracy
        self._connection_delay = connection_delay
        
        self._is_connected = False
        self._output_enabled = False
        self._set_voltage = 0.0
        self._set_current = 0.0
        
        logger.info(f"MockPowerService initialized with {max_voltage}V/{max_current}A limits")
    
    async def connect(self) -> bool:
        """
        하드웨어 연결 (시뮬레이션)
        
        Returns:
            연결 성공 여부
        """
        logger.info("Connecting to mock Power Supply...")
        
        # 연결 지연 시뮬레이션
        await asyncio.sleep(self._connection_delay)
        
        # 95% 확률로 성공
        success = random.random() > 0.05
        
        if success:
            self._is_connected = True
            self._output_enabled = False  # 안전을 위해 비활성화
            logger.info("Mock Power Supply connected successfully")
        else:
            logger.warning("Mock Power Supply connection failed")
        
        return success
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제 (시뮬레이션)
        
        Returns:
            연결 해제 성공 여부
        """
        logger.info("Disconnecting mock Power Supply...")
        
        await asyncio.sleep(0.1)
        
        self._is_connected = False
        self._output_enabled = False
        self._set_voltage = 0.0
        self._set_current = 0.0
        
        logger.info("Mock Power Supply disconnected")
        return True
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def set_output(self, voltage: float, current: float) -> bool:
        """
        전압과 전류 출력 설정 (시뮬레이션)
        
        Args:
            voltage: 출력 전압 (V)
            current: 출력 전류 (A)
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            ValueError: 잘못된 값 범위
        """
        if not self._is_connected:
            raise ConnectionError("Mock Power Supply is not connected")
        
        # 값 범위 검증
        if not (0 <= voltage <= self._max_voltage):
            raise ValueError(f"Voltage must be 0-{self._max_voltage}V, got {voltage}V")
        if not (0 <= current <= self._max_current):
            raise ValueError(f"Current must be 0-{self._max_current}A, got {current}A")
        
        # 설정 지연 시뮬레이션
        await asyncio.sleep(0.05)
        
        self._set_voltage = voltage
        self._set_current = current
        
        logger.info(f"Mock Power Supply set to: {voltage}V, {current}A")
        return True
    
    async def enable_output(self, enable: bool = True) -> bool:
        """
        출력 활성화/비활성화 (시뮬레이션)
        
        Args:
            enable: 활성화 여부
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        if not self._is_connected:
            raise ConnectionError("Mock Power Supply is not connected")
        
        await asyncio.sleep(0.05)
        
        self._output_enabled = enable
        status = "enabled" if enable else "disabled"
        logger.info(f"Mock Power Supply output {status}")
        
        return True
    
    async def measure_output(self) -> tuple[float, float]:
        """
        실제 출력 전압/전류 측정 (시뮬레이션)
        
        Returns:
            (전압, 전류) 튜플
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        if not self._is_connected:
            raise ConnectionError("Mock Power Supply is not connected")
        
        # 측정 지연 시뮬레이션
        await asyncio.sleep(0.02)
        
        if not self._output_enabled:
            # 출력이 비활성화된 경우
            return 0.0, 0.0
        
        # 설정값에 약간의 오차 추가
        voltage_error = random.uniform(-self._voltage_accuracy, self._voltage_accuracy)
        current_error = random.uniform(-self._current_accuracy, self._current_accuracy)
        
        actual_voltage = max(0, self._set_voltage + voltage_error)
        actual_current = max(0, self._set_current + current_error)
        
        logger.debug(f"Mock Power Supply measurements: {actual_voltage:.3f}V, {actual_current:.3f}A")
        return actual_voltage, actual_current
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': self._is_connected,
            'hardware_type': 'Mock',
            'max_voltage': self._max_voltage,
            'max_current': self._max_current,
            'output_enabled': self._output_enabled,
            'set_voltage': self._set_voltage,
            'set_current': self._set_current,
            'voltage_accuracy': self._voltage_accuracy,
            'current_accuracy': self._current_accuracy
        }
        
        if self._is_connected:
            try:
                voltage, current = await self.measure_output()
                status['measured_voltage'] = voltage
                status['measured_current'] = current
                status['last_error'] = None
            except Exception as e:
                status['measured_voltage'] = None
                status['measured_current'] = None
                status['last_error'] = str(e)
        
        return status
    
    def set_accuracy(self, voltage_accuracy: float, current_accuracy: float) -> None:
        """
        측정 정확도 설정
        
        Args:
            voltage_accuracy: 전압 정확도 (V)
            current_accuracy: 전류 정확도 (A)
        """
        self._voltage_accuracy = voltage_accuracy
        self._current_accuracy = current_accuracy
        logger.info(f"Accuracy updated: ±{voltage_accuracy}V, ±{current_accuracy}A")
    
    def set_limits(self, max_voltage: float, max_current: float) -> None:
        """
        최대 출력 한계 설정
        
        Args:
            max_voltage: 최대 전압 (V)
            max_current: 최대 전류 (A)
        """
        self._max_voltage = max_voltage
        self._max_current = max_current
        logger.info(f"Limits updated: {max_voltage}V/{max_current}A")
    
    async def simulate_load(self, resistance: float) -> tuple[float, float]:
        """
        부하 시뮬레이션
        
        Args:
            resistance: 부하 저항 (Ω)
            
        Returns:
            (전압, 전류) 튜플 - 부하 적용 후
        """
        if not self._is_connected or not self._output_enabled:
            return 0.0, 0.0
        
        # 옴의 법칙 적용: I = V/R
        if resistance > 0:
            theoretical_current = self._set_voltage / resistance
            actual_current = min(theoretical_current, self._set_current)
            actual_voltage = actual_current * resistance
        else:
            actual_voltage = self._set_voltage
            actual_current = self._set_current
        
        # 정확도 오차 추가
        voltage_error = random.uniform(-self._voltage_accuracy, self._voltage_accuracy)
        current_error = random.uniform(-self._current_accuracy, self._current_accuracy)
        
        actual_voltage = max(0, actual_voltage + voltage_error)
        actual_current = max(0, actual_current + current_error)
        
        logger.debug(f"Mock load simulation ({resistance}Ω): {actual_voltage:.3f}V, {actual_current:.3f}A")
        return actual_voltage, actual_current