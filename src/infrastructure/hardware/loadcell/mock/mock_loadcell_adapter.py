"""
Mock LoadCell Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Optional, Dict, Any, List
from loguru import logger

from application.interfaces.loadcell import LoadCellService
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.exceptions import HardwareOperationError
from domain.value_objects.measurements import ForceValue
from domain.enums.measurement_units import MeasurementUnit


class MockLoadCellAdapter(LoadCellService):
    """Mock 로드셀 서비스 (테스트용)"""
    
    def __init__(
        self,
        mock_values: Optional[List[float]] = None,
        base_force: float = 10.0,
        noise_level: float = 0.1,
        connection_delay: float = 0.1
    ):
        """
        초기화
        
        Args:
            mock_values: 사전 정의된 측정값 리스트
            base_force: 기본 힘 값 (N)
            noise_level: 노이즈 레벨 (N)
            connection_delay: 연결 지연시간 (초)
        """
        self._mock_values = mock_values or []
        self._base_force = base_force
        self._noise_level = noise_level
        self._connection_delay = connection_delay
        
        self._is_connected = False
        self._zero_offset = 0.0
        self._value_index = 0
        self._measurement_rate = 10  # Hz
        
        logger.info(f"MockLoadCellAdapter initialized with base force: {base_force}N")
    
    async def connect(self) -> None:
        """
        하드웨어 연결 (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        logger.info("Connecting to mock LoadCell...")
        
        # 연결 지연 시뮬레이션
        await asyncio.sleep(self._connection_delay)
        
        # 테스트 환경에서는 항상 성공하도록 변경 (원래는 90% 확률)
        success = True  # random.random() > 0.1
        
        if success:
            self._is_connected = True
            logger.info("Mock LoadCell connected successfully")
        else:
            logger.warning("Mock LoadCell connection failed")
            raise HardwareConnectionException(
                hardware_type="loadcell",
                connection_status="connection_failed",
                operation="connect",
                details={"error": "Simulated connection failure"}
            )
    
    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제 (시뮬레이션)
        
        Raises:
            HardwareOperationError: If disconnection fails
        """
        logger.info("Disconnecting mock LoadCell...")
        
        await asyncio.sleep(0.05)  # 짧은 지연
        
        self._is_connected = False
        self._zero_offset = 0.0
        
        logger.info("Mock LoadCell disconnected")
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def read_force(self) -> ForceValue:
        """
        힘 측정값 읽기 (시뮬레이션)
        
        Returns:
            측정된 힘 값 (N)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        if not self._is_connected:
            raise ConnectionError("Mock LoadCell is not connected")
        
        # 짧은 측정 지연
        await asyncio.sleep(0.05)
        
        if self._mock_values and self._value_index < len(self._mock_values):
            # 사전 정의된 값 사용
            force = self._mock_values[self._value_index]
            self._value_index = (self._value_index + 1) % len(self._mock_values)
        else:
            # 랜덤 값 생성 (기본값 + 노이즈)
            noise = random.uniform(-self._noise_level, self._noise_level)
            force = self._base_force + noise
        
        # 영점 오프셋 적용
        force -= self._zero_offset
        
        logger.debug(f"Mock LoadCell reading: {force:.3f}N")
        return ForceValue(force, MeasurementUnit.NEWTON)
    
    async def zero_calibration(self) -> None:
        """
        영점 조정 (시뮬레이션)
        
        Raises:
            HardwareOperationError: If calibration fails
        """
        if not self._is_connected:
            raise HardwareConnectionException(
                hardware_type="mock_loadcell",
                connection_status="not_connected", 
                operation="zero_calibration",
                details={"error": "LoadCell is not connected"}
            )
        
        try:
            logger.info("Zeroing mock LoadCell...")
            
            # 영점 조정 시뮬레이션
            await asyncio.sleep(0.5)
            
            # 현재 읽기값을 영점으로 설정
            if self._mock_values and self._value_index < len(self._mock_values):
                self._zero_offset = self._mock_values[self._value_index]
            else:
                noise = random.uniform(-self._noise_level, self._noise_level)
                self._zero_offset = self._base_force + noise
            
            logger.info(f"Mock LoadCell zeroed (offset: {self._zero_offset:.3f}N)")
            
        except Exception as e:
            logger.error(f"Mock LoadCell zero calibration failed: {e}")
            raise HardwareOperationError("mock_loadcell", "zero_calibration", str(e))
    
    async def read_raw_value(self) -> float:
        """
        원시 ADC 값 읽기 (시뮬레이션)
        
        Returns:
            원시 측정값
        """
        if not self._is_connected:
            raise HardwareConnectionException(
                hardware_type="mock_loadcell",
                connection_status="not_connected", 
                operation="read_raw_value",
                details={"error": "LoadCell is not connected"}
            )
        
        # 짧은 측정 지연
        await asyncio.sleep(0.02)
        
        # 원시 값은 실제 힘값에 임의의 스케일 팩터를 적용
        force_value = await self.read_force() 
        raw_value = force_value.value * 1000.0 + random.uniform(-10, 10)  # 시뮬레이션
        
        logger.debug(f"Mock LoadCell raw reading: {raw_value:.1f}")
        return raw_value
    
    async def set_measurement_rate(self, rate_hz: int) -> None:
        """
        측정 샘플링 레이트 설정
        
        Args:
            rate_hz: 샘플링 레이트 (Hz)
            
        Raises:
            HardwareOperationError: If rate setting fails
        """
        if not self._is_connected:
            raise HardwareConnectionException(
                hardware_type="mock_loadcell",
                connection_status="not_connected", 
                operation="set_measurement_rate",
                details={"error": "LoadCell is not connected"}
            )
        
        if rate_hz <= 0 or rate_hz > 1000:
            raise HardwareOperationError("mock_loadcell", "set_measurement_rate", 
                                       f"Invalid measurement rate: {rate_hz} Hz (must be 1-1000)")
        
        self._measurement_rate = rate_hz
        logger.info(f"Mock LoadCell measurement rate set to {rate_hz} Hz")
    
    async def get_measurement_rate(self) -> int:
        """
        현재 측정 샘플링 레이트 조회
        
        Returns:
            현재 샘플링 레이트 (Hz)
        """
        if not self._is_connected:
            raise HardwareConnectionException(
                hardware_type="mock_loadcell",
                connection_status="not_connected", 
                operation="get_measurement_rate",
                details={"error": "LoadCell is not connected"}
            )
        
        return self._measurement_rate
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': self._is_connected,
            'hardware_type': 'Mock',
            'base_force': self._base_force,
            'noise_level': self._noise_level,
            'zero_offset': self._zero_offset,
            'mock_values_count': len(self._mock_values),
            'value_index': self._value_index
        }
        
        if self._is_connected:
            try:
                force_value = await self.read_force()
                status['current_force'] = force_value.value
                status['measurement_rate'] = self._measurement_rate
                status['last_error'] = None
            except Exception as e:
                status['current_force'] = None
                status['last_error'] = str(e)
        
        return status
    
    async def read_multiple_samples(self, count: int, interval_ms: int = 100) -> List[float]:
        """
        여러 샘플 연속 측정
        
        Args:
            count: 측정 횟수
            interval_ms: 측정 간격 (밀리초)
            
        Returns:
            힘 값 리스트
        """
        if not self._is_connected:
            raise ConnectionError("Mock LoadCell is not connected")
        
        samples = []
        interval_sec = interval_ms / 1000.0
        
        logger.info(f"Reading {count} mock samples with {interval_ms}ms interval")
        
        for i in range(count):
            if i > 0:
                await asyncio.sleep(interval_sec)
            
            force_value = await self.read_force()
            force = force_value.value
            samples.append(force)
            logger.debug(f"Mock sample {i+1}/{count}: {force:.3f}N")
        
        avg = sum(samples) / len(samples)
        logger.info(f"Completed {count} mock samples, avg: {avg:.3f}N")
        return samples
    
    def set_mock_values(self, values: List[float]) -> None:
        """
        Mock 값 리스트 설정
        
        Args:
            values: 새로운 Mock 값 리스트
        """
        self._mock_values = values
        self._value_index = 0
        logger.info(f"Mock values updated: {len(values)} values")
    
    def set_base_force(self, force: float) -> None:
        """
        기본 힘 값 설정
        
        Args:
            force: 새로운 기본 힘 값 (N)
        """
        self._base_force = force
        logger.info(f"Base force updated to {force}N")
    
    def set_noise_level(self, noise: float) -> None:
        """
        노이즈 레벨 설정
        
        Args:
            noise: 새로운 노이즈 레벨 (N)
        """
        self._noise_level = noise
        logger.info(f"Noise level updated to {noise}N")