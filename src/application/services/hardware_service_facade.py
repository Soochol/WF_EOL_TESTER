"""
Hardware Service Facade

Facade pattern implementation to group and simplify hardware service interactions.
"""

import asyncio
from typing import Dict, List

from loguru import logger

from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService, TestMode
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.hardware_configuration import HardwareConfiguration
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.measurements import (
    TestMeasurements,
    PositionMeasurements,
    MeasurementReading,
)


class HardwareServiceFacade:
    """
    Facade for managing all hardware services together

    This class provides a simplified interface for common hardware operations
    and manages the complexity of coordinating multiple hardware services.
    """

    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service

    async def connect_all_hardware(self, hardware_config: HardwareConfiguration) -> None:
        """Connect all required hardware"""
        logger.info("Connecting hardware...")

        connection_tasks = []
        hardware_names = []

        # Check and connect each hardware service
        if not await self._robot.is_connected():
            connection_tasks.append(self._robot.connect(hardware_config.robot))
            hardware_names.append("Robot")

        if not await self._mcu.is_connected():
            connection_tasks.append(self._mcu.connect(hardware_config.mcu))
            hardware_names.append("MCU")

        if not await self._power.is_connected():
            connection_tasks.append(self._power.connect(hardware_config.power))
            hardware_names.append("Power")

        if not await self._loadcell.is_connected():
            connection_tasks.append(self._loadcell.connect(hardware_config.loadcell))
            hardware_names.append("LoadCell")

        # Execute all connections concurrently
        if connection_tasks:
            try:
                await asyncio.gather(*connection_tasks)
                logger.info(f"Successfully connected: {', '.join(hardware_names)}")
            except Exception as e:
                raise HardwareConnectionException(
                    f"Failed to connect hardware: {str(e)}",
                    details={"failed_hardware": hardware_names},
                )
        else:
            logger.info("All hardware already connected")

    async def initialize_hardware(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> None:
        """Initialize all hardware with configuration settings"""
        logger.info("Initializing hardware with configuration...")

        try:
            # Initialize power settings
            await self._power.set_voltage(config.voltage)
            await self._power.set_current_limit(config.current)
            await self._power.enable_output(False)  # Start with output disabled
            await asyncio.sleep(config.power_stabilization)

            # # Initialize MCU settings
            # await self._mcu.set_upper_temperature(config.upper_temperature)
            # await self._mcu.set_fan_speed(config.fan_speed)

            # Initialize robot position using robot configuration
            await self._robot.move_absolute(
                axis=hardware_config.robot.axis,
                position=config.initial_position,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            await asyncio.sleep(config.stabilization_delay)

            # Zero the load cell
            await self._loadcell.zero()
            await asyncio.sleep(config.loadcell_zero_delay)

            logger.info("Hardware initialization completed")

        except Exception as e:
            await self._power.enable_output(False)  # Safety: disable power on error
            raise HardwareConnectionException(
                f"Failed to initialize hardware: {str(e)}", details={"config": config.to_dict()}
            )

    async def perform_force_test_sequence(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> TestMeasurements:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        logger.info("Starting force test sequence...")
        logger.info(
            f"Test matrix: {len(config.temperature_list)} temperatures × {len(config.stroke_positions)} positions = {len(config.temperature_list) * len(config.stroke_positions)} total measurements"
        )

        measurements_dict = {}

        try:
            # Outer loop: Iterate through temperature list
            for temp_idx, temperature in enumerate(config.temperature_list):
                logger.info(
                    f"Setting temperature to {temperature}°C ({temp_idx+1}/{len(config.temperature_list)})"
                )

                # Set MCU temperature for this test cycle
                await self._mcu.set_temperature(temperature)
                logger.info(f"Temperature set to {temperature}°C, waiting for stabilization...")

                # Wait for temperature stabilization
                await asyncio.sleep(config.temperature_stabilization)
                logger.info(f"Temperature stabilized at {temperature}°C")

                # Inner loop: Iterate through stroke positions
                for pos_idx, position in enumerate(config.stroke_positions):
                    logger.info(
                        f"Measuring at temp {temperature}°C, position {position}mm ({pos_idx+1}/{len(config.stroke_positions)})"
                    )

                    # Move to position using robot configuration
                    await self._robot.move_absolute(
                        axis=hardware_config.robot.axis,
                        position=position,
                        velocity=hardware_config.robot.velocity,
                        acceleration=hardware_config.robot.acceleration,
                        deceleration=hardware_config.robot.deceleration,
                    )
                    await asyncio.sleep(config.stabilization_delay)

                    # Take measurements
                    force = await self._loadcell.read_force()
                    # measured_temperature = await self._mcu.read_temperature()

                    # # Get power measurements
                    # power_data = await self._power.measure_output()

                    # Store measurement data using TestMeasurements structure
                    if temperature not in measurements_dict:
                        measurements_dict[temperature] = {}
                    measurements_dict[temperature][position] = {"force": force}

                    # # Allow stabilization between positions (if not last position)
                    # if pos_idx < len(config.stroke_positions) - 1:
                    #     await asyncio.sleep(config.stabilization_delay)

                logger.info(f"Completed all positions for temperature {temperature}°C")

            # Convert to TestMeasurements value object
            measurements = TestMeasurements.from_legacy_dict(measurements_dict)

            logger.info(
                f"Force test sequence completed with {measurements.get_total_measurement_count()} measurements"
            )
            logger.info(
                f"Test matrix completed: {measurements.get_temperature_count()} temperatures × {len(config.stroke_positions)} positions"
            )
            return measurements

        except Exception as e:
            logger.error(f"Force test sequence failed: {e}")
            raise

    async def return_to_safe_position(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> None:
        """Return robot to safe standby position"""
        try:
            # Return to safe position using robot configuration
            await self._robot.move_absolute(
                axis=0,  # Default axis
                position=config.standby_position,
                velocity=100.0,  # Default velocity
                acceleration=100.0,  # Default acceleration
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info(f"Robot returned to safe position: {config.standby_position}mm")
        except Exception as e:
            logger.error(f"Failed to return to safe position: {e}")
            raise

    async def shutdown_hardware(self) -> None:
        """Safely shutdown all hardware"""
        logger.info("Shutting down hardware...")

        shutdown_tasks = []

        try:
            # Disable power output first for safety
            await self._power.enable_output(False)

            # Add disconnect tasks
            if await self._robot.is_connected():
                shutdown_tasks.append(self._robot.disconnect())

            if await self._mcu.is_connected():
                shutdown_tasks.append(self._mcu.disconnect())

            if await self._power.is_connected():
                shutdown_tasks.append(self._power.disconnect())

            if await self._loadcell.is_connected():
                shutdown_tasks.append(self._loadcell.disconnect())

            # Execute all disconnections concurrently
            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)

            logger.info("Hardware shutdown completed")

        except Exception as e:
            logger.error(f"Error during hardware shutdown: {e}")
            # Don't re-raise as this is cleanup

    async def get_hardware_status(self) -> Dict[str, bool]:
        """Get connection status of all hardware"""
        return {
            "robot": await self._robot.is_connected(),
            "mcu": await self._mcu.is_connected(),
            "power": await self._power.is_connected(),
            "loadcell": await self._loadcell.is_connected(),
        }

    async def setup_test(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> None:
        """Setup hardware for test execution"""
        logger.info("Setting up test...")

        try:
            # Enable power output
            await self._power.enable_output(True)
            logger.info(f"Power enabled: {config.voltage}V, {config.current}A")

            # Wait for MCU boot complete signal (directly using MCU service)
            logger.info("Waiting for MCU boot complete signal...")
            await asyncio.wait_for(self._mcu.wait_boot_complete(), timeout=config.timeout_seconds)
            logger.info("MCU boot complete signal received")

            # Enter test mode 1 (always executed)
            await self._mcu.set_test_mode(TestMode.MODE_1)
            logger.info("MCU set to test mode 1")

            # MCU configuration (upper temperature, fan speed)
            upper_temp = config.upper_temperature
            fan_speed = config.fan_speed

            await self._mcu.set_upper_temperature(upper_temp)
            await self._mcu.set_fan_speed(fan_speed)
            logger.info(f"MCU configured: upper_temp={upper_temp}°C, fan_speed={fan_speed}%")

            # Set LMA standby sequence
            await self._hardware.set_lma_standby(config)
            logger.info("LMA standby sequence set")

            logger.info("Test setup completed successfully")

        except asyncio.TimeoutError:
            await self._power.enable_output(False)  # Safety: disable power on timeout
            raise HardwareConnectionException(
                "MCU boot timeout during test setup", details={"timeout": config.timeout_seconds}
            )
        except Exception as e:
            await self._power.enable_output(False)  # Safety: disable power on error
            raise HardwareConnectionException(
                f"Failed to setup test: {str(e)}", details={"config": config.to_dict()}
            )

    async def teardown_test(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> None:
        """Teardown test and return hardware to safe state"""
        logger.info("Tearing down test...")

        try:
            # Return robot to safe standby position
            logger.info(f"Returning robot to safe position: {config.standby_position}mm")
            await self._robot.move_absolute(
                axis=0,  # Default axis
                position=config.standby_position,
                velocity=100.0,  # Default velocity
                acceleration=100.0,  # Default acceleration
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info("Robot returned to safe position")

            # MCU teardown - exit test mode, reset to normal temperature
            logger.info("Resetting MCU to normal state...")
            if hasattr(self._mcu, "set_test_mode"):
                # Try to set to normal mode (MODE_0 or similar)
                try:
                    await self._mcu.set_test_mode(TestMode.MODE_0)
                    logger.info("MCU test mode reset to normal")
                except:
                    logger.warning("Could not reset MCU test mode")

            # Reset MCU temperature to default
            await self._mcu.set_upper_temperature(config.upper_temperature)
            logger.info(f"MCU temperature reset to default: {config.upper_temperature}°C")

            # set lma standby sequence
            await self.set_lma_standby(config)
            logger.info("LMA standby sequence set for teardown")

            # Power teardown - disable output for safety
            logger.info("Disabling power output for safety...")
            await self._power.enable_output(False)
            logger.info("Power output disabled")

            logger.info("Test teardown completed successfully")

        except Exception as e:
            logger.error(f"Test teardown failed: {e}")
            # Don't re-raise to allow cleanup to continue
            # But ensure power is disabled for safety
            try:
                await self._power.enable_output(False)
                logger.info("Power output disabled during teardown error handling")
            except:
                logger.error("Failed to disable power output during teardown error")

    async def set_lma_standby(
        self, config: TestConfiguration, hardware_config: HardwareConfiguration
    ) -> None:
        """Set LMA standby sequence - coordinate MCU and Robot for LMA standby state"""
        logger.info("Setting LMA standby sequence...")

        try:
            # MCU start standby heating
            await self._mcu.start_standby_heating()
            logger.info("MCU standby heating started")

            # Robot to max stroke position using robot configuration
            await self._robot.move_absolute(
                axis=hardware_config.robot.axis,
                position=config.max_stroke,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info(f"Robot moved to max stroke position: {config.max_stroke}mm")

            # Robot to initial position using robot configuration
            await self._robot.move_absolute(
                axis=hardware_config.robot.axis,
                position=config.initial_position,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info(f"Robot moved to initial position: {config.initial_position}mm")

            # MCU start standby cooling
            await self._mcu.start_standby_cooling()
            logger.info("MCU standby cooling started")

            logger.info("LMA standby sequence completed successfully")

        except Exception as e:
            logger.error(f"LMA standby sequence failed: {e}")
            raise HardwareConnectionException(
                f"Failed to set LMA standby sequence: {str(e)}",
                details={"config": config.to_dict()},
            )

    def get_hardware_services(self) -> Dict[str, object]:
        """Get direct access to hardware services (for advanced usage)"""
        return {
            "robot": self._robot,
            "mcu": self._mcu,
            "power": self._power,
            "loadcell": self._loadcell,
        }
