"""
Hardware Service Facade

Facade pattern implementation to group and simplify hardware service interactions.
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from loguru import logger

# IDE 개발용 타입 힌트 - 런타임에는 영향 없음
if TYPE_CHECKING:
    from infrastructure.implementation.hardware.digital_input.ajinextek.ajinextek_dio import (
        AjinextekDIO,
    )
    from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import (
        BS205LoadCell,
    )
    from infrastructure.implementation.hardware.mcu.lma.lma_mcu import (
        LMAMCU,
    )
    from infrastructure.implementation.hardware.power.oda.oda_power import (
        OdaPower,
    )
    from infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot import (
        AjinextekRobot,
    )

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

# Type checking imports removed as they are no longer needed
# The constructor now uses interface types instead of concrete types
from domain.exceptions.hardware_exceptions import (
    HardwareConnectionException,
)
from domain.value_objects.hardware_configuration import HardwareConfiguration
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

    # ============================================================================
    # 생성자
    # ============================================================================

    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_input_service: DigitalInputService,
    ):
        # IDE 개발용 타입 힌트 - 실제 구현체로 인식하도록 함 (런타임에는 동일)
        if TYPE_CHECKING:
            self._robot = cast("AjinextekRobot", robot_service)
            self._mcu = cast("LMAMCU", mcu_service)
            self._loadcell = cast("BS205LoadCell", loadcell_service)
            self._power = cast("OdaPower", power_service)
            self._digital_input = cast("AjinextekDIO", digital_input_service)
        else:
            self._robot = robot_service
            self._mcu = mcu_service
            self._loadcell = loadcell_service
            self._power = power_service
            self._digital_input = digital_input_service

    # ============================================================================
    # 기본 하드웨어 관리 (라이프사이클 순서)
    # ============================================================================

    async def connect_all_hardware(self, hardware_config: HardwareConfiguration) -> None:
        """Connect all required hardware"""
        logger.info("Connecting hardware...")

        connection_tasks = []
        hardware_names = []

        # Check and connect each hardware service
        if not await self._robot.is_connected():
            # Connect to robot with connection parameters from configuration
            connection_tasks.append(
                self._robot.connect(
                    axis_id=hardware_config.robot.axis_id,
                    irq_no=hardware_config.robot.irq_no,
                )
            )
            hardware_names.append("Robot")

        if not await self._mcu.is_connected():
            connection_tasks.append(
                self._mcu.connect(
                    port=hardware_config.mcu.port,
                    baudrate=hardware_config.mcu.baudrate,
                    timeout=hardware_config.mcu.timeout,
                    bytesize=hardware_config.mcu.bytesize,
                    stopbits=hardware_config.mcu.stopbits,
                    parity=hardware_config.mcu.parity,
                )
            )
            hardware_names.append("MCU")

        if not await self._power.is_connected():
            connection_tasks.append(
                self._power.connect(
                    host=hardware_config.power.host,
                    port=hardware_config.power.port,
                    timeout=hardware_config.power.timeout,
                    channel=hardware_config.power.channel,
                )
            )
            hardware_names.append("Power")

        if not await self._loadcell.is_connected():
            connection_tasks.append(
                self._loadcell.connect(
                    port=hardware_config.loadcell.port,
                    baudrate=hardware_config.loadcell.baudrate,
                    timeout=hardware_config.loadcell.timeout,
                    bytesize=hardware_config.loadcell.bytesize,
                    stopbits=hardware_config.loadcell.stopbits,
                    parity=hardware_config.loadcell.parity,
                    indicator_id=hardware_config.loadcell.indicator_id,
                )
            )
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

    async def get_hardware_status(self) -> Dict[str, bool]:
        """Get connection status of all hardware"""
        return {
            "robot": await self._robot.is_connected(),
            "mcu": await self._mcu.is_connected(),
            "power": await self._power.is_connected(),
            "loadcell": await self._loadcell.is_connected(),
        }

    async def shutdown_hardware(
        self, hardware_config: Optional[HardwareConfiguration] = None
    ) -> None:
        """Safely shutdown all hardware"""
        logger.info("Shutting down hardware...")

        shutdown_tasks = []

        try:
            # Disable power output first for safety
            await self._power.disable_output()

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

    # ============================================================================
    # 하드웨어 설정
    # ============================================================================

    async def initialize_hardware(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> None:
        """Initialize all hardware with configuration settings"""
        logger.info("Initializing hardware with configuration...")

        try:
            # Initialize power settings
            await self._power.disable_output()
            await asyncio.sleep(test_config.power_stabilization)

            await self._power.set_voltage(test_config.voltage)
            await asyncio.sleep(test_config.power_stabilization)

            await self._power.set_current(test_config.current)
            await asyncio.sleep(test_config.power_stabilization)

            await self._power.set_current_limit(test_config.upper_current)
            await asyncio.sleep(test_config.power_stabilization)

            # Initialize robot - enable servo first, then move to initial position
            logger.info(f"Enabling servo for axis {hardware_config.robot.axis_id}...")
            await self._robot.enable_servo(hardware_config.robot.axis_id)
            logger.info("Robot servo enabled successfully")

            logger.info(f"Moving robot to initial position: {test_config.initial_position}mm")
            await self._robot.move_absolute(
                position=test_config.initial_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            await asyncio.sleep(test_config.stabilization_delay)
            logger.info("Robot initialized at initial position successfully")

            # Zero the load cell
            # await self._loadcell.zero_calibration()
            # await asyncio.sleep(config.loadcell_zero_delay)

            logger.info("Hardware initialization completed")

        except Exception as e:
            raise HardwareConnectionException(
                f"Failed to initialize hardware: {str(e)}",
                details={"config": test_config.to_dict()},
            ) from e

    async def set_lma_standby(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> None:
        """Set LMA standby sequence - coordinate MCU and Robot for LMA standby state"""
        logger.info("Setting LMA standby sequence...")

        try:
            # MCU start standby heating
            # Calculate standby temperature: minimum of configured standby temp and test temperature list minimum
            if not test_config.temperature_list:
                raise ValueError("Temperature list cannot be empty")

            min_test_temp = min(test_config.temperature_list)
            calculated_standby_temp = min(test_config.standby_temperature, min_test_temp)

            await self._mcu.start_standby_heating(
                operating_temp=test_config.activation_temperature,
                standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
            )
            logger.info(
                "MCU standby heating started - operating: %s°C, standby: %s°C",
                test_config.activation_temperature,
                calculated_standby_temp,
            )

            # Robot to max stroke position using parameters from hardware config
            await self._robot.move_absolute(
                position=test_config.max_stroke,
                axis_id=hardware_config.robot.axis_id,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info(f"Robot moved to max stroke position: {test_config.max_stroke}mm")

            # Wait for standby heating stabilization
            await asyncio.sleep(test_config.standby_stabilization)
            logger.info(f"Standby heating stabilized after {test_config.standby_stabilization}s")

            # Robot to initial position using test configuration
            await self._robot.move_absolute(
                position=test_config.initial_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=hardware_config.robot.velocity,
                acceleration=hardware_config.robot.acceleration,
                deceleration=hardware_config.robot.deceleration,
            )
            logger.info(f"Robot moved to initial position: {test_config.initial_position}mm")

            # MCU start standby cooling
            await self._mcu.start_standby_cooling()
            logger.info("MCU standby cooling started")

            logger.info("LMA standby sequence completed successfully")

        except Exception as e:
            logger.error(f"LMA standby sequence failed: {e}")
            raise HardwareConnectionException(
                f"Failed to set LMA standby sequence: {str(e)}",
                details={"config": test_config.to_dict()},
            ) from e

    # ============================================================================
    # 테스트 실행 (테스트 라이프사이클 순서)
    # ============================================================================

    async def setup_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> None:
        """Setup hardware for test execution"""
        logger.info("Setting up test...")

        try:
            # Enable power output
            await self._power.enable_output()
            logger.info(f"Power enabled: {test_config.voltage}V, {test_config.current}A")

            # Wait for MCU boot complete signal (directly using MCU service)
            logger.info("Waiting for MCU boot complete signal...")
            await asyncio.wait_for(
                self._mcu.wait_boot_complete(),
                timeout=test_config.timeout_seconds,
            )
            logger.info("MCU boot complete signal received")

            # Enter test mode 1 (always executed)
            await self._mcu.set_test_mode(TestMode.MODE_1)
            logger.info("MCU set to test mode 1")

            # MCU configuration (upper temperature, fan speed)
            upper_temp = test_config.upper_temperature
            fan_speed = test_config.fan_speed

            await self._mcu.set_upper_temperature(upper_temp)
            await self._mcu.set_fan_speed(fan_speed)
            logger.info(f"MCU configured: upper_temp={upper_temp}°C, fan_speed={fan_speed}%")

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
            raise HardwareConnectionException(
                f"Failed to setup test: {str(e)}",
                details={"config": test_config.to_dict()},
            ) from e

    async def perform_force_test_sequence(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> TestMeasurements:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        logger.info("Starting force test sequence...")
        total_tests = len(test_config.temperature_list) * len(test_config.stroke_positions)
        logger.info(
            "Test matrix: %s×%s = %s measurements",
            len(test_config.temperature_list),
            len(test_config.stroke_positions),
            total_tests,
        )

        measurements_dict: Dict[float, Dict[float, Dict[str, Any]]] = {}

        try:
            # Outer loop: Iterate through temperature list
            for temp_idx, temperature in enumerate(test_config.temperature_list):
                logger.info(
                    "Setting temperature to %s°C (%s/%s)",
                    temperature,
                    temp_idx + 1,
                    len(test_config.temperature_list),
                )

                # Loadcell holds force measurement
                await self._loadcell.hold()
                logger.info("Loadcell is holding")

                # MCU set upper temperature
                await self._mcu.set_upper_temperature(test_config.upper_temperature)
                logger.info(f"Upper temperature set to {test_config.upper_temperature}°C")

                # MCU heat up
                await self._mcu.set_temperature(temperature)
                logger.info(f"Temperature set to {temperature}°C, waiting for stabilization...")

                # Wait for temperature stabilization
                await asyncio.sleep(test_config.temperature_stabilization)
                logger.info(f"Temperature stabilized at {temperature}°C")

                # Inner loop: Iterate through stroke positions
                for pos_idx, position in enumerate(test_config.stroke_positions):
                    logger.info(
                        f"Measuring at temp {temperature}°C, position {position}mm ({pos_idx+1}/{len(test_config.stroke_positions)})"
                    )

                    # Move to position using parameters from hardware config
                    await self._robot.move_absolute(
                        position=position,
                        axis_id=hardware_config.robot.axis_id,
                        velocity=hardware_config.robot.velocity,
                        acceleration=hardware_config.robot.acceleration,
                        deceleration=hardware_config.robot.deceleration,
                    )
                    await asyncio.sleep(test_config.stabilization_delay)

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

                # mcu standy heating
                min_test_temp = min(test_config.temperature_list)
                calculated_standby_temp = min(test_config.standby_temperature, min_test_temp)

                # MCU start standby heating
                await self._mcu.start_standby_heating(
                    operating_temp=test_config.activation_temperature,
                    standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
                )
                logger.info(
                    "MCU standby heating started - operating: %s°C",
                    test_config.activation_temperature,
                )

                # Robot to initial stroke position
                await self._robot.move_absolute(
                    position=test_config.initial_position,
                    axis_id=hardware_config.robot.axis_id,
                    velocity=hardware_config.robot.velocity,
                    acceleration=hardware_config.robot.acceleration,
                    deceleration=hardware_config.robot.deceleration,
                )

                await asyncio.sleep(test_config.stabilization_delay)
                logger.info(f"Robot returned to initial position: {test_config.initial_position}mm")

                await self._mcu.start_standby_cooling()
                logger.info(
                    "MCU standby heating started - standby: %s°C",
                    calculated_standby_temp,
                )

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
                len(test_config.stroke_positions),
            )
            return measurements

        except Exception as e:
            logger.error(f"Force test sequence failed: {e}")
            raise

    async def teardown_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfiguration,
    ) -> None:
        """Teardown test and return hardware to safe state"""
        logger.info("Tearing down test...")

        try:

            # Power teardown - disable output for safety
            logger.info("Disabling power output for safety...")
            await self._power.disable_output()
            logger.info("Power output disabled")

            logger.info("Test teardown completed successfully")

        except Exception as e:
            logger.error(f"Test teardown failed: {e}")
            # Don't re-raise to allow cleanup to continue
