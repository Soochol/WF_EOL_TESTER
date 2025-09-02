"""
Hardware Initialization Service

Handles hardware initialization and setup operations.
Extracted from HardwareServiceFacade for single responsibility compliance.
"""

import asyncio

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.test_configuration import TestConfiguration


class HardwareInitializationService:
    """
    Manages hardware initialization and setup operations
    
    Handles configuring hardware services with test parameters and ensuring proper initialization.
    """
    
    def __init__(
        self,
        robot_service: RobotService,
        power_service: PowerService,
        digital_io_service: DigitalIOService,
        loadcell_service: LoadCellService,
    ):
        self._robot = robot_service
        self._power = power_service
        self._digital_io = digital_io_service
        self._loadcell = loadcell_service
        
        # Robot homing state management
        self._robot_homed = False

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

    def is_robot_homed(self) -> bool:
        """Check if robot has been homed"""
        return self._robot_homed

    def reset_homing_state(self) -> None:
        """Reset robot homing state (useful for testing or re-initialization)"""
        self._robot_homed = False
        logger.debug("Robot homing state reset")