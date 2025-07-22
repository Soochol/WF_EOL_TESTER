"""
Mock AJINEXTEK Robot Controller

This module provides a mock implementation of the AJINEXTEK robot controller
for testing and development purposes. It simulates all robot behaviors without
requiring actual hardware.
"""

import time
from typing import Optional, Dict, Any

from loguru import logger

from ....domain.enums.hardware_status import HardwareStatus


class MockAjinextekRobotController:
    """Mock AJINEXTEK robot controller for testing"""

    def __init__(self, irq_no: int = 7):
        self.controller_type = "robot"
        self.vendor = "ajinextek_mock"
        self.connection_info = f'IRQ_{irq_no}'
        self.status = HardwareStatus.DISCONNECTED
        self._error_message = None
        
        # Robot-specific attributes
        self.irq_no = irq_no
        self.axis_count = 8  # Simulate 8 axes
        
        # Mock state
        self.servo_states = {}
        self.positions = {}
        self.command_positions = {}
        self.moving_states = {}
        self.motion_start_times = {}
        
        # Initialize mock states
        for axis in range(self.axis_count):
            self.servo_states[axis] = False
            self.positions[axis] = 0.0
            self.command_positions[axis] = 0.0
            self.moving_states[axis] = False
            self.motion_start_times[axis] = 0.0

    def connect(self, irq_no: Optional[int] = None, **kwargs) -> bool:
        """Connect to mock robot controller"""
        logger.info(f"Mock robot controller connected (IRQ: {irq_no or self.irq_no})")
        self.status = HardwareStatus.CONNECTED
        return True

    def disconnect(self) -> None:
        """Disconnect mock robot controller"""
        logger.info("Mock robot controller disconnected")
        self.status = HardwareStatus.DISCONNECTED

    def is_alive(self) -> bool:
        """Check if mock controller is alive"""
        return self.status == HardwareStatus.CONNECTED

    def configure_axis(self, axis_no: int, **kwargs) -> None:
        """Configure axis parameters"""
        self._check_axis(axis_no)
        logger.info(f"Mock axis {axis_no} configured with parameters: {kwargs}")

    def set_servo_on(self, axis_no: int) -> None:
        """Turn servo on for specified axis"""
        self._check_axis(axis_no)
        self.servo_states[axis_no] = True
        logger.info(f"Mock servo {axis_no} turned ON")

    def set_servo_off(self, axis_no: int) -> None:
        """Turn servo off for specified axis"""
        self._check_axis(axis_no)
        self.servo_states[axis_no] = False
        logger.info(f"Mock servo {axis_no} turned OFF")

    def is_servo_on(self, axis_no: int) -> bool:
        """Check if servo is on"""
        self._check_axis(axis_no)
        return self.servo_states[axis_no]

    def move_to_position(self, axis_no: int, position: float, velocity: float,
                        accel: float = 100.0, decel: float = 100.0) -> None:
        """Move axis to absolute position"""
        from ..exceptions import RobotError
        
        self._check_axis(axis_no)
        
        if not self.servo_states[axis_no]:
            logger.warning(f"Mock servo {axis_no} is not ON")
            raise RobotError(f"Servo {axis_no} is not ON - cannot move axis")
        
        # Simulate motion
        self.command_positions[axis_no] = position
        self.moving_states[axis_no] = True
        self.motion_start_times[axis_no] = time.time()
        
        logger.info(f"Mock axis {axis_no} started movement to position {position}")

    def move_relative(self, axis_no: int, distance: float, velocity: float,
                     accel: float = 100.0, decel: float = 100.0) -> bool:
        """Move axis by relative distance"""
        if not self._check_axis(axis_no):
            return False
        
        current_pos = self.positions[axis_no]
        target_pos = current_pos + distance
        return self.move_to_position(axis_no, target_pos, velocity, accel, decel)

    def stop(self, axis_no: int, decel: float = 100.0) -> bool:
        """Stop axis motion"""
        if not self._check_axis(axis_no):
            return False
        
        self.moving_states[axis_no] = False
        logger.info(f"Mock axis {axis_no} stopped")
        return True

    def stop_all(self, decel: float = 100.0) -> bool:
        """Stop all axes"""
        for axis in range(self.axis_count):
            self.stop(axis, decel)
        return True

    def home(self, axis_no: int, **kwargs) -> bool:
        """Perform homing for specified axis"""
        if not self._check_axis(axis_no):
            return False
        
        if not self.servo_states[axis_no]:
            logger.warning(f"Mock servo {axis_no} is not ON")
            return False
        
        # Simulate homing - move to zero position
        self.positions[axis_no] = 0.0
        self.command_positions[axis_no] = 0.0
        self.moving_states[axis_no] = True
        self.motion_start_times[axis_no] = time.time()
        
        logger.info(f"Mock axis {axis_no} started homing")
        return True

    def get_position(self, axis_no: int) -> Optional[float]:
        """Get current actual position of axis"""
        if not self._check_axis(axis_no):
            return None
        
        # Simulate gradual position change during motion
        if self.moving_states[axis_no]:
            elapsed = time.time() - self.motion_start_times[axis_no]
            if elapsed > 1.0:  # Simulate 1 second motion time
                self.positions[axis_no] = self.command_positions[axis_no]
                self.moving_states[axis_no] = False
        
        return self.positions[axis_no]

    def get_command_position(self, axis_no: int) -> Optional[float]:
        """Get command position of axis"""
        if not self._check_axis(axis_no):
            return None
        
        return self.command_positions[axis_no]

    def set_position(self, axis_no: int, position: float) -> bool:
        """Set current position (both actual and command)"""
        if not self._check_axis(axis_no):
            return False
        
        self.positions[axis_no] = position
        self.command_positions[axis_no] = position
        logger.info(f"Mock axis {axis_no} position set to {position}")
        return True

    def is_moving(self, axis_no: int) -> Optional[bool]:
        """Check if axis is currently moving"""
        if not self._check_axis(axis_no):
            return None
        
        # Update motion state based on time
        if self.moving_states[axis_no]:
            elapsed = time.time() - self.motion_start_times[axis_no]
            if elapsed > 1.0:  # Simulate 1 second motion time
                self.moving_states[axis_no] = False
                self.positions[axis_no] = self.command_positions[axis_no]
        
        return self.moving_states[axis_no]

    def wait_for_stop(self, axis_no: int, timeout: float = 30.0) -> bool:
        """Wait for axis to stop moving"""
        if not self._check_axis(axis_no):
            return False
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            is_moving = self.is_moving(axis_no)
            if is_moving is None:
                return False
            if not is_moving:
                return True
            time.sleep(0.01)  # Check every 10ms
        
        logger.warning(f"Mock axis {axis_no} timeout waiting for stop")
        return False

    def _check_axis(self, axis_no: int) -> None:
        """Check if axis number is valid"""
        from ..exceptions import RobotError, RobotConnectionError
        
        if self.status != HardwareStatus.CONNECTED:
            logger.error("Mock controller not initialized")
            raise RobotConnectionError("Mock controller not connected")
        
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