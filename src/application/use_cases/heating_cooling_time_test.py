"""
Heating/Cooling Time Test Use Case

Measures the time taken for MCU heating and cooling operations.
Tests temperature transitions between standby and activation temperatures.
"""

import asyncio
from typing import Any, Dict, Optional

from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.power_monitor import PowerMonitor
from domain.enums.mcu_enums import TestMode
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import TestDuration


class HeatingCoolingTimeTestCommand:
    """Heating/Cooling Time Test Command"""

    def __init__(self, operator_id: str = "cli_user", repeat_count: int = 1):
        """
        Initialize test command

        Args:
            operator_id: ID of the operator running the test
            repeat_count: Number of heating/cooling cycles to perform
        """
        self.operator_id = operator_id
        self.repeat_count = repeat_count


class HeatingCoolingTimeTestResult:
    """Heating/Cooling Time Test Result"""

    def __init__(
        self,
        test_id: TestId,
        test_status: TestStatus,
        execution_duration: TestDuration,
        is_passed: bool,
        measurements: Dict[str, Any],
        error_message: Optional[str] = None,
    ):
        """
        Initialize test result

        Args:
            test_id: Unique test identifier
            test_status: Test execution status
            execution_duration: Total test execution time
            is_passed: Whether test passed or failed
            measurements: Timing measurements and statistics
            error_message: Error message if test failed
        """
        self.test_id = test_id
        self.test_status = test_status
        self.execution_duration = execution_duration
        self.is_passed = is_passed
        self.measurements = measurements
        self.error_message = error_message

    @property
    def heating_count(self) -> int:
        """Number of heating measurements"""
        return len(self.measurements.get("heating_measurements", []))

    @property
    def cooling_count(self) -> int:
        """Number of cooling measurements"""
        return len(self.measurements.get("cooling_measurements", []))

    def format_duration(self) -> str:
        """Format execution duration as string"""
        return f"{self.execution_duration.seconds:.3f}s"


