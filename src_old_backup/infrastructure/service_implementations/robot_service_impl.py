"""
Robot Service Implementation

Concrete implementation of RobotService interface using RobotAdapter.
Provides business logic layer for robot motion control with safety validation.
"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional

from loguru import logger

from ...application.interfaces.robot_service import RobotService, AxisStatus, MotionMode
from ...domain.entities.hardware_device import HardwareDevice
from ...domain.value_objects.measurements import PositionValue, VelocityValue
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    UnsafeOperationException
)

# Import adapter interface
from ..adapters.interfaces.robot_adapter import RobotAdapter


class RobotServiceImpl(RobotService):
    """Robot service implementation using RobotAdapter"""
    
    def __init__(self, adapter: RobotAdapter):
        """
        Initialize service with Robot adapter
        
        Args:
            adapter: RobotAdapter implementation
        """
        self._adapter = adapter
        self._axis_configurations: Dict[int, Dict[str, Any]] = {}
        self._safety_limits: Dict[int, Dict[str, Any]] = {}
        logger.info(f"RobotServiceImpl initialized with {adapter.vendor} adapter")
    
    # Connection Management
    async def connect(self) -> None:
        """Connect to robot controller"""
        try:
            await self._adapter.connect()
            
            # Initialize default safety limits for all axes
            axis_count = await self._adapter.get_axis_count()
            for axis_no in range(axis_count):
                self._safety_limits[axis_no] = {
                    'max_velocity': 100.0,  # Default safe velocity
                    'max_acceleration': 100.0,  # Default safe acceleration
                    'position_min': -1000.0,  # Default position limits
                    'position_max': 1000.0,
                    'homed': False
                }
            
            logger.info(f"Robot service connected: {axis_count} axes initialized")
            
        except Exception as e:
            logger.error(f"Robot service connection failed: {e}")
            raise HardwareNotReadyException(f"Robot controller connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from robot controller"""
        try:
            # Disable all servos before disconnect for safety
            await self.disable_all_servos()
            await self._adapter.disconnect()
            logger.info("Robot service disconnected")
            
        except Exception as e:
            logger.error(f"Robot service disconnection failed: {e}")
            raise BusinessRuleViolationException(f"Robot controller disconnect failed: {e}")
    
    async def is_connected(self) -> bool:
        """Check if robot controller is connected"""
        return self._adapter.is_connected
    
    async def get_hardware_device(self) -> HardwareDevice:
        """Get hardware device entity"""
        return await self._adapter.get_hardware_device()
    
    # Axis Configuration and Management
    async def get_axis_count(self) -> int:
        """Get number of available axes"""
        return await self._adapter.get_axis_count()
    
    async def configure_axis(
        self, 
        axis_no: int, 
        max_velocity: VelocityValue,
        max_acceleration: VelocityValue,
        position_limits: Tuple[PositionValue, PositionValue],
        **kwargs
    ) -> None:
        """Configure axis parameters with safety validation"""
        try:
            self._validate_axis_number(axis_no)
            
            # Validate parameters
            if max_velocity.value <= 0:
                raise UnsafeOperationException(f"Invalid velocity: {max_velocity.value}")
            if max_acceleration.value <= 0:
                raise UnsafeOperationException(f"Invalid acceleration: {max_acceleration.value}")
            
            min_pos, max_pos = position_limits
            if min_pos.value >= max_pos.value:
                raise UnsafeOperationException(f"Invalid position limits: {min_pos.value} >= {max_pos.value}")
            
            # Store safety limits
            self._safety_limits[axis_no] = {
                'max_velocity': max_velocity.value,
                'max_acceleration': max_acceleration.value,
                'position_min': min_pos.value,
                'position_max': max_pos.value,
                'homed': False
            }
            
            # Store configuration
            self._axis_configurations[axis_no] = {
                'max_velocity': max_velocity.value,
                'max_acceleration': max_acceleration.value,
                'position_limits': (min_pos.value, max_pos.value),
                'configured_at': logger.info(f"Axis {axis_no} configured successfully")
            }
            
            logger.info(f"Axis {axis_no} configured: vel={max_velocity.value}, acc={max_acceleration.value}")
            
        except Exception as e:
            logger.error(f"Failed to configure axis {axis_no}: {e}")
            if isinstance(e, (UnsafeOperationException, BusinessRuleViolationException)):
                raise
            raise BusinessRuleViolationException(f"Axis configuration failed: {e}")
    
    async def get_axis_configuration(self, axis_no: int) -> Dict[str, Any]:
        """Get axis configuration parameters"""
        self._validate_axis_number(axis_no)
        
        if axis_no not in self._axis_configurations:
            raise BusinessRuleViolationException(f"Axis {axis_no} not configured")
        
        return self._axis_configurations[axis_no].copy()
    
    # Servo Control
    async def enable_servo(self, axis_no: int) -> None:
        """Enable servo for specified axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            await self._adapter.enable_servo(axis_no)
            logger.info(f"Servo {axis_no} enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable servo {axis_no}: {e}")
            if isinstance(e, (BusinessRuleViolationException, UnsafeOperationException)):
                raise
            raise BusinessRuleViolationException(f"Servo enable failed: {e}")
    
    async def disable_servo(self, axis_no: int) -> None:
        """Disable servo for specified axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            await self._adapter.disable_servo(axis_no)
            logger.info(f"Servo {axis_no} disabled")
            
        except Exception as e:
            logger.error(f"Failed to disable servo {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Servo disable failed: {e}")
    
    async def enable_all_servos(self) -> None:
        """Enable servos for all axes"""
        axis_count = await self.get_axis_count()
        failed_axes = []
        
        for axis_no in range(axis_count):
            try:
                await self.enable_servo(axis_no)
            except Exception as e:
                failed_axes.append((axis_no, str(e)))
                logger.error(f"Failed to enable servo {axis_no}: {e}")
        
        if failed_axes:
            error_details = "; ".join([f"Axis {axis}: {error}" for axis, error in failed_axes])
            raise BusinessRuleViolationException(f"Failed to enable {len(failed_axes)} servos: {error_details}")
        
        logger.info("All servos enabled")
    
    async def disable_all_servos(self) -> None:
        """Disable servos for all axes"""
        try:
            axis_count = await self.get_axis_count()
            failed_axes = []
            
            for axis_no in range(axis_count):
                try:
                    await self.disable_servo(axis_no)
                except Exception as e:
                    failed_axes.append((axis_no, str(e)))
                    logger.error(f"Failed to disable servo {axis_no}: {e}")
            
            if failed_axes:
                logger.warning(f"Failed to disable {len(failed_axes)} servos, but continuing")
            
            logger.info("All servos disabled")
            
        except Exception as e:
            logger.warning(f"Error disabling all servos: {e}")
            # Don't raise exception for safety shutdown
    
    async def is_servo_enabled(self, axis_no: int) -> bool:
        """Check if servo is enabled for axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            return await self._adapter.is_servo_enabled(axis_no)
            
        except Exception as e:
            logger.error(f"Failed to check servo status {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Servo status check failed: {e}")
    
    # Motion Control
    async def move_to_position(
        self, 
        axis_no: int, 
        position: PositionValue,
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        deceleration: Optional[VelocityValue] = None
    ) -> None:
        """Move axis to absolute position with safety validation"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            await self._validate_servo_enabled(axis_no)
            
            # Safety validation
            await self._validate_position_safe(axis_no, position)
            await self._validate_velocity_safe(axis_no, velocity)
            
            # Use default acceleration/deceleration if not provided
            accel = acceleration.value if acceleration else self._safety_limits[axis_no]['max_acceleration']
            decel = deceleration.value if deceleration else accel
            
            await self._adapter.move_to_position(
                axis_no, position.value, velocity.value, accel, decel
            )
            
            logger.info(f"Started absolute move: axis {axis_no} to {position.value} at {velocity.value}")
            
        except Exception as e:
            logger.error(f"Failed to move axis {axis_no} to position {position.value}: {e}")
            if isinstance(e, (BusinessRuleViolationException, UnsafeOperationException)):
                raise
            raise BusinessRuleViolationException(f"Position move failed: {e}")
    
    async def move_relative(
        self, 
        axis_no: int, 
        distance: PositionValue,
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        deceleration: Optional[VelocityValue] = None
    ) -> None:
        """Move axis by relative distance with safety validation"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            await self._validate_servo_enabled(axis_no)
            
            # Check if target position will be safe
            current_pos = await self.get_current_position(axis_no)
            target_position = PositionValue(current_pos.value + distance.value, current_pos.unit)
            await self._validate_position_safe(axis_no, target_position)
            await self._validate_velocity_safe(axis_no, velocity)
            
            # Use default acceleration/deceleration if not provided
            accel = acceleration.value if acceleration else self._safety_limits[axis_no]['max_acceleration']
            decel = deceleration.value if deceleration else accel
            
            await self._adapter.move_relative(
                axis_no, distance.value, velocity.value, accel, decel
            )
            
            logger.info(f"Started relative move: axis {axis_no} by {distance.value} at {velocity.value}")
            
        except Exception as e:
            logger.error(f"Failed to move axis {axis_no} by distance {distance.value}: {e}")
            if isinstance(e, (BusinessRuleViolationException, UnsafeOperationException)):
                raise
            raise BusinessRuleViolationException(f"Relative move failed: {e}")
    
    async def move_multiple_axes(
        self, 
        axis_positions: Dict[int, PositionValue],
        velocity: VelocityValue,
        acceleration: Optional[VelocityValue] = None,
        synchronized: bool = True
    ) -> None:
        """Move multiple axes simultaneously"""
        try:
            # Validate all axes and positions first
            for axis_no, position in axis_positions.items():
                self._validate_axis_number(axis_no)
                await self._validate_servo_enabled(axis_no)
                await self._validate_position_safe(axis_no, position)
                await self._validate_velocity_safe(axis_no, velocity)
            
            # Execute moves
            if synchronized:
                # Start all moves simultaneously
                tasks = []
                for axis_no, position in axis_positions.items():
                    accel = acceleration.value if acceleration else self._safety_limits[axis_no]['max_acceleration']
                    task = self._adapter.move_to_position(
                        axis_no, position.value, velocity.value, accel, accel
                    )
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                logger.info(f"Started synchronized move for {len(axis_positions)} axes")
            else:
                # Execute moves sequentially
                for axis_no, position in axis_positions.items():
                    await self.move_to_position(axis_no, position, velocity, acceleration)
                logger.info(f"Started sequential move for {len(axis_positions)} axes")
            
        except Exception as e:
            logger.error(f"Failed to move multiple axes: {e}")
            if isinstance(e, (BusinessRuleViolationException, UnsafeOperationException)):
                raise
            raise BusinessRuleViolationException(f"Multiple axis move failed: {e}")
    
    async def stop_motion(self, axis_no: int, emergency: bool = False) -> None:
        """Stop motion for specified axis"""
        try:
            self._validate_axis_number(axis_no)
            
            decel = 0.0 if emergency else self._safety_limits[axis_no]['max_acceleration']
            await self._adapter.stop_motion(axis_no, decel)
            
            logger.info(f"Stopped motion on axis {axis_no} (emergency: {emergency})")
            
        except Exception as e:
            logger.error(f"Failed to stop axis {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Motion stop failed: {e}")
    
    async def stop_all_motion(self, emergency: bool = False) -> None:
        """Stop motion for all axes"""
        try:
            decel = 0.0 if emergency else 100.0  # Use safe default deceleration
            await self._adapter.stop_all_motion(decel)
            
            logger.info(f"Stopped all motion (emergency: {emergency})")
            
        except Exception as e:
            logger.error(f"Failed to stop all motion: {e}")
            raise BusinessRuleViolationException(f"All motion stop failed: {e}")
    
    # Homing Operations
    async def home_axis(self, axis_no: int, **kwargs) -> None:
        """Perform homing operation for specified axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            await self._validate_servo_enabled(axis_no)
            
            # Extract homing parameters with defaults
            home_dir = kwargs.get('home_direction', 0)  # CCW
            signal_level = kwargs.get('signal_level', 0)  # LOW
            mode = kwargs.get('mode', 0)  # Mode 0
            offset = kwargs.get('offset', 0.0)
            vel_first = kwargs.get('vel_first', 10.0)
            vel_second = kwargs.get('vel_second', 5.0)
            accel = kwargs.get('acceleration', 100.0)
            decel = kwargs.get('deceleration', 100.0)
            
            await self._adapter.home_axis(
                axis_no, home_dir, signal_level, mode, offset,
                vel_first, vel_second, accel, decel
            )
            
            # Mark as homed
            self._safety_limits[axis_no]['homed'] = True
            
            logger.info(f"Started homing for axis {axis_no}")
            
        except Exception as e:
            logger.error(f"Failed to home axis {axis_no}: {e}")
            if isinstance(e, (BusinessRuleViolationException, UnsafeOperationException)):
                raise
            raise BusinessRuleViolationException(f"Homing failed: {e}")
    
    async def home_all_axes(self, sequential: bool = True) -> None:
        """Perform homing operation for all axes"""
        axis_count = await self.get_axis_count()
        
        try:
            if sequential:
                for axis_no in range(axis_count):
                    await self.home_axis(axis_no)
                    # Wait for homing to complete before next axis
                    await self._adapter.wait_for_motion_complete(axis_no, 60.0)
                logger.info("Sequential homing completed for all axes")
            else:
                # Start all homing operations simultaneously
                tasks = [self.home_axis(axis_no) for axis_no in range(axis_count)]
                await asyncio.gather(*tasks)
                logger.info("Simultaneous homing started for all axes")
            
        except Exception as e:
            logger.error(f"Failed to home all axes: {e}")
            raise BusinessRuleViolationException(f"Homing all axes failed: {e}")
    
    async def is_homed(self, axis_no: int) -> bool:
        """Check if axis has been homed"""
        self._validate_axis_number(axis_no)
        return self._safety_limits.get(axis_no, {}).get('homed', False)
    
    # Position Control and Feedback
    async def get_current_position(self, axis_no: int) -> PositionValue:
        """Get current actual position of axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            position = await self._adapter.get_current_position(axis_no)
            return PositionValue(position, "mm")  # Assume mm units
            
        except Exception as e:
            logger.error(f"Failed to get current position for axis {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Position reading failed: {e}")
    
    async def get_command_position(self, axis_no: int) -> PositionValue:
        """Get command position of axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            position = await self._adapter.get_command_position(axis_no)
            return PositionValue(position, "mm")  # Assume mm units
            
        except Exception as e:
            logger.error(f"Failed to get command position for axis {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Command position reading failed: {e}")
    
    async def get_all_positions(self) -> Dict[int, PositionValue]:
        """Get current positions for all axes"""
        try:
            axis_count = await self.get_axis_count()
            positions = {}
            
            for axis_no in range(axis_count):
                try:
                    positions[axis_no] = await self.get_current_position(axis_no)
                except Exception as e:
                    logger.warning(f"Failed to get position for axis {axis_no}: {e}")
                    positions[axis_no] = PositionValue(0.0, "mm")  # Default value
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get all positions: {e}")
            raise BusinessRuleViolationException(f"All positions reading failed: {e}")
    
    async def set_position_reference(self, axis_no: int, position: PositionValue) -> None:
        """Set position reference for axis (zero point setting)"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            # Check if axis is stopped
            if not await self.is_motion_complete(axis_no):
                raise UnsafeOperationException(f"Cannot set reference while axis {axis_no} is moving")
            
            await self._adapter.set_position_reference(axis_no, position.value)
            logger.info(f"Set position reference for axis {axis_no} to {position.value}")
            
        except Exception as e:
            logger.error(f"Failed to set position reference for axis {axis_no}: {e}")
            if isinstance(e, UnsafeOperationException):
                raise
            raise BusinessRuleViolationException(f"Reference setting failed: {e}")
    
    # Status and Monitoring
    async def get_axis_status(self, axis_no: int) -> AxisStatus:
        """Get current status of axis"""
        try:
            self._validate_axis_number(axis_no)
            self._ensure_connected()
            
            # Check servo status
            servo_enabled = await self._adapter.is_servo_enabled(axis_no)
            if not servo_enabled:
                return AxisStatus.SERVO_OFF
            
            # Check motion status
            motion_complete = await self._adapter.is_motion_complete(axis_no)
            if not motion_complete:
                return AxisStatus.MOVING
            
            # Check if homed
            if not self.is_homed(axis_no):
                return AxisStatus.STOPPED  # Stopped but not homed
            
            return AxisStatus.STOPPED
            
        except Exception as e:
            logger.error(f"Failed to get axis status for {axis_no}: {e}")
            return AxisStatus.ERROR
    
    async def get_all_axes_status(self) -> Dict[int, AxisStatus]:
        """Get status for all axes"""
        try:
            axis_count = await self.get_axis_count()
            statuses = {}
            
            for axis_no in range(axis_count):
                statuses[axis_no] = await self.get_axis_status(axis_no)
            
            return statuses
            
        except Exception as e:
            logger.error(f"Failed to get all axes status: {e}")
            raise BusinessRuleViolationException(f"All axes status check failed: {e}")
    
    async def is_motion_complete(self, axis_no: int) -> bool:
        """Check if motion is complete for axis"""
        try:
            self._validate_axis_number(axis_no)
            return await self._adapter.is_motion_complete(axis_no)
            
        except Exception as e:
            logger.error(f"Failed to check motion status for axis {axis_no}: {e}")
            raise BusinessRuleViolationException(f"Motion status check failed: {e}")
    
    async def wait_for_motion_complete(
        self, 
        axis_no: int, 
        timeout_ms: int = 30000
    ) -> bool:
        """Wait for motion to complete on axis"""
        try:
            self._validate_axis_number(axis_no)
            timeout_seconds = timeout_ms / 1000.0
            return await self._adapter.wait_for_motion_complete(axis_no, timeout_seconds)
            
        except Exception as e:
            logger.error(f"Failed to wait for motion complete on axis {axis_no}: {e}")
            return False
    
    async def wait_for_all_motion_complete(self, timeout_ms: int = 30000) -> bool:
        """Wait for motion to complete on all axes"""
        try:
            axis_count = await self.get_axis_count()
            timeout_seconds = timeout_ms / 1000.0
            
            tasks = []
            for axis_no in range(axis_count):
                task = self._adapter.wait_for_motion_complete(axis_no, timeout_seconds)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return all(result is True for result in results if not isinstance(result, Exception))
            
        except Exception as e:
            logger.error(f"Failed to wait for all motion complete: {e}")
            return False
    
    # Safety and Validation
    async def validate_position_limits(
        self, 
        axis_no: int, 
        position: PositionValue
    ) -> bool:
        """Validate if position is within axis limits"""
        try:
            self._validate_axis_number(axis_no)
            
            limits = self._safety_limits.get(axis_no, {})
            min_pos = limits.get('position_min', -1000.0)
            max_pos = limits.get('position_max', 1000.0)
            
            return min_pos <= position.value <= max_pos
            
        except Exception:
            return False
    
    async def validate_velocity_limits(
        self, 
        axis_no: int, 
        velocity: VelocityValue
    ) -> bool:
        """Validate if velocity is within axis limits"""
        try:
            self._validate_axis_number(axis_no)
            
            limits = self._safety_limits.get(axis_no, {})
            max_vel = limits.get('max_velocity', 100.0)
            
            return 0 < velocity.value <= max_vel
            
        except Exception:
            return False
    
    async def emergency_stop(self) -> None:
        """Perform emergency stop for all axes"""
        try:
            await self.stop_all_motion(emergency=True)
            await self.disable_all_servos()
            logger.warning("Emergency stop executed")
            
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            raise BusinessRuleViolationException(f"Emergency stop failed: {e}")
    
    async def reset_errors(self) -> None:
        """Reset any error conditions on the robot controller"""
        try:
            # Re-establish connection if needed
            if not self._adapter.is_connected:
                await self._adapter.connect()
            
            logger.info("Robot errors reset")
            
        except Exception as e:
            logger.error(f"Error reset failed: {e}")
            raise BusinessRuleViolationException(f"Error reset failed: {e}")
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get robot controller device information"""
        try:
            return await self._adapter.get_device_info()
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            raise BusinessRuleViolationException(f"Device info retrieval failed: {e}")
    
    async def run_self_test(self) -> Dict[str, Any]:
        """Run robot controller self-test diagnostics"""
        try:
            # Basic connectivity test
            is_alive = await self._adapter.is_alive()
            axis_count = await self.get_axis_count()
            
            # Test servo status for all axes
            servo_tests = {}
            for axis_no in range(axis_count):
                try:
                    servo_status = await self._adapter.is_servo_enabled(axis_no)
                    servo_tests[f"axis_{axis_no}_servo"] = "pass" if servo_status is not None else "fail"
                except Exception:
                    servo_tests[f"axis_{axis_no}_servo"] = "fail"
            
            return {
                'connectivity': 'pass' if is_alive else 'fail',
                'axis_count': axis_count,
                'servo_tests': servo_tests,
                'overall_status': 'pass' if is_alive and axis_count > 0 else 'fail',
                'timestamp': logger.info("Self-test completed")
            }
            
        except Exception as e:
            logger.error(f"Self-test failed: {e}")
            raise BusinessRuleViolationException(f"Self-test failed: {e}")
    
    # Motion Planning and Coordination (Simplified Implementation)
    async def plan_trajectory(
        self, 
        waypoints: List[Dict[int, PositionValue]],
        velocity: VelocityValue,
        **kwargs
    ) -> Dict[str, Any]:
        """Plan trajectory through multiple waypoints"""
        try:
            # Validate all waypoints
            for i, waypoint in enumerate(waypoints):
                for axis_no, position in waypoint.items():
                    self._validate_axis_number(axis_no)
                    await self._validate_position_safe(axis_no, position)
                    await self._validate_velocity_safe(axis_no, velocity)
            
            # Simple trajectory plan
            plan = {
                'waypoints': waypoints,
                'velocity': velocity.value,
                'total_waypoints': len(waypoints),
                'estimated_time': len(waypoints) * 2.0,  # Simplified estimation
                'validated': True
            }
            
            logger.info(f"Trajectory planned: {len(waypoints)} waypoints")
            return plan
            
        except Exception as e:
            logger.error(f"Trajectory planning failed: {e}")
            if isinstance(e, UnsafeOperationException):
                raise
            raise BusinessRuleViolationException(f"Trajectory planning failed: {e}")
    
    async def execute_trajectory(self, trajectory_plan: Dict[str, Any]) -> None:
        """Execute pre-planned trajectory"""
        try:
            waypoints = trajectory_plan['waypoints']
            velocity = VelocityValue(trajectory_plan['velocity'], "mm/s")
            
            for i, waypoint in enumerate(waypoints):
                logger.info(f"Executing waypoint {i+1}/{len(waypoints)}")
                await self.move_multiple_axes(waypoint, velocity, synchronized=True)
                await self.wait_for_all_motion_complete()
            
            logger.info("Trajectory execution completed")
            
        except Exception as e:
            logger.error(f"Trajectory execution failed: {e}")
            raise BusinessRuleViolationException(f"Trajectory execution failed: {e}")
    
    # Private helper methods
    def _validate_axis_number(self, axis_no: int) -> None:
        """Validate axis number"""
        if axis_no < 0:
            raise BusinessRuleViolationException(f"Invalid axis number: {axis_no}")
    
    def _ensure_connected(self) -> None:
        """Ensure adapter is connected"""
        if not self._adapter.is_connected:
            raise HardwareNotReadyException("Robot controller not connected")
    
    async def _validate_servo_enabled(self, axis_no: int) -> None:
        """Validate servo is enabled for axis"""
        if not await self._adapter.is_servo_enabled(axis_no):
            raise UnsafeOperationException(f"Servo {axis_no} is not enabled")
    
    async def _validate_position_safe(self, axis_no: int, position: PositionValue) -> None:
        """Validate position is within safe limits"""
        if not await self.validate_position_limits(axis_no, position):
            limits = self._safety_limits.get(axis_no, {})
            min_pos = limits.get('position_min', -1000.0)
            max_pos = limits.get('position_max', 1000.0)
            raise UnsafeOperationException(
                f"Position {position.value} outside limits [{min_pos}, {max_pos}] for axis {axis_no}"
            )
    
    async def _validate_velocity_safe(self, axis_no: int, velocity: VelocityValue) -> None:
        """Validate velocity is within safe limits"""
        if not await self.validate_velocity_limits(axis_no, velocity):
            max_vel = self._safety_limits.get(axis_no, {}).get('max_velocity', 100.0)
            raise UnsafeOperationException(
                f"Velocity {velocity.value} exceeds maximum {max_vel} for axis {axis_no}"
            )