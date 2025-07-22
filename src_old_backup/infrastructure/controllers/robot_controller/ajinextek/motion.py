"""
High-level motion control API for AJINEXTEK robots

This module provides a user-friendly interface for robot motion control.
"""

import time
from typing import Optional, List, Tuple, Any

from loguru import logger

# Beautiful Debug Console
from ....utils.debug_console import debug_console, ComponentType, StatusType

from ....domain.enums.hardware_status import HardwareStatus
# Use robot-specific exceptions instead of generic hardware exceptions
from .axl_wrapper import AXLWrapper
from .constants import *
from .error_codes import AXT_RT_SUCCESS, get_error_message


class AjinextekRobotController:
    """High-level robot controller class for AJINEXTEK"""
    
    def __init__(self, irq_no: int = 7):
        self.controller_type = "robot"
        self.vendor = "ajinextek"
        self.connection_info = f'IRQ_{irq_no}'
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Robot-specific attributes
        self.axis_count = 0
        self.axl = AXLWrapper()
        self.servo_states = {}
        self.irq_no = irq_no

    def set_error(self, message: str) -> None:
        """Set error message and status"""
        self._error_message = message
        self.status = HardwareStatus.ERROR
        
    def connect(self, irq_no: Optional[int] = None, **kwargs) -> None:
        """
        Connect to the robot controller (exception-first design)
        
        Args:
            irq_no: IRQ number for the library (default: 7)
            
        Raises:
            RobotConnectionError: If connection fails
        """
        try:
            # Use provided irq_no or default from constructor
            actual_irq = irq_no if irq_no is not None else self.irq_no
            
            # Open library
            result = self.axl.open(actual_irq)
            if result != AXT_RT_SUCCESS:
                debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to open AXL library", f"Error code: {result}")
                from ..exceptions import RobotConnectionError
                raise RobotConnectionError(f"Failed to open AXL library: error code {result}", "ajinextek", details=f"IRQ: {actual_irq}")
            
            # Get board count
            try:
                board_count = self.axl.get_board_count()
                debug_console.log(ComponentType.ROBOT, StatusType.SUCCESS, "Board count detected", f"{board_count} board(s)")
            except Exception as e:
                debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to get board count", str(e))
                from ..exceptions import RobotConnectionError
                raise RobotConnectionError(f"Failed to get board count: {e}", "ajinextek", details=str(e))
            
            # Get axis count
            try:
                self.axis_count = self.axl.get_axis_count()
                debug_console.log(ComponentType.ROBOT, StatusType.SUCCESS, "Axis count detected", f"{self.axis_count} axis(es)")
            except Exception as e:
                debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to get axis count", str(e))
                from ..exceptions import RobotConnectionError
                raise RobotConnectionError(f"Failed to get axis count: {e}", "ajinextek", details=str(e))
            
            # Get library version
            try:
                version = self.axl.get_lib_version()
                debug_console.log(ComponentType.ROBOT, StatusType.INFO, "AXL Library version", version)
            except Exception:
                pass  # Library version is not critical
            
            self.status = HardwareStatus.CONNECTED
            debug_console.log(ComponentType.ROBOT, StatusType.SUCCESS, "Robot controller connected", f"IRQ: {actual_irq}, Axes: {self.axis_count}")
            
            # Initialize servo states
            for axis in range(self.axis_count):
                self.servo_states[axis] = False
            
        except RobotConnectionError:
            # Re-raise robot connection errors to preserve error context
            self.status = HardwareStatus.DISCONNECTED
            raise
        except Exception as e:
            debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to initialize robot controller", str(e))
            self.status = HardwareStatus.DISCONNECTED
            from ..exceptions import RobotConnectionError
            raise RobotConnectionError(f"Robot controller initialization failed: {e}", "ajinextek", details=str(e))
    
    def disconnect(self) -> None:
        """Disconnect the robot controller"""
        try:
            if self.status == HardwareStatus.CONNECTED:
                # Turn off all servos
                for axis in range(self.axis_count):
                    self.set_servo_off(axis)
                
                # Close library
                result = self.axl.close()
                if result == AXT_RT_SUCCESS:
                    self.status = HardwareStatus.DISCONNECTED
                    debug_console.log(ComponentType.ROBOT, StatusType.SUCCESS, "Robot controller disconnected")
                else:
                    debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to disconnect library", f"Error code: {result}")
                    self.set_error(f"Disconnect failed: error {result}")
            
        except Exception as e:
            debug_console.log(ComponentType.ROBOT, StatusType.ERROR, "Failed to disconnect robot controller", str(e))
            self.set_error(f"Disconnect failed: {e}")
            from ..exceptions import RobotError
            raise RobotError(f"Robot controller disconnect failed: {e}", "ajinextek", details=str(e))
    
    def configure_axis(self, axis_no: int, pulse_method: int = PULSE_OUT_METHOD_TWOPULSE,
                      unit_per_pulse: float = 1.0, pulse: int = 1) -> None:
        """
        Configure axis parameters
        
        Args:
            axis_no: Axis number
            pulse_method: Pulse output method (default: 2 pulse CW/CCW)
            unit_per_pulse: Movement unit per pulse (default: 1.0)
            pulse: Number of pulses (default: 1)
            
        Raises:
            RobotError: If configuration fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            # Set pulse output method
            result = self.axl.set_pulse_out_method(axis_no, pulse_method)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set pulse method for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set pulse method for axis {axis_no}: {error_msg}")
            
            # Set movement unit per pulse
            result = self.axl.set_move_unit_per_pulse(axis_no, unit_per_pulse, pulse)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set unit/pulse for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set unit/pulse for axis {axis_no}: {error_msg}")
                
            logger.info(f"Axis {axis_no} configured successfully")
            
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to configure axis {axis_no}: {e}")
            raise RobotError(f"Failed to configure axis {axis_no}: {e}")
    
    def set_servo_on(self, axis_no: int) -> None:
        """Turn servo on for specified axis"""
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            result = self.axl.servo_on(axis_no, SERVO_ON)
            if result == AXT_RT_SUCCESS:
                self.servo_states[axis_no] = True
                logger.info(f"Servo {axis_no} turned ON")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn on servo {axis_no}: {error_msg}")
                raise RobotError(f"Failed to turn on servo {axis_no}: {error_msg}")
                
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to turn on servo {axis_no}: {e}")
            raise RobotError(f"Failed to turn on servo {axis_no}: {e}")
    
    def set_servo_off(self, axis_no: int) -> None:
        """Turn servo off for specified axis"""
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            result = self.axl.servo_on(axis_no, SERVO_OFF)
            if result == AXT_RT_SUCCESS:
                self.servo_states[axis_no] = False
                logger.info(f"Servo {axis_no} turned OFF")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to turn off servo {axis_no}: {error_msg}")
                raise RobotError(f"Failed to turn off servo {axis_no}: {error_msg}")
                
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to turn off servo {axis_no}: {e}")
            raise RobotError(f"Failed to turn off servo {axis_no}: {e}")
    
    def is_servo_on(self, axis_no: int) -> bool:
        """Check if servo is on"""
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            is_on = self.axl.is_servo_on(axis_no)
            self.servo_states[axis_no] = is_on
            return is_on
        except Exception as e:
            logger.error(f"Failed to check servo status for axis {axis_no}: {e}")
            raise RobotError(f"Failed to check servo status for axis {axis_no}: {e}")
    
    def move_to_position(self, axis_no: int, position: float, velocity: float,
                        accel: float = 100.0, decel: float = 100.0) -> None:
        """
        Move axis to absolute position
        
        Args:
            axis_no: Axis number
            position: Target position
            velocity: Movement velocity
            accel: Acceleration (default: 100.0)
            decel: Deceleration (default: 100.0)
            
        Raises:
            RobotError: If movement fails or servo not enabled
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        if not self.servo_states.get(axis_no, False):
            logger.warning(f"Servo {axis_no} is not ON")
            raise RobotError(f"Servo {axis_no} is not ON - cannot move axis")
            
        try:
            result = self.axl.move_start_pos(axis_no, position, velocity, accel, decel)
            if result == AXT_RT_SUCCESS:
                logger.info(f"Started movement to position {position} on axis {axis_no}")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to start movement on axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to start movement on axis {axis_no}: {error_msg}")
                
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to move axis {axis_no}: {e}")
            raise RobotError(f"Failed to move axis {axis_no}: {e}")
    
    def move_relative(self, axis_no: int, distance: float, velocity: float,
                     accel: float = 100.0, decel: float = 100.0) -> None:
        """
        Move axis by relative distance
        
        Args:
            axis_no: Axis number
            distance: Relative distance to move
            velocity: Movement velocity
            accel: Acceleration (default: 100.0)
            decel: Deceleration (default: 100.0)
            
        Raises:
            RobotError: If movement fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        # Get current position
        try:
            current_pos = self.axl.get_act_pos(axis_no)
        except Exception as e:
            logger.error(f"Failed to get current position for axis {axis_no}: {e}")
            raise RobotError(f"Failed to get current position for axis {axis_no}: {e}")
            
        target_pos = current_pos + distance
        self.move_to_position(axis_no, target_pos, velocity, accel, decel)
    
    def stop(self, axis_no: int, decel: float = 100.0) -> None:
        """
        Stop axis motion
        
        Args:
            axis_no: Axis number
            decel: Deceleration for stop (default: 100.0)
            
        Raises:
            RobotError: If stop command fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            result = self.axl.move_stop(axis_no, decel)
            if result == AXT_RT_SUCCESS:
                logger.info(f"Stop command sent to axis {axis_no}")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to stop axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to stop axis {axis_no}: {error_msg}")
                
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to stop axis {axis_no}: {e}")
            raise RobotError(f"Failed to stop axis {axis_no}: {e}")
    
    def stop_all(self, decel: float = 100.0) -> None:
        """
        Stop all axes
        
        Args:
            decel: Deceleration for stop (default: 100.0)
            
        Raises:
            RobotError: If any stop command fails
        """
        from ..exceptions import RobotError
        
        failed_axes = []
        for axis in range(self.axis_count):
            try:
                self.stop(axis, decel)
            except RobotError as e:
                failed_axes.append((axis, str(e)))
                logger.error(f"Failed to stop axis {axis}: {e}")
        
        if failed_axes:
            error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
            raise RobotError(f"Failed to stop {len(failed_axes)} axes: {error_details}")
    
    def home(self, axis_no: int, home_dir: int = HOME_DIR_CCW,
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
            RobotError: If homing setup or start fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        if not self.servo_states.get(axis_no, False):
            logger.warning(f"Servo {axis_no} is not ON")
            raise RobotError(f"Servo {axis_no} is not ON - cannot perform homing")
            
        try:
            # Set homing method
            result = self.axl.home_set_method(axis_no, home_dir, signal_level, mode, offset)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing method for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set homing method for axis {axis_no}: {error_msg}")
            
            # Set homing velocities
            result = self.axl.home_set_vel(axis_no, vel_first, vel_second, accel, decel)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set homing velocities for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set homing velocities for axis {axis_no}: {error_msg}")
            
            # Start homing
            result = self.axl.home_set_start(axis_no)
            if result == AXT_RT_SUCCESS:
                logger.info(f"Started homing for axis {axis_no}")
            else:
                error_msg = get_error_message(result)
                logger.error(f"Failed to start homing for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to start homing for axis {axis_no}: {error_msg}")
                
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to home axis {axis_no}: {e}")
            raise RobotError(f"Failed to home axis {axis_no}: {e}")
    
    def get_position(self, axis_no: int) -> Optional[float]:
        """Get current actual position of axis"""
        try:
            self._check_axis(axis_no)
        except Exception:
            return None
            
        try:
            position = self.axl.get_act_pos(axis_no)
            return position
                
        except Exception as e:
            logger.error(f"Failed to get position: {e}")
            return None
    
    def get_command_position(self, axis_no: int) -> Optional[float]:
        """Get command position of axis"""
        try:
            self._check_axis(axis_no)
        except Exception:
            return None
            
        try:
            position = self.axl.get_cmd_pos(axis_no)
            return position
                
        except Exception as e:
            logger.error(f"Failed to get command position: {e}")
            return None
    
    def set_position(self, axis_no: int, position: float) -> None:
        """
        Set current position (both actual and command)
        
        Args:
            axis_no: Axis number
            position: Position value to set
            
        Raises:
            RobotError: If setting position fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        try:
            # Set actual position
            result = self.axl.set_act_pos(axis_no, position)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set actual position for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set actual position for axis {axis_no}: {error_msg}")
            
            # Set command position
            result = self.axl.set_cmd_pos(axis_no, position)
            if result != AXT_RT_SUCCESS:
                error_msg = get_error_message(result)
                logger.error(f"Failed to set command position for axis {axis_no}: {error_msg}")
                raise RobotError(f"Failed to set command position for axis {axis_no}: {error_msg}")
                
            logger.info(f"Set position of axis {axis_no} to {position}")
            
        except RobotError:
            # Re-raise robot specific errors to preserve error context
            raise
        except Exception as e:
            logger.error(f"Failed to set position: {e}")
            raise RobotError(f"Failed to set position: {e}")
    
    def is_moving(self, axis_no: int) -> Optional[bool]:
        """Check if axis is currently moving"""
        try:
            self._check_axis(axis_no)
        except Exception:
            return None
            
        try:
            in_motion = self.axl.read_in_motion(axis_no)
            return in_motion
                
        except Exception as e:
            logger.error(f"Failed to check motion status: {e}")
            return None
    
    def wait_for_stop(self, axis_no: int, timeout: float = 30.0) -> None:
        """
        Wait for axis to stop moving
        
        Args:
            axis_no: Axis number
            timeout: Maximum wait time in seconds
            
        Raises:
            RobotError: If axis doesn't stop within timeout or status check fails
        """
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            is_moving = self.is_moving(axis_no)
            if is_moving is None:
                raise RobotError(f"Failed to check motion status for axis {axis_no}")
            if not is_moving:
                logger.info(f"Axis {axis_no} stopped successfully")
                return
            time.sleep(0.01)  # Check every 10ms
            
        logger.warning(f"Timeout waiting for axis {axis_no} to stop")
        raise RobotError(f"Timeout waiting for axis {axis_no} to stop after {timeout} seconds")
    
    def is_alive(self) -> bool:
        """Check if robot controller connection is alive and responsive"""
        if self.status != HardwareStatus.CONNECTED:
            return False
        
        try:
            # Try to get board count to verify connection
            self.axl.get_board_count()
            return True
        except Exception:
            return False
    
    def _check_axis(self, axis_no: int) -> None:
        """Check if axis number is valid"""
        from ..exceptions import RobotError, RobotConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            logger.error("Controller not connected")
            raise RobotConnectionError("Robot controller not connected")
            
        if axis_no < 0 or axis_no >= self.axis_count:
            logger.error(f"Invalid axis number: {axis_no} (valid: 0-{self.axis_count-1})")
            raise RobotError(f"Invalid axis number: {axis_no} (valid: 0-{self.axis_count-1})")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Context manager exit"""
        # Always disconnect regardless of exception
        try:
            self.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect in context manager: {e}")
        # Return False to propagate any exceptions
        return False

