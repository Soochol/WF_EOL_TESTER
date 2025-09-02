"""
Robot Connection Service

Handles robot connection, servo enable/disable, and status verification.
Manages robot hardware lifecycle for operations.
"""

from typing import Optional
from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from domain.exceptions.hardware_exceptions import HardwareConnectionException


class RobotConnectionService:
    """
    Robot connection service
    
    Manages robot connection lifecycle, servo operations, and status verification
    for robot operations.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize robot connection service
        
        Args:
            hardware_services: Hardware service facade
        """
        self._hardware_services = hardware_services

    async def setup_robot_connection(self, hardware_config) -> int:
        """
        Setup robot connection and enable servo

        Args:
            hardware_config: Hardware configuration containing robot settings
            
        Returns:
            Robot axis ID for further operations

        Raises:
            HardwareConnectionException: If robot setup fails
        """
        self._validate_robot_service()
        
        axis_id = hardware_config.robot.axis_id
        irq_no = hardware_config.robot.irq_no
        logger.info(f"Connecting to robot with axis_id={axis_id}, irq_no={irq_no}...")

        try:
            await self._ensure_connection(axis_id)
            await self._enable_servo(axis_id)
            return axis_id
            
        except Exception as robot_error:
            self._handle_connection_error(robot_error, axis_id, irq_no)
            raise  # This line should never be reached due to the error handler raising

    async def execute_homing(self, axis_id: int) -> None:
        """
        Execute robot homing operation
        
        Args:
            axis_id: Robot axis ID to home
            
        Raises:
            Exception: If homing operation fails
        """
        logger.info(f"Starting homing operation for axis {axis_id}...")
        await self._hardware_services.robot_service.home_axis(axis_id)
        logger.info("Robot homing completed successfully")

    async def cleanup_on_error(self, axis_id: Optional[int] = None) -> None:
        """
        Cleanup operations when an error occurs

        Args:
            axis_id: Robot axis ID for servo cleanup
        """
        try:
            if axis_id is None:
                axis_id = 0  # Default fallback

            if self._hardware_services.robot_service:
                try:
                    await self._hardware_services.robot_service.disable_servo(axis_id)
                    logger.info("Robot servo disabled after error")
                except Exception as servo_error:
                    logger.warning(f"Failed to disable servo after error: {servo_error}")
        except Exception as cleanup_error:
            logger.warning(f"Error during cleanup: {cleanup_error}")

    async def get_robot_status(self, hardware_config) -> dict:
        """
        Get current robot status for diagnostics
        
        Args:
            hardware_config: Hardware configuration containing robot settings

        Returns:
            Dictionary containing robot status information
        """
        try:
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

    def _validate_robot_service(self) -> None:
        """
        Validate that robot service is available
        
        Raises:
            HardwareConnectionException: If robot service is not available
        """
        if not self._hardware_services.robot_service:
            raise HardwareConnectionException(
                "Robot service is not available. Please check system configuration.",
                details={"robot_service": None},
            )

    async def _ensure_connection(self, axis_id: int) -> None:
        """
        Ensure robot is connected and verify status
        
        Args:
            axis_id: Robot axis ID for status verification
            
        Raises:
            Exception: If connection or verification fails
        """
        # Connect to robot if not already connected
        if not await self._hardware_services.robot_service.is_connected():
            await self._hardware_services.robot_service.connect()
            logger.info("Robot connected successfully")
        else:
            logger.info("Robot already connected")

        # Verify connection with status check
        await self._hardware_services.robot_service.get_status(axis_id=axis_id)
        logger.info("Robot connection verified")

    async def _enable_servo(self, axis_id: int) -> None:
        """
        Enable servo for the specified axis
        
        Args:
            axis_id: Robot axis ID
            
        Raises:
            Exception: If servo enable fails
        """
        logger.info(f"Enabling servo for axis {axis_id}...")
        await self._hardware_services.robot_service.enable_servo(axis_id)
        logger.info("Robot servo enabled successfully")

    def _handle_connection_error(self, robot_error: Exception, axis_id: int, irq_no: int) -> None:
        """
        Handle and classify robot connection errors
        
        Args:
            robot_error: The original exception
            axis_id: Robot axis ID for context
            irq_no: IRQ number for context
            
        Raises:
            HardwareConnectionException: Classified hardware error
        """
        if "servo" in str(robot_error).lower():
            logger.error(f"Servo enable failed: {robot_error}")
            raise HardwareConnectionException(
                f"Failed to enable servo for axis {axis_id}: {str(robot_error)}",
                details={"axis_id": axis_id, "servo_error": str(robot_error)},
            ) from robot_error
        else:
            logger.error(f"Robot connection failed: {robot_error}")
            raise HardwareConnectionException(
                f"Failed to connect to robot: {str(robot_error)}",
                details={"axis_id": axis_id, "irq_no": irq_no, "error": str(robot_error)},
            ) from robot_error
