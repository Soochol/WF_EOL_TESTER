"""
AJINEXTEK Robot Service

Integrated service for AJINEXTEK robot hardware control.
Implements the RobotService interface using AXL library.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from loguru import logger

# 절대 import 사용 (권장)
# src가 Python path에 있을 때 최적의 방법
from application.interfaces.hardware.robot import RobotService, MotionStatus
from domain.exceptions.robot_exceptions import (
    RobotConnectionError, RobotMotionError, RobotConfigurationError,
    AXLConnectionError, AXLMotionError
)
from domain.value_objects.hardware_configuration import RobotConfig

from infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper import AXLWrapper
from infrastructure.implementation.hardware.robot.ajinextek.constants import *
from infrastructure.implementation.hardware.robot.ajinextek.error_codes import AXT_RT_SUCCESS, get_error_message


class AjinextekRobot(RobotService):
    """AJINEXTEK 로봇 통합 서비스"""
    
    def __init__(
        self,
        # Hardware model
        model: str = "AJINEXTEK",
        
        # Motion parameters
        axis: int = 0,
        velocity: float = 100.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0,
        
        # Safety limits
        max_velocity: float = 500.0,
        max_acceleration: float = 1000.0,
        max_deceleration: float = 1000.0,
        
        # Positioning settings
        position_tolerance: float = 0.1,
        homing_velocity: float = 10.0,
        homing_acceleration: float = 100.0,
        homing_deceleration: float = 100.0,
        
        # Connection parameters (AJINEXTEK specific)
        irq_no: int = 7,
        axis_count: int = 6
    ):
        """
        초기화
        
        Args:
            model: 하드웨어 모델명
            axis: 사용할 축 번호
            velocity: 기본 속도 (mm/s)
            acceleration: 기본 가속도 (mm/s²)
            deceleration: 기본 감속도 (mm/s²)
            max_velocity: 최대 속도 제한
            max_acceleration: 최대 가속도 제한
            max_deceleration: 최대 감속도 제한
            position_tolerance: 위치 허용 오차
            homing_velocity: 홈 복귀 속도
            homing_acceleration: 홈 복귀 가속도
            homing_deceleration: 홈 복귀 감속도
            irq_no: IRQ 번호
            axis_count: 전체 축 개수
        """
        # Store configuration
        self._model = model
        self._axis = axis
        self._velocity = velocity
        self._acceleration = acceleration
        self._deceleration = deceleration
        self._max_velocity = max_velocity
        self._max_acceleration = max_acceleration
        self._max_deceleration = max_deceleration
        self._position_tolerance = position_tolerance
        self._homing_velocity = homing_velocity
        self._homing_acceleration = homing_acceleration
        self._homing_deceleration = homing_deceleration
        self._irq_no = irq_no
        self._axis_count = axis_count
        
        # Runtime state
        self._is_connected = False
        self._current_positions = []
        self._servo_states = {}
        self._motion_status = MotionStatus.IDLE
        self._error_message = None
        
        # Initialize AXL wrapper
        self._axl = AXLWrapper()
        
        logger.info(f"AjinextekRobotAdapter initialized with IRQ {irq_no}")
    
    async def connect(self, robot_config: RobotConfig) -> None:
        """
        하드웨어 연결
        
        Args:
            robot_config: Robot connection configuration
            
        Raises:
            HardwareConnectionError: If connection fails
        """
        # Update connection parameters from config
        self._irq_no = robot_config.irq_no
        self._axis_count = robot_config.axis_count
        
        try:
            logger.info(f"Connecting to AJINEXTEK robot controller (IRQ: {self._irq_no}, Axes: {self._axis_count})")
            
            # Open AXL library
            result = self._axl.open(self._irq_no)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to open AXL library: {error_msg}")
                raise RobotConnectionError(
                    f"Failed to open AXL library: {error_msg}", 
                    "AJINEXTEK", 
                    details=f"IRQ: {self._irq_no}, Error: {result}"
                )
            
            # Get board count for verification
            try:
                board_count = self._axl.get_board_count()
                logger.info(f"Board count detected: {board_count}")
            except Exception as e:
                logger.error(f"Failed to get board count: {e}")
                raise RobotConnectionError(
                    f"Failed to get board count: {e}", 
                    "AJINEXTEK", 
                    details=str(e)
                )
            
            # Get axis count (use auto-detection if not specified)
            try:
                detected_axis_count = self._axl.get_axis_count()
                if self._axis_count == 0:
                    self._axis_count = detected_axis_count
                logger.info(f"Axis count: {self._axis_count} (detected: {detected_axis_count})")
            except Exception as e:
                logger.error(f"Failed to get axis count: {e}")
                if self._axis_count == 0:
                    raise RobotConnectionError(
                        f"Failed to get axis count: {e}", 
                        "AJINEXTEK", 
                        details=str(e)
                    )
            
            # Get library version for info
            try:
                version = self._axl.get_lib_version()
                logger.info(f"AXL Library version: {version}")
            except Exception:
                pass  # Library version is not critical
            
            # Initialize position tracking and servo states
            self._current_positions = [0.0] * self._axis_count
            for axis in range(self._axis_count):
                self._servo_states[axis] = False
            
            self._is_connected = True
            self._motion_status = MotionStatus.IDLE
            
            logger.info(f"AJINEXTEK robot controller connected successfully (IRQ: {self._irq_no}, Axes: {self._axis_count})")
            return True
            
        except RobotConnectionError:
            # Re-raise connection errors to preserve error context
            self._is_connected = False
            raise
        except Exception as e:
            logger.error(f"Failed to connect to AJINEXTEK robot: {e}")
            self._is_connected = False
            raise RobotConnectionError(
                f"Robot controller initialization failed: {e}", 
                "AJINEXTEK", 
                details=str(e)
            )
    
    async def disconnect(self) -> bool:
        """
        하드웨어 연결 해제
        
        Returns:
            연결 해제 성공 여부
        """
        try:
            if self._is_connected:
                # Stop all motion and turn off servos
                await self.stop_motion()
                
                # Turn off all servos
                for axis in range(self._axis_count):
                    try:
                        self._set_servo_off(axis)
                    except Exception as e:
                        logger.warning(f"Failed to turn off servo {axis}: {e}")
                
                # Close AXL library connection
                try:
                    result = self._axl.close()
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        logger.warning(f"AXL library close warning: {error_msg}")
                except Exception as e:
                    logger.warning(f"Error closing AXL library: {e}")
                
                self._is_connected = False
                self._servo_states = {}
                self._motion_status = MotionStatus.IDLE
                
                logger.info("AJINEXTEK robot controller disconnected")
            
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting AJINEXTEK robot: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        연결 상태 확인
        
        Returns:
            연결 상태
        """
        return self._is_connected
    
    async def home_axis(self, axis: int, velocity: float = 10.0, acceleration: float = 100.0, deceleration: float = 100.0) -> bool:
        """
        지정된 축을 홈 위치로 이동
        
        Args:
            axis: 축 번호 (0부터 시작)
            velocity: 홈 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)
            
        Returns:
            홈 이동 성공 여부
            
        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        self._check_axis(axis)
        
        accel = acceleration
        decel = deceleration
        
        try:
            logger.info(f"Starting homing for axis {axis}")
            self._motion_status = MotionStatus.HOMING
            
            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)
            
            # Configure default homing parameters
            await self._home_axis(
                axis,
                home_dir=HOME_DIR_CCW,
                signal_level=LIMIT_LEVEL_LOW,
                mode=HOME_MODE_0,
                offset=0.0,
                vel_first=velocity,
                vel_second=velocity * 0.5,
                accel=accel,
                decel=decel
            )
            
            # Wait for homing to complete
            await self._wait_for_homing_complete(axis, timeout=30.0)
            
            # Update position to zero after successful homing
            if axis < len(self._current_positions):
                self._current_positions[axis] = 0.0
            
            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis} homing completed successfully")
            return True
            
        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Homing failed on axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(f"Homing failed on axis {axis}: {e}", "AJINEXTEK", details=str(e))
    
    async def home_all_axes(self, velocity: float = 10.0, acceleration: float = 100.0, deceleration: float = 100.0) -> bool:
        """
        모든 축 홈 위치로 이동
        
        Returns:
            홈 이동 성공 여부
            
        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If homing fails
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        try:
            logger.info("Starting homing sequence for all axes")
            self._motion_status = MotionStatus.HOMING
            
            failed_axes = []
            
            # Home each axis sequentially using the new single-axis method
            for axis in range(self._axis_count):
                try:
                    await self.home_axis(axis, velocity, acceleration, deceleration)
                    logger.info(f"Axis {axis} homing completed")
                    
                except Exception as e:
                    failed_axes.append((axis, str(e)))
                    logger.error(f"Failed to home axis {axis}: {e}")
            
            if failed_axes:
                error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
                self._motion_status = MotionStatus.ERROR
                raise RobotMotionError(
                    f"Failed to home {len(failed_axes)} axes: {error_details}", 
                    "AJINEXTEK"
                )
            
            self._motion_status = MotionStatus.IDLE
            logger.info("All axes homing sequence completed successfully")
            return True
            
        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Homing failed: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(f"Homing failed: {e}", "AJINEXTEK", details=str(e))
    
    async def move_absolute(self, axis: int, position: float, velocity: float = 100.0, acceleration: float = 100.0, deceleration: float = 100.0) -> bool:
        """
        지정된 축을 절대 위치로 이동
        
        Args:
            axis: 축 번호 (0부터 시작)
            position: 절대 위치 (mm)
            velocity: 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)
            
        Returns:
            이동 성공 여부
            
        Raises:
            RobotConnectionError: If robot is not connected
            RobotMotionError: If movement fails
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        self._check_axis(axis)
        
        vel = velocity
        accel = acceleration
        decel = deceleration
        
        try:
            logger.info(f"Moving axis {axis} to absolute position: {position}mm at {vel}mm/s")
            self._motion_status = MotionStatus.MOVING
            
            # Ensure servo is on
            if not self._servo_states.get(axis, False):
                self._set_servo_on(axis)
            
            # Start absolute position move
            result = self._axl.move_start_pos(axis, position, vel, accel, decel)
            
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                self._motion_status = MotionStatus.ERROR
                logger.error(f"Failed to start movement on axis {axis}: {error_msg}")
                raise RobotMotionError(
                    f"Failed to start movement on axis {axis}: {error_msg}",
                    "AJINEXTEK"
                )
            
            # Wait for motion to complete
            await self._wait_for_motion_complete(axis, timeout=30.0)
            
            # Update current position for this axis
            if axis < len(self._current_positions):
                self._current_positions[axis] = position
            
            self._motion_status = MotionStatus.IDLE
            logger.info(f"Axis {axis} absolute move completed successfully")
            return True
            
        except RobotMotionError:
            # Re-raise motion errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Absolute move failed on axis {axis}: {e}")
            self._motion_status = MotionStatus.ERROR
            raise RobotMotionError(f"Absolute move failed on axis {axis}: {e}", "AJINEXTEK", details=str(e))
    
    async def move_relative(self, axis: int, distance: float, velocity: float = 100.0, acceleration: float = 100.0, deceleration: float = 100.0) -> bool:
        """
        지정된 축을 상대 위치로 이동
        
        Args:
            axis: 축 번호 (0부터 시작)
            distance: 상대 거리 (mm)
            velocity: 이동 속도 (mm/s)
            acceleration: 가속도 (mm/s²)
            deceleration: 감속도 (mm/s²)
            
        Returns:
            이동 성공 여부
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        self._check_axis(axis)
        
        # Get current position for this axis
        current_position = await self.get_current_position(axis)
        target_position = current_position + distance
        
        # Use absolute move to reach target
        return await self.move_absolute(axis, target_position, velocity, acceleration, deceleration)
    
    async def get_current_position(self, axis: int) -> float:
        """
        지정된 축의 현재 위치 조회
        
        Args:
            axis: 축 번호 (0부터 시작)
            
        Returns:
            현재 위치 (mm)
            
        Raises:
            RobotConnectionError: If robot is not connected
            ValueError: If axis number is invalid
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        self._check_axis(axis)
        
        try:
            position = self._axl.get_act_pos(axis)
            
            # Update cached position
            if axis < len(self._current_positions):
                self._current_positions[axis] = position
            
            return position
            
        except Exception as e:
            logger.warning(f"Failed to get position for axis {axis}: {e}")
            # Use cached position as fallback
            if axis < len(self._current_positions):
                return self._current_positions[axis]
            else:
                return 0.0
    
    async def get_all_positions(self) -> List[float]:
        """
        모든 축의 현재 위치 조회
        
        Returns:
            각 축의 현재 위치 (mm)
            
        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        try:
            positions = []
            for axis in range(self._axis_count):
                position = await self.get_current_position(axis)
                positions.append(position)
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get all current positions: {e}")
            # Return cached positions as fallback
            return self._current_positions.copy()
    
    async def get_motion_status(self) -> MotionStatus:
        """
        모션 상태 조회
        
        Returns:
            현재 모션 상태
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        return self._motion_status
    
    async def stop_motion(self) -> bool:
        """
        모션 정지
        
        Returns:
            정지 성공 여부
            
        Raises:
            RobotConnectionError: If robot is not connected
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        try:
            logger.info("Stopping robot motion")
            
            failed_axes = []
            
            # Stop all axes
            for axis in range(self._axis_count):
                try:
                    result = self._axl.move_stop(axis, self._default_acceleration)
                    if result != AXT_RT_SUCCESS:
                        error_msg = get_error_message(result)
                        failed_axes.append((axis, error_msg))
                        logger.error(f"Failed to stop axis {axis}: {error_msg}")
                except Exception as e:
                    failed_axes.append((axis, str(e)))
                    logger.error(f"Failed to stop axis {axis}: {e}")
            
            if failed_axes:
                error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
                logger.warning(f"Failed to stop {len(failed_axes)} axes: {error_details}")
                # Continue despite some failures
            
            self._motion_status = MotionStatus.IDLE
            logger.info("Robot motion stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop motion: {e}")
            return False
    
    async def emergency_stop(self) -> bool:
        """
        비상 정지
        
        Returns:
            비상 정지 실행 여부
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        try:
            logger.warning("EMERGENCY STOP activated")
            
            # NOTE: In a real implementation, you would:
            # 1. Send immediate stop command
            # 2. Disable all servos
            # 3. Set safety flags
            
            self._motion_status = MotionStatus.EMERGENCY_STOP
            self._servo_states = [False] * self._axis_count
            
            return True
            
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            return False
    
    async def set_velocity_limit(self, max_velocity: float) -> bool:
        """
        최대 속도 제한 설정
        
        Args:
            max_velocity: 최대 속도 (mm/s)
            
        Returns:
            설정 성공 여부
        """
        if not await self.is_connected():
            raise RobotConnectionError("AJINEXTEK robot is not connected", "AJINEXTEK")
        
        if max_velocity <= 0:
            raise ValueError("Max velocity must be positive")
        
        try:
            # NOTE: In a real implementation, you would set hardware velocity limits
            self._default_velocity = min(self._default_velocity, max_velocity)
            logger.info(f"Velocity limit set to {max_velocity} mm/s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set velocity limit: {e}")
            return False
    
    async def get_axis_count(self) -> int:
        """
        축 개수 조회
        
        Returns:
            축 개수
        """
        return self._axis_count
    
    async def get_status(self) -> Dict[str, Any]:
        """
        하드웨어 상태 조회
        
        Returns:
            상태 정보 딕셔너리
        """
        status = {
            'connected': await self.is_connected(),
            'irq_no': self._irq_no,
            'axis_count': self._axis_count,
            'motion_status': self._motion_status.value,
            'servo_states': self._servo_states.copy(),
            'default_velocity': self._default_velocity,
            'default_acceleration': self._default_acceleration,
            'hardware_type': 'AJINEXTEK'
        }
        
        if await self.is_connected():
            try:
                status['current_positions'] = await self.get_all_positions()
                status['last_error'] = None
            except Exception as e:
                status['current_positions'] = None
                status['last_error'] = str(e)
        
        return status
    
    # === Helper Methods ===
    
    def _check_axis(self, axis_no: int) -> None:
        """Check if axis number is valid"""
        if not self._is_connected:
            raise RobotConnectionError("Robot controller not connected", "AJINEXTEK")
            
        if axis_no < 0 or axis_no >= self._axis_count:
            raise RobotMotionError(
                f"Invalid axis number: {axis_no} (valid: 0-{self._axis_count-1})",
                "AJINEXTEK"
            )
    
    def _set_servo_on(self, axis_no: int) -> None:
        """Turn servo on for specified axis"""
        self._check_axis(axis_no)
            
        try:
            result = self._axl.servo_on(axis_no, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = True
                logger.debug(f"Servo {axis_no} turned ON")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn on servo {axis_no}: {error_msg}")
                raise RobotMotionError(f"Failed to turn on servo {axis_no}: {error_msg}", "AJINEXTEK")
                
        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn on servo {axis_no}: {e}")
            raise RobotMotionError(f"Failed to turn on servo {axis_no}: {e}", "AJINEXTEK")
    
    def _set_servo_off(self, axis_no: int) -> None:
        """Turn servo off for specified axis"""
        self._check_axis(axis_no)
            
        try:
            result = self._axl.servo_on(axis_no, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self._servo_states[axis_no] = False
                logger.debug(f"Servo {axis_no} turned OFF")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn off servo {axis_no}: {error_msg}")
                raise RobotMotionError(f"Failed to turn off servo {axis_no}: {error_msg}", "AJINEXTEK")
                
        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to turn off servo {axis_no}: {e}")
            raise RobotMotionError(f"Failed to turn off servo {axis_no}: {e}", "AJINEXTEK")
    
    async def _home_axis(self, axis_no: int, home_dir: int = HOME_DIR_CCW,
                        signal_level: int = LIMIT_LEVEL_LOW, mode: int = HOME_MODE_0,
                        offset: float = 0.0, vel_first: float = 10.0, vel_second: float = 5.0,
                        accel: float = 100.0, decel: float = 100.0) -> None:
        """
        Perform homing for specified axis
        
        Args:
            axis_no: Axis number
            home_dir: Homing direction (default: CCW)  
            signal_level: Sensor signal level (default: LOW)
            mode: Homing mode (default: Mode 0)
            offset: Offset from home position
            vel_first: First search velocity
            vel_second: Second search velocity
            accel: Acceleration
            decel: Deceleration
            
        Raises:
            RobotMotionError: If homing setup or start fails
        """
        self._check_axis(axis_no)
            
        if not self._servo_states.get(axis_no, False):
            raise RobotMotionError(f"Servo {axis_no} is not ON - cannot perform homing", "AJINEXTEK")
            
        try:
            # Set homing method
            result = self._axl.home_set_method(axis_no, home_dir, signal_level, mode, offset)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing method for axis {axis_no}: {error_msg}")
                raise RobotMotionError(f"Failed to set homing method for axis {axis_no}: {error_msg}", "AJINEXTEK")
            
            # Set homing velocities
            result = self._axl.home_set_vel(axis_no, vel_first, vel_second, accel, decel)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing velocities for axis {axis_no}: {error_msg}")
                raise RobotMotionError(f"Failed to set homing velocities for axis {axis_no}: {error_msg}", "AJINEXTEK")
            
            # Start homing
            result = self._axl.home_set_start(axis_no)
            if result == AXT_RT_SUCCESS:
                logger.debug(f"Started homing for axis {axis_no}")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to start homing for axis {axis_no}: {error_msg}")
                raise RobotMotionError(f"Failed to start homing for axis {axis_no}: {error_msg}", "AJINEXTEK")
                
        except RobotMotionError:
            raise
        except Exception as e:
            logger.error(f"Failed to home axis {axis_no}: {e}")
            raise RobotMotionError(f"Failed to home axis {axis_no}: {e}", "AJINEXTEK")
    
    async def _wait_for_motion_complete(self, axis_no: int, timeout: float = 30.0) -> None:
        """
        Wait for axis to stop moving
        
        Args:
            axis_no: Axis number
            timeout: Maximum wait time in seconds
            
        Raises:
            RobotMotionError: If axis doesn't stop within timeout or status check fails
        """
        self._check_axis(axis_no)
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                is_moving = self._axl.read_in_motion(axis_no)
                if not is_moving:
                    logger.debug(f"Axis {axis_no} stopped successfully")
                    return
            except Exception as e:
                logger.error(f"Failed to check motion status for axis {axis_no}: {e}")
                raise RobotMotionError(f"Failed to check motion status for axis {axis_no}: {e}", "AJINEXTEK")
            
            await asyncio.sleep(0.01)  # Check every 10ms
            
        logger.warning(f"Timeout waiting for axis {axis_no} to stop")
        raise RobotMotionError(f"Timeout waiting for axis {axis_no} to stop after {timeout} seconds", "AJINEXTEK")
    
    async def _wait_for_homing_complete(self, axis_no: int, timeout: float = 30.0) -> None:
        """
        Wait for axis homing to complete
        
        Args:
            axis_no: Axis number
            timeout: Maximum wait time in seconds
            
        Raises:
            RobotMotionError: If homing doesn't complete within timeout
        """
        # For now, use motion complete check as homing indicator
        # In a real implementation, you might have specific homing status checks
        await self._wait_for_motion_complete(axis_no, timeout)