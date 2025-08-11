"""
Robot Home Use Case

Simple use case for homing the robot to its reference position.
This operation moves the robot to its home position using the configured axis.
"""

import asyncio
from typing import Optional

from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration
from domain.enums.test_status import TestStatus
from domain.exceptions.hardware_exceptions import HardwareConnectionException


class RobotHomeCommand:
    """Robot Home Execution Command"""

    def __init__(self, operator_id: str = "system"):
        self.operator_id = operator_id


class RobotHomeResult:
    """Robot Home Operation Result"""

    def __init__(
        self,
        operation_id: TestId,
        test_status: TestStatus,
        execution_duration: TestDuration,
        is_success: bool,
        error_message: Optional[str] = None,
    ):
        self.operation_id = operation_id
        self.test_status = test_status
        self.execution_duration = execution_duration
        self.is_success = is_success
        self.error_message = error_message


class RobotHomeUseCase:
    """
    Robot Home Use Case

    Performs robot homing operation by moving the robot to its reference position.
    This is a simple operation that enables servo and executes homing sequence.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize Robot Home Use Case

        Args:
            hardware_services: Hardware service facade for robot control
        """
        self._hardware_services = hardware_services

    async def execute(self, command: RobotHomeCommand) -> RobotHomeResult:
        """
        Execute robot homing operation

        Args:
            command: Robot home command containing operator information

        Returns:
            RobotHomeResult containing operation outcome and execution details

        Raises:
            HardwareConnectionException: If robot connection fails or hardware errors occur
        """
        operation_id = TestId.generate()
        start_time = asyncio.get_event_loop().time()

        logger.info(f"Starting robot homing operation - ID: {operation_id}")

        try:
            # Step 1: Check if robot service is available
            if not self._hardware_services._robot:
                raise HardwareConnectionException(
                    "Robot service is not available. Please check system configuration.",
                    details={"robot_service": None}
                )

            # Step 2: Check robot status to verify it's available
            logger.info("Checking robot connection status...")
            try:
                robot_status = await self._hardware_services._robot.get_status()
                logger.info("Robot status check successful")
            except Exception as status_error:
                logger.error(f"Robot status check failed: {status_error}")
                raise HardwareConnectionException(
                    f"Robot is not available or not connected: {str(status_error)}",
                    details={"status_error": str(status_error)}
                )

            # Step 3: Verify hardware status after connection
            hardware_status = await self._hardware_services.get_hardware_status()
            
            if not hardware_status.get("robot", False):
                raise HardwareConnectionException(
                    "Robot is not connected. Please check hardware connections.",
                    details={"hardware_status": hardware_status}
                )

            # Step 4: Load robot configuration for axis parameters
            # For now, use axis 0 as that's what's configured in hardware_configuration.yaml
            axis_id = 0
            logger.info(f"Using robot axis_id: {axis_id}")

            # Step 5: Enable servo for the robot axis
            logger.info(f"Enabling servo for axis {axis_id}...")
            await self._hardware_services._robot.enable_servo(axis_id)
            logger.info("Robot servo enabled successfully")

            # Step 6: Execute homing operation
            logger.info(f"Starting homing operation for axis {axis_id}...")
            await self._hardware_services._robot.home_axis(axis_id)
            logger.info("Robot homing completed successfully")

            # Calculate execution duration
            end_time = asyncio.get_event_loop().time()
            duration = TestDuration.from_seconds(end_time - start_time)

            logger.info(
                f"Robot homing operation completed successfully - Duration: {duration.seconds:.2f}s"
            )

            return RobotHomeResult(
                operation_id=operation_id,
                test_status=TestStatus.COMPLETED,
                execution_duration=duration,
                is_success=True,
                error_message=None,
            )

        except Exception as e:
            # Calculate execution duration for failure case
            end_time = asyncio.get_event_loop().time()
            duration = TestDuration.from_seconds(end_time - start_time)

            error_message = f"Robot homing failed: {str(e)}"
            logger.error(error_message)

            # Try to cleanup on error for safety
            try:
                axis_id = locals().get('axis_id', 0)
                if self._hardware_services._robot:
                    # Try to disable servo if it was enabled
                    try:
                        await self._hardware_services._robot.disable_servo(axis_id)
                        logger.info("Robot servo disabled after error")
                    except Exception as servo_error:
                        logger.warning(f"Failed to disable servo after error: {servo_error}")
                    
                    # Note: We don't disconnect as the robot connection is managed elsewhere
            except Exception as cleanup_error:
                logger.warning(f"Error during cleanup: {cleanup_error}")

            return RobotHomeResult(
                operation_id=operation_id,
                test_status=TestStatus.ERROR,
                execution_duration=duration,
                is_success=False,
                error_message=error_message,
            )

    async def get_robot_status(self) -> dict:
        """
        Get current robot status for diagnostics

        Returns:
            Dictionary containing robot status information
        """
        try:
            hardware_status = await self._hardware_services.get_hardware_status()
            robot_connected = hardware_status.get("robot", False)

            if robot_connected:
                robot_status = await self._hardware_services._robot.get_status()
                return {
                    "connected": True,
                    "robot_details": robot_status,
                    "hardware_status": hardware_status,
                }
            else:
                return {
                    "connected": False,
                    "robot_details": None,
                    "hardware_status": hardware_status,
                }

        except Exception as e:
            logger.error(f"Failed to get robot status: {e}")
            return {
                "connected": False,
                "error": str(e),
                "robot_details": None,
                "hardware_status": None,
            }