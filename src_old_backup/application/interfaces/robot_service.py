"""
Robot Service Interface

Application layer interface for robot motion control operations.
Defines the contract for multi-axis motion control, servo management, and positioning.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from ...domain.entities.hardware_device import HardwareDevice
from ...domain.value_objects.measurements import PositionValue, VelocityValue


class AxisStatus(Enum):
    """Axis status enumeration"""
    UNKNOWN = "unknown"
    STOPPED = "stopped"
    MOVING = "moving"
    HOMING = "homing"
    ERROR = "error"
    SERVO_OFF = "servo_off"


class MotionMode(Enum):
    """Motion mode enumeration"""
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    JOG = "jog"
    HOME = "home"


class RobotService(ABC):
    """
    Abstract interface for robot service operations
    
    Provides business logic interface for multi-axis robot control including
    motion planning, servo management, and coordinate positioning.
    """
    
    # Connection Management
    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to robot controller
        
        Raises:
            BusinessRuleViolationException: If connection fails
            HardwareNotReadyException: If robot not available
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from robot controller
        
        Raises:
            BusinessRuleViolationException: If disconnection fails
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if robot controller is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_hardware_device(self) -> HardwareDevice:
        """
        Get hardware device entity
        
        Returns:
            HardwareDevice entity with current status
        """
        pass
    
    # Axis Configuration and Management
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
        max_velocity: VelocityValue,
        max_acceleration: VelocityValue,
        position_limits: Tuple[PositionValue, PositionValue],
        **kwargs
    ) -> None:
        """
        Configure axis parameters with safety validation
        
        Args:
            axis_no: Axis number
            max_velocity: Maximum velocity for this axis
            max_acceleration: Maximum acceleration for this axis
            position_limits: (min_position, max_position) tuple
            **kwargs: Additional axis-specific parameters
            
        Raises:
            BusinessRuleViolationException: If configuration fails
            UnsafeOperationException: If parameters are unsafe
        """
        pass
    
    @abstractmethod
    async def get_axis_configuration(self, axis_no: int) -> Dict[str, Any]:
        """
        Get axis configuration parameters
        
        Args:
            axis_no: Axis number
            
        Returns:
            Dictionary containing axis configuration
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
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
            BusinessRuleViolationException: If servo enable fails
            UnsafeOperationException: If axis not ready for servo
        """
        pass
    
    @abstractmethod
    async def disable_servo(self, axis_no: int) -> None:
        """
        Disable servo for specified axis
        
        Args:
            axis_no: Axis number
            
        Raises:
            BusinessRuleViolationException: If servo disable fails
        """
        pass
    
    @abstractmethod
    async def enable_all_servos(self) -> None:
        """
        Enable servos for all axes
        
        Raises:
            BusinessRuleViolationException: If any servo enable fails
        """
        pass
    
    @abstractmethod
    async def disable_all_servos(self) -> None:
        """
        Disable servos for all axes
        
        Raises:
            BusinessRuleViolationException: If any servo disable fails
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
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
        """
        pass
    
    # Motion Control
    @abstractmethod
    async def move_to_position(
        self, 
        axis_no: int, 
        position: PositionValue,
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        deceleration: Optional[VelocityValue] = None
    ) -> None:
        """
        Move axis to absolute position with safety validation
        
        Args:
            axis_no: Axis number
            position: Target position
            velocity: Movement velocity
            acceleration: Movement acceleration (optional)
            deceleration: Movement deceleration (optional)
            
        Raises:
            BusinessRuleViolationException: If motion fails to start
            UnsafeOperationException: If position/velocity is unsafe
        """
        pass
    
    @abstractmethod
    async def move_relative(
        self, 
        axis_no: int, 
        distance: PositionValue,
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        deceleration: Optional[VelocityValue] = None
    ) -> None:
        """
        Move axis by relative distance with safety validation
        
        Args:
            axis_no: Axis number
            distance: Relative distance to move
            velocity: Movement velocity
            acceleration: Movement acceleration (optional)
            deceleration: Movement deceleration (optional)
            
        Raises:
            BusinessRuleViolationException: If motion fails to start
            UnsafeOperationException: If distance/velocity is unsafe
        """
        pass
    
    @abstractmethod
    async def move_multiple_axes(
        self, 
        axis_positions: Dict[int, PositionValue],
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        synchronized: bool = True
    ) -> None:
        """
        Move multiple axes simultaneously
        
        Args:
            axis_positions: Dictionary mapping axis numbers to target positions
            velocity: Movement velocity for all axes
            acceleration: Movement acceleration (optional)
            synchronized: Whether to synchronize motion completion
            
        Raises:
            BusinessRuleViolationException: If motion fails to start
            UnsafeOperationException: If any position/velocity is unsafe
        """
        pass
    
    @abstractmethod
    async def stop_motion(self, axis_no: int, emergency: bool = False) -> None:
        """
        Stop motion for specified axis
        
        Args:
            axis_no: Axis number
            emergency: Whether to perform emergency stop (immediate)
            
        Raises:
            BusinessRuleViolationException: If stop command fails
        """
        pass
    
    @abstractmethod
    async def stop_all_motion(self, emergency: bool = False) -> None:
        """
        Stop motion for all axes
        
        Args:
            emergency: Whether to perform emergency stop (immediate)
            
        Raises:
            BusinessRuleViolationException: If stop command fails
        """
        pass
    
    # Homing Operations
    @abstractmethod
    async def home_axis(self, axis_no: int, **kwargs) -> None:
        """
        Perform homing operation for specified axis
        
        Args:
            axis_no: Axis number
            **kwargs: Homing-specific parameters
            
        Raises:
            BusinessRuleViolationException: If homing fails
            UnsafeOperationException: If axis not ready for homing
        """
        pass
    
    @abstractmethod
    async def home_all_axes(self, sequential: bool = True) -> None:
        """
        Perform homing operation for all axes
        
        Args:
            sequential: Whether to home axes sequentially (default) or simultaneously
            
        Raises:
            BusinessRuleViolationException: If homing fails
        """
        pass
    
    @abstractmethod
    async def is_homed(self, axis_no: int) -> bool:
        """
        Check if axis has been homed
        
        Args:
            axis_no: Axis number
            
        Returns:
            True if axis is homed, False otherwise
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
        """
        pass
    
    # Position Control and Feedback
    @abstractmethod
    async def get_current_position(self, axis_no: int) -> PositionValue:
        """
        Get current actual position of axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            Current actual position
            
        Raises:
            BusinessRuleViolationException: If position reading fails
        """
        pass
    
    @abstractmethod
    async def get_command_position(self, axis_no: int) -> PositionValue:
        """
        Get command position of axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            Current command position
            
        Raises:
            BusinessRuleViolationException: If position reading fails
        """
        pass
    
    @abstractmethod
    async def get_all_positions(self) -> Dict[int, PositionValue]:
        """
        Get current positions for all axes
        
        Returns:
            Dictionary mapping axis numbers to current positions
        """
        pass
    
    @abstractmethod
    async def set_position_reference(self, axis_no: int, position: PositionValue) -> None:
        """
        Set position reference for axis (zero point setting)
        
        Args:
            axis_no: Axis number
            position: Position value to set as reference
            
        Raises:
            BusinessRuleViolationException: If reference setting fails
            UnsafeOperationException: If axis is moving
        """
        pass
    
    # Status and Monitoring
    @abstractmethod
    async def get_axis_status(self, axis_no: int) -> AxisStatus:
        """
        Get current status of axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            Current axis status
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
        """
        pass
    
    @abstractmethod
    async def get_all_axes_status(self) -> Dict[int, AxisStatus]:
        """
        Get status for all axes
        
        Returns:
            Dictionary mapping axis numbers to their status
        """
        pass
    
    @abstractmethod
    async def is_motion_complete(self, axis_no: int) -> bool:
        """
        Check if motion is complete for axis
        
        Args:
            axis_no: Axis number
            
        Returns:
            True if motion is complete, False if still moving
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
        """
        pass
    
    @abstractmethod
    async def wait_for_motion_complete(
        self, 
        axis_no: int, 
        timeout_ms: int = 30000
    ) -> bool:
        """
        Wait for motion to complete on axis
        
        Args:
            axis_no: Axis number
            timeout_ms: Maximum wait time in milliseconds
            
        Returns:
            True if motion completed within timeout, False otherwise
            
        Raises:
            BusinessRuleViolationException: If axis is invalid
        """
        pass
    
    @abstractmethod
    async def wait_for_all_motion_complete(self, timeout_ms: int = 30000) -> bool:
        """
        Wait for motion to complete on all axes
        
        Args:
            timeout_ms: Maximum wait time in milliseconds
            
        Returns:
            True if all motion completed within timeout, False otherwise
        """
        pass
    
    # Safety and Validation
    @abstractmethod
    async def validate_position_limits(
        self, 
        axis_no: int, 
        position: PositionValue
    ) -> bool:
        """
        Validate if position is within axis limits
        
        Args:
            axis_no: Axis number
            position: Position to validate
            
        Returns:
            True if position is within limits, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_velocity_limits(
        self, 
        axis_no: int, 
        velocity: VelocityValue
    ) -> bool:
        """
        Validate if velocity is within axis limits
        
        Args:
            axis_no: Axis number
            velocity: Velocity to validate
            
        Returns:
            True if velocity is within limits, False otherwise
        """
        pass
    
    @abstractmethod
    async def emergency_stop(self) -> None:
        """
        Perform emergency stop for all axes
        
        Immediately stops all motion and disables servos.
        
        Raises:
            BusinessRuleViolationException: If emergency stop fails
        """
        pass
    
    @abstractmethod
    async def reset_errors(self) -> None:
        """
        Reset any error conditions on the robot controller
        
        Raises:
            BusinessRuleViolationException: If error reset fails
        """
        pass
    
    @abstractmethod
    async def get_device_info(self) -> Dict[str, Any]:
        """
        Get robot controller device information
        
        Returns:
            Dictionary containing device specifications and capabilities
        """
        pass
    
    @abstractmethod
    async def run_self_test(self) -> Dict[str, Any]:
        """
        Run robot controller self-test diagnostics
        
        Returns:
            Dictionary containing test results and system health status
            
        Raises:
            BusinessRuleViolationException: If self-test fails
        """
        pass
    
    # Motion Planning and Coordination
    @abstractmethod
    async def plan_trajectory(
        self, 
        waypoints: List[Dict[int, PositionValue]],
        velocity: VelocityValue,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Plan trajectory through multiple waypoints
        
        Args:
            waypoints: List of position dictionaries for each waypoint
            velocity: Trajectory velocity
            **kwargs: Additional trajectory parameters
            
        Returns:
            Trajectory plan information
            
        Raises:
            BusinessRuleViolationException: If trajectory planning fails
            UnsafeOperationException: If trajectory is unsafe
        """
        pass
    
    @abstractmethod
    async def execute_trajectory(self, trajectory_plan: Dict[str, Any]) -> None:
        """
        Execute pre-planned trajectory
        
        Args:
            trajectory_plan: Trajectory plan from plan_trajectory
            
        Raises:
            BusinessRuleViolationException: If trajectory execution fails
        """
        pass