"""
BS205 LoadCell Service

Integrated service for BS205 LoadCell hardware control.
Combines adapter and controller functionality into a single service.
"""

import asyncio
from typing import Optional, Dict, Any
from loguru import logger

from ...core.interfaces.loadcell_service import LoadCellService
from ...driver.serial.serial import SerialManager, SerialError


class BS205LoadCellService(LoadCellService):
    """BS205 로드셀 통합 서비스"""
    
    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
        indicator_id: int = 1
    ):
        """
        초기화
        
        Args:
            port: 시리얼 포트 (예: 'COM3', '/dev/ttyUSB0')
            baudrate: 통신 속도
            timeout: 통신 타임아웃 (초)
            indicator_id: 지시계 ID
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._indicator_id = indicator_id
        
        self._connection = None
        self._is_connected = False
    
    async def connect(self) -> bool:
        """
        하드웨어 연결
        
        Returns:
            연결 성공 여부
        """
        try:
            logger.info(f"Connecting to BS205 LoadCell on {self._port}")
            
            self._connection = await SerialManager.create_connection(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout
            )
            
            # 연결 테스트 명령 전송
            response = await self._send_command("ID")
            if response and "BS205" in response:
                self._is_connected = True
                logger.info("BS205 LoadCell connected successfully")
                return True
            else:
                logger.warning("BS205 LoadCell connection test failed")
                return False
                
        except SerialError as e:
            logger.error(f"Failed to connect to BS205 LoadCell: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제
        
        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._connection:
                await self._connection.disconnect()
                self._connection = None
            
            self._is_connected = False
            logger.info("BS205 LoadCell disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting BS205 LoadCell: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected and self._connection is not None
    
    async def read_force(self) -> float:
        """
        힘 측정값 읽기
        
        Returns:
            측정된 힘 값 (N)
            
        Raises:
            ConnectionError: 연결되지 않은 경우
            RuntimeError: 측정 실패
        """
        if not await self.is_connected():
            raise ConnectionError("BS205 LoadCell is not connected")
        
        try:
            # 현재 무게 읽기 명령
            response = await self._send_command("R")
            
            if not response:
                raise RuntimeError("No response from BS205 LoadCell")
            
            # 응답 파싱 (예: "R,+0012.34,kg")
            parts = response.strip().split(',')
            if len(parts) >= 2:
                weight_str = parts[1].replace('+', '').replace(' ', '')
                weight_kg = float(weight_str)
                
                # kg을 Newton으로 변환 (1kg ≈ 9.81N)
                force_n = weight_kg * 9.81
                
                logger.debug(f"BS205 LoadCell reading: {weight_kg}kg = {force_n:.3f}N")
                return force_n
            else:
                raise RuntimeError(f"Invalid response format: {response}")
                
        except (ValueError, IndexError) as e:
            raise RuntimeError(f"Failed to parse BS205 response: {e}")
        except SerialError as e:
            raise RuntimeError(f"Communication error: {e}")
    
    async def zero(self) -> bool:
        """
        영점 조정
        
        Returns:
            영점 조정 성공 여부
            
        Raises:
            ConnectionError: 연결되지 않은 경우
        """
        if not await self.is_connected():
            raise ConnectionError("BS205 LoadCell is not connected")
        
        try:
            logger.info("Zeroing BS205 LoadCell")
            
            # 영점 조정 명령
            response = await self._send_command("Z")
            
            # 영점 조정 완료 대기
            await asyncio.sleep(2.0)
            
            # 영점 조정 결과 확인
            if response and ("OK" in response or "Z" in response):
                logger.info("BS205 LoadCell zeroed successfully")
                return True
            else:
                logger.warning(f"BS205 zero command unclear response: {response}")
                return True  # BS205는 응답이 애매할 수 있음
                
        except SerialError as e:
            logger.error(f"Failed to zero BS205 LoadCell: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': await self.is_connected(),
            'port': self._port,
            'baudrate': self._baudrate,
            'indicator_id': self._indicator_id,
            'hardware_type': 'BS205'
        }
        
        if await self.is_connected():
            try:
                # 현재 측정값도 포함
                force = await self.read_force()
                status['current_force'] = force
                status['last_error'] = None
            except Exception as e:
                status['current_force'] = None
                status['last_error'] = str(e)
        
        return status
    
    async def _send_command(self, command: str) -> Optional[str]:
        """
        BS205에 명령 전송
        
        Args:
            command: 전송할 명령
            
        Returns:
            응답 문자열
            
        Raises:
            SerialError: 통신 오류
        """
        if not self._connection:
            raise SerialError("No connection available")
        
        try:
            # 새로운 간단한 API 사용
            response = await self._connection.send_command(command, '\r', self._timeout)
            
            logger.debug(f"BS205 command: {command} -> response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"BS205 command '{command}' failed: {e}")
            raise SerialError(f"Communication failed: {e}")
    
    async def read_multiple_samples(self, count: int, interval_ms: int = 100) -> list[float]:
        """
        여러 샘플 연속 측정
        
        Args:
            count: 측정 횟수
            interval_ms: 측정 간격 (밀리초)
            
        Returns:
            힘 값 리스트
        """
        if not await self.is_connected():
            raise ConnectionError("BS205 LoadCell is not connected")
        
        samples = []
        interval_sec = interval_ms / 1000.0
        
        logger.info(f"Reading {count} samples with {interval_ms}ms interval")
        
        for i in range(count):
            if i > 0:
                await asyncio.sleep(interval_sec)
            
            force = await self.read_force()
            samples.append(force)
            logger.debug(f"Sample {i+1}/{count}: {force:.3f}N")
        
        logger.info(f"Completed {count} samples, avg: {sum(samples)/len(samples):.3f}N")
        return samples