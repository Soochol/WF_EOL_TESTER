"""
Robot Adapter Interface

Infrastructure layer interface for robot motion control hardware adapters.
Provides hardware abstraction for multi-axis robot controllers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

from ....domain.entities.hardware_device import HardwareDevice
from ....domain.value_objects.measurements import PositionValue, VelocityValue


class RobotAdapter(ABC):
    """
    Abstract interface for robot adapter implementations
    
    Provides hardware abstraction layer for robot controllers,
    handling low-level communication and motion control operations.
    """
    
    @property
    @abstractmethod
    def vendor(self) -> str:
        """Get adapter vendor name"""
        pass
    
    @property
    @abstractmethod
    def device_type(self) -> str:
        """Get device type (should return 'robot')"""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if adapter is connected to hardware"""
        pass
    
    # Connection Management
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to robot controller hardware
        
        Raises:
            Exception: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from robot controller hardware
        
        Raises:
            Exception: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity with current status
        
        Returns:
            HardwareDevice entity representing the robot controller
        """
        pass
    
    # Axis Configuration
    @abstractmethod
    async def get_axis_count(self) -> int:
        """
        Get number of available axes
        
        Returns:
            Number of configured axes
        """
        pass
    
    @abstractmethod
    async def configure_axis(
        self, 
        axis_no: int, 
        pulse_method: int,
        unit_per_pulse: float,
        pulse_count: int = 1
    ) -> None:
        """
        Configure axis hardware parameters
        
        Args:
            axis_no: Axis number
            pulse_method: Hardware pulse output method
            unit_per_pulse: Movement unit per pulse
            pulse_count: Number of pulses per unit
            
        Raises:
            Exception: If configuration fails
        """
        pass
    
    # Servo Control
    @abstractmethod
    async def enable_servo(self, axis_no: int) -> None:
        """
        Enable servo for specified axis
        
        Args:
            axis_no: Axis number
            
        Raises:
            Exception: If servo enable fails
        """
        pass
    
    @abstractmethod
    async def disable_servo(self, axis_no: int) -> None:
        """
        Disable servo for specified axis
        
        Args:
            axis_no: Axis number
            
        Raises:
            Exception: If servo disable fails
        """
        pass
    
    @abstractmethod
    async def is_servo_enabled(self, axis_no: int) -> bool:
        """
        Check if servo is enabled for axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            True if servo is enabled, False otherwise
        """
        pass
    
    # Motion Control
    @abstractmethod
    async def move_to_position(
        self, 
        axis_no: int, 
        position: float,
        velocity: float,
        acceleration: float = 100.0,
        deceleration: float = 100.0
    ) -> None:
        """
        Move axis to absolute position
        
        Args:
            axis_no: Axis number
            position: Target position in hardware units
            velocity: Movement velocity in hardware units
            acceleration: Movement acceleration
            deceleration: Movement deceleration
            
        Raises:
            Exception: If motion fails to start
        """
        pass
    
    @abstractmethod
    async def move_relative(
        self, 
        axis_no: int, 
        distance: float,
        velocity: float,
        acceleration: float = 100.0,
        deceleration: float = 100.0
    ) -> None:
        """
        Move axis by relative distance
        
        Args:
            axis_no: Axis number
            distance: Relative distance in hardware units
            velocity: Movement velocity in hardware units
            acceleration: Movement acceleration
            deceleration: Movement deceleration
            
        Raises:
            Exception: If motion fails to start
        """
        pass
    
    @abstractmethod
    async def stop_motion(self, axis_no: int, deceleration: float = 100.0) -> None:
        """
        Stop motion for specified axis
        
        Args:
            axis_no: Axis number
            deceleration: Deceleration for stop
            
        Raises:
            Exception: If stop command fails
        """
        pass
    
    @abstractmethod
    async def stop_all_motion(self, deceleration: float = 100.0) -> None:
        """
        Stop motion for all axes
        
        Args:
            deceleration: Deceleration for stop
            
        Raises:
            Exception: If stop command fails
        """
        pass
    
    # Homing Operations
    @abstractmethod
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
        """
        Perform homing operation for specified axis
        
        Args:
            axis_no: Axis number
            home_direction: Homing direction
            signal_level: Sensor signal level
            mode: Homing mode
            offset: Offset from home position
            vel_first: First search velocity
            vel_second: Second search velocity
            acceleration: Movement acceleration
            deceleration: Movement deceleration
            
        Raises:
            Exception: If homing fails
        """
        pass
    
    # Position Control and Feedback
    @abstractmethod
    async def get_current_position(self, axis_no: int) -> float:
        """
        Get current actual position of axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            Current actual position in hardware units
            
        Raises:
            Exception: If position reading fails
        """
        pass
    
    @abstractmethod
    async def get_command_position(self, axis_no: int) -> float:
        """
        Get command position of axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            Current command position in hardware units
            
        Raises:
            Exception: If position reading fails
        """
        pass
    
    @abstractmethod
    async def set_position_reference(self, axis_no: int, position: float) -> None:
        """
        Set position reference for axis (zero point setting)
        
        Args:
            axis_no: Axis number
            position: Position value to set as reference
            
        Raises:
            Exception: If reference setting fails
        """
        pass
    
    # Status and Monitoring
    @abstractmethod
    async def is_motion_complete(self, axis_no: int) -> bool:
        """
        Check if motion is complete for axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            True if motion is complete, False if still moving
        """
        pass
    
    @abstractmethod
    async def wait_for_motion_complete(
        self, 
        axis_no: int, 
        timeout_seconds: float = 30.0
    ) -> bool:
        """
        Wait for motion to complete on axis
        
        Args:
            axis_no: Axis number
            timeout_seconds: Maximum wait time in seconds
            
        Returns:
            True if motion completed within timeout, False otherwise
        """
        pass
    
    # Device Information
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get robot controller device information
        
        Returns:
            Dictionary containing device specifications and capabilities
        """
        pass
    
    @abstractmethod
    async def get_connection_info(self) -> str:
        """
        Get connection information string
        
        Returns:
            String describing the connection (e.g., "IRQ_7")
        """
        pass
    
    # Health Check
    @abstractmethod
    async def is_alive(self) -> bool:
        """
        Check if robot controller is alive and responsive
        
        Returns:
            True if controller is responsive, False otherwise
        """
        pass