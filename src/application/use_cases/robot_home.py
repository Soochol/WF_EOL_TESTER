"""
Robot Home Use Case

Simple use case for homing the robot to its reference position.
This operation moves the robot to its home position using the configured axis.
"""

import asyncio
from typing import Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from domain.enums.test_status import TestStatus
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


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
        *,
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

    def __init__(self, hardware_services: HardwareServiceFacade, configuration_service: ConfigurationService):
        """
        Initialize Robot Home Use Case

        Args:
            hardware_services: Hardware service facade for robot control
            configuration_service: Configuration service for loading hardware settings
        """
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service

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

        # Load hardware configuration dynamically
        hardware_config = await self._configuration_service.load_hardware_config()

        try:
            # Step 0: Enable servo brake release digital output for robot homing preparation
            servo_brake_channel = hardware_config.digital_io.servo1_brake_release
            logger.info(
                f"Enabling servo brake release on Digital Output channel {servo_brake_channel} for robot homing preparation..."
            )

            # Step 0.1: Connect to Digital I/O service if not already connected
            irq_no = hardware_config.robot.irq_no
            logger.info(f"Checking Digital I/O service connection with irq_no={irq_no}...")

            try:
                # Check if already connected, if not connect
                if not await self._hardware_services.digital_io_service.is_connected():
                    await self._hardware_services.digital_io_service.connect()
                    logger.info("Digital I/O service connected successfully")
                else:
                    logger.info("Digital I/O service already connected")

                # Verify connection by checking status
                # Note: Digital I/O service may not have explicit status check, so we rely on is_connected()
                if not await self._hardware_services.digital_io_service.is_connected():
                    raise HardwareConnectionException(
                        "Digital I/O service connection verification failed"
                    )
                logger.info("Digital I/O service connection verified")

            except Exception as dio_connect_error:
                logger.error(f"Digital I/O service connection failed: {dio_connect_error}")
                raise HardwareConnectionException(
                    f"Failed to connect to Digital I/O service: {str(dio_connect_error)}",
                    details={"irq_no": irq_no, "error": str(dio_connect_error)},
                ) from dio_connect_error

            try:
                await self._hardware_services.digital_io_service.write_output(
                    servo_brake_channel, True
                )
                logger.info(
                    f"Digital Output channel {servo_brake_channel} (servo brake release) enabled successfully"
                )
            except Exception as dio_error:
                logger.error(
                    f"Failed to enable Digital Output channel {servo_brake_channel} (servo brake release): {dio_error}"
                )
                raise HardwareConnectionException(
                    f"Failed to enable servo brake release on Digital Output channel {servo_brake_channel} for robot homing: {str(dio_error)}",
                    details={"dio_channel": servo_brake_channel, "dio_error": str(dio_error)},
                ) from dio_error
            # Step 1: Check if robot service is available
            if not self._hardware_services.robot_service:
                raise HardwareConnectionException(
                    "Robot service is not available. Please check system configuration.",
                    details={"robot_service": None},
                )

            # Step 2: Connect to robot explicitly
            axis_id = hardware_config.robot.axis_id
            irq_no = hardware_config.robot.irq_no
            logger.info(f"Connecting to robot with axis_id={axis_id}, irq_no={irq_no}...")

            try:
                # Check if already connected, if not connect
                if not await self._hardware_services.robot_service.is_connected():
                    await self._hardware_services.robot_service.connect()
                    logger.info("Robot connected successfully")
                else:
                    logger.info("Robot already connected")

                # Verify connection with status check
                await self._hardware_services.robot_service.get_status(
                    axis_id=hardware_config.robot.axis_id
                )
                logger.info("Robot connection verified")

            except Exception as connect_error:
                logger.error(f"Robot connection failed: {connect_error}")
                raise HardwareConnectionException(
                    f"Failed to connect to robot: {str(connect_error)}",
                    details={"axis_id": axis_id, "irq_no": irq_no, "error": str(connect_error)},
                ) from connect_error

            # Step 3: Enable servo for the robot axis
            logger.info(f"Enabling servo for axis {axis_id}...")
            try:
                await self._hardware_services.robot_service.enable_servo(axis_id)
                logger.info("Robot servo enabled successfully")
            except Exception as servo_error:
                logger.error(f"Servo enable failed: {servo_error}")
                raise HardwareConnectionException(
                    f"Failed to enable servo for axis {axis_id}: {str(servo_error)}",
                    details={"axis_id": axis_id, "servo_error": str(servo_error)},
                ) from servo_error

            # Step 4: Execute homing operation
            logger.info(f"Starting homing operation for axis {axis_id}...")
            await self._hardware_services.robot_service.home_axis(axis_id)
            logger.info("Robot homing completed successfully")

            # Calculate execution duration
            end_time = asyncio.get_event_loop().time()
            duration = TestDuration.from_seconds(end_time - start_time)

            logger.info(
                f"Robot homing operation completed successfully - Duration: {duration.seconds:.2f}s"
            )

            return RobotHomeResult(
                operation_id,
                TestStatus.COMPLETED,
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
                axis_id = locals().get("axis_id", 0)
                if self._hardware_services.robot_service:
                    # Try to disable servo if it was enabled
                    try:
                        await self._hardware_services.robot_service.disable_servo(axis_id)
                        logger.info("Robot servo disabled after error")
                    except Exception as servo_error:
                        logger.warning(f"Failed to disable servo after error: {servo_error}")

                    # Note: We don't disconnect as the robot connection is managed elsewhere
            except Exception as cleanup_error:
                logger.warning(f"Error during cleanup: {cleanup_error}")

            return RobotHomeResult(
                operation_id,
                TestStatus.ERROR,
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
            # Load hardware configuration
            hardware_config = await self._configuration_service.load_hardware_config()

            hardware_status = await self._hardware_services.get_hardware_status()
            robot_connected = hardware_status.get("robot", False)

            if robot_connected:
                robot_status = await self._hardware_services.robot_service.get_status(
                    axis_id=hardware_config.robot.axis_id
                )
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
