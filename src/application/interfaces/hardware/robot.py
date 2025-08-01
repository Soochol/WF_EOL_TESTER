"""
Robot Interface

Interface for robot control and motion operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.enums.robot_enums import MotionStatus


class RobotService(ABC):
    """Abstract interface for robot control operations"""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to robot hardware

        Raises:
            HardwareConnectionError: If connection fails
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from robot hardware

        Raises:
            HardwareOperationError: If disconnection fails
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if robot is connected

        Returns:
            True if connected, False otherwise
        """
        ...


    @abstractmethod
    async def move_to_position(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
    ) -> None:
        """
        Move axis to absolute position

        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def move_relative(
        self,
        axis: int,
        distance: float,
        velocity: Optional[float] = None,
    ) -> None:
        """
        Move axis by relative distance

        Args:
            axis: Axis number to move
            distance: Distance to move in mm
            velocity: Optional velocity override in mm/s

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def move_absolute(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            axis: Axis number to move
            position: Target position in mm
            velocity: Optional velocity override in mm/s
            acceleration: Optional acceleration override in mm/s²
            deceleration: Optional deceleration override in mm/s²

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def get_position(self, axis: int) -> float:
        """
        Get current position of axis

        Args:
            axis: Axis number

        Returns:
            Current position in mm
        """
        ...

    @abstractmethod
    async def get_all_positions(self) -> List[float]:
        """
        Get current positions of all axes

        Returns:
            List of positions for all axes in mm
        """
        ...

    @abstractmethod
    async def stop_motion(self, axis: int, deceleration: float) -> None:
        """
        Stop motion on specified axis

        Args:
            axis: Axis number to stop
            deceleration: Deceleration rate for stopping (mm/s²)

        Raises:
            HardwareOperationError: If stop operation fails
        """
        ...

    @abstractmethod
    async def emergency_stop(self) -> None:
        """
        Emergency stop all motion immediately

        Raises:
            HardwareOperationError: If emergency stop fails
        """
        ...

    @abstractmethod
    async def is_moving(self, axis: Optional[int] = None) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check (None checks if any axis is moving)

        Returns:
            True if moving, False otherwise
        """
        ...

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
        ...

    @abstractmethod
    async def get_velocity(self, axis: int) -> float:
        """
        Get current velocity setting for axis

        Args:
            axis: Axis number

        Returns:
            Current velocity in mm/s
        """
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        axis: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Wait for motion to complete

        Args:
            axis: Axis to wait for (None waits for all axes)
            timeout: Maximum wait time in seconds

        Raises:
            HardwareOperationError: If wait operation fails
            TimeoutError: If motion doesn't complete within timeout
        """
        ...

    @abstractmethod
    async def get_motion_status(self) -> MotionStatus:
        """
        Get current motion status

        Returns:
            Current motion status
        """
        ...

    @abstractmethod
    async def enable_servo(self, axis: int) -> None:
        """
        Enable servo for specific axis

        This method should be called before attempting motion operations on the axis.
        It enables the servo motor for the specified axis only.

        Args:
            axis: Axis number to enable servo for

        Raises:
            HardwareOperationError: If servo enable operation fails
        """
        ...

    @abstractmethod
    async def disable_servo(self, axis: int) -> None:
        """
        Disable servo for specific axis

        This method disables the servo motor for the specified axis.
        Should be called during shutdown or emergency situations.

        Args:
            axis: Axis number to disable servo for

        Raises:
            HardwareOperationError: If servo disable operation fails
        """
        ...

    @abstractmethod
    async def get_axis_count(self) -> int:
        """
        Get the number of axes supported by this robot

        Returns:
            Total number of axes
        """
        ...

    @abstractmethod
    async def get_primary_axis_id(self) -> int:
        """
        Get the primary axis ID that should be controlled

        Returns:
            Primary axis ID from hardware configuration
        """
        ...

    @abstractmethod
    async def home_axis(self, axis: int) -> None:
        """
        Home a single axis

        All homing parameters are configured in the robot controller via parameter files.

        Args:
            axis: Axis number to home

        Raises:
            HardwareOperationError: If homing operation fails
        """
        ...

    @abstractmethod
    async def home_all_axes(
        self,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> bool:
        """
        Home all axes

        Args:
            velocity: Optional homing velocity in mm/s
            acceleration: Optional homing acceleration in mm/s²
            deceleration: Optional homing deceleration in mm/s²

        Returns:
            True if all axes homed successfully

        Raises:
            HardwareOperationError: If homing operation fails
        """
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get robot status information

        Returns:
            Dictionary containing robot status
        """
        ...
