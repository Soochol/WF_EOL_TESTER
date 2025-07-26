"""
Mock MCU Service

Mock implementation for testing and development without real hardware.
Simulates LMA MCU behavior for testing purposes.
"""

import asyncio
import random
from typing import Dict, Any
from loguru import logger

from application.interfaces.mcu import MCUService, TestMode, MCUStatus


class MockMCUAdapter(MCUService):
    """Mock MCU 서비스 (테스트용)"""
    
    def __init__(
        self,
        initial_temperature: float = 25.0,
        temperature_drift_rate: float = 0.1,
        response_delay: float = 0.1
    ):
        """
        초기화
        
        Args:
            initial_temperature: 초기 온도 (°C)
            temperature_drift_rate: 온도 변화율 (°C/s)
            response_delay: 응답 지연 시간 (초)
        """
        self._initial_temperature = initial_temperature
        self._temperature_drift_rate = temperature_drift_rate
        self._response_delay = response_delay
        
        self._is_connected = False
        self._current_temperature = initial_temperature
        self._target_temperature = initial_temperature
        self._current_test_mode = TestMode.MODE_1
        self._current_fan_speed = 50.0  # percentage
        self._mcu_status = MCUStatus.IDLE
        
        # Temperature simulation
        self._temperature_task = None
        self._heating_enabled = False
        self._cooling_enabled = False
    
    async def connect(self) -> bool:
        """
        하드웨어 연결 (시뮬레이션)
        
        Returns:
            연결 성공 여부
        """
        try:
            logger.info("Connecting to Mock MCU")
            
            # Simulate connection delay
            await asyncio.sleep(self._response_delay)
            
            # Start temperature simulation task
            self._temperature_task = asyncio.create_task(self._simulate_temperature())
            
            self._is_connected = True
            logger.info("Mock MCU connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Mock MCU: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제 (시뮬레이션)
        
        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._temperature_task and not self._temperature_task.done():
                self._temperature_task.cancel()
                try:
                    await self._temperature_task
                except asyncio.CancelledError:
                    pass
            
            self._is_connected = False
            logger.info("Mock MCU disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting Mock MCU: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def set_temperature(self, target_temp: float) -> bool:
        """
        목표 온도 설정 (시뮬레이션)
        
        Args:
            target_temp: 목표 온도 (°C)
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        if not (-40.0 <= target_temp <= 150.0):
            raise ValueError(f"Temperature must be -40°C to 150°C, got {target_temp}°C")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._target_temperature = target_temp
            
            # Determine heating/cooling mode
            if target_temp > self._current_temperature:
                self._heating_enabled = True
                self._cooling_enabled = False
                self._mcu_status = MCUStatus.HEATING
            elif target_temp < self._current_temperature:
                self._heating_enabled = False
                self._cooling_enabled = True
                self._mcu_status = MCUStatus.COOLING
            else:
                self._heating_enabled = False
                self._cooling_enabled = False
                self._mcu_status = MCUStatus.HOLDING
            
            logger.info(f"Mock MCU target temperature set to {target_temp}°C")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU temperature: {e}")
            return False
    
    async def get_temperature(self) -> float:
        """
        현재 온도 측정 (시뮬레이션)
        
        Returns:
            현재 온도 (°C)
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            # Add small random noise to simulate sensor readings
            noise = random.uniform(-0.1, 0.1)
            measured_temp = self._current_temperature + noise
            
            logger.debug(f"Mock MCU temperature: {measured_temp:.1f}°C")
            return measured_temp
            
        except Exception as e:
            logger.error(f"Failed to get Mock MCU temperature: {e}")
            raise RuntimeError(f"Temperature measurement failed: {e}")
    
    async def set_test_mode(self, mode: TestMode) -> bool:
        """
        테스트 모드 설정 (시뮬레이션)
        
        Args:
            mode: 테스트 모드
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._current_test_mode = mode
            logger.info(f"Mock MCU test mode set to {mode.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU test mode: {e}")
            return False
    
    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회
        
        Returns:
            현재 테스트 모드
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        return self._current_test_mode
    
    async def wait_for_boot_complete(self) -> None:
        """
        MCU 부팅 완료 신호 대기 (시뮬레이션)
        
        Mock 환경에서는 짧은 지연 후 부팅 완료로 처리
        
        Raises:
            ConnectionError: 연결되지 않은 경우
            RuntimeError: 부팅 완료 타임아웃 (시뮬레이션)
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        logger.info("Mock MCU: Simulating boot complete wait...")
        
        # 실제 하드웨어 부팅 시간 시뮬레이션 (1-3초)
        boot_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(boot_time)
        
        logger.info(f"Mock MCU: Boot complete after {boot_time:.1f}s")
    
    async def set_fan_speed(self, speed_percent: float) -> bool:
        """
        팬 속도 설정 (시뮬레이션)
        
        Args:
            speed_percent: 팬 속도 (0-100%)
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        if not (0 <= speed_percent <= 100):
            raise ValueError(f"Fan speed must be 0-100%, got {speed_percent}%")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._current_fan_speed = speed_percent
            logger.info(f"Mock MCU fan speed set to {speed_percent}%")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU fan speed: {e}")
            return False
    
    async def get_fan_speed(self) -> float:
        """
        현재 팬 속도 조회
        
        Returns:
            현재 팬 속도 (0-100%)
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        return self._current_fan_speed
    
    async def start_heating(self) -> bool:
        """
        가열 시작 (시뮬레이션)
        
        Returns:
            시작 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = True
            self._cooling_enabled = False
            self._mcu_status = MCUStatus.HEATING
            
            logger.info("Mock MCU heating started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Mock MCU heating: {e}")
            return False
    
    async def start_cooling(self) -> bool:
        """
        냉각 시작 (시뮬레이션)
        
        Returns:
            시작 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = False
            self._cooling_enabled = True
            self._mcu_status = MCUStatus.COOLING
            
            logger.info("Mock MCU cooling started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Mock MCU cooling: {e}")
            return False
    
    async def stop_temperature_control(self) -> bool:
        """
        온도 제어 중지 (시뮬레이션)
        
        Returns:
            중지 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = False
            self._cooling_enabled = False
            self._mcu_status = MCUStatus.IDLE
            
            logger.info("Mock MCU temperature control stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop Mock MCU temperature control: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': await self.is_connected(),
            'current_temperature': self._current_temperature,
            'target_temperature': self._target_temperature,
            'test_mode': self._current_test_mode.name,
            'fan_speed': self._current_fan_speed,
            'mcu_status': self._mcu_status.name,
            'heating_enabled': self._heating_enabled,
            'cooling_enabled': self._cooling_enabled,
            'hardware_type': 'Mock MCU',
            'last_error': None
        }
        
        return status
    
    # Private helper methods
    
    async def _simulate_temperature(self):
        """Background task to simulate temperature changes"""
        try:
            while self._is_connected:
                await asyncio.sleep(1.0)  # Update every second
                
                if self._heating_enabled:
                    # Simulate heating towards target
                    if self._current_temperature < self._target_temperature:
                        temp_diff = self._target_temperature - self._current_temperature
                        change_rate = min(self._temperature_drift_rate, temp_diff * 0.1)
                        self._current_temperature += change_rate
                        
                        # Check if target reached
                        if abs(self._current_temperature - self._target_temperature) < 0.5:
                            self._mcu_status = MCUStatus.HOLDING
                            
                elif self._cooling_enabled:
                    # Simulate cooling towards target
                    if self._current_temperature > self._target_temperature:
                        temp_diff = self._current_temperature - self._target_temperature
                        change_rate = min(self._temperature_drift_rate, temp_diff * 0.1)
                        self._current_temperature -= change_rate
                        
                        # Check if target reached
                        if abs(self._current_temperature - self._target_temperature) < 0.5:
                            self._mcu_status = MCUStatus.HOLDING
                            
                else:
                    # Natural temperature drift towards ambient
                    ambient_temp = self._initial_temperature
                    if abs(self._current_temperature - ambient_temp) > 0.1:
                        if self._current_temperature > ambient_temp:
                            self._current_temperature -= self._temperature_drift_rate * 0.1
                        else:
                            self._current_temperature += self._temperature_drift_rate * 0.1
                
        except asyncio.CancelledError:
            logger.debug("Mock MCU temperature simulation cancelled")
        except Exception as e:
            logger.error(f"Mock MCU temperature simulation error: {e}")