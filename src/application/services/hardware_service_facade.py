"""
Hardware Service Facade

Facade pattern implementation to group and simplify hardware service interactions.
"""

import asyncio
from typing import Dict, Union, Any

from loguru import logger

from application.interfaces.hardware.digital_input import (
    DigitalInputService,
)
from application.interfaces.hardware.loadcell import (
    LoadCellService,
)
from application.interfaces.hardware.mcu import (
    MCUService,
    TestMode,
)
from application.interfaces.hardware.power import (
    PowerService,
)
from application.interfaces.hardware.robot import (
    RobotService,
)
from domain.exceptions.hardware_exceptions import (
    HardwareConnectionException,
)
from domain.value_objects.measurements import (
    TestMeasurements,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
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
        *,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_input_service: DigitalInputService,
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service
        self._digital_input = digital_input_service

    async def connect_all_hardware(self) -> None:
        """Connect all required hardware"""
        logger.info("Connecting hardware...")

        connection_tasks = []
        hardware_names = []

        # Check and connect each hardware service
        if not await self._robot.is_connected():
            connection_tasks.append(self._robot.connect())
            hardware_names.append("Robot")

        if not await self._mcu.is_connected():
            connection_tasks.append(self._mcu.connect())
            hardware_names.append("MCU")

        if not await self._power.is_connected():
            connection_tasks.append(self._power.connect())
            hardware_names.append("Power")

        if not await self._loadcell.is_connected():
            connection_tasks.append(self._loadcell.connect())
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
                ) from e
        else:
            logger.info("All hardware already connected")

    async def startup_initialization(self) -> None:
        """
        Perform one-time startup initialization including robot homing
        
        This method should be called once when the application starts
        to perform essential initialization tasks like robot homing.
        """
        logger.info("Performing startup initialization...")
        
        try:
            # Connect robot if not already connected
            if not await self._robot.is_connected():
                logger.info("Connecting robot for startup initialization...")
                await self._robot.connect()
            
            # Enable servo for primary axis - required before any motion operations
            primary_axis = await self._robot.get_primary_axis_id()
            logger.info("Enabling servo for primary axis %d...", primary_axis)
            await self._robot.enable_servo(primary_axis)
            
            # Perform robot homing - this is the main purpose of startup initialization
            logger.info("Performing robot homing...")
            # Home primary axis using parameters from .mot file
            primary_axis = await self._robot.get_primary_axis_id()
            await self._robot.home_axis(primary_axis)
            
            logger.info("Startup initialization completed successfully")
            
        except Exception as e:
            logger.error("Startup initialization failed: %s", e)
            raise HardwareConnectionException(
                f"Failed during startup initialization: {str(e)}",
                details={"operation": "startup_initialization"},
            ) from e

    async def initialize_hardware(
        self,
        config: TestConfiguration,
    ) -> None:
        """Initialize all hardware with configuration settings"""
        logger.info("Initializing hardware with configuration...")

        try:
            # Initialize power settings
            await self._power.set_voltage(config.voltage)
            await self._power.set_current_limit(config.current)
            await self._power.disable_output()  # Start with output disabled
            await asyncio.sleep(config.power_stabilization)

            # # Initialize MCU settings
            # await self._mcu.set_upper_temperature(config.upper_temperature)
            # await self._mcu.set_fan_speed(config.fan_speed)

            # Initialize robot position using test configuration
            await self._robot.move_absolute(
                axis=config.axis_id,
                position=config.initial_position,
                velocity=config.velocity,
                acceleration=config.acceleration,
                deceleration=config.deceleration,
            )
            await asyncio.sleep(config.stabilization_delay)

            # Zero the load cell
            await self._loadcell.zero_calibration()
            await asyncio.sleep(config.loadcell_zero_delay)

            logger.info("Hardware initialization completed")

        except Exception as e:
            raise HardwareConnectionException(
                f"Failed to initialize hardware: {str(e)}",
                details={"config": config.to_dict()},
            ) from e

    async def perform_force_test_sequence(
        self,
        config: TestConfiguration,
    ) -> TestMeasurements:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        logger.info("Starting force test sequence...")
        total_tests = len(config.temperature_list) * len(config.stroke_positions)
        logger.info(
            "Test matrix: %s×%s = %s measurements",
            len(config.temperature_list),
            len(config.stroke_positions),
            total_tests,
        )

        measurements_dict: Dict[float, Dict[float, Dict[str, Any]]] = {}

        try:
            # Outer loop: Iterate through temperature list
            for temp_idx, temperature in enumerate(config.temperature_list):
                logger.info(
                    "Setting temperature to %s°C (%s/%s)",
                    temperature,
                    temp_idx + 1,
                    len(config.temperature_list),
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

                    # Move to position using test configuration
                    await self._robot.move_absolute(
                        axis=config.axis_id,
                        position=position,
                        velocity=config.velocity,
                        acceleration=config.acceleration,
                        deceleration=config.deceleration,
                    )
                    await asyncio.sleep(config.stabilization_delay)

                    # Take measurements
                    force = await self._loadcell.read_force()
                    # Get current temperature from MCU
                    current_temp = await self._mcu.get_temperature()
                    # Get current position from robot
                    current_position = await self._robot.get_position(config.axis_id)

                    # Store measurement data using TestMeasurements structure
                    if temperature not in measurements_dict:
                        measurements_dict[temperature] = {}
                    measurements_dict[temperature][position] = {
                        "temperature": current_temp,
                        "stroke": current_position,
                        "force": force.value,
                    }

                    # # Allow stabilization between positions (if not last position)
                    # if pos_idx < len(config.stroke_positions) - 1:
                    #     await asyncio.sleep(config.stabilization_delay)

                logger.info(f"Completed all positions for temperature {temperature}°C")

            # Convert to TestMeasurements value object
            measurements = TestMeasurements.from_legacy_dict(measurements_dict)

            logger.info(
                "Force test sequence completed with %s measurements",
                measurements.get_total_measurement_count(),
            )
            logger.info(
                "Test matrix completed: %s temperatures × %s positions",
                measurements.get_temperature_count(),
                len(config.stroke_positions),
            )
            return measurements

        except Exception as e:
            logger.error(f"Force test sequence failed: {e}")
            raise

    async def return_to_safe_position(
        self,
        config: TestConfiguration,
    ) -> None:
        """Return robot to safe standby position"""
        try:
            # Return to safe position using test configuration
            await self._robot.move_absolute(
                axis=config.axis_id,
                position=config.initial_position,
                velocity=config.velocity,
                acceleration=config.acceleration,
                deceleration=config.deceleration,
            )
            logger.info(f"Robot returned to safe position: {config.initial_position}mm")
        except Exception as e:
            logger.error(f"Failed to return to safe position: {e}")
            raise

    async def shutdown_hardware(self) -> None:
        """Safely shutdown all hardware"""
        logger.info("Shutting down hardware...")

        shutdown_tasks = []

        try:
            # Disable power output first for safety
            await self._power.disable_output()

            # Disable servo for primary axis for safety before disconnection
            if await self._robot.is_connected():
                try:
                    primary_axis = await self._robot.get_primary_axis_id()
                    logger.info("Disabling servo for primary axis %d for safe shutdown...", primary_axis)
                    await self._robot.disable_servo(primary_axis)
                    logger.info("Primary axis servo disabled")
                except Exception as servo_error:
                    logger.error("Failed to disable servo during shutdown: %s", servo_error)
                    # Continue with shutdown even if servo disable fails

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
        self,
        config: TestConfiguration,
    ) -> None:
        """Setup hardware for test execution"""
        logger.info("Setting up test...")

        try:
            # Enable power output
            await self._power.enable_output()
            logger.info(f"Power enabled: {config.voltage}V, {config.current}A")

            # Wait for MCU boot complete signal (directly using MCU service)
            logger.info("Waiting for MCU boot complete signal...")
            await asyncio.wait_for(
                self._mcu.wait_boot_complete(),
                timeout=config.timeout_seconds,
            )
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
            await self.set_lma_standby(config)
            logger.info("LMA standby sequence set")

            logger.info("Test setup completed successfully")

        except asyncio.TimeoutError as e:
            raise HardwareConnectionException(
                "MCU boot timeout during test setup",
                details={"timeout": config.timeout_seconds},
            ) from e
        except Exception as e:
            raise HardwareConnectionException(
                f"Failed to setup test: {str(e)}",
                details={"config": config.to_dict()},
            ) from e

    async def teardown_test(
        self,
        config: TestConfiguration,
    ) -> None:
        """Teardown test and return hardware to safe state"""
        logger.info("Tearing down test...")

        try:
            # Return robot to safe standby position
            logger.info(f"Returning robot to safe position: {config.initial_position}mm")
            await self._robot.move_absolute(
                axis=config.axis_id,
                position=config.initial_position,
                velocity=config.velocity,
                acceleration=config.acceleration,
                deceleration=config.deceleration,
            )
            logger.info("Robot returned to safe position")

            # Reset MCU temperature to default
            await self._mcu.set_upper_temperature(config.upper_temperature)
            logger.info(f"MCU temperature reset to default: {config.upper_temperature}°C")

            # set lma standby sequence
            await self.set_lma_standby(config)
            logger.info("LMA standby sequence set for teardown")

            # Power teardown - disable output for safety
            logger.info("Disabling power output for safety...")
            await self._power.disable_output()
            logger.info("Power output disabled")

            logger.info("Test teardown completed successfully")

        except Exception as e:
            logger.error(f"Test teardown failed: {e}")
            # Don't re-raise to allow cleanup to continue

    async def set_lma_standby(
        self,
        config: TestConfiguration,
    ) -> None:
        """Set LMA standby sequence - coordinate MCU and Robot for LMA standby state"""
        logger.info("Setting LMA standby sequence...")

        try:
            # MCU start standby heating
            # Calculate standby temperature: minimum of configured standby temp and test temperature list minimum
            if not config.temperature_list:
                raise ValueError("Temperature list cannot be empty")

            min_test_temp = min(config.temperature_list)
            calculated_standby_temp = min(config.standby_temperature, min_test_temp)

            await self._mcu.start_standby_heating(
                operating_temp=config.activation_temperature,
                standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
            )
            logger.info(
                "MCU standby heating started - operating: %s°C, standby: %s°C",
                config.activation_temperature,
                calculated_standby_temp,
            )

            # Robot to max stroke position using test configuration
            await self._robot.move_absolute(
                axis=config.axis_id,
                position=config.max_stroke,
                velocity=config.velocity,
                acceleration=config.acceleration,
                deceleration=config.deceleration,
            )
            logger.info(f"Robot moved to max stroke position: {config.max_stroke}mm")

            # Wait for standby heating stabilization
            await asyncio.sleep(config.standby_stabilization)
            logger.info(f"Standby heating stabilized after {config.standby_stabilization}s")

            # Robot to initial position using test configuration
            await self._robot.move_absolute(
                axis=config.axis_id,
                position=config.initial_position,
                velocity=config.velocity,
                acceleration=config.acceleration,
                deceleration=config.deceleration,
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
            ) from e

    def get_hardware_services(
        self,
    ) -> Dict[
        str, Union[RobotService, MCUService, PowerService, LoadCellService, DigitalInputService]
    ]:
        """Get direct access to hardware services (for advanced usage)"""
        return {
            "robot": self._robot,
            "mcu": self._mcu,
            "power": self._power,
            "loadcell": self._loadcell,
        }
