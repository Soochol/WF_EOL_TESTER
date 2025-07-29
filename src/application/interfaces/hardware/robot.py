"""
Robot Interface

Interface for robot control and motion operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from domain.enums.robot_enums import MotionStatus
from domain.value_objects.hardware_configuration import RobotConfig


class RobotService(ABC):
    """Abstract interface for robot control operations"""

    @abstractmethod
    async def connect(self, robot_config: RobotConfig) -> None:
        """
        Connect to robot hardware

        Args:
            robot_config: Robot connection configuration

        Raises:
            HardwareConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from robot hardware

        Raises:
            HardwareOperationError: If disconnection fails
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
    async def initialize_axes(self) -> None:
        """
        Initialize robot axes and perform homing

        Raises:
            HardwareOperationError: If initialization fails
        """
        pass

    @abstractmethod
    async def move_to_position(self, axis: int, position: float, velocity: Optional[float] = None) -> None:
        """
        Move axis to absolute position

        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        pass

    @abstractmethod
    async def move_relative(self, axis: int, distance: float, velocity: Optional[float] = None) -> None:
        """
        Move axis by relative distance

        Args:
            axis: Axis number to move
            distance: Distance to move in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
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
    async def stop_motion(self, axis: Optional[int] = None) -> None:
        """
        Stop motion on specified axis or all axes

        Args:
            axis: Axis to stop (None for all axes)

        Raises:
            HardwareOperationError: If stop operation fails
        """
        pass

    @abstractmethod
    async def emergency_stop(self) -> None:
        """
        Emergency stop all motion immediately

        Raises:
            HardwareOperationError: If emergency stop fails
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
    async def set_velocity(self, axis: int, velocity: float) -> None:
        """
        Set default velocity for axis

        Args:
            axis: Axis number
            velocity: Velocity in mm/s

        Raises:
            HardwareOperationError: If velocity setting fails
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
    async def wait_for_completion(self, axis: Optional[int] = None, timeout: Optional[float] = None) -> None:
        """
        Wait for motion to complete

        Args:
            axis: Axis to wait for (None waits for all axes)
            timeout: Maximum wait time in seconds

        Raises:
            HardwareOperationError: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
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
