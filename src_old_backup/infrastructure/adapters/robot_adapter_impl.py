"""
Robot Adapter Implementation

Concrete implementation of RobotAdapter interface using AJINEXTEK robot controllers.
Provides hardware abstraction layer for robot motion control.
"""

import asyncio
from typing import Dict, Any, Optional

from loguru import logger

from ..controllers.robot_controller.ajinextek.motion import AjinextekRobotController
from .interfaces.robot_adapter import RobotAdapter
from ...domain.entities.hardware_device import HardwareDevice
from ...domain.enums.hardware_status import HardwareStatus


class RobotAdapterImpl(RobotAdapter):
    """Robot adapter implementation using AJINEXTEK controller"""
    
    def __init__(self, controller: AjinextekRobotController):
        """
        Initialize robot adapter with controller
        
        Args:
            controller: AJINEXTEK robot controller instance
        """
        self._controller = controller
        self._hardware_device: Optional[HardwareDevice] = None
        logger.info(f"RobotAdapterImpl initialized with {controller.vendor} controller")
    
    @property
    def vendor(self) -> str:
        """Get adapter vendor name"""
        return self._controller.vendor
    
    @property
    def device_type(self) -> str:
        """Get device type"""
        return self._controller.controller_type
    
    @property
    def is_connected(self) -> bool:
        """Check if adapter is connected to hardware"""
        return self._controller.status == HardwareStatus.CONNECTED
    
    # Connection Management
    async def connect(self) -> None:
        """Connect to robot controller hardware"""
        try:
            # Run synchronous connect in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.connect)
            
            # Create or update hardware device entity
            self._hardware_device = HardwareDevice(
                device_type=self._controller.controller_type,
                vendor=self._controller.vendor,
                connection_info=self._controller.connection_info,
                capabilities={
                    'axis_count': self._controller.axis_count,
                    'servo_control': True,
                    'position_control': True,
                    'homing': True
                }
            )
            self._hardware_device.set_status(HardwareStatus.CONNECTED)
            
            logger.info(f"Robot adapter connected: {self._controller.axis_count} axes available")
            
        except Exception as e:
            if self._hardware_device:
                self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            logger.error(f"Robot adapter connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from robot controller hardware"""
        try:
            # Run synchronous disconnect in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.disconnect)
            
            if self._hardware_device:
                self._hardware_device.set_status(HardwareStatus.DISCONNECTED)
            
            logger.info("Robot adapter disconnected")
            
        except Exception as e:
            if self._hardware_device:
                self._hardware_device.set_status(HardwareStatus.ERROR, str(e))
            logger.error(f"Robot adapter disconnection failed: {e}")
            raise
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity with current status"""
        if not self._hardware_device:
            # Create default hardware device if not exists
            self._hardware_device = HardwareDevice(
                device_type=self._controller.controller_type,
                vendor=self._controller.vendor,
                connection_info=self._controller.connection_info
            )
            self._hardware_device.set_status(self._controller.status)
        
        return self._hardware_device
    
    # Axis Configuration
    async def get_axis_count(self) -> int:
        """Get number of available axes"""
        return self._controller.axis_count
    
    async def configure_axis(
        self, 
        axis_no: int, 
        pulse_method: int,
        unit_per_pulse: float,
        pulse_count: int = 1
    ) -> None:
        """Configure axis hardware parameters"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                self._controller.configure_axis,
                axis_no, pulse_method, unit_per_pulse, pulse_count
            )
            logger.info(f"Axis {axis_no} configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure axis {axis_no}: {e}")
            raise
    
    # Servo Control
    async def enable_servo(self, axis_no: int) -> None:
        """Enable servo for specified axis"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.set_servo_on, axis_no)
            logger.debug(f"Servo {axis_no} enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable servo {axis_no}: {e}")
            raise
    
    async def disable_servo(self, axis_no: int) -> None:
        """Disable servo for specified axis"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.set_servo_off, axis_no)
            logger.debug(f"Servo {axis_no} disabled")
            
        except Exception as e:
            logger.error(f"Failed to disable servo {axis_no}: {e}")
            raise
    
    async def is_servo_enabled(self, axis_no: int) -> bool:
        """Check if servo is enabled for axis"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._controller.is_servo_on, axis_no)
            
        except Exception as e:
            logger.error(f"Failed to check servo status {axis_no}: {e}")
            raise
    
    # Motion Control
    async def move_to_position(
        self, 
        axis_no: int, 
        position: float,
        velocity: float,
        acceleration: float = 100.0,
        deceleration: float = 100.0
    ) -> None:
        """Move axis to absolute position"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._controller.move_to_position,
                axis_no, position, velocity, acceleration, deceleration
            )
            logger.debug(f"Started absolute move on axis {axis_no} to position {position}")
            
        except Exception as e:
            logger.error(f"Failed to move axis {axis_no} to position {position}: {e}")
            raise
    
    async def move_relative(
        self, 
        axis_no: int, 
        distance: float,
        velocity: float,
        acceleration: float = 100.0,
        deceleration: float = 100.0
    ) -> None:
        """Move axis by relative distance"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._controller.move_relative,
                axis_no, distance, velocity, acceleration, deceleration
            )
            logger.debug(f"Started relative move on axis {axis_no} by distance {distance}")
            
        except Exception as e:
            logger.error(f"Failed to move axis {axis_no} by distance {distance}: {e}")
            raise
    
    async def stop_motion(self, axis_no: int, deceleration: float = 100.0) -> None:
        """Stop motion for specified axis"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.stop, axis_no, deceleration)
            logger.debug(f"Stopped motion on axis {axis_no}")
            
        except Exception as e:
            logger.error(f"Failed to stop axis {axis_no}: {e}")
            raise
    
    async def stop_all_motion(self, deceleration: float = 100.0) -> None:
        """Stop motion for all axes"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.stop_all, deceleration)
            logger.debug("Stopped motion on all axes")
            
        except Exception as e:
            logger.error(f"Failed to stop all axes: {e}")
            raise
    
    # Homing Operations
    async def home_axis(
        self, 
        axis_no: int,
        home_direction: int,
        signal_level: int,
        mode: int,
        offset: float = 0.0,
        vel_first: float = 10.0,
        vel_second: float = 5.0,
        acceleration: float = 100.0,
        deceleration: float = 100.0
    ) -> None:
        """Perform homing operation for specified axis"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._controller.home,
                axis_no, home_direction, signal_level, mode, offset,
                vel_first, vel_second, acceleration, deceleration
            )
            logger.info(f"Started homing for axis {axis_no}")
            
        except Exception as e:
            logger.error(f"Failed to home axis {axis_no}: {e}")
            raise
    
    # Position Control and Feedback
    async def get_current_position(self, axis_no: int) -> float:
        """Get current actual position of axis"""
        try:
            loop = asyncio.get_event_loop()
            position = await loop.run_in_executor(None, self._controller.get_position, axis_no)
            if position is None:
                raise RuntimeError(f"Failed to read position for axis {axis_no}")
            return position
            
        except Exception as e:
            logger.error(f"Failed to get current position for axis {axis_no}: {e}")
            raise
    
    async def get_command_position(self, axis_no: int) -> float:
        """Get command position of axis"""
        try:
            loop = asyncio.get_event_loop()
            position = await loop.run_in_executor(None, self._controller.get_command_position, axis_no)
            if position is None:
                raise RuntimeError(f"Failed to read command position for axis {axis_no}")
            return position
            
        except Exception as e:
            logger.error(f"Failed to get command position for axis {axis_no}: {e}")
            raise
    
    async def set_position_reference(self, axis_no: int, position: float) -> None:
        """Set position reference for axis (zero point setting)"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._controller.set_position, axis_no, position)
            logger.info(f"Set position reference for axis {axis_no} to {position}")
            
        except Exception as e:
            logger.error(f"Failed to set position reference for axis {axis_no}: {e}")
            raise
    
    # Status and Monitoring
    async def is_motion_complete(self, axis_no: int) -> bool:
        """Check if motion is complete for axis"""
        try:
            loop = asyncio.get_event_loop()
            is_moving = await loop.run_in_executor(None, self._controller.is_moving, axis_no)
            if is_moving is None:
                raise RuntimeError(f"Failed to read motion status for axis {axis_no}")
            return not is_moving  # Motion complete = not moving
            
        except Exception as e:
            logger.error(f"Failed to check motion status for axis {axis_no}: {e}")
            raise
    
    async def wait_for_motion_complete(
        self, 
        axis_no: int, 
        timeout_seconds: float = 30.0
    ) -> bool:
        """Wait for motion to complete on axis"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                self._controller.wait_for_stop, 
                axis_no, timeout_seconds
            )
            return True
            
        except Exception as e:
            logger.warning(f"Motion wait failed for axis {axis_no}: {e}")
            return False
    
    # Device Information
    async def get_device_info(self) -> Dict[str, Any]:
        """Get robot controller device information"""
        return {
            'vendor': self._controller.vendor,
            'controller_type': self._controller.controller_type,
            'connection_info': self._controller.connection_info,
            'axis_count': self._controller.axis_count,
            'servo_states': self._controller.servo_states.copy(),
            'status': self._controller.status.value,
            'capabilities': {
                'servo_control': True,
                'position_control': True,
                'velocity_control': True,
                'homing': True,
                'multi_axis': True
            }
        }
    
    async def get_connection_info(self) -> str:
        """Get connection information string"""
        return self._controller.connection_info
    
    # Health Check
    async def is_alive(self) -> bool:
        """Check if robot controller is alive and responsive"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._controller.is_alive)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False