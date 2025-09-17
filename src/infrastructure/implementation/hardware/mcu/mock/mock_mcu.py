"""
Mock MCU Service

Mock implementation for testing and development without real hardware.
Simulates LMA MCU behavior for testing purposes.
"""

import random
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncio
from loguru import logger

from application.interfaces.hardware.mcu import MCUService
from domain.exceptions import (
    HardwareConnectionError,
    HardwareOperationError,
)
from domain.enums.mcu_enums import MCUStatus, TestMode


class MockMCU(MCUService):
    """Mock MCU 서비스 (테스트용)"""

    def __init__(
        self,
        port: str = "",
        baudrate: int = 9600,
        timeout: float = 1.0,
        bytesize: int = 8,
        stopbits: int = 1,
        parity: Optional[str] = None,
    ):
        """
        초기화

        Args:
            port: Serial port (e.g., "COM4")
            baudrate: Baud rate (e.g., 115200)
            timeout: Connection timeout in seconds
            bytesize: Data bits
            stopbits: Stop bits
            parity: Parity setting
        """
        # State initialization
        self._is_connected = False
        self._current_test_mode = TestMode.MODE_1
        self._mcu_status = MCUStatus.IDLE

        # Connection parameters (injected at creation time)
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._bytesize = bytesize
        self._stopbits = stopbits
        self._parity = parity

        # Mock operational defaults
        self._temperature = 25.0
        self._fan_speed = 50.0
        self._temperature_drift_rate = 0.1
        self._response_delay = 0.1
        self._connection_delay = 0.1
        self._max_temperature = 150.0
        self._min_temperature = -40.0
        self._max_fan_speed = 100.0

        # Initialize temperature values
        self._initial_temperature = self._temperature
        self._current_temperature = self._initial_temperature
        self._target_temperature = self._initial_temperature
        self._upper_temperature_limit = self._max_temperature
        self._current_fan_speed = self._fan_speed

        # Temperature simulation
        self._temperature_task: Optional[asyncio.Task[None]] = None
        self._heating_enabled = False
        self._cooling_enabled = False
        
        # Verification stability - disable drift during temperature verification
        self._verification_mode = False
        
        # Timing data storage for heating/cooling tests
        self._heating_timing_history: List[Dict[str, Any]] = []
        self._cooling_timing_history: List[Dict[str, Any]] = []


    async def connect(self) -> None:
        """
        하드웨어 연결 (시뮬레이션)

        Raises:
            HardwareConnectionError: If connection fails
        """

        try:
            logger.info(f"Connecting to Mock MCU on {self._port} at {self._baudrate} baud")

            # Simulate connection delay
            await asyncio.sleep(self._connection_delay)

            # 테스트 환경에서는 항상 성공하도록 변경 (원래는 95% 확률)
            # if random.random() <= 0.05:
            #     raise HardwareConnectionError("mock_mcu", "Simulated connection failure")

            # Start temperature simulation task
            self._temperature_task = asyncio.create_task(self._simulate_temperature())

            self._is_connected = True
            logger.info("Mock MCU connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Mock MCU: {e}")
            self._is_connected = False
            raise HardwareConnectionError("mock_mcu", str(e)) from e

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
                    ...

            self._is_connected = False
            logger.info("Mock MCU disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting Mock MCU: {e}")
            raise HardwareOperationError("mock_mcu", "disconnect", str(e)) from e

    async def is_connected(self) -> bool:
        """
        연결 상태 확인

        Returns:
            연결 상태
        """
        return self._is_connected

    async def set_operating_temperature(self, target_temp: float) -> None:
        """
        Set operating temperature for the MCU (시뮬레이션)

        Args:
            target_temp: Operating temperature in Celsius

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If operating temperature setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)

            self._target_temperature = target_temp
            # In mock mode, immediately set temperature to target for fast verification
            self._current_temperature = target_temp

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
            
            # Enable verification mode for stable temperature readings
            self._verification_mode = True

            logger.info(f"Mock MCU target temperature set to {target_temp}°C (verification_mode enabled)")

        except Exception as e:
            logger.error(f"Failed to set Mock MCU temperature: {e}")
            raise HardwareOperationError("mock_mcu", "set_temperature", str(e)) from e

    async def set_upper_temperature(self, upper_temp: float) -> None:
        """
        Set upper temperature limit for the MCU (시뮬레이션)

        Args:
            upper_temp: Upper temperature limit in Celsius

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If upper temperature setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)

            if not self._min_temperature <= upper_temp <= self._max_temperature:
                raise HardwareOperationError(
                    "mock_mcu",
                    "set_upper_temperature",
                    f"Upper temperature must be {self._min_temperature}°C to {self._max_temperature}°C, got {upper_temp}°C",
                )

            # Store upper temperature limit (for validation purposes)
            self._upper_temperature_limit = upper_temp
            logger.info(f"Mock MCU upper temperature limit set to {upper_temp}°C")

        except Exception as e:
            logger.error(f"Failed to set Mock MCU upper temperature: {e}")
            raise HardwareOperationError("mock_mcu", "set_upper_temperature", str(e)) from e

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

            # In verification mode, return exact temperature with minimal noise for reliable testing
            if self._verification_mode:
                # Very small noise for realistic simulation but within tolerance
                noise = random.uniform(-0.05, 0.05)
                measured_temp: float = self._current_temperature + noise
            else:
                # Normal noise for regular simulation
                noise = random.uniform(-0.1, 0.1)
                measured_temp: float = self._current_temperature + noise

            logger.debug(f"Mock MCU temperature: {measured_temp:.1f}°C (verification_mode: {self._verification_mode})")
            return measured_temp

        except Exception as e:
            logger.error(f"Failed to get Mock MCU temperature: {e}")
            raise HardwareOperationError("mock_mcu", "get_temperature", str(e)) from e

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
            raise HardwareOperationError("mock_mcu", "set_test_mode", str(e)) from e

    async def get_test_mode(self) -> TestMode:
        """
        현재 테스트 모드 조회

        Returns:
            현재 테스트 모드
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        return self._current_test_mode

    async def wait_boot_complete(self) -> None:
        """
        Wait for MCU boot process to complete (시뮬레이션)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If boot waiting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        try:
            logger.info("Mock MCU: Waiting for boot complete...")

            # 부팅 완료 대기 시뮬레이션 (1-3초)
            boot_time = random.uniform(1.0, 3.0)
            await asyncio.sleep(boot_time)

            self._mcu_status = MCUStatus.IDLE
            logger.info(f"Mock MCU: Boot complete after {boot_time:.1f}s")

        except asyncio.CancelledError:
            # Re-raise CancelledError to preserve KeyboardInterrupt behavior
            raise
        except Exception as e:
            logger.error(f"Mock MCU wait boot complete failed: {e}")
            raise HardwareOperationError("mock_mcu", "wait_boot_complete", str(e)) from e

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
            self._current_fan_speed = 5.0  # Reset to level 5 (middle range)
            self._mcu_status = MCUStatus.IDLE
            self._heating_enabled = False
            self._cooling_enabled = False
            self._verification_mode = False  # Reset verification mode

            logger.info("Mock MCU reset completed")

        except Exception as e:
            logger.error(f"Mock MCU reset failed: {e}")
            raise HardwareOperationError("mock_mcu", "reset", str(e)) from e

    async def send_command(
        self,
        command: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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
                "timestamp": asyncio.get_event_loop().time(),
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
            raise HardwareOperationError("mock_mcu", "send_command", str(e)) from e

    async def set_fan_speed(self, fan_level: int) -> None:
        """
        팬 속도 설정 (시뮬레이션)

        Args:
            fan_level: 팬 레벨 (1-10)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If fan speed setting fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)

            self._current_fan_speed = float(fan_level)
            logger.info(f"Mock MCU fan speed set to level {fan_level}")

        except Exception as e:
            logger.error(f"Failed to set Mock MCU fan speed: {e}")
            raise HardwareOperationError("mock_mcu", "set_fan_speed", str(e)) from e

    async def get_fan_speed(self) -> int:
        """
        현재 팬 속도 조회

        Returns:
            현재 팬 레벨 (1-10)
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        return int(self._current_fan_speed)

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
            raise HardwareOperationError("mock_mcu", "start_heating", str(e)) from e

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
            raise HardwareOperationError("mock_mcu", "start_cooling", str(e)) from e

    async def start_standby_heating(
        self,
        operating_temp: float,
        standby_temp: float,
        hold_time_ms: int = 10000,
    ) -> None:
        """
        대기 가열 시작 (시뮬레이션)

        Args:
            operating_temp: 동작온도 (°C)
            standby_temp: 대기온도 (°C)
            hold_time_ms: 유지시간 (밀리초)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If standby heating start fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        # 매개변수 검증
        if not self._min_temperature <= operating_temp <= self._max_temperature:
            raise HardwareOperationError(
                "mock_mcu",
                "start_standby_heating",
                f"Operating temperature must be {self._min_temperature}°C to {self._max_temperature}°C, got {operating_temp}°C",
            )

        if not self._min_temperature <= standby_temp <= self._max_temperature:
            raise HardwareOperationError(
                "mock_mcu",
                "start_standby_heating",
                f"Standby temperature must be {self._min_temperature}°C to {self._max_temperature}°C, got {standby_temp}°C",
            )

        if hold_time_ms < 0:
            raise HardwareOperationError(
                "mock_mcu",
                "start_standby_heating",
                f"Hold time must be non-negative, got {hold_time_ms}ms",
            )

        try:

            # Simulate response delay for successful calls
            await asyncio.sleep(self._response_delay)

            # Set target temperatures for simulation
            self._target_temperature = operating_temp
            # In mock mode, immediately set temperature to target for fast verification
            self._current_temperature = operating_temp
            self._heating_enabled = True
            self._cooling_enabled = False
            self._mcu_status = MCUStatus.HEATING
            
            # Enable verification mode for stable temperature readings
            self._verification_mode = True
            
            # Generate mock timing data for heating transition
            mock_heating_data = {
                "transition": f"{standby_temp}°C → {operating_temp}°C",
                "from_temperature": standby_temp,
                "to_temperature": operating_temp,
                "ack_duration_ms": random.uniform(80, 120),  # Mock ACK time
                "total_duration_ms": random.uniform(1200, 1800),  # Mock total time
                "timestamp": datetime.now().isoformat(),
                "attempt_number": 1,
                "total_attempts": 1,
            }
            self._heating_timing_history.append(mock_heating_data)

            logger.info(
                f"Mock MCU standby heating started - op:{operating_temp}°C, "
                f"standby:{standby_temp}°C, hold:{hold_time_ms}ms (verification_mode enabled)"
            )
            logger.debug(f"Mock heating timing data added: {mock_heating_data}")

        except asyncio.TimeoutError:
            # Re-raise timeout error to trigger retry logic
            raise
        except Exception as e:
            logger.error(f"Failed to start Mock MCU standby heating: {e}")
            raise HardwareOperationError("mock_mcu", "start_standby_heating", str(e)) from e

    async def start_standby_cooling(self) -> None:
        """
        대기 냉각 시작 (시뮬레이션)

        Raises:
            HardwareConnectionError: If not connected
            HardwareOperationError: If standby cooling start fails
        """
        if not await self.is_connected():
            raise HardwareConnectionError("mock_mcu", "MCU is not connected")

        try:
            # Simulate response delay
            await asyncio.sleep(self._response_delay)

            self._heating_enabled = False
            self._cooling_enabled = True
            self._mcu_status = MCUStatus.RUNNING
            
            # In mock mode, immediately set temperature to standby temperature (38.0°C)
            # This should match the calculated_standby_temp from the hardware facade
            standby_temp = 38.0  # Default standby temperature for cooling verification
            self._current_temperature = standby_temp
            self._target_temperature = standby_temp
            
            # Enable verification mode for stable temperature readings
            self._verification_mode = True
            
            # Generate mock timing data for cooling transition
            # Assuming cooling from current temperature to standby temperature
            from_temp = self._current_temperature if self._current_temperature > standby_temp else 95.0  # Mock from temperature
            mock_cooling_data = {
                "transition": f"{from_temp}°C → {standby_temp}°C",
                "from_temperature": from_temp,
                "to_temperature": standby_temp,
                "ack_duration_ms": random.uniform(70, 110),  # Mock ACK time
                "total_duration_ms": random.uniform(1800, 2500),  # Mock total time (cooling usually takes longer)
                "timestamp": datetime.now().isoformat(),
                "attempt_number": 1,
                "total_attempts": 1,
            }
            self._cooling_timing_history.append(mock_cooling_data)

            logger.info(f"Mock MCU standby cooling started - temperature set to {standby_temp}°C (verification_mode enabled)")
            logger.debug(f"Mock cooling timing data added: {mock_cooling_data}")

        except Exception as e:
            logger.error(f"Failed to start Mock MCU standby cooling: {e}")
            raise HardwareOperationError("mock_mcu", "start_standby_cooling", str(e)) from e

    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회

        Returns:
            상태 정보 딕셔너리
        """
        status = {
            "connected": await self.is_connected(),
            "current_temperature": self._current_temperature,
            "target_temperature": self._target_temperature,
            "test_mode": self._current_test_mode.name,
            "fan_speed": self._current_fan_speed,
            "mcu_status": self._mcu_status.name,
            "heating_enabled": self._heating_enabled,
            "cooling_enabled": self._cooling_enabled,
            "hardware_type": "Mock MCU",
            "last_error": None,
        }

        return status

    # Private helper methods

    async def _simulate_temperature(self) -> None:
        """Background task to simulate temperature changes"""
        try:
            while self._is_connected:
                await asyncio.sleep(1.0)  # Update every second

                # Skip simulation if in verification mode (temperature is locked for verification)
                if self._verification_mode:
                    continue

                if self._heating_enabled:
                    # Simulate heating towards target
                    if self._current_temperature < self._target_temperature:
                        temp_diff = self._target_temperature - self._current_temperature
                        change_rate = min(
                            self._temperature_drift_rate,
                            temp_diff * 0.1,
                        )
                        self._current_temperature += change_rate

                        # Check if target reached
                        if abs(self._current_temperature - self._target_temperature) < 0.5:
                            self._mcu_status = MCUStatus.IDLE

                elif self._cooling_enabled:
                    # Simulate cooling towards target
                    if self._current_temperature > self._target_temperature:
                        temp_diff = self._current_temperature - self._target_temperature
                        change_rate = min(
                            self._temperature_drift_rate,
                            temp_diff * 0.1,
                        )
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

    async def set_cooling_temperature(self, target_temp: float) -> None:
        raise NotImplementedError
    
    def disable_verification_mode(self) -> None:
        """Disable verification mode to allow normal temperature simulation"""
        self._verification_mode = False
        logger.debug("Mock MCU verification mode disabled - normal temperature simulation resumed")

    def clear_timing_history(self) -> None:
        """Clear timing history for new test sessions"""
        self._heating_timing_history.clear()
        self._cooling_timing_history.clear()
        logger.debug("Mock MCU timing history cleared")

    def get_all_timing_data(self) -> Dict[str, Any]:
        """Get all heating/cooling timing data"""
        logger.debug(f"Mock MCU returning timing data: {len(self._heating_timing_history)} heating, {len(self._cooling_timing_history)} cooling")
        return {
            "heating_transitions": self._heating_timing_history.copy(),
            "cooling_transitions": self._cooling_timing_history.copy(),
            "total_heating_count": len(self._heating_timing_history),
            "total_cooling_count": len(self._cooling_timing_history),
        }
