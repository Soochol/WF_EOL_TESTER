"""
Robot Interface

Interface for robot control and motion operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from domain.enums.robot_enums import MotionStatus
from domain.value_objects.axis_parameter import AxisParameter


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
        position: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        Move axis to absolute position

        Args:
            position: Target position in mm
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def move_relative(
        self,
        distance: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        Move axis by relative distance

        Args:
            distance: Distance to move in mm
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

        Raises:
            HardwareOperationError: If movement fails
        """
        ...

    @abstractmethod
    async def move_absolute(
        self,
        position: float,
        axis_param: AxisParameter,
    ) -> None:
        """
        Move axis to absolute position with motion parameters

        Args:
            position: Target position in mm
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)

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
    async def stop_motion(self, axis_param: AxisParameter) -> None:
        """
        Stop motion on specified axis

        Args:
            axis_param: 축 모션 파라미터 (축 번호, 속도, 가속도, 감속도)
                       deceleration 값이 사용됨

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
        axis: int,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Wait for motion to complete on specific axis

        Args:
            axis: Specific axis to wait for (required for thread safety)
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

    # home_all_axes method removed - use individual home_axis() for each axis in separate threads

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get robot status information

        Returns:
            Dictionary containing robot status
        """
        ...
