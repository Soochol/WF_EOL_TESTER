"""
Mock MCU Service

Mock implementation for testing and development without real hardware.
Simulates LMA MCU behavior for testing purposes.
"""

import asyncio
import random
from typing import Dict, Any
from loguru import logger

from application.interfaces.mcu import MCUService
from domain.exceptions import HardwareConnectionError, HardwareOperationError
from typing import Optional
from enum import Enum

class TestMode(Enum):
    """테스트 모드"""
    MODE_1 = "mode_1"
    MODE_2 = "mode_2"
    MODE_3 = "mode_3"

class MCUStatus(Enum):
    """MCU 상태"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


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
    
    async def connect(self) -> None:
        """
        하드웨어 연결 (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If connection fails
        """
        try:
            logger.info("Connecting to Mock MCU")
            
            # Simulate connection delay
            await asyncio.sleep(self._response_delay)
            
            # 95% 확률로 성공
            if random.random() <= 0.05:
                raise Exception("Simulated connection failure")
            
            # Start temperature simulation task
            self._temperature_task = asyncio.create_task(self._simulate_temperature())
            
            self._is_connected = True
            logger.info("Mock MCU connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Mock MCU: {e}")
            self._is_connected = False
            raise HardwareConnectionError("mock_mcu", str(e))
    
    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제 (시뮬레이션)
        
        Raises:
            HardwareOperationError: If disconnection fails
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
            
        except Exception as e:
            logger.error(f"Error disconnecting Mock MCU: {e}")
            raise HardwareOperationError("mock_mcu", "disconnect", str(e))
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def set_temperature_control(self, enabled: bool, target_temp: Optional[float] = None) -> None:
        """
        Enable/disable temperature control (시뮬레이션)
        
        Args:
            enabled: Whether to enable temperature control
            target_temp: Target temperature in Celsius (if enabling)
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If temperature control setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            if enabled:
                if target_temp is None:
                    raise HardwareOperationError("mock_mcu", "set_temperature_control", 
                                               "Target temperature required when enabling")
                
                if not (-40.0 <= target_temp <= 150.0):
                    raise HardwareOperationError("mock_mcu", "set_temperature_control", 
                                               f"Temperature must be -40°C to 150°C, got {target_temp}°C")
                
                self._target_temperature = target_temp
                
                # Determine heating/cooling mode
                if target_temp > self._current_temperature:
                    self._heating_enabled = True
                    self._cooling_enabled = False
                    self._mcu_status = MCUStatus.RUNNING
                elif target_temp < self._current_temperature:
                    self._heating_enabled = False
                    self._cooling_enabled = True
                    self._mcu_status = MCUStatus.RUNNING
                else:
                    self._heating_enabled = False
                    self._cooling_enabled = False
                    self._mcu_status = MCUStatus.RUNNING
                
                logger.info(f"Mock MCU temperature control enabled, target: {target_temp}°C")
                
            else:
                self._heating_enabled = False
                self._cooling_enabled = False
                self._mcu_status = MCUStatus.IDLE
                logger.info("Mock MCU temperature control disabled")
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU temperature control: {e}")
            raise HardwareOperationError("mock_mcu", "set_temperature_control", str(e))
    
    async def get_temperature(self) -> float:
        """
        Get current temperature reading (시뮬레이션)
        
        Returns:
            Current temperature in Celsius
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If temperature reading fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
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
            raise HardwareOperationError("mock_mcu", "get_temperature", str(e))
    
    async def set_test_mode(self, mode: TestMode) -> None:
        """
        테스트 모드 설정 (시뮬레이션)
        
        Args:
            mode: 테스트 모드
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If test mode setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._current_test_mode = mode
            logger.info(f"Mock MCU test mode set to {mode.name}")
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU test mode: {e}")
            raise HardwareOperationError("mock_mcu", "set_test_mode", str(e))
    
    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회
        
        Returns:
            현재 테스트 모드
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        return self._current_test_mode
    
    async def boot_complete(self) -> None:
        """
        Signal MCU that boot process is complete (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If boot complete signal fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            logger.info("Mock MCU: Sending boot complete signal...")
            
            # 부팅 완료 신호 시뮬레이션 (1-3초)
            boot_time = random.uniform(1.0, 3.0)
            await asyncio.sleep(boot_time)
            
            self._mcu_status = MCUStatus.IDLE
            logger.info(f"Mock MCU: Boot complete signal sent after {boot_time:.1f}s")
            
        except Exception as e:
            logger.error(f"Mock MCU boot complete failed: {e}")
            raise HardwareOperationError("mock_mcu", "boot_complete", str(e))
    
    async def reset(self) -> None:
        """
        Reset the MCU (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If reset fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            logger.info("Mock MCU: Resetting...")
            
            # 리셋 시뮬레이션
            await asyncio.sleep(self._response_delay * 2)
            
            # 상태 초기화
            self._current_temperature = self._initial_temperature
            self._target_temperature = self._initial_temperature
            self._current_test_mode = TestMode.MODE_1
            self._current_fan_speed = 50.0
            self._mcu_status = MCUStatus.IDLE
            self._heating_enabled = False
            self._cooling_enabled = False
            
            logger.info("Mock MCU reset completed")
            
        except Exception as e:
            logger.error(f"Mock MCU reset failed: {e}")
            raise HardwareOperationError("mock_mcu", "reset", str(e))
    
    async def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send command to MCU (시뮬레이션)
        
        Args:
            command: Command string to send
            data: Optional data payload
            
        Returns:
            Response from MCU as dictionary
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If command sending fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            logger.info(f"Mock MCU: Sending command '{command}' with data: {data}")
            
            # 명령어 처리 지연
            await asyncio.sleep(self._response_delay)
            
            # Mock response based on command
            response = {
                "status": "success",
                "command": command,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            if command == "get_temp":
                response["temperature"] = await self.get_temperature()
            elif command == "get_status":
                response["mcu_status"] = self._mcu_status.value
            elif command == "set_fan":
                if data and "speed" in data:
                    self._current_fan_speed = data["speed"]
                    response["fan_speed"] = self._current_fan_speed
            
            logger.debug(f"Mock MCU command response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Mock MCU command failed: {e}")
            raise HardwareOperationError("mock_mcu", "send_command", str(e))
    
    async def set_fan_speed(self, speed_percent: float) -> None:
        """
        팬 속도 설정 (시뮬레이션)
        
        Args:
            speed_percent: 팬 속도 (0-100%)
            
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If fan speed setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        if not (0 <= speed_percent <= 100):
            raise HardwareOperationError("mock_mcu", "set_fan_speed", 
                                       f"Fan speed must be 0-100%, got {speed_percent}%")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._current_fan_speed = speed_percent
            logger.info(f"Mock MCU fan speed set to {speed_percent}%")
            
        except Exception as e:
            logger.error(f"Failed to set Mock MCU fan speed: {e}")
            raise HardwareOperationError("mock_mcu", "set_fan_speed", str(e))
    
    async def get_fan_speed(self) -> float:
        """
        현재 팬 속도 조회
        
        Returns:
            현재 팬 속도 (0-100%)
        """
        if not await self.is_connected():
            raise ConnectionError("Mock MCU is not connected")
        
        return self._current_fan_speed
    
    async def start_heating(self) -> None:
        """
        가열 시작 (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If heating start fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = True
            self._cooling_enabled = False
            self._mcu_status = MCUStatus.RUNNING
            
            logger.info("Mock MCU heating started")
            
        except Exception as e:
            logger.error(f"Failed to start Mock MCU heating: {e}")
            raise HardwareOperationError("mock_mcu", "start_heating", str(e))
    
    async def start_cooling(self) -> None:
        """
        냉각 시작 (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If cooling start fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = False
            self._cooling_enabled = True
            self._mcu_status = MCUStatus.RUNNING
            
            logger.info("Mock MCU cooling started")
            
        except Exception as e:
            logger.error(f"Failed to start Mock MCU cooling: {e}")
            raise HardwareOperationError("mock_mcu", "start_cooling", str(e))
    
    async def stop_temperature_control(self) -> None:
        """
        온도 제어 중지 (시뮬레이션)
        
        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If temperature control stop fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")
        
        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)
            
            self._heating_enabled = False
            self._cooling_enabled = False
            self._mcu_status = MCUStatus.IDLE
            
            logger.info("Mock MCU temperature control stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop Mock MCU temperature control: {e}")
            raise HardwareOperationError("mock_mcu", "stop_temperature_control", str(e))
    
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
                            self._mcu_status = MCUStatus.IDLE
                            
                elif self._cooling_enabled:
                    # Simulate cooling towards target
                    if self._current_temperature > self._target_temperature:
                        temp_diff = self._current_temperature - self._target_temperature
                        change_rate = min(self._temperature_drift_rate, temp_diff * 0.1)
                        self._current_temperature -= change_rate
                        
                        # Check if target reached
                        if abs(self._current_temperature - self._target_temperature) < 0.5:
                            self._mcu_status = MCUStatus.IDLE
                            
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