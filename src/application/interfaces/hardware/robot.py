"""
Robot Interface

Interface for robot control and motion operations.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict

# Local application imports
from domain.enums.robot_enums import MotionStatus


class RobotService(ABC):
    """Abstract interface for robot control operations"""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to robot hardware

        All connection parameters are configured via dependency injection
        in the hardware container.

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
    async def move_relative(
        self,
        distance: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis by relative distance

        Args:
            distance: Distance to move in mm
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            position: Target position in mm
            axis_id: Axis ID number
            velocity: Motion velocity
            acceleration: Motion acceleration
            deceleration: Motion deceleration

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

    # get_all_positions method removed - use individual get_position() for each axis

    @abstractmethod
    async def stop_motion(self, axis_id: int, deceleration: float) -> None:
        """
        Stop motion on specified axis

        Args:
            axis_id: Axis ID number
            deceleration: Deceleration value for stopping

        Raises:
            HardwareOperationError: If stop operation fails
        """
        ...

    @abstractmethod
    async def emergency_stop(self, axis: int) -> None:
        """
        Emergency stop motion immediately for specific axis

        Args:
            axis: Specific axis to stop

        Raises:
            HardwareOperationError: If emergency stop fails
        """
        ...

    @abstractmethod
    async def is_moving(self, axis: int) -> bool:
        """
        Check if axis is currently moving

        Args:
            axis: Axis to check

        Returns:
            True if moving, False otherwise
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
    async def reset_servo_alarm(self, axis: int) -> None:
        """
        Reset servo alarm status (required after emergency stop)

        After emergency stop, the robot controller may enter servo alarm state.
        This method resets the alarm to allow servo re-enabling.

        Args:
            axis: Axis number to reset alarm for

        Raises:
            HardwareOperationError: If alarm reset operation fails
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

    # home_all_axes method removed - use individual home_axis() for each axis in separate threads

    @abstractmethod
    async def get_status(self, axis_id: int = 0) -> Dict[str, Any]:
        """
        Get robot status information

        Args:
            axis_id: Axis ID number (defaults to 0)

        Returns:
            Dictionary containing robot status
        """
        ...

    @abstractmethod
    async def get_load_ratio(self, axis: int, ratio_type: int = 0) -> float:
        """
        Get servo load ratio

        Args:
            axis: Axis number
            ratio_type: Monitor selection
                0x00 - Accumulated load ratio (default)
                0x01 - Regenerative load ratio
                0x02 - Reference Torque load ratio

        Returns:
            Load ratio in percentage

        Raises:
            HardwareOperationError: If read operation fails
        """
        ...

    @abstractmethod
    async def get_torque(self, axis: int) -> float:
        """
        Get current torque value

        Args:
            axis: Axis number

        Returns:
            Current torque value

        Raises:
            HardwareOperationError: If read operation fails
        """
        ...
