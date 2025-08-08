"""
Hardware Test Executor

Handles execution of all hardware test phases and measurement collection.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade
from domain.exceptions.test_exceptions import TestExecutionException
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.test_configuration import TestConfiguration

from .constants import TestExecutionConstants


class HardwareTestExecutor:
    """Handles hardware test phase execution and measurement collection"""

    def __init__(self, hardware_services: HardwareServiceFacade):
        self._hardware_services = hardware_services

    def validate_configurations_loaded(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> None:
        """
        Validate that all required configurations are loaded

        Args:
            test_config: Test configuration to validate
            hardware_config: Hardware configuration to validate

        Raises:
            TestExecutionException: If any required configuration is missing
        """
        if test_config is None:
            raise TestExecutionException(TestExecutionConstants.TEST_CONFIG_REQUIRED_ERROR)

        if hardware_config is None:
            raise TestExecutionException(TestExecutionConstants.HARDWARE_CONFIG_REQUIRED_ERROR)

    async def execute_hardware_test_phases(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> TestMeasurements:
        """
        Execute all hardware test phases and collect measurements

        Args:
            test_config: Test configuration for hardware operations
            hardware_config: Hardware configuration for connections

        Returns:
            TestMeasurements: Collected measurements from hardware tests

        Raises:
            TestExecutionException: If hardware test execution fails
        """
        logger.info(TestExecutionConstants.LOG_HARDWARE_TEST_START)

        try:
            # Connect all hardware
            logger.info(TestExecutionConstants.LOG_HARDWARE_CONNECTION_START)
            await self._hardware_services.connect_all_hardware(hardware_config)
            logger.info(TestExecutionConstants.LOG_HARDWARE_CONNECTION_SUCCESS)

            # Initialize hardware with configuration
            logger.info(TestExecutionConstants.LOG_HARDWARE_CONFIG_START)
            await self._hardware_services.initialize_hardware(test_config, hardware_config)
            logger.info(TestExecutionConstants.LOG_HARDWARE_CONFIG_SUCCESS)
3
            # Setup test environment
            await self._hardware_services.setup_test(test_config, hardware_config)

            # Execute test measurements
            measurements = await self._hardware_services.perform_force_test_sequence(
                test_config, hardware_config
            )
            logger.info(
                TestExecutionConstants.LOG_HARDWARE_TEST_COMPLETED.format(len(measurements))
            )

            return measurements

        except Exception as hardware_error:
            logger.error("Hardware test execution failed: {}", hardware_error)
            raise TestExecutionException(
                f"{TestExecutionConstants.HARDWARE_TEST_EXECUTION_ERROR_PREFIX}: {str(hardware_error)}"
            ) from hardware_error
