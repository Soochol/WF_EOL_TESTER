"""
Robot Interface

Interface for robot control and motion operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class RobotService(ABC):
    """Abstract interface for robot control operations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to robot hardware
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from robot hardware
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if robot is connected
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    async def initialize_axes(self) -> bool:
        """
        Initialize robot axes and perform homing
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def move_to_position(self, axis: int, position: float, velocity: Optional[float] = None) -> bool:
        """
        Move axis to absolute position
        
        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s
            
        Returns:
            True if movement successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def move_relative(self, axis: int, distance: float, velocity: Optional[float] = None) -> bool:
        """
        Move axis by relative distance
        
        Args:
            axis: Axis number to move
            distance: Distance to move in mm
            velocity: Optional velocity override in mm/s
            
        Returns:
            True if movement successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_position(self, axis: int) -> float:
        """
        Get current position of axis
        
        Args:
            axis: Axis number
            
        Returns:
            Current position in mm
        """
        pass
    
    @abstractmethod
    async def get_all_positions(self) -> List[float]:
        """
        Get current positions of all axes
        
        Returns:
            List of positions for all axes in mm
        """
        pass
    
    @abstractmethod
    async def stop_motion(self, axis: Optional[int] = None) -> bool:
        """
        Stop motion on specified axis or all axes
        
        Args:
            axis: Axis to stop (None for all axes)
            
        Returns:
            True if stop successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def emergency_stop(self) -> bool:
        """
        Emergency stop all motion immediately
        
        Returns:
            True if emergency stop successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def is_moving(self, axis: Optional[int] = None) -> bool:
        """
        Check if axis is currently moving
        
        Args:
            axis: Axis to check (None checks if any axis is moving)
            
        Returns:
            True if moving, False otherwise
        """
        pass
    
    @abstractmethod
    async def set_velocity(self, axis: int, velocity: float) -> bool:
        """
        Set default velocity for axis
        
        Args:
            axis: Axis number
            velocity: Velocity in mm/s
            
        Returns:
            True if velocity set successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_velocity(self, axis: int) -> float:
        """
        Get current velocity setting for axis
        
        Args:
            axis: Axis number
            
        Returns:
            Current velocity in mm/s
        """
        pass
    
    @abstractmethod
    async def wait_for_completion(self, axis: Optional[int] = None, timeout: Optional[float] = None) -> bool:
        """
        Wait for motion to complete
        
        Args:
            axis: Axis to wait for (None waits for all axes)
            timeout: Maximum wait time in seconds
            
        Returns:
            True if motion completed, False if timeout
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get robot status information
        
        Returns:
            Dictionary containing robot status
        """
        pass