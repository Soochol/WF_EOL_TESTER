"""
ODA Power Supply Service

Integrated service for ODA power supply hardware control.
Combines adapter and controller functionality into a single service.
"""

import asyncio
from typing import Optional, Dict, Any
from loguru import logger

from application.interfaces.power import PowerService
from driver.tcp.communication import TCPCommunication
from driver.tcp.exceptions import TCPError


class OdaPowerAdapter(PowerService):
    """ODA 전원 공급 장치 통합 서비스"""
    
    def __init__(
        self,
        host: str,
        port: int = 8080,
        timeout: float = 5.0,
        channel: int = 1
    ):
        """
        초기화
        
        Args:
            host: IP 주소
            port: TCP 포트
            timeout: 통신 타임아웃 (초)
            channel: 출력 채널 번호
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = channel
        
        self._tcp_comm = TCPCommunication(host, port, timeout)
        self._is_connected = False
        self._output_enabled = False
    
    async def connect(self) -> bool:
        """
        하드웨어 연결
        
        Returns:
            연결 성공 여부
        """
        try:
            logger.info(f"Connecting to ODA Power Supply at {self._host}:{self._port}")
            
            await self._tcp_comm.connect()
            
            # 연결 테스트 및 초기화
            response = await self._send_command("*IDN?")
            if response and "ODA" in response:
                self._is_connected = True
                
                # 안전을 위해 출력 비활성화
                await self.enable_output(False)
                
                logger.info("ODA Power Supply connected successfully")
                return True
            else:
                logger.warning("ODA Power Supply identification failed")
                return False
                
        except TCPError as e:
            logger.error(f"Failed to connect to ODA Power Supply: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제
        
        Returns:
            연결 해제 성공 여부
        """
        try:
            # 안전을 위해 출력 비활성화
            if self._is_connected:
                await self.enable_output(False)
            
            await self._tcp_comm.disconnect()
            self._is_connected = False
            self._output_enabled = False
            
            logger.info("ODA Power Supply disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting ODA Power Supply: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected and self._tcp_comm.is_connected()
    
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
            ValueError: 잘못된 값 범위
        """
        if not await self.is_connected():
            raise ConnectionError("ODA Power Supply is not connected")
        
        # 값 범위 검증
        if not (0 <= voltage <= 30):
            raise ValueError(f"Voltage must be 0-30V, got {voltage}V")
        if not (0 <= current <= 5):
            raise ValueError(f"Current must be 0-5A, got {current}A")
        
        try:
            logger.info(f"Setting ODA output: {voltage}V, {current}A")
            
            # 전압 설정
            voltage_response = await self._send_command(f"VOLT {voltage:.3f}")
            
            # 전류 한계 설정
            current_response = await self._send_command(f"CURR {current:.3f}")
            
            # 설정 확인
            if voltage_response is not None and current_response is not None:
                logger.info("ODA output settings applied successfully")
                return True
            else:
                logger.error("Failed to apply ODA output settings")
                return False
                
        except TCPError as e:
            logger.error(f"Failed to set ODA output: {e}")
            return False
    
    async def enable_output(self, enable: bool = True) -> bool:
        """
        출력 활성화/비활성화
        
        Args:
            enable: 활성화 여부
            
        Returns:
            설정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        if not await self.is_connected():
            raise ConnectionError("ODA Power Supply is not connected")
        
        try:
            command = "OUTP ON" if enable else "OUTP OFF"
            response = await self._send_command(command)
            
            if response is not None:
                self._output_enabled = enable
                status = "enabled" if enable else "disabled"
                logger.info(f"ODA output {status}")
                return True
            else:
                logger.error(f"Failed to {'enable' if enable else 'disable'} ODA output")
                return False
                
        except TCPError as e:
            logger.error(f"Failed to control ODA output: {e}")
            return False
    
    async def measure_output(self) -> tuple[float, float]:
        """
        실제 출력 전압/전류 측정
        
        Returns:
            (전압, 전류) 튜플
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            RuntimeError: 측정 실패
        """
        if not await self.is_connected():
            raise ConnectionError("ODA Power Supply is not connected")
        
        try:
            # 전압 측정
            voltage_response = await self._send_command("MEAS:VOLT?")
            # 전류 측정
            current_response = await self._send_command("MEAS:CURR?")
            
            if voltage_response is None or current_response is None:
                raise RuntimeError("Failed to get measurement responses")
            
            voltage = float(voltage_response.strip())
            current = float(current_response.strip())
            
            logger.debug(f"ODA measurements: {voltage:.3f}V, {current:.3f}A")
            return voltage, current
            
        except (ValueError, AttributeError) as e:
            raise RuntimeError(f"Failed to parse ODA measurements: {e}")
        except TCPError as e:
            raise RuntimeError(f"Communication error during measurement: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': await self.is_connected(),
            'host': self._host,
            'port': self._port,
            'channel': self._channel,
            'output_enabled': self._output_enabled,
            'hardware_type': 'ODA'
        }
        
        if await self.is_connected():
            try:
                # 현재 측정값도 포함
                voltage, current = await self.measure_output()
                status['current_voltage'] = voltage
                status['current_current'] = current
                status['last_error'] = None
            except Exception as e:
                status['current_voltage'] = None
                status['current_current'] = None
                status['last_error'] = str(e)
        
        return status
    
    async def _send_command(self, command: str) -> Optional[str]:
        """
        ODA에 명령 전송
        
        Args:
            command: 전송할 명령
            
        Returns:
            응답 문자열
            
        Raises:
            TCPError: 통신 오류
        """
        if not self._tcp_comm.is_connected:
            raise TCPError("No connection available")
        
        try:
            # 명령 전송 및 응답 수신 (SCPI 형식)
            command_with_terminator = f"{command}\n"
            
            # Use query() method for commands that expect responses
            if command.endswith('?'):
                response = await self._tcp_comm.query(command_with_terminator)
            else:
                # For commands that don't expect responses, just send
                await self._tcp_comm.send_command(command_with_terminator)
                response = None
            
            if response:
                response = response.strip()
            
            logger.debug(f"ODA command: {command} -> response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"ODA command '{command}' failed: {e}")
            raise TCPError(f"Communication failed: {e}")
    
    async def set_voltage_only(self, voltage: float) -> bool:
        """
        전압만 설정 (전류는 현재 값 유지)
        
        Args:
            voltage: 출력 전압 (V)
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("ODA Power Supply is not connected")
        
        try:
            response = await self._send_command(f"VOLT {voltage:.3f}")
            return response is not None
        except TCPError as e:
            logger.error(f"Failed to set voltage: {e}")
            return False
    
    async def set_current_limit(self, current: float) -> bool:
        """
        전류 한계만 설정 (전압은 현재 값 유지)
        
        Args:
            current: 전류 한계 (A)
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise ConnectionError("ODA Power Supply is not connected")
        
        try:
            response = await self._send_command(f"CURR {current:.3f}")
            return response is not None
        except TCPError as e:
            logger.error(f"Failed to set current limit: {e}")
            return False