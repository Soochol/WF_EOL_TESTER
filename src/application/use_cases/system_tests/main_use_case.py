"""
Simple MCU Test Main Use Case

Main orchestrator for simple MCU communication test.
Coordinates MCU connection, test sequence execution, and result processing.
"""

# Standard library imports
from typing import Optional, TYPE_CHECKING

# Third-party imports
from loguru import logger

# Local application imports
from application.services.core.configuration_service import ConfigurationService
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.emergency_stop_service import EmergencyStopService

if TYPE_CHECKING:
    from application.services.industrial.industrial_system_manager import IndustrialSystemManager
from application.use_cases.common.base_use_case import BaseUseCase
from domain.enums.test_status import TestStatus

# Local folder imports
from .input import SimpleMCUTestInput
from .mcu_connection_service import MCUConnectionService
from .result import SimpleMCUTestResult
from .test_sequence_executor import TestSequenceExecutor


class SimpleMCUTestUseCase(BaseUseCase):
    """
    Simple MCU Communication Test Use Case

    Performs direct MCU communication testing with the same sequence
    as simple_serial_test.py but integrated into the UseCase framework.
    """

    def __init__(
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
        emergency_stop_service: Optional[EmergencyStopService] = None,
        industrial_system_manager: Optional["IndustrialSystemManager"] = None,
    ):
        """
        Initialize Simple MCU Test Use Case

        Args:
            hardware_services: Hardware service facade
            configuration_service: Configuration service
            emergency_stop_service: Emergency stop service for hardware safety (optional)
        """
        super().__init__("Simple MCU Test", emergency_stop_service)
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service
        self._mcu_connection = MCUConnectionService(hardware_services)
        self._test_executor = TestSequenceExecutor(hardware_services)
        self._industrial_system_manager = industrial_system_manager

    async def _execute_implementation(
        self, input_data: SimpleMCUTestInput, context
    ) -> SimpleMCUTestResult:
        """
        Execute Simple MCU Communication Test implementation

        Args:
            input_data: Test input with operator information
            context: Execution context

        Returns:
            SimpleMCUTestResult with test outcomes and timing information
        """
        logger.info(f"Test parameters - Operator: {input_data.operator_id}")

        try:
            # Load hardware configuration
            logger.info("Loading hardware configuration...")
            hardware_config = await self._configuration_service.load_hardware_config()

            # Set system status to running
            if self._industrial_system_manager:
                from application.services.industrial.tower_lamp_service import SystemStatus
                await self._industrial_system_manager.set_system_status(SystemStatus.SYSTEM_RUNNING)

            # Connect and initialize MCU
            await self._mcu_connection.connect_and_initialize(hardware_config)

            # Execute test sequence
            test_results = await self._test_executor.execute_test_sequence()

            # Disconnect from MCU
            await self._mcu_connection.disconnect()

            # Calculate results
            successful_steps = len([r for r in test_results if r["success"]])
            total_steps = len(test_results)
            is_passed = successful_steps == total_steps

            # Set system status based on test result
            if self._industrial_system_manager:
                await self._industrial_system_manager.handle_test_completion(test_success=is_passed)

            logger.info(f"Simple MCU Test completed - Success: {successful_steps}/{total_steps}")

            return SimpleMCUTestResult(
                test_status=TestStatus.COMPLETED if is_passed else TestStatus.FAILED,
                is_success=is_passed,
                test_results=test_results,
                error_message=None,
            )

        except Exception as e:
            # Set system status to error
            if self._industrial_system_manager:
                await self._industrial_system_manager.handle_test_completion(test_success=False, test_error=True)

            # Cleanup on error
            await self._mcu_connection.cleanup_on_error()
            raise e

    def _create_failure_result(
        self, input_data: SimpleMCUTestInput, context, execution_duration, error_message: str
    ) -> SimpleMCUTestResult:
        """
        Create a failure result when execution fails

        Args:
            input_data: Original input data that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description

        Returns:
            SimpleMCUTestResult indicating failure
        """
        return SimpleMCUTestResult(
            test_status=TestStatus.ERROR,
            is_success=False,
            test_results=[],
            error_message=f"Simple MCU Test failed: {error_message}",
        )

    async def execute(self, input_data: SimpleMCUTestInput) -> SimpleMCUTestResult:
        """
        Execute the simple MCU communication test

        Args:
            input_data: Test input data with operator information

        Returns:
            SimpleMCUTestResult with test outcomes
        """
        result = await super().execute(input_data)
        return result  # type: ignore
