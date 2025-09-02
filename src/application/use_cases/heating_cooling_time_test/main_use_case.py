"""
Heating/Cooling Time Test Main Use Case

Main orchestrator for heating/cooling time test use case.
Coordinates hardware setup, test execution, and result processing.
"""

from loguru import logger

from application.use_cases.common.base_use_case import BaseUseCase
from application.services.core.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from domain.enums.test_status import TestStatus

from .command import HeatingCoolingTimeTestCommand
from .result import HeatingCoolingTimeTestResult
from .hardware_setup_service import HardwareSetupService
from .test_cycle_executor import TestCycleExecutor
from .statistics_calculator import StatisticsCalculator


class HeatingCoolingTimeTestUseCase(BaseUseCase):
    """
    Heating/Cooling Time Test Use Case

    Measures MCU heating and cooling performance by testing temperature
    transitions between standby and activation temperatures.
    """

    def __init__(
        self,
        hardware_services: HardwareServiceFacade,
        configuration_service: ConfigurationService,
    ):
        """
        Initialize Heating/Cooling Time Test Use Case

        Args:
            hardware_services: Hardware service facade
            configuration_service: Configuration service
        """
        super().__init__("Heating/Cooling Time Test")
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service
        self._hardware_setup = HardwareSetupService(hardware_services)

    async def _execute_implementation(
        self, 
        command: HeatingCoolingTimeTestCommand, 
        context
    ) -> HeatingCoolingTimeTestResult:
        """
        Execute Heating/Cooling Time Test implementation

        Args:
            command: Test command with parameters
            context: Execution context

        Returns:
            HeatingCoolingTimeTestResult with timing measurements
        """
        logger.info(f"Test parameters - Operator: {command.operator_id}, Cycles: {command.repeat_count}")

        # 1. Load configurations
        logger.info("Loading configurations...")
        await self._configuration_service.load_hardware_config()  # Validate config exists
        hc_config = await self._configuration_service.load_heating_cooling_config()

        # 2. Connect and setup hardware
        await self._hardware_setup.connect_hardware()
        await self._hardware_setup.setup_power_supply(
            hc_config.voltage, hc_config.current, hc_config.poweron_stabilization
        )
        await self._hardware_setup.setup_mcu(hc_config)
        await self._hardware_setup.initialize_temperature(hc_config)

        # 3. Execute test cycles
        test_executor = TestCycleExecutor(self._hardware_services, self._hardware_setup.power_monitor)
        
        # Determine actual repeat count
        actual_repeat_count = hc_config.repeat_count if hc_config.repeat_count != 1 else command.repeat_count
        logger.info(f"Using repeat count: {actual_repeat_count} (config: {hc_config.repeat_count}, command: {command.repeat_count})")
        
        cycle_results = await test_executor.execute_test_cycles(hc_config, actual_repeat_count)
        
        # 4. Process results
        timing_data = cycle_results["timing_data"]
        power_data = cycle_results["power_data"]
        
        heating_results = timing_data["heating_results"]
        cooling_results = timing_data["cooling_results"]
        
        # 5. Calculate statistics
        statistics = StatisticsCalculator.calculate_statistics(
            heating_results, cooling_results, power_data, actual_repeat_count
        )
        
        # Log summary
        StatisticsCalculator.log_summary(statistics)

        # 6. Create result
        measurements = {
            "configuration": {
                "activation_temperature": hc_config.activation_temperature,
                "standby_temperature": hc_config.standby_temperature,
                "voltage": hc_config.voltage,
                "current": hc_config.current,
                "fan_speed": hc_config.fan_speed,
                "repeat_count": actual_repeat_count,
                "heating_wait_time": hc_config.heating_wait_time,
                "cooling_wait_time": hc_config.cooling_wait_time,
                "stabilization_wait_time": hc_config.stabilization_wait_time,
                "power_monitoring_interval": hc_config.power_monitoring_interval,
                "power_monitoring_enabled": hc_config.power_monitoring_enabled,
            },
            "heating_measurements": heating_results,
            "cooling_measurements": cooling_results,
            "full_cycle_power_data": power_data,
            "statistics": statistics,
        }

        return HeatingCoolingTimeTestResult(
            test_status=TestStatus.COMPLETED,
            is_success=True,
            measurements=measurements,
            error_message=None,
        )

    def _create_failure_result(
        self, 
        command: HeatingCoolingTimeTestCommand, 
        context, 
        execution_duration, 
        error_message: str
    ) -> HeatingCoolingTimeTestResult:
        """
        Create a failure result when execution fails

        Args:
            command: Original command that failed
            context: Execution context
            execution_duration: How long execution took before failing
            error_message: Error description
            
        Returns:
            HeatingCoolingTimeTestResult indicating failure
        """
        return HeatingCoolingTimeTestResult(
            test_status=TestStatus.ERROR,
            is_success=False,
            measurements={},
            error_message=f"Heating/Cooling Time Test failed: {error_message}",
        )

    async def cleanup(self) -> None:
        """
        Clean up resources after test execution
        """
        try:
            await self._hardware_setup.cleanup_hardware()
        except Exception as cleanup_error:
            logger.warning(f"Cleanup warning in main use case: {cleanup_error}")

    async def execute(self, command: HeatingCoolingTimeTestCommand) -> HeatingCoolingTimeTestResult:
        """
        Execute the heating/cooling time test with proper cleanup

        Args:
            command: Test command with parameters
            
        Returns:
            HeatingCoolingTimeTestResult with timing measurements
        """
        try:
            result = await super().execute(command)
            # Cast to the correct type since BaseUseCase.execute returns BaseResult
            return result  # type: ignore
        finally:
            await self.cleanup()
