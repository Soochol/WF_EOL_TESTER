"""
Hardware Service Facade

Facade pattern implementation to group and simplify hardware service interactions.
"""

import asyncio
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from loguru import logger

from application.interfaces.hardware.digital_io import (
    DigitalIOService,
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
from domain.exceptions.eol_exceptions import (
    HardwareOperationError,
)
from domain.exceptions.hardware_exceptions import (
    HardwareConnectionException,
)
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.measurements import (
    TestMeasurements,
)
from domain.value_objects.test_configuration import (
    TestConfiguration,
)

# IDE 개발용 타입 힌트 - 런타임에는 영향 없음
if TYPE_CHECKING:
    from infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio import (
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

# Type checking imports removed as they are no longer needed
# The constructor now uses interface types instead of concrete types


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
        digital_io_service: DigitalIOService,
    ):
        # IDE 개발용 타입 힌트 - 실제 구현체로 인식하도록 함 (런타임에는 동일)
        if TYPE_CHECKING:
            self._robot = cast("AjinextekRobot", robot_service)
            self._mcu = cast("LMAMCU", mcu_service)
            self._loadcell = cast("BS205LoadCell", loadcell_service)
            self._power = cast("OdaPower", power_service)
            self._digital_io = cast("AjinextekDIO", digital_io_service)
        else:
            self._robot = robot_service
            self._mcu = mcu_service
            self._loadcell = loadcell_service
            self._power = power_service
            self._digital_io = digital_io_service

        # Robot homing state management
        self._robot_homed = False

    # ============================================================================
    # 서비스 접근자 (Public Accessors)
    # ============================================================================

    @property
    def robot_service(self) -> RobotService:
        """Get robot service instance"""
        return self._robot

    @property
    def mcu_service(self) -> MCUService:
        """Get MCU service instance"""
        return self._mcu

    @property
    def loadcell_service(self) -> LoadCellService:
        """Get loadcell service instance"""
        return self._loadcell

    @property
    def power_service(self) -> PowerService:
        """Get power service instance"""
        return self._power

    @property
    def digital_io_service(self) -> DigitalIOService:
        """Get digital I/O service instance"""
        return self._digital_io

    # ============================================================================
    # 기본 하드웨어 관리 (라이프사이클 순서)
    # ============================================================================

    async def connect_all_hardware(self, hardware_config: HardwareConfig) -> None:
        """Connect all required hardware"""
        logger.info("Connecting hardware...")

        connection_tasks = []
        hardware_names = []

        # Check and connect each hardware service
        if not await self._robot.is_connected():
            # Connect to robot (configuration already injected in constructor)
            connection_tasks.append(self._robot.connect())
            hardware_names.append("Robot")

        if not await self._mcu.is_connected():
            # Connect to MCU (configuration already injected in constructor)
            connection_tasks.append(self._mcu.connect())
            hardware_names.append("MCU")

        if not await self._power.is_connected():
            # Connect to power (configuration already injected in constructor)
            connection_tasks.append(self._power.connect())
            hardware_names.append("Power")

        if not await self._loadcell.is_connected():
            # Connect to loadcell (configuration already injected in constructor)
            connection_tasks.append(self._loadcell.connect())
            hardware_names.append("LoadCell")

        # Digital I/O connection (if connect method is available)
        if not await self._digital_io.is_connected():
            # Check if digital I/O service has connect method
            if hasattr(self._digital_io, "connect") and callable(
                getattr(self._digital_io, "connect")
            ):
                try:
                    # Connect to digital I/O (configuration already injected in constructor)
                    connection_tasks.append(self._digital_io.connect())
                    hardware_names.append("DigitalIO")
                except Exception as e:
                    logger.warning(f"Digital I/O connection preparation failed: {e}")
            else:
                logger.debug(
                    "Digital I/O service does not have connect method - assuming always connected"
                )

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
            "digital_io": await self._digital_io.is_connected(),
        }

    async def shutdown_hardware(
        self, hardware_config: Optional[HardwareConfig] = None
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

            # Digital I/O disconnection (if disconnect method is available)
            if await self._digital_io.is_connected():
                if hasattr(self._digital_io, "disconnect") and callable(
                    getattr(self._digital_io, "disconnect")
                ):
                    shutdown_tasks.append(self._digital_io.disconnect())
                else:
                    logger.debug("Digital I/O service does not have disconnect method")

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
        hardware_config: HardwareConfig,
    ) -> None:
        """Initialize all hardware with configuration settings"""
        logger.info("Initializing hardware with configuration...")

        try:
            # Digital Output servo1_brake_release 채널 ON (서보 브레이크 해제 신호)
            await self._digital_io.write_output(
                hardware_config.digital_io.servo1_brake_release, True
            )
            logger.info(
                f"Digital output channel {hardware_config.digital_io.servo1_brake_release} enabled for servo brake release"
            )

            # Initialize power settings
            await self._power.disable_output()
            await asyncio.sleep(test_config.power_command_stabilization)

            await self._power.set_voltage(test_config.voltage)
            await asyncio.sleep(test_config.power_command_stabilization)

            await self._power.set_current(test_config.current)
            await asyncio.sleep(test_config.power_command_stabilization)

            await self._power.set_current_limit(test_config.upper_current)
            await asyncio.sleep(test_config.power_command_stabilization)

            # Initialize robot - enable servo, ensure homed, then move to initial position
            logger.info(f"Enabling servo for axis {hardware_config.robot.axis_id}...")
            await self._robot.enable_servo(hardware_config.robot.axis_id)
            logger.info("Robot servo enabled successfully")

            # Ensure robot is homed (only on first execution)
            await self._ensure_robot_homed(hardware_config.robot.axis_id)

            logger.info(f"Moving robot to initial position: {test_config.initial_position}μm")
            await self._robot.move_absolute(
                position=test_config.initial_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=test_config.velocity,
                acceleration=test_config.acceleration,
                deceleration=test_config.deceleration,
            )
            await asyncio.sleep(test_config.robot_move_stabilization)
            logger.info("Robot initialized at initial position successfully")

            # Zero the load cell
            # await self._loadcell.zero_calibration()
            # await asyncio.sleep(config.loadcell_zero_delay)

            logger.info("Hardware initialization completed")

        except Exception as e:
            logger.debug(f"Hardware initialization failed with config: {test_config.to_dict()}")
            raise HardwareConnectionException(
                f"Failed to initialize hardware: {str(e)}",
                details={"voltage": test_config.voltage, "current": test_config.current},
            ) from e

    async def _ensure_robot_homed(self, axis_id: int) -> None:
        """
        Ensure robot is homed (only perform homing on first call)

        Args:
            axis_id: Robot axis ID to home
        """
        if not self._robot_homed:
            logger.info("Performing initial robot homing...")
            await self._robot.home_axis(axis_id)
            self._robot_homed = True
            logger.info("Initial robot homing completed")
        else:
            logger.debug("Robot already homed, skipping homing")

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

            min_test_temp = min(test_config.temperature_list)
            calculated_standby_temp = min(test_config.standby_temperature, min_test_temp)

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

                # Calculate operating temperature: maximum of configured activation temp and test temperature list maximum
                max_test_temp = max(test_config.temperature_list)
                calculated_operating_temp = max(test_config.activation_temperature, max_test_temp)

                await self._mcu.start_standby_heating(
                    operating_temp=calculated_operating_temp,
                    standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
                )
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(
                    f"MCU standby heating started - operating: {calculated_operating_temp}°C, standby: {calculated_standby_temp}°C"
                )

                # Verify MCU temperature reached operating temperature
                await self.verify_mcu_temperature(calculated_operating_temp, test_config)
                logger.info(
                    f"Temperature verification passed for operating temperature {calculated_operating_temp}°C"
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
                await self.verify_mcu_temperature(calculated_standby_temp, test_config)
                logger.info(
                    f"Temperature verification passed for standby temperature {calculated_standby_temp}°C"
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

    # ============================================================================
    # 테스트 실행 (테스트 라이프사이클 순서)
    # ============================================================================

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

                # MCU set upper temperature
                await self._mcu.set_upper_temperature(test_config.upper_temperature)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(f"Upper temperature set to {test_config.upper_temperature}°C")

                await self._mcu.set_fan_speed(test_config.fan_speed)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                # MCU heat up
                # Calculate standby temperature: minimum of configured standby temp and test temperature list minimum
                min_test_temp = min(test_config.temperature_list)
                calculated_standby_temp = min(test_config.standby_temperature, min_test_temp)

                await self._mcu.start_standby_heating(
                    operating_temp=temperature,
                    standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
                )
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(f"Temperature set to {temperature}°C, waiting for stabilization...")

                # Wait for temperature stabilization
                await asyncio.sleep(test_config.mcu_temperature_stabilization)
                logger.info(f"Temperature stabilized at {temperature}°C")

                # Verify MCU temperature reached target
                await self.verify_mcu_temperature(temperature, test_config)
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

                # mcu standy heating
                min_test_temp = min(test_config.temperature_list)
                calculated_standby_temp = min(test_config.standby_temperature, min_test_temp)

                # MCU configuration before standby heating
                await self._mcu.set_upper_temperature(test_config.upper_temperature)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                await self._mcu.set_fan_speed(test_config.fan_speed)
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(test_config.mcu_command_stabilization)

                # Calculate operating temperature: maximum of configured activation temp and test temperature list maximum
                max_test_temp = max(test_config.temperature_list)
                calculated_operating_temp = max(test_config.activation_temperature, max_test_temp)

                # MCU start standby heating
                await self._mcu.start_standby_heating(
                    operating_temp=calculated_operating_temp,
                    standby_temp=calculated_standby_temp,  # 대기온도는 설정값과 테스트 최소온도 중 작은 값
                )
                logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
                await asyncio.sleep(
                    test_config.mcu_command_stabilization
                )  # MCU stabilization delay
                logger.info(
                    f"MCU standby heating started - operating: {calculated_operating_temp}°C"
                )

                # Verify MCU temperature reached operating temperature
                await self.verify_mcu_temperature(calculated_operating_temp, test_config)
                logger.info(
                    f"Temperature verification passed for operating temperature {calculated_operating_temp}°C"
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
                logger.info(f"MCU standby cooling started - standby: {calculated_standby_temp}°C")

                # Verify MCU temperature reached standby temperature
                await self.verify_mcu_temperature(calculated_standby_temp, test_config)
                logger.info(
                    f"Temperature verification passed for standby temperature {calculated_standby_temp}°C"
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

    # ============================================================================
    # 온도 검증
    # ============================================================================

    async def verify_mcu_temperature(
        self, expected_temp: float, test_config: TestConfiguration
    ) -> None:
        """
        Verify MCU temperature is within acceptable range of expected value

        Uses MCU get_temperature() to read actual temperature and compares
        against expected value with configurable tolerance range.
        Includes retry logic: 10 additional attempts with 1-second delays if initial verification fails.

        Args:
            expected_temp: Expected temperature value (°C)
            test_config: Test configuration containing tolerance settings

        Raises:
            HardwareOperationError: If temperature verification fails after all retries
            HardwareConnectionException: If MCU temperature read fails consistently
        """
        logger.info(
            f"Verifying MCU temperature - Expected: {expected_temp}°C (±{test_config.temperature_tolerance}°C)"
        )

        max_retries = 10
        retry_delay = 1.0

        for attempt in range(max_retries + 1):  # 0-10 (11 total attempts)
            try:
                # Read actual temperature from MCU
                actual_temp = await self._mcu.get_temperature()

                # Calculate temperature difference
                temp_diff = abs(actual_temp - expected_temp)

                # Check if within tolerance
                is_within_tolerance = temp_diff <= test_config.temperature_tolerance

                if is_within_tolerance:
                    if attempt == 0:
                        logger.info(
                            f"✅ Temperature verification PASSED on first attempt - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (≤{test_config.temperature_tolerance:.1f}°C)"
                        )
                    else:
                        logger.info(
                            f"✅ Temperature verification PASSED on attempt {attempt + 1}/{max_retries + 1} - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (≤{test_config.temperature_tolerance:.1f}°C)"
                        )
                    return
                else:
                    if attempt < max_retries:
                        logger.warning(
                            f"❌ Temperature verification attempt {attempt + 1}/{max_retries + 1} failed - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (>{test_config.temperature_tolerance:.1f}°C) - Retrying in {retry_delay}s..."
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        # Final failure after all retries
                        error_msg = f"Temperature verification failed after {max_retries + 1} attempts - Final: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (>{test_config.temperature_tolerance:.1f}°C)"
                        logger.error(f"❌ {error_msg}")
                        raise HardwareOperationError(
                            device="mcu", operation="verify_temperature", reason=error_msg
                        )

            except HardwareOperationError:
                # Re-raise our own temperature verification failures
                raise
            except Exception as e:
                # Handle MCU communication errors
                if attempt < max_retries:
                    logger.warning(
                        f"⚠️  MCU communication error on attempt {attempt + 1}/{max_retries + 1} - {str(e)} - Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    # Final communication failure after all retries
                    error_msg = f"MCU temperature verification failed after {max_retries + 1} attempts due to communication errors: {str(e)}"
                    logger.error(error_msg)
                    raise HardwareConnectionException(
                        error_msg,
                        details={
                            "expected_temp": expected_temp,
                            "tolerance": test_config.temperature_tolerance,
                            "final_error": str(e),
                            "attempts_made": max_retries + 1,
                        },
                    ) from e
