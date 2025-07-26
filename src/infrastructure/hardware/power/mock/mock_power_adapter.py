"""
Mock Power Service

Mock implementation for testing and development without real hardware.
"""

import asyncio
import random
from typing import Dict, Any
from loguru import logger

from application.interfaces.power import PowerService
from domain.exceptions import HardwareConnectionError, HardwareOperationError


class MockPowerAdapter(PowerService):
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
        
        logger.info(f"MockPowerAdapter initialized with {max_voltage}V/{max_current}A limits")
    
    async def connect(self) -> None:
        """
        Connect to power supply hardware (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        logger.info("Connecting to mock Power Supply...")
        
        try:
            # 연결 지연 시뮬레이션
            await asyncio.sleep(self._connection_delay)
            
            # 95% 확률로 성공
            if random.random() <= 0.05:
                raise Exception("Simulated connection failure")
            
            self._is_connected = True
            self._output_enabled = False  # 안전을 위해 비활성화
            logger.info("Mock Power Supply connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to mock Power Supply: {e}")
            raise HardwareConnectionError("mock_power", str(e))
    
    async def disconnect(self) -> None:
        """
        Disconnect from power supply hardware (시뮬레이션)
        
        Raises:
            HardwareOperationError: If disconnection fails
        """
        try:
            logger.info("Disconnecting mock Power Supply...")
            
            await asyncio.sleep(0.1)
            
            self._is_connected = False
            self._output_enabled = False
            self._set_voltage = 0.0
            self._set_current = 0.0
            
            logger.info("Mock Power Supply disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting mock Power Supply: {e}")
            raise HardwareOperationError("mock_power", "disconnect", str(e))
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def set_voltage(self, voltage: float) -> None:
        """
        Set output voltage (시뮬레이션)
        
        Args:
            voltage: Target voltage in volts
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If voltage setting fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            # 값 범위 검증
            if not (0 <= voltage <= self._max_voltage):
                raise HardwareOperationError("mock_power", "set_voltage", 
                                           f"Voltage must be 0-{self._max_voltage}V, got {voltage}V")
            
            # 설정 지연 시뮬레이션
            await asyncio.sleep(0.05)
            
            self._set_voltage = voltage
            logger.info(f"Mock Power Supply voltage set to: {voltage}V")
            
        except Exception as e:
            logger.error(f"Failed to set mock Power Supply voltage: {e}")
            raise HardwareOperationError("mock_power", "set_voltage", str(e))
    
    async def get_voltage(self) -> float:
        """
        Get current output voltage (시뮬레이션)
        
        Returns:
            Current voltage in volts
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If voltage reading fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            await asyncio.sleep(0.02)
            
            if not self._output_enabled:
                return 0.0
            
            # 설정값에 약간의 오차 추가
            voltage_error = random.uniform(-self._voltage_accuracy, self._voltage_accuracy)
            actual_voltage = max(0, self._set_voltage + voltage_error)
            
            logger.debug(f"Mock Power Supply voltage: {actual_voltage:.3f}V")
            return actual_voltage
            
        except Exception as e:
            logger.error(f"Failed to get mock Power Supply voltage: {e}")
            raise HardwareOperationError("mock_power", "get_voltage", str(e))
    
    async def set_current_limit(self, current: float) -> None:
        """
        Set current limit (시뮬레이션)
        
        Args:
            current: Current limit in amperes
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current limit setting fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            # 값 범위 검증
            if not (0 <= current <= self._max_current):
                raise HardwareOperationError("mock_power", "set_current_limit", 
                                           f"Current must be 0-{self._max_current}A, got {current}A")
            
            # 설정 지연 시뮬레이션
            await asyncio.sleep(0.05)
            
            self._set_current = current
            logger.info(f"Mock Power Supply current limit set to: {current}A")
            
        except Exception as e:
            logger.error(f"Failed to set mock Power Supply current limit: {e}")
            raise HardwareOperationError("mock_power", "set_current_limit", str(e))
    
    async def get_current(self) -> float:
        """
        Get current output current (시뮬레이션)
        
        Returns:
            Current in amperes
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If current reading fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            await asyncio.sleep(0.02)
            
            if not self._output_enabled:
                return 0.0
            
            # 설정값에 약간의 오차 추가
            current_error = random.uniform(-self._current_accuracy, self._current_accuracy)
            actual_current = max(0, self._set_current + current_error)
            
            logger.debug(f"Mock Power Supply current: {actual_current:.3f}A")
            return actual_current
            
        except Exception as e:
            logger.error(f"Failed to get mock Power Supply current: {e}")
            raise HardwareOperationError("mock_power", "get_current", str(e))
    
    async def enable_output(self) -> None:
        """
        Enable power output (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If output enabling fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            await asyncio.sleep(0.05)
            
            self._output_enabled = True
            logger.info("Mock Power Supply output enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable mock Power Supply output: {e}")
            raise HardwareOperationError("mock_power", "enable_output", str(e))
    
    async def disable_output(self) -> None:
        """
        Disable power output (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If output disabling fails
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        try:
            await asyncio.sleep(0.05)
            
            self._output_enabled = False
            logger.info("Mock Power Supply output disabled")
            
        except Exception as e:
            logger.error(f"Failed to disable mock Power Supply output: {e}")
            raise HardwareOperationError("mock_power", "disable_output", str(e))
    
    async def is_output_enabled(self) -> bool:
        """
        Check if power output is enabled (시뮬레이션)
        
        Returns:
            True if output is enabled, False otherwise
            
        Raises:
            HardwareConnectionError: If not connected
        """
        if not self._is_connected:
            raise HardwareConnectionError("mock_power", "Power Supply is not connected")
        
        return self._output_enabled
    
    
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
                status['measured_voltage'] = await self.get_voltage()
                status['measured_current'] = await self.get_current()
                status['output_enabled'] = await self.is_output_enabled()
                status['last_error'] = None
            except Exception as e:
                status['measured_voltage'] = None
                status['measured_current'] = None
                status['output_enabled'] = None
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