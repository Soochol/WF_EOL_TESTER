"""
Robot Home Main Use Case

Main orchestrator for robot homing operation.
Coordinates Digital I/O setup, robot connection, and homing execution.
"""

from loguru import logger

from application.services.core.configuration_service import ConfigurationService
from application.services.hardware_facade import HardwareServiceFacade
from application.use_cases.common.base_use_case import BaseUseCase
from domain.enums.test_status import TestStatus

from .input import RobotHomeInput
from .digital_io_setup_service import DigitalIOSetupService
from .result import RobotHomeResult
from .robot_connection_service import RobotConnectionService


class RobotHomeUseCase(BaseUseCase):
    """
    Robot Home Use Case

    Performs robot homing operation by moving the robot to its reference position.
    This is a simple operation that enables servo and executes homing sequence.
    """

    def __init__(
        self, hardware_services: HardwareServiceFacade, configuration_service: ConfigurationService
    ):
        """
        Initialize Robot Home Use Case

        Args:
            hardware_services: Hardware service facade for robot control
            configuration_service: Configuration service for loading hardware settings
        """
        super().__init__("Robot Home")
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service
        self._digital_io_setup = DigitalIOSetupService(hardware_services)
        self._robot_connection = RobotConnectionService(hardware_services)

    async def _execute_implementation(self, input_data: RobotHomeInput, context) -> RobotHomeResult:
        """
        Execute robot homing operation implementation

        Args:
            input_data: Robot home input containing operator information
            context: Execution context

        Returns:
            RobotHomeResult containing operation outcome and execution details
        """
        # Load hardware configuration dynamically
        hardware_config = await self._configuration_service.load_hardware_config()

        try:
            # Setup Digital I/O for servo brake release
            await self._digital_io_setup.setup_servo_brake_release(hardware_config)

            # Setup robot connection and enable servo
            axis_id = await self._robot_connection.setup_robot_connection(hardware_config)

            # Execute homing operation
            await self._robot_connection.execute_homing(axis_id)

            return RobotHomeResult(
                test_status=TestStatus.COMPLETED,
                is_success=True,
                error_message=None,
            )

        except Exception as e:
            # Cleanup on error for safety
            axis_id = hardware_config.robot.axis_id if hardware_config else None
            await self._robot_connection.cleanup_on_error(axis_id)
            raise e

    def _create_failure_result(
        self, input_data: RobotHomeInput, context, execution_duration, error_message: str
    ) -> RobotHomeResult:
        """
        Create a failure result when execution fails

        Args:
            input_data: Original input data that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description

        Returns:
            RobotHomeResult indicating failure
        """
        return RobotHomeResult(
            test_status=TestStatus.ERROR,
            is_success=False,
            error_message=f"Robot homing failed: {error_message}",
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
            return await self._robot_connection.get_robot_status(hardware_config)

        except Exception as e:
            logger.error(f"Failed to get robot status: {e}")
            return {
                "connected": False,
                "error": str(e),
                "robot_details": None,
                "hardware_status": None,
            }

    async def execute(self, input_data: RobotHomeInput) -> RobotHomeResult:
        """
        Execute the robot homing operation

        Args:
            input_data: Robot home input data

        Returns:
            RobotHomeResult with operation outcome
        """
        result = await super().execute(input_data)
        return result  # type: ignore
