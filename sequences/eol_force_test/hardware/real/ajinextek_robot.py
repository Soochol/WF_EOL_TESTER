"""
Ajinextek Robot Service

Real hardware implementation for Ajinextek Robot controller.
Standalone version for EOL Tester package (Windows only).
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...interfaces import RobotService
from ...driver.ajinextek import (
    AXLWrapper,
    AXT_RT_SUCCESS,
    HOME_SUCCESS,
    HOME_SEARCHING,
)
from ...driver.ajinextek.exceptions import AXLError, AXLMotionError


class AjinextekRobot(RobotService):
    """Ajinextek Robot real hardware implementation."""

    def __init__(
        self,
        axis_count: int = 4,
        velocity: float = 100.0,
        acceleration: float = 500.0,
        deceleration: float = 500.0,
        motion_param_file: Optional[str] = None,
    ):
        """
        Initialize Ajinextek Robot.

        Args:
            axis_count: Number of axes (default: 4)
            velocity: Default motion velocity
            acceleration: Default acceleration
            deceleration: Default deceleration
            motion_param_file: Path to .mot motion parameter file (optional)
        """
        self._axis_count = axis_count
        self._default_velocity = velocity
        self._default_accel = acceleration
        self._default_decel = deceleration
        self._motion_param_file = motion_param_file

        self._axl: Optional[AXLWrapper] = None
        self._is_connected = False
        self._is_homed = False

    async def connect(self) -> None:
        """Connect to Ajinextek robot controller."""
        try:
            self._axl = AXLWrapper.get_instance()
            self._axl.connect()

            # Load motion parameters from file
            if self._motion_param_file:
                # Use config-specified path
                try:
                    self._axl.load_motion_parameters(self._motion_param_file)
                    print(f"DEBUG: Loaded motion parameters from {self._motion_param_file}")
                except FileNotFoundError as e:
                    print(f"WARNING: Motion parameter file not found: {e}")
                except Exception as e:
                    print(f"WARNING: Failed to load motion parameters: {e}")
            else:
                # Use default path discovery
                await self._load_robot_parameters()

            self._is_connected = True

        except AXLError as e:
            self._is_connected = False
            raise ConnectionError(f"Ajinextek Robot connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from robot controller."""
        try:
            if self._axl:
                # Turn off all servos before disconnecting
                for axis in range(self._axis_count):
                    try:
                        self._axl.servo_off(axis)
                    except Exception:
                        pass

                self._axl.disconnect()
        except Exception:
            pass
        finally:
            self._is_connected = False

    async def is_connected(self) -> bool:
        """Check connection status."""
        if not self._axl:
            return False
        try:
            return self._is_connected and self._axl.is_opened()
        except Exception:
            return False

    async def home(self) -> bool:
        """Perform homing for all axes."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        try:
            # Enable servos for all axes
            for axis in range(self._axis_count):
                result = self._axl.servo_on(axis)
                if result != AXT_RT_SUCCESS:
                    raise AXLMotionError(f"Failed to enable servo for axis {axis}")

            await asyncio.sleep(0.5)

            # Start homing for all axes
            for axis in range(self._axis_count):
                result = self._axl.home_set_start(axis)
                if result != AXT_RT_SUCCESS:
                    raise AXLMotionError(f"Failed to start homing for axis {axis}")

            # Wait for homing to complete
            max_wait = 60.0  # 60 second timeout
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < max_wait:
                all_complete = True
                for axis in range(self._axis_count):
                    home_result = self._axl.home_get_result(axis)
                    if home_result == HOME_SEARCHING:
                        all_complete = False
                        break
                    elif home_result != HOME_SUCCESS:
                        raise AXLMotionError(
                            f"Homing failed for axis {axis}: result={home_result}"
                        )

                if all_complete:
                    self._is_homed = True
                    return True

                await asyncio.sleep(0.1)

            raise RuntimeError("Homing timeout")

        except AXLError as e:
            raise RuntimeError(f"Homing failed: {e}") from e

    async def is_homed(self) -> bool:
        """Check if all axes are homed."""
        return self._is_homed

    async def move_to(
        self,
        positions: List[float],
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """Move to absolute positions."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if len(positions) != self._axis_count:
            raise ValueError(f"Expected {self._axis_count} positions, got {len(positions)}")

        vel = velocity if velocity is not None else self._default_velocity
        accel = acceleration if acceleration is not None else self._default_accel
        decel = deceleration if deceleration is not None else self._default_decel

        try:
            # Start motion for all axes
            for axis, position in enumerate(positions):
                result = self._axl.move_start_pos(axis, position, vel, accel, decel)
                if result != AXT_RT_SUCCESS:
                    raise AXLMotionError(f"Failed to start motion for axis {axis}")

            # Wait for motion to complete
            await self._wait_motion_complete()

        except AXLError as e:
            raise RuntimeError(f"Move failed: {e}") from e

    async def move_axis(
        self,
        axis: int,
        position: float,
        velocity: Optional[float] = None,
        acceleration: Optional[float] = None,
        deceleration: Optional[float] = None,
    ) -> None:
        """Move single axis to position."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if axis < 0 or axis >= self._axis_count:
            raise ValueError(f"Invalid axis: {axis}")

        vel = velocity if velocity is not None else self._default_velocity
        accel = acceleration if acceleration is not None else self._default_accel
        decel = deceleration if deceleration is not None else self._default_decel

        try:
            result = self._axl.move_start_pos(axis, position, vel, accel, decel)
            if result != AXT_RT_SUCCESS:
                raise AXLMotionError(f"Failed to start motion for axis {axis}")

            # Wait for motion to complete
            await self._wait_axis_motion_complete(axis)

        except AXLError as e:
            raise RuntimeError(f"Move axis failed: {e}") from e

    async def stop(self) -> None:
        """Stop all motion."""
        if not self._axl:
            return

        for axis in range(self._axis_count):
            try:
                self._axl.move_smooth_stop(axis)
            except Exception:
                pass

    async def emergency_stop(self) -> None:
        """Emergency stop all motion."""
        if not self._axl:
            return

        for axis in range(self._axis_count):
            try:
                self._axl.move_emergency_stop(axis)
            except Exception:
                pass

    async def get_position(self, axis: int) -> float:
        """Get current position for axis."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        return self._axl.get_act_pos(axis)

    async def get_all_positions(self) -> List[float]:
        """Get current positions for all axes."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        positions = []
        for axis in range(self._axis_count):
            positions.append(self._axl.get_act_pos(axis))

        return positions

    async def is_moving(self) -> bool:
        """Check if any axis is in motion."""
        if not self._axl:
            return False

        for axis in range(self._axis_count):
            try:
                if self._axl.read_in_motion(axis):
                    return True
            except Exception:
                pass

        return False

    async def servo_on(self, axis: Optional[int] = None) -> None:
        """Enable servo for axis or all axes."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if axis is not None:
            result = self._axl.servo_on(axis)
            if result != AXT_RT_SUCCESS:
                raise RuntimeError(f"Failed to enable servo for axis {axis}")
        else:
            for ax in range(self._axis_count):
                result = self._axl.servo_on(ax)
                if result != AXT_RT_SUCCESS:
                    raise RuntimeError(f"Failed to enable servo for axis {ax}")

    async def servo_off(self, axis: Optional[int] = None) -> None:
        """Disable servo for axis or all axes."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if axis is not None:
            result = self._axl.servo_off(axis)
            if result != AXT_RT_SUCCESS:
                raise RuntimeError(f"Failed to disable servo for axis {axis}")
        else:
            for ax in range(self._axis_count):
                result = self._axl.servo_off(ax)
                if result != AXT_RT_SUCCESS:
                    raise RuntimeError(f"Failed to disable servo for axis {ax}")

    async def is_servo_on(self, axis: int) -> bool:
        """Check if servo is enabled for axis."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        return self._axl.is_servo_on(axis)

    async def get_status(self) -> Dict[str, Any]:
        """Get hardware status."""
        status = {
            "connected": await self.is_connected(),
            "is_homed": self._is_homed,
            "axis_count": self._axis_count,
            "hardware_type": "Ajinextek",
        }

        if await self.is_connected():
            try:
                status["positions"] = await self.get_all_positions()
                status["is_moving"] = await self.is_moving()
                status["servo_states"] = [
                    await self.is_servo_on(ax) for ax in range(self._axis_count)
                ]
            except Exception as e:
                status["last_error"] = str(e)

        return status

    async def _wait_motion_complete(self, timeout: float = 30.0) -> None:
        """Wait for all axes motion to complete."""
        if not self._axl:
            return

        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            all_stopped = True
            for axis in range(self._axis_count):
                if self._axl.read_in_motion(axis):
                    all_stopped = False
                    break

            if all_stopped:
                return

            await asyncio.sleep(0.01)

        raise RuntimeError("Motion timeout")

    async def _wait_axis_motion_complete(self, axis: int, timeout: float = 30.0) -> None:
        """Wait for single axis motion to complete."""
        if not self._axl:
            return

        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            if not self._axl.read_in_motion(axis):
                return

            await asyncio.sleep(0.01)

        raise RuntimeError(f"Motion timeout for axis {axis}")

    async def _load_robot_parameters(self) -> None:
        """Load robot parameters from AJINEXTEK standard parameter file.

        Uses AxmMotLoadParaAll to load motion settings including homing
        parameters from the robot_motion_settings.mot file.

        Raises:
            RuntimeError: If parameter loading fails
        """
        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        try:
            # Find the .mot file relative to this module
            # The file should be in sequences/eol_force_test/config/
            config_dir = Path(__file__).parent.parent.parent / "config"
            mot_file = config_dir / "robot_motion_settings.mot"

            if not mot_file.exists():
                print(f"WARNING: Robot motion settings file not found: {mot_file}")
                print("Homing may fail without proper motion parameters.")
                return

            print(f"Loading robot motion settings from: {mot_file}")

            result = self._axl.load_para_all(str(mot_file))

            if result != AXT_RT_SUCCESS:
                print(f"WARNING: Failed to load motion settings (error={result})")
                print("Homing may fail without proper motion parameters.")
            else:
                print("Robot motion settings loaded successfully")

        except Exception as e:
            print(f"WARNING: Failed to load robot parameters: {e}")
            # Don't raise - allow connection to proceed even if params fail
            # Homing will likely fail but we want to provide detailed error then

    # =========================================================================
    # RobotService Interface Implementation
    # =========================================================================

    async def enable_servo(self, axis_id: int) -> None:
        """Enable servo for specified axis (interface method)."""
        await self.servo_on(axis_id)

    async def home_axis(self, axis_id: int) -> None:
        """Home specified axis (interface method)."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        try:
            # Enable servo first
            result = self._axl.servo_on(axis_id)
            if result != AXT_RT_SUCCESS:
                raise AXLMotionError(f"Failed to enable servo for axis {axis_id}")

            await asyncio.sleep(0.5)

            # Start homing
            result = self._axl.home_set_start(axis_id)
            if result != AXT_RT_SUCCESS:
                raise AXLMotionError(f"Failed to start homing for axis {axis_id}")

            # Wait for homing to complete
            max_wait = 60.0
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < max_wait:
                home_result = self._axl.home_get_result(axis_id)
                if home_result == HOME_SUCCESS:
                    self._is_homed = True
                    return
                elif home_result != HOME_SEARCHING:
                    raise AXLMotionError(
                        f"Homing failed for axis {axis_id}: result={home_result}"
                    )

                await asyncio.sleep(0.1)

            raise RuntimeError(f"Homing timeout for axis {axis_id}")

        except AXLError as e:
            raise RuntimeError(f"Homing axis {axis_id} failed: {e}") from e

    async def move_absolute(
        self,
        position: float,
        axis_id: int,
        velocity: float,
        acceleration: float,
        deceleration: float,
    ) -> None:
        """Move axis to absolute position (interface method)."""
        if not await self.is_connected():
            raise RuntimeError("Ajinextek Robot is not connected")

        if not self._axl:
            raise RuntimeError("AXL wrapper not initialized")

        if axis_id < 0 or axis_id >= self._axis_count:
            raise ValueError(f"Invalid axis: {axis_id}")

        try:
            result = self._axl.move_start_pos(
                axis_id, position, velocity, acceleration, deceleration
            )
            if result != AXT_RT_SUCCESS:
                raise AXLMotionError(f"Failed to start motion for axis {axis_id}")

            # Wait for motion to complete
            await self._wait_axis_motion_complete(axis_id)

        except AXLError as e:
            raise RuntimeError(f"Move absolute failed: {e}") from e
