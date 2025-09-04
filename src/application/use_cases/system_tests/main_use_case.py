"""
Simple MCU Test Main Use Case

Main orchestrator for simple MCU communication test.
Coordinates MCU connection, test sequence execution, and result processing.
"""

from typing import TYPE_CHECKING, Optional

from loguru import logger

from application.services.core.configuration_service import ConfigurationService
from application.services.hardware_facade import HardwareServiceFacade
from application.use_cases.common.base_use_case import BaseUseCase
from domain.enums.test_status import TestStatus

if TYPE_CHECKING:
    from application.services.monitoring.emergency_stop_service import EmergencyStopService

from .command import SimpleMCUTestInput
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
        emergency_stop_service: Optional["EmergencyStopService"] = None
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

    async def _execute_implementation(
        self, command: SimpleMCUTestInput, context
    ) -> SimpleMCUTestResult:
        """
        Execute Simple MCU Communication Test implementation

        Args:
            command: Test command with operator information
            context: Execution context

        Returns:
            SimpleMCUTestResult with test outcomes and timing information
        """
        logger.info(f"Test parameters - Operator: {command.operator_id}")

        try:
            # Load hardware configuration
            logger.info("Loading hardware configuration...")
            hardware_config = await self._configuration_service.load_hardware_config()

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

            logger.info(f"Simple MCU Test completed - Success: {successful_steps}/{total_steps}")

            return SimpleMCUTestResult(
                test_status=TestStatus.COMPLETED if is_passed else TestStatus.FAILED,
                is_success=is_passed,
                test_results=test_results,
                error_message=None,
            )

        except Exception as e:
            # Cleanup on error
            await self._mcu_connection.cleanup_on_error()
            raise e

    def _create_failure_result(
        self, command: SimpleMCUTestInput, context, execution_duration, error_message: str
    ) -> SimpleMCUTestResult:
        """
        Create a failure result when execution fails

        Args:
            command: Original command that failed
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

    async def execute(self, command: SimpleMCUTestInput) -> SimpleMCUTestResult:
        """
        Execute the simple MCU communication test

        Args:
            command: Test command with operator information

        Returns:
            SimpleMCUTestResult with test outcomes
        """
        result = await super().execute(command)
        return result  # type: ignore
