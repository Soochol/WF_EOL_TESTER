"""
Hardware Test Executor

Executes test sequences and manages test lifecycle operations.
Extracted from HardwareServiceFacade for single responsibility compliance.
"""

import asyncio
from typing import Any, Dict

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService, TestMode
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.test_configuration import TestConfiguration


class HardwareTestExecutor:
    """
    Manages test execution sequences and lifecycle operations
    
    Handles test setup, execution, and teardown processes.
    """
    
    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_io_service: DigitalIOService,
        verification_service=None,  # Will be injected later to avoid circular dependency
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service
        self._digital_io = digital_io_service
        self._verification_service = verification_service

    def set_verification_service(self, verification_service) -> None:
        """Set verification service after initialization to avoid circular dependency"""
        self._verification_service = verification_service

    async def setup_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Setup hardware for test execution"""
        logger.info("Setting up test...")

        try:
            # Enable power output
            await self._power.enable_output()
            logger.info(f"Power enabled: {test_config.voltage}V, {test_config.current}A")
            logger.info(f"⏳ Power stabilization delay: {test_config.poweron_stabilization}s...")
            await asyncio.sleep(test_config.poweron_stabilization)

            # Wait for MCU boot complete signal (directly using MCU service)
            logger.info("Waiting for MCU boot complete signal...")
            await asyncio.wait_for(
                self._mcu.wait_boot_complete(),
                timeout=test_config.timeout_seconds,
            )
            logger.info(
                f"MCU boot complete stabilization delay: {test_config.mcu_boot_complete_stabilization}s..."
            )
            await asyncio.sleep(
                test_config.mcu_boot_complete_stabilization
            )  # MCU boot complete stabilization delay

            logger.info("MCU boot complete signal received")

            # Enter test mode 1 (always executed)
            await self._mcu.set_test_mode(TestMode.MODE_1)
            logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
            await asyncio.sleep(test_config.mcu_command_stabilization)  # MCU stabilization delay
            logger.info("MCU set to test mode 1")

            # Set LMA standby sequence
            await self.set_lma_standby(test_config, hardware_config)
            logger.info("LMA standby sequence set")

            logger.info("Test setup completed successfully")

        except asyncio.TimeoutError as e:
            raise HardwareConnectionException(
                "MCU boot timeout during test setup",
                details={"timeout": test_config.timeout_seconds},
            ) from e
        except Exception as e:
            logger.debug(f"Test setup failed with config: {test_config.to_dict()}")
            raise HardwareConnectionException(
                f"Failed to setup test: {str(e)}",
                details={
                    "test_mode": "MODE_1",
                    "temperature_count": len(test_config.temperature_list),
                },
            ) from e

    async def set_lma_standby(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Set LMA standby sequence - coordinate MCU and Robot for LMA standby state"""
        logger.info("Starting LMA standby sequence...")

        try:
            # MCU start standby heating
            logger.info("Starting MCU standby heating...")

            # Calculate standby temperature: minimum of configured standby temp and test temperature list minimum
            if not test_config.temperature_list:
                raise ValueError("Temperature list cannot be empty")

            try:
                # MCU configuration before standby heating
                await self._mcu.set_upper_temperature(test_config.upper_temperature)
                logger.info(f"Upper temperature set to {test_config.upper_temperature}°C")
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                await self._mcu.set_fan_speed(test_config.fan_speed)
                logger.info(f"Fan speed set to {test_config.fan_speed}")
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                await self._mcu.start_standby_heating(
                    operating_temp=test_config.activation_temperature,
                    standby_temp=test_config.standby_temperature,
                )
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(
                    f"MCU standby heating started - operating: {test_config.activation_temperature}°C, standby: {test_config.standby_temperature}°C"
                )

                # Verify MCU temperature reached operating temperature
                if self._verification_service:
                    await self._verification_service.verify_mcu_temperature(test_config.activation_temperature, test_config)
                    logger.info(
                        f"Temperature verification passed for operating temperature {test_config.activation_temperature}°C"
                    )
            except Exception as e:
                logger.error(f"MCU standby heating failed - {e}")
                raise

            # Robot to max stroke position
            logger.info("Moving robot to max stroke position...")
            try:
                await self._robot.move_absolute(
                    position=test_config.max_stroke,
                    axis_id=hardware_config.robot.axis_id,
                    velocity=test_config.velocity,
                    acceleration=test_config.acceleration,
                    deceleration=test_config.deceleration,
                )
                logger.info(f"Robot moved to max stroke position: {test_config.max_stroke}μm")
            except Exception as e:
                logger.error(f"Robot move to max stroke failed - {e}")
                raise

            # Wait for standby heating stabilization
            stabilization_time = test_config.robot_standby_stabilization
            logger.info(f"Waiting for standby heating stabilization ({stabilization_time}s)...")

            # Robot to initial position
            logger.info("Moving robot to initial position...")
            try:
                await self._robot.move_absolute(
                    position=test_config.initial_position,
                    axis_id=hardware_config.robot.axis_id,
                    velocity=test_config.velocity,
                    acceleration=test_config.acceleration,
                    deceleration=test_config.deceleration,
                )
                logger.info(f"Robot moved to initial position: {test_config.initial_position}μm")
            except Exception as e:
                logger.error(f"Robot move to initial position failed - {e}")
                raise

            # MCU start standby cooling
            logger.info("Starting MCU standby cooling...")
            try:
                await self._mcu.start_standby_cooling()
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info("MCU standby cooling started")

                # Verify MCU temperature reached standby temperature
                if self._verification_service:
                    await self._verification_service.verify_mcu_temperature(test_config.standby_temperature, test_config)
                    logger.info(
                        f"Temperature verification passed for standby temperature {test_config.standby_temperature}°C"
                    )
            except Exception as e:
                logger.error(f"MCU standby cooling failed - {e}")
                raise

            logger.info("LMA standby sequence completed successfully")

        except Exception as e:
            logger.error(f"LMA standby sequence failed: {e}")
            logger.debug(f"LMA standby sequence failed with config: {test_config.to_dict()}")
            raise HardwareConnectionException(
                f"Failed to set LMA standby sequence: {str(e)}",
                details={
                    "temperature_range": (
                        f"{min(test_config.temperature_list)}-{max(test_config.temperature_list)}°C"
                    )
                },
            ) from e

    async def perform_force_test_sequence(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> TestMeasurements:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        logger.info("Starting force test sequence...")
        total_tests = len(test_config.temperature_list) * len(test_config.stroke_positions)
        logger.info(
            f"Test matrix: {len(test_config.temperature_list)}×{len(test_config.stroke_positions)} = {total_tests} measurements"
        )

        measurements_dict: Dict[float, Dict[float, Dict[str, Any]]] = {}

        try:
            # Outer loop: Iterate through temperature list
            for temp_idx, temperature in enumerate(test_config.temperature_list):
                logger.info(
                    f"Setting temperature to {temperature}°C ({temp_idx + 1}/{len(test_config.temperature_list)})"
                )

                # Loadcell holds force measurement
                await self._loadcell.hold()
                logger.info("Loadcell is holding")

                # MCU heat up
                await self._mcu.set_operating_temperature(temperature)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(f"Temperature set to {temperature}°C, waiting for stabilization...")

                # Wait for temperature stabilization
                await asyncio.sleep(test_config.mcu_temperature_stabilization)
                logger.info(f"Temperature stabilized at {temperature}°C")

                # Verify MCU temperature reached target
                if self._verification_service:
                    await self._verification_service.verify_mcu_temperature(temperature, test_config)
                    logger.info(f"Temperature verification passed for {temperature}°C")

                # Inner loop: Iterate through stroke positions
                for pos_idx, position in enumerate(test_config.stroke_positions):
                    logger.info(
                        f"Measuring at temp {temperature}°C, position {position}μm ({pos_idx+1}/{len(test_config.stroke_positions)})"
                    )

                    # Move to position using parameters from hardware config
                    await self._robot.move_absolute(
                        position=position,
                        axis_id=hardware_config.robot.axis_id,
                        velocity=test_config.velocity,
                        acceleration=test_config.acceleration,
                        deceleration=test_config.deceleration,
                    )
                    await asyncio.sleep(test_config.robot_move_stabilization)

                    # Take measurements
                    force = await self._loadcell.read_force()

                    # Use set temperature for simplicity
                    current_temp = temperature

                    # Use set position for simplicity
                    current_position = position

                    # Store measurement data using TestMeasurements structure
                    if temperature not in measurements_dict:
                        measurements_dict[temperature] = {}
                    measurements_dict[temperature][position] = {
                        "temperature": current_temp,
                        "stroke": current_position,
                        "force": force.value,
                    }

                # Loadcell release hold after measurement
                await self._loadcell.hold_release()
                logger.info("Loadcell released the hold after measurements")

                # MCU configuration before standby heating
                await self._mcu.set_upper_temperature(test_config.upper_temperature)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                await self._mcu.set_fan_speed(test_config.fan_speed)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                # Calculate operating temperature: maximum of configured activation temp and test temperature list maximum
                # MCU start standby heating
                await self._mcu.start_standby_heating(
                    operating_temp=test_config.activation_temperature,
                    standby_temp=test_config.standby_temperature,
                )
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(
                    f"MCU standby heating started - operating: {test_config.activation_temperature}°C"
                )

                # Verify MCU temperature reached operating temperature
                if self._verification_service:
                    await self._verification_service.verify_mcu_temperature(test_config.activation_temperature, test_config)
                    logger.info(
                        f"Temperature verification passed for operating temperature {test_config.activation_temperature}°C"
                    )

                # Robot to initial stroke position
                await self._robot.move_absolute(
                    position=test_config.initial_position,
                    axis_id=hardware_config.robot.axis_id,
                    velocity=test_config.velocity,
                    acceleration=test_config.acceleration,
                    deceleration=test_config.deceleration,
                )

                await asyncio.sleep(test_config.robot_move_stabilization)
                logger.info(f"Robot returned to initial position: {test_config.initial_position}μm")

                await self._mcu.start_standby_cooling()
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(
                    f"MCU standby cooling started - standby: {test_config.standby_temperature}°C"
                )

                # Verify MCU temperature reached standby temperature
                if self._verification_service:
                    await self._verification_service.verify_mcu_temperature(test_config.standby_temperature, test_config)
                    logger.info(
                        f"Temperature verification passed for standby temperature {test_config.standby_temperature}°C"
                    )

                logger.info(f"Completed all positions for temperature {temperature}°C")

            # Convert to TestMeasurements value object
            measurements = TestMeasurements.from_legacy_dict(measurements_dict)

            logger.info(
                f"Force test sequence completed with {measurements.get_total_measurement_count()} measurements"
            )
            logger.info(
                f"Test matrix completed: {measurements.get_temperature_count()} temperatures × {len(test_config.stroke_positions)} positions"
            )
            return measurements

        except Exception as e:
            logger.error(f"Force test sequence failed: {e}")
            raise

    async def teardown_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Teardown test and return hardware to safe state"""
        logger.info("Tearing down test...")

        try:
            # Power teardown - disable output for safety
            logger.info("Disabling power output for safety...")
            await self._power.disable_output()
            logger.info("Power output disabled")

            # Robot teardown - move to initial position for safety
            logger.info(f"Moving robot to initial position: {test_config.initial_position}μm")
            await self._robot.move_absolute(
                position=test_config.initial_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=test_config.velocity,
                acceleration=test_config.acceleration,
                deceleration=test_config.deceleration,
            )
            await asyncio.sleep(test_config.robot_move_stabilization)
            logger.info("Robot moved to initial position successfully")

            logger.info("Test teardown completed successfully")

        except Exception as e:
            logger.error(f"Test teardown failed: {e}")
            # Don't re-raise to allow cleanup to continue