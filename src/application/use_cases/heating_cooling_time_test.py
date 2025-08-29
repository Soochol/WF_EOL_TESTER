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

            # 2. Get temperature settings
            activation_temp = test_config.activation_temperature
            standby_temp = test_config.standby_temperature
            logger.info(f"Temperature range: {standby_temp}°C ↔ {activation_temp}°C")

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
            logger.info(f"Setting up power supply: {test_config.voltage}V, {test_config.current}A")
            await power_service.set_voltage(test_config.voltage)
            await power_service.set_current(test_config.current)
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

            await mcu_service.set_upper_temperature(test_config.upper_temperature)
            await asyncio.sleep(test_config.mcu_command_stabilization)

            await mcu_service.set_fan_speed(test_config.fan_speed)
            await asyncio.sleep(test_config.mcu_command_stabilization)

            # 7. Initial temperature setup (set to standby)
            logger.info("Setting initial temperature to standby...")
            await mcu_service.start_standby_heating(
                operating_temp=activation_temp, standby_temp=standby_temp
            )
            await asyncio.sleep(test_config.mcu_command_stabilization)

            # Cool down to standby temperature
            await mcu_service.start_standby_cooling()
            logger.info(f"Initial cooling to standby temperature ({standby_temp}°C)...")
            await asyncio.sleep(test_config.mcu_temperature_stabilization)

            # Clear timing history (exclude initial setup)
            mcu_service.clear_timing_history()

            # 8. Perform test cycles
            heating_results = []
            cooling_results = []

            for i in range(command.repeat_count):
                logger.info(f"=== Test Cycle {i+1}/{command.repeat_count} ===")

                # 8.1 Heating measurement with power monitoring (standby → activation)
                logger.info(f"Heating: {standby_temp}°C → {activation_temp}°C")
                
                # Verify Power Monitor state before starting
                logger.info(f"Power Monitor object: {self._power_monitor} (type: {type(self._power_monitor)})")
                logger.info(f"Power Monitor is_monitoring: {self._power_monitor.is_monitoring()}")
                
                # Start power monitoring for heating
                logger.info("🔋 Starting power monitoring for HEATING cycle...")
                try:
                    await self._power_monitor.start_monitoring(interval=0.5)
                    logger.info("✅ Power monitoring started successfully for heating")
                except Exception as e:
                    logger.error(f"❌ Failed to start power monitoring for heating: {e}")
                    logger.exception("Power monitoring start exception details:")
                
                await mcu_service.start_standby_heating(
                    operating_temp=activation_temp, standby_temp=standby_temp
                )
                
                # Stop power monitoring and get data
                logger.info("🔋 Stopping power monitoring for heating cycle...")
                try:
                    heating_power_data = await self._power_monitor.stop_monitoring()
                    logger.info(f"✅ Power monitoring stopped for heating. Data: {heating_power_data}")
                except Exception as e:
                    logger.error(f"❌ Failed to stop power monitoring for heating: {e}")
                    heating_power_data = {"error": str(e), "sample_count": 0}

                # Get timing data from MCU
                timing_data = mcu_service.get_all_timing_data()
                if timing_data["heating_transitions"]:
                    latest_heating = timing_data["heating_transitions"][-1]
                    # Add power consumption data to timing result
                    latest_heating["power_consumption"] = heating_power_data
                    heating_results.append(latest_heating)
                    
                    avg_power = heating_power_data.get("average_power_watts", 0)
                    logger.info(f"Heating time: {latest_heating['total_duration_ms']:.1f}ms, Avg power: {avg_power:.1f}W")

                # Temperature stabilization
                await asyncio.sleep(test_config.mcu_temperature_stabilization)

                # 8.2 Cooling measurement with power monitoring (activation → standby)
                logger.info(f"Cooling: {activation_temp}°C → {standby_temp}°C")
                
                # Start power monitoring for cooling
                logger.info("🔋 Starting power monitoring for COOLING cycle...")
                try:
                    await self._power_monitor.start_monitoring(interval=0.5)
                    logger.info("✅ Power monitoring started successfully for cooling")
                except Exception as e:
                    logger.error(f"❌ Failed to start power monitoring for cooling: {e}")
                    logger.exception("Power monitoring start exception details:")
                
                await mcu_service.start_standby_cooling()
                
                # Stop power monitoring and get data
                logger.info("🔋 Stopping power monitoring for cooling cycle...")
                try:
                    cooling_power_data = await self._power_monitor.stop_monitoring()
                    logger.info(f"✅ Power monitoring stopped for cooling. Data: {cooling_power_data}")
                except Exception as e:
                    logger.error(f"❌ Failed to stop power monitoring for cooling: {e}")
                    cooling_power_data = {"error": str(e), "sample_count": 0}

                # Get timing data from MCU
                timing_data = mcu_service.get_all_timing_data()
                if timing_data["cooling_transitions"]:
                    latest_cooling = timing_data["cooling_transitions"][-1]
                    # Add power consumption data to timing result
                    latest_cooling["power_consumption"] = cooling_power_data
                    cooling_results.append(latest_cooling)
                    
                    avg_power = cooling_power_data.get("average_power_watts", 0)
                    logger.info(f"Cooling time: {latest_cooling['total_duration_ms']:.1f}ms, Avg power: {avg_power:.1f}W")

                # Temperature stabilization
                await asyncio.sleep(test_config.mcu_temperature_stabilization)

            # 9. Calculate statistics (including power consumption)
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
            
            # Power consumption statistics
            avg_heating_power = (
                sum(h["power_consumption"].get("average_power_watts", 0) for h in heating_results) / len(heating_results)
                if heating_results
                else 0
            )
            avg_cooling_power = (
                sum(c["power_consumption"].get("average_power_watts", 0) for c in cooling_results) / len(cooling_results)
                if cooling_results
                else 0
            )
            total_energy_heating = sum(h["power_consumption"].get("total_energy_wh", 0) for h in heating_results)
            total_energy_cooling = sum(c["power_consumption"].get("total_energy_wh", 0) for c in cooling_results)
            total_energy_consumed = total_energy_heating + total_energy_cooling

            # 10. Create result
            end_time = asyncio.get_event_loop().time()
            execution_duration = TestDuration.from_seconds(end_time - start_time)

            measurements = {
                "configuration": {
                    "activation_temperature": activation_temp,
                    "standby_temperature": standby_temp,
                    "voltage": test_config.voltage,
                    "current": test_config.current,
                    "fan_speed": test_config.fan_speed,
                    "repeat_count": command.repeat_count,
                },
                "heating_measurements": heating_results,
                "cooling_measurements": cooling_results,
                "statistics": {
                    "average_heating_time_ms": avg_heating_time,
                    "average_cooling_time_ms": avg_cooling_time,
                    "average_heating_ack_ms": avg_heating_ack,
                    "average_cooling_ack_ms": avg_cooling_ack,
                    "average_heating_power_watts": avg_heating_power,
                    "average_cooling_power_watts": avg_cooling_power,
                    "total_energy_heating_wh": total_energy_heating,
                    "total_energy_cooling_wh": total_energy_cooling,
                    "total_energy_consumed_wh": total_energy_consumed,
                    "power_ratio_heating_to_cooling": avg_heating_power / avg_cooling_power if avg_cooling_power > 0 else 0,
                    "total_cycles": command.repeat_count,
                    "total_heating_cycles": len(heating_results),
                    "total_cooling_cycles": len(cooling_results),
                },
            }

            logger.info("=== Test Summary ===")
            logger.info(f"Cycles completed: {command.repeat_count}")
            logger.info(f"Average heating time: {avg_heating_time:.1f}ms")
            logger.info(f"Average cooling time: {avg_cooling_time:.1f}ms")
            logger.info(f"Average heating power: {avg_heating_power:.1f}W")
            logger.info(f"Average cooling power: {avg_cooling_power:.1f}W")
            logger.info(f"Total energy consumed: {total_energy_consumed:.3f}Wh")

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