class HeatingCoolingTimeTestUseCase:
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
        self._hardware_services = hardware_services
        self._configuration_service = configuration_service
        self._is_running = False
        self._power_monitor = None

    def is_running(self) -> bool:
        """Check if test is currently running"""
        return self._is_running

    async def execute(self, command: HeatingCoolingTimeTestCommand) -> HeatingCoolingTimeTestResult:
        """
        Execute Heating/Cooling Time Test

        Args:
            command: Test command with parameters

        Returns:
            HeatingCoolingTimeTestResult with timing measurements
        """
        test_id = TestId.generate()
        start_time = asyncio.get_event_loop().time()
        self._is_running = True

        logger.info(f"Starting Heating/Cooling Time Test - ID: {test_id}")
        logger.info(
            f"Test parameters - Operator: {command.operator_id}, Cycles: {command.repeat_count}"
        )

        try:
            # 1. Load configurations
            logger.info("Loading configurations...")
            await self._configuration_service.load_hardware_config()  # Validate config exists
            test_config = await self._configuration_service.load_test_config("default")
            
            # Load heating/cooling specific configuration
            hc_config = await self._configuration_service.load_heating_cooling_config()

            # 2. Get temperature settings from hc_config
            logger.info(f"Temperature range: {hc_config.standby_temperature}°C ↔ {hc_config.activation_temperature}°C")
            logger.info(f"Wait times - Heating: {hc_config.heating_wait_time}s, Cooling: {hc_config.cooling_wait_time}s, Stabilization: {hc_config.stabilization_wait_time}s")

            # 3. Connect hardware (Power Supply + MCU)
            logger.info("Connecting hardware...")
            power_service = self._hardware_services.power_service
            mcu_service = self._hardware_services.mcu_service

            await power_service.connect()
            await mcu_service.connect()
            
            # 3.1. Initialize Power Monitor
            self._power_monitor = PowerMonitor(power_service)
            logger.info("Power monitor initialized")

            # 4. Power supply setup
            logger.info(f"Setting up power supply: {hc_config.voltage}V, {hc_config.current}A")
            await power_service.set_voltage(hc_config.voltage)
            await power_service.set_current(hc_config.current)
            await power_service.enable_output()
            await asyncio.sleep(test_config.poweron_stabilization)

            # 5. Wait for MCU boot completion
            logger.info("Waiting for MCU boot completion...")
            await mcu_service.wait_boot_complete()
            await asyncio.sleep(test_config.mcu_boot_complete_stabilization)

            # 6. MCU setup
            logger.info("Setting up MCU...")
            await mcu_service.set_test_mode(TestMode.MODE_1)
            await asyncio.sleep(test_config.mcu_command_stabilization)

            await mcu_service.set_upper_temperature(hc_config.upper_temperature)
            await asyncio.sleep(test_config.mcu_command_stabilization)

            await mcu_service.set_fan_speed(hc_config.fan_speed)
            await asyncio.sleep(test_config.mcu_command_stabilization)

            # 7. Initial temperature setup (set to standby)
            logger.info("Setting initial temperature to standby...")
            await mcu_service.start_standby_heating(
                operating_temp=hc_config.activation_temperature, standby_temp=hc_config.standby_temperature
            )
            await asyncio.sleep(test_config.mcu_command_stabilization)

            # Cool down to standby temperature
            await mcu_service.start_standby_cooling()
            logger.info(f"Initial cooling to standby temperature ({hc_config.standby_temperature}°C)...")
            await asyncio.sleep(test_config.mcu_temperature_stabilization)

            # Clear timing history (exclude initial setup)
            mcu_service.clear_timing_history()

            # 8. Perform test cycles with full-cycle power monitoring
            heating_results = []
            cooling_results = []
            
            # Override repeat count from hc_config if different
            actual_repeat_count = hc_config.repeat_count if hc_config.repeat_count != 1 else command.repeat_count
            logger.info(f"Using repeat count: {actual_repeat_count} (config: {hc_config.repeat_count}, command: {command.repeat_count})")

            # Start power monitoring for ENTIRE test cycle
            if hc_config.power_monitoring_enabled:
                logger.info("🔋 Starting power monitoring for ENTIRE test cycle...")
                logger.info(f"Power Monitor object: {self._power_monitor} (type: {type(self._power_monitor)})")
                logger.info(f"Power Monitor is_monitoring: {self._power_monitor.is_monitoring()}")
                
                try:
                    await self._power_monitor.start_monitoring(interval=hc_config.power_monitoring_interval)
                    logger.info("✅ Power monitoring started successfully for full cycle")
                except Exception as e:
                    logger.error(f"❌ Failed to start power monitoring: {e}")
                    logger.exception("Power monitoring start exception details:")

            for i in range(actual_repeat_count):
                logger.info(f"=== Test Cycle {i+1}/{actual_repeat_count} ===")

                # 8.1 Heating phase (standby → activation)
                logger.info(f"Heating: {hc_config.standby_temperature}°C → {hc_config.activation_temperature}°C")
                await mcu_service.start_standby_heating(
                    operating_temp=hc_config.activation_temperature, standby_temp=hc_config.standby_temperature
                )
                
                # Wait after heating completion
                logger.info(f"Heating wait time: {hc_config.heating_wait_time}s")
                await asyncio.sleep(hc_config.heating_wait_time)

                # 8.2 Cooling phase (activation → standby)
                logger.info(f"Cooling: {hc_config.activation_temperature}°C → {hc_config.standby_temperature}°C")
                await mcu_service.start_standby_cooling()
                
                # Wait after cooling completion  
                logger.info(f"Cooling wait time: {hc_config.cooling_wait_time}s")
                await asyncio.sleep(hc_config.cooling_wait_time)

                # Stabilization wait between cycles
                if i < actual_repeat_count - 1:  # Don't wait after last cycle
                    logger.info(f"Stabilization wait time: {hc_config.stabilization_wait_time}s")
                    await asyncio.sleep(hc_config.stabilization_wait_time)

            # Stop power monitoring and get full cycle data
            full_cycle_power_data = {}
            if hc_config.power_monitoring_enabled:
                logger.info("🔋 Stopping power monitoring for full cycle...")
                try:
                    full_cycle_power_data = await self._power_monitor.stop_monitoring()
                    logger.info(f"✅ Power monitoring stopped. Data: {full_cycle_power_data}")
                except Exception as e:
                    logger.error(f"❌ Failed to stop power monitoring: {e}")
                    full_cycle_power_data = {"error": str(e), "sample_count": 0}

            # Get timing data from MCU for all cycles
            timing_data = mcu_service.get_all_timing_data()
            heating_results = timing_data.get("heating_transitions", [])
            cooling_results = timing_data.get("cooling_transitions", [])

            # 9. Calculate statistics (including full cycle power consumption)
            avg_heating_time = (
                sum(h["total_duration_ms"] for h in heating_results) / len(heating_results)
                if heating_results
                else 0
            )
            avg_cooling_time = (
                sum(c["total_duration_ms"] for c in cooling_results) / len(cooling_results)
                if cooling_results
                else 0
            )
            avg_heating_ack = (
                sum(h["ack_duration_ms"] for h in heating_results) / len(heating_results)
                if heating_results
                else 0
            )
            avg_cooling_ack = (
                sum(c["ack_duration_ms"] for c in cooling_results) / len(cooling_results)
                if cooling_results
                else 0
            )
            
            # Full cycle power consumption statistics
            full_cycle_avg_power = full_cycle_power_data.get("average_power_watts", 0)
            full_cycle_peak_power = full_cycle_power_data.get("peak_power_watts", 0)
            full_cycle_min_power = full_cycle_power_data.get("min_power_watts", 0)
            total_energy_consumed = full_cycle_power_data.get("total_energy_wh", 0)
            sample_count = full_cycle_power_data.get("sample_count", 0)
            duration_seconds = full_cycle_power_data.get("duration_seconds", 0)

            # 10. Create result
            end_time = asyncio.get_event_loop().time()
            execution_duration = TestDuration.from_seconds(end_time - start_time)

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
                "full_cycle_power_data": full_cycle_power_data,
                "statistics": {
                    "average_heating_time_ms": avg_heating_time,
                    "average_cooling_time_ms": avg_cooling_time,
                    "average_heating_ack_ms": avg_heating_ack,
                    "average_cooling_ack_ms": avg_cooling_ack,
                    "full_cycle_average_power_watts": full_cycle_avg_power,
                    "full_cycle_peak_power_watts": full_cycle_peak_power,
                    "full_cycle_min_power_watts": full_cycle_min_power,
                    "total_energy_consumed_wh": total_energy_consumed,
                    "power_sample_count": sample_count,
                    "measurement_duration_seconds": duration_seconds,
                    "total_cycles": actual_repeat_count,
                    "total_heating_cycles": len(heating_results),
                    "total_cooling_cycles": len(cooling_results),
                },
            }

            logger.info("=== Test Summary ===")
            logger.info(f"Cycles completed: {actual_repeat_count}")
            logger.info(f"Average heating time: {avg_heating_time:.1f}ms")
            logger.info(f"Average cooling time: {avg_cooling_time:.1f}ms")
            logger.info(f"Full cycle average power: {full_cycle_avg_power:.1f}W")
            logger.info(f"Full cycle peak power: {full_cycle_peak_power:.1f}W")
            logger.info(f"Total energy consumed: {total_energy_consumed:.3f}Wh")
            logger.info(f"Power samples collected: {sample_count}")
            logger.info(f"Measurement duration: {duration_seconds:.1f}s")

            result = HeatingCoolingTimeTestResult(
                test_id=test_id,
                test_status=TestStatus.COMPLETED,
                execution_duration=execution_duration,
                is_passed=True,
                measurements=measurements,
                error_message=None,
            )

            return result

        except Exception as e:
            error_msg = f"Heating/Cooling Time Test failed: {str(e)}"
            logger.error(error_msg)

            end_time = asyncio.get_event_loop().time()
            execution_duration = TestDuration.from_seconds(end_time - start_time)

            return HeatingCoolingTimeTestResult(
                test_id=test_id,
                test_status=TestStatus.ERROR,
                execution_duration=execution_duration,
                is_passed=False,
                measurements={},
                error_message=error_msg,
            )

        finally:
            # Hardware cleanup
            try:
                logger.info("Cleaning up hardware...")
                power_service = self._hardware_services.power_service
                mcu_service = self._hardware_services.mcu_service

                await power_service.disable_output()
                await power_service.disconnect()
                await mcu_service.disconnect()
            except Exception as cleanup_error:
                logger.warning(f"Hardware cleanup warning: {cleanup_error}")

            self._is_running = False
            logger.info(f"Heating/Cooling Time Test completed - ID: {test_id}")

