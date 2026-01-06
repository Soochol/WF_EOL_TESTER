"""
Hardware Service Facade (Refactored)

Lightweight coordinator that orchestrates hardware services following single responsibility principle.
Previously 786 lines, now significantly reduced by delegating to specialized services.
"""

# Standard library imports
import asyncio
import time
from datetime import datetime
from typing import cast, Dict, List, Optional, Tuple, TYPE_CHECKING

# Third-party imports
from loguru import logger
from rich.console import Console
from rich.panel import Panel

# Local application imports
from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.power_analyzer import PowerAnalyzerService
from application.interfaces.hardware.robot import RobotService
from domain.enums.robot_state import RobotState
from domain.value_objects.cycle_result import CycleResult
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.measurements import TestMeasurements
from domain.value_objects.test_configuration import TestConfiguration
from domain.value_objects.time_values import TestDuration

# Note: All hardware service functionality has been integrated directly into this facade

# IDE 개발용 타입 힌트 - 런타임에는 영향 없음
if TYPE_CHECKING:
    from application.services.core.repository_service import RepositoryService
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


class HardwareServiceFacade:
    """
    Lightweight coordinator for hardware services

    This refactored facade delegates operations to specialized services while maintaining
    the same public interface for backward compatibility.

    Services coordinated:
    - HardwareConnectionManager: Connection lifecycle
    - HardwareInitializationService: Hardware setup and configuration
    - HardwareTestExecutor: Test execution sequences
    - HardwareVerificationService: Hardware validation operations
    """

    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_io_service: DigitalIOService,
        repository_service: Optional[
            "RepositoryService"
        ] = None,  # Optional for cycle-by-cycle saving
        gui_state_manager = None,  # Optional for GUI cycle updates
        power_analyzer_service: Optional[PowerAnalyzerService] = None,  # Optional power analyzer
    ):
        # Store services for property access (backward compatibility)
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

        # Optional power analyzer for measurement-only operations
        self._power_analyzer = power_analyzer_service

        # Repository service for cycle-by-cycle saving (optional)
        self._repository_service: Optional["RepositoryService"] = repository_service

        # GUI State Manager for cycle updates (optional)
        self._gui_state_manager = gui_state_manager

        # Robot homing state management (from initialization service)
        self._robot_homed = False

        # Robot position state tracking
        self._robot_state = RobotState.UNKNOWN

    # ============================================================================
    # Service Property Accessors (Backward Compatibility)
    # ============================================================================
    #
    # These properties provide backward compatibility for external components
    # that need to access hardware services directly:
    # - GUI State Manager: Hardware status monitoring
    # - Emergency Stop Service: Hardware shutdown during emergency
    # - Monitoring Services: Hardware health checks
    #
    # Internal facade methods use _robot, _mcu, etc. directly for performance
    # External code uses .robot_service, .mcu_service, etc. for encapsulation
    # ============================================================================

    @property
    def robot_service(self) -> RobotService:
        """
        Get robot service instance for external access

        Returns:
            RobotService: Robot hardware service interface

        Note:
            Used by GUI state manager and emergency stop service
        """
        return self._robot

    @property
    def mcu_service(self) -> MCUService:
        """
        Get MCU service instance for external access

        Returns:
            MCUService: MCU hardware service interface

        Note:
            Used by GUI state manager and monitoring services
        """
        return self._mcu

    @property
    def loadcell_service(self) -> LoadCellService:
        """
        Get loadcell service instance for external access

        Returns:
            LoadCellService: Load cell hardware service interface

        Note:
            Used by GUI state manager for force monitoring
        """
        return self._loadcell

    @property
    def power_service(self) -> PowerService:
        """
        Get power service instance for external access

        Returns:
            PowerService: Power supply hardware service interface

        Note:
            Used by emergency stop service and power monitoring
        """
        return self._power

    @property
    def digital_io_service(self) -> DigitalIOService:
        """
        Get digital I/O service instance for external access

        Returns:
            DigitalIOService: Digital I/O hardware service interface

        Note:
            Used by GUI state manager and I/O monitoring
        """
        return self._digital_io

    @property
    def power_analyzer_service(self) -> Optional[PowerAnalyzerService]:
        """
        Get power analyzer service instance for external access

        Returns:
            PowerAnalyzerService: Power analyzer hardware service interface (optional)

        Note:
            Used by power monitoring in specific test cases
        """
        return self._power_analyzer

    def _log_phase_separator(self, phase_name: str) -> None:
        """
        Log a visual box separator for major test phases

        Args:
            phase_name: Name of the test phase to display
        """
        # Create box with consistent width
        box_width = max(40, len(phase_name) + 8)
        top_line = "╭" + "─" * (box_width - 2) + "╮"
        middle_line = f"│{phase_name:^{box_width - 2}}│"
        bottom_line = "╰" + "─" * (box_width - 2) + "╯"

        logger.info(top_line)
        logger.info(middle_line)
        logger.info(bottom_line)

    # ============================================================================
    # Connection Management (Delegated to HardwareConnectionManager)
    # ============================================================================

    async def connect_all_hardware(self, hardware_config: HardwareConfig) -> None:
        """Connect all required hardware"""
        self._log_phase_separator("CONNECTING ALL HARDWARE")
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

        if not await self._digital_io.is_connected():
            connection_tasks.append(self._digital_io.connect())
            hardware_names.append("DigitalIO")

        # Execute all connections concurrently
        if connection_tasks:
            try:
                await asyncio.gather(*connection_tasks)
                logger.info(f"Successfully connected: {', '.join(hardware_names)}")
            except Exception as e:
                # Local application imports
                from domain.exceptions.hardware_exceptions import (
                    HardwareConnectionException,
                )

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

    async def shutdown_hardware(self, hardware_config: Optional[HardwareConfig] = None) -> None:
        """Safely shutdown all hardware"""
        self._log_phase_separator("SHUTTING DOWN HARDWARE")
        logger.info("Shutting down hardware...")

        shutdown_tasks = []

        try:
            # Disable power output first for safety (only if connected)
            if await self._power.is_connected():
                try:
                    await self._power.disable_output()
                except Exception as e:
                    logger.warning(f"Failed to disable power output during shutdown: {e}")

            # Add disconnect tasks
            if await self._robot.is_connected():
                shutdown_tasks.append(self._robot.disconnect())

            if await self._mcu.is_connected():
                shutdown_tasks.append(self._mcu.disconnect())

            if await self._power.is_connected():
                shutdown_tasks.append(self._power.disconnect())

            if await self._loadcell.is_connected():
                shutdown_tasks.append(self._loadcell.disconnect())

            if await self._digital_io.is_connected():
                shutdown_tasks.append(self._digital_io.disconnect())

            # Execute all disconnections concurrently
            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)

            logger.info("Hardware shutdown completed")

        except Exception as e:
            logger.error(f"Error during hardware shutdown: {e}")
            # Don't re-raise as this is cleanup

    # ============================================================================
    # Hardware Initialization (Delegated to HardwareInitializationService)
    # ============================================================================

    async def initialize_hardware(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Initialize all hardware with configuration settings"""
        self._log_phase_separator("INITIALIZING HARDWARE")
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
            # Local application imports
            from domain.exceptions.hardware_exceptions import (
                HardwareConnectionException,
            )

            raise HardwareConnectionException(
                f"Failed to initialize hardware: {str(e)}",
                details={"voltage": test_config.voltage, "current": test_config.current},
            ) from e

    async def _ensure_robot_homed(self, axis_id: int) -> None:
        """
        Ensure robot is homed (only perform homing on first call or after errors)

        Homing is performed when:
        - First test execution (_robot_homed is False)
        - After test errors (flag is reset by error handlers)

        Homing is skipped when:
        - Previous test completed successfully (PASS or FAIL)

        Args:
            axis_id: Robot axis ID to home
        """
        if not self._robot_homed:
            logger.info("Performing robot homing (first run or after error)...")
            self._robot_state = RobotState.MOVING
            await self._robot.home_axis(axis_id)
            self._robot_homed = True
            self._robot_state = RobotState.HOME
            logger.info("Robot homing completed")
        else:
            logger.debug("Robot already homed, skipping homing")

    # ============================================================================
    # Test Execution (Delegated to HardwareTestExecutor)
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

            # Display power switch instruction to user
            # Note: Skip console output if no terminal (GUI mode) or encoding issues
            try:
                import sys
                # Only print to console if we have a real terminal and UTF-8 support
                if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                    console = Console()
                    power_panel = Panel(
                        "TURN ON POWER SWITCH",
                        title="[!] User Action Required",  # Changed emoji to text
                        title_align="left",
                        style="bold yellow",
                        border_style="yellow",
                    )
                    console.print(power_panel)
                else:
                    # GUI mode - log instead of console print
                    logger.info("[!] USER ACTION: TURN ON POWER SWITCH")
            except Exception as console_err:
                # Fallback to simple logging if console fails
                logger.warning(f"Console output failed: {console_err}")
                logger.info("[!] USER ACTION: TURN ON POWER SWITCH")

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
            # Local application imports
            from application.interfaces.hardware.mcu import TestMode

            await self._mcu.set_test_mode(TestMode.MODE_1)
            logger.info(f"MCU stabilization delay: {test_config.mcu_command_stabilization}s...")
            await asyncio.sleep(test_config.mcu_command_stabilization)  # MCU stabilization delay
            logger.info("MCU set to test mode 1")

            # Set LMA standby sequence
            await self.set_lma_standby(test_config, hardware_config)
            logger.info("LMA standby sequence set")

            logger.info("Test setup completed successfully")

        except asyncio.TimeoutError as e:
            # Local application imports
            from domain.exceptions.hardware_exceptions import (
                HardwareConnectionException,
            )

            raise HardwareConnectionException(
                "MCU boot timeout during test setup",
                details={"timeout": test_config.timeout_seconds},
            ) from e
        except asyncio.CancelledError:
            # Re-raise CancelledError to preserve KeyboardInterrupt behavior
            raise
        except Exception as e:
            logger.debug(f"Test setup failed with config: {test_config.to_dict()}")
            # Local application imports
            from domain.exceptions.hardware_exceptions import (
                HardwareConnectionException,
            )

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

            # MCU configuration before standby heating
            await self._mcu.set_upper_temperature(test_config.upper_temperature)
            logger.info(f"Upper temperature set to {test_config.upper_temperature}°C")
            await asyncio.sleep(test_config.mcu_command_stabilization)

            await self._mcu.set_fan_speed(test_config.fan_speed)
            logger.info(f"Fan speed set to {test_config.fan_speed}")
            await asyncio.sleep(test_config.mcu_command_stabilization)

            await self._mcu.start_standby_heating(
                operating_temp=test_config.activation_temperature,
                standby_temp=test_config.standby_temperature,
            )
            await asyncio.sleep(test_config.mcu_command_stabilization)
            logger.info(
                f"MCU standby heating started - operating: {test_config.activation_temperature}°C, standby: {test_config.standby_temperature}°C"
            )

            # Verify MCU temperature reached operating temperature
            await self.verify_mcu_temperature(test_config.activation_temperature, test_config)

            # Robot movements and cooling sequence after temperature verification
            self._robot_state = RobotState.MOVING
            await self._robot.move_absolute(
                position=test_config.operating_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=test_config.velocity,
                acceleration=test_config.acceleration,
                deceleration=test_config.deceleration,
            )
            await asyncio.sleep(test_config.robot_move_stabilization)
            self._robot_state = RobotState.MAX_STROKE
            logger.info(f"Robot moved to operating position: {test_config.operating_position}μm")

            # Delay for stabilization
            await asyncio.sleep(test_config.robot_standby_stabilization)

            # Move robot back to initial position
            self._robot_state = RobotState.MOVING
            await self._robot.move_absolute(
                position=test_config.initial_position,
                axis_id=hardware_config.robot.axis_id,
                velocity=test_config.velocity,
                acceleration=test_config.acceleration,
                deceleration=test_config.deceleration,
            )
            await asyncio.sleep(test_config.robot_move_stabilization)
            self._robot_state = RobotState.INITIAL_POSITION
            logger.info(f"Robot moved to initial position: {test_config.initial_position}μm")

            # Start standby cooling
            await self._mcu.start_standby_cooling()
            await asyncio.sleep(test_config.mcu_command_stabilization)
            logger.info("MCU standby cooling started")

            # Final temperature verification
            await self.verify_mcu_temperature(test_config.standby_temperature, test_config)

            logger.info("LMA standby sequence completed successfully")

        except Exception as e:
            logger.debug(f"LMA standby sequence failed with config: {test_config.to_dict()}")
            # Local application imports
            from domain.exceptions.hardware_exceptions import (
                HardwareConnectionException,
            )

            raise HardwareConnectionException(
                f"Failed to set LMA standby: {str(e)}",
                details={
                    "operating_temp": test_config.activation_temperature,
                    "standby_temp": test_config.standby_temperature,
                },
            ) from e

    async def perform_force_test_sequence(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
        dut_info: DUTCommandInfo,
    ) -> Tuple[TestMeasurements, List[CycleResult]]:
        """Perform complete force test measurement sequence with temperature and position matrix"""
        self._log_phase_separator("PERFORMING FORCE TEST SEQUENCE")
        logger.info("Starting force test sequence...")

        # Get repeat count from configuration
        repeat_count = test_config.repeat_count
        if repeat_count > 1:
            logger.info(f"Force test sequence will be repeated {repeat_count} times")

        # Collect measurements in dictionary format
        measurements_dict = {}

        # Data structure for timing measurements (heating/cooling times per cycle and temperature)
        timing_data = {}

        # Collect individual cycle results for repeat testing
        individual_cycle_results = []

        try:
            # Repeat the entire force test sequence
            for repeat_idx in range(repeat_count):
                # Initialize cycle-specific measurements for this repeat
                cycle_measurements_dict = {}
                cycle_timing_data = {}
                cycle_start_time = datetime.now()
                if repeat_count > 1:
                    # Create compact repetition header with background color
                    repetition_header = f"===== Force Test Sequence Repetition {repeat_idx + 1}/{repeat_count} ====="
                    color_start = "\033[48;5;0m\033[93m"  # Black background, bright yellow text
                    color_end = "\033[0m"

                    logger.info(f"{color_start}{repetition_header}{color_end}")

                # Temperature and position matrix iteration for each cycle
                for temp_idx, temperature in enumerate(test_config.temperature_list):
                    # Log temperature progress
                    total_temps = len(test_config.temperature_list)
                    total_positions = len(test_config.stroke_positions)
                    total_measurements = total_temps * total_positions * repeat_count

                    logger.info(
                        f"Setting temperature to {temperature}°C ({temp_idx + 1}/{total_temps})"
                    )
                    if repeat_count == 1:
                        logger.info(
                            f"Test matrix: {total_temps}×{total_positions} = {total_measurements} measurements"
                        )
                    else:
                        logger.info(
                            f"Test matrix: {total_temps}×{total_positions}×{repeat_count} = {total_measurements} measurements"
                        )

                    # 1. Set MCU temperature (temperature rise) - measure heating time
                    heating_start_time = time.time()
                    await self._mcu.set_operating_temperature(temperature)
                    await asyncio.sleep(test_config.mcu_command_stabilization)
                    heating_end_time = time.time()
                    heating_time_s = heating_end_time - heating_start_time

                    # Verify temperature reached
                    await self.verify_mcu_temperature(temperature, test_config)

                    # Initialize position measurements for this temperature (first time only)
                    if repeat_idx == 0:
                        measurements_dict[temperature] = {}

                    # Initialize cycle measurements for this temperature
                    cycle_measurements_dict[temperature] = {}

                    # Initialize timing data for this cycle-temperature combination
                    cycle_key = f"cycle_{repeat_idx + 1}_temp_{int(temperature)}"
                    timing_data[cycle_key] = {
                        "cycle": repeat_idx + 1,
                        "temperature": temperature,
                        "heating_time_s": heating_time_s,
                        "cooling_time_s": 0.0,  # Will be updated after cooling
                    }

                    # Store cycle timing data
                    cycle_timing_data[f"temp_{int(temperature)}"] = {
                        "temperature": temperature,
                        "heating_time_s": heating_time_s,
                        "cooling_time_s": 0.0,  # Will be updated after cooling
                    }

                    # 2. Measure at each position (robot movement + force measurement)
                    for pos_idx, position in enumerate(test_config.stroke_positions):
                        if repeat_count == 1:
                            logger.info(
                                f"Measuring at position {position}μm ({pos_idx+1}/{len(test_config.stroke_positions)})"
                            )
                        else:
                            logger.info(
                                f"Measuring at position {position}μm (rep {repeat_idx+1}/{repeat_count}, pos {pos_idx+1}/{len(test_config.stroke_positions)})"
                            )

                        # Move robot to measurement position
                        self._robot_state = RobotState.MOVING
                        await self._robot.move_absolute(
                            position=position,
                            axis_id=hardware_config.robot.axis_id,
                            velocity=test_config.velocity,
                            acceleration=test_config.acceleration,
                            deceleration=test_config.deceleration,
                        )
                        await asyncio.sleep(test_config.robot_move_stabilization)
                        self._robot_state = RobotState.MEASUREMENT_POSITION

                        # Take peak force measurement (already in kgf from LoadCell)
                        force = await self._loadcell.read_peak_force()

                        # Store measurement in dictionary format with repeat index
                        if repeat_count == 1:
                            # Single measurement - store as before (already in kgf)
                            measurements_dict[temperature][position] = {"force": force.value}
                        else:
                            # Multiple measurements - store as list with repeat index (already in kgf)
                            if position not in measurements_dict[temperature]:
                                measurements_dict[temperature][position] = {"force": []}
                            measurements_dict[temperature][position]["force"].append(force.value)

                        # Store individual cycle measurement (already in kgf)
                        cycle_measurements_dict[temperature][position] = {"force": force.value}

                        logger.debug(
                            f"Measurement completed - Position: {position}μm, Force: {force.value:.3f}kgf"
                        )

                    # 3. Return robot to initial position (robot return)
                    logger.debug("Returning robot to initial position...")
                    if self._robot_state != RobotState.INITIAL_POSITION:
                        self._robot_state = RobotState.MOVING
                        await self._robot.move_absolute(
                            position=test_config.initial_position,
                            axis_id=hardware_config.robot.axis_id,
                            velocity=test_config.velocity,
                            acceleration=test_config.acceleration,
                            deceleration=test_config.deceleration,
                        )
                        await asyncio.sleep(test_config.robot_move_stabilization)
                        self._robot_state = RobotState.INITIAL_POSITION
                        logger.debug(
                            f"Robot returned to initial position: {test_config.initial_position}μm"
                        )
                    else:
                        logger.debug("Robot already at initial position, skipping movement")

                    # 4. Start standby cooling (temperature fall) - measure cooling time
                    logger.debug("Starting standby cooling...")
                    cooling_start_time = time.time()
                    await self._mcu.start_standby_cooling()
                    await asyncio.sleep(test_config.mcu_command_stabilization)
                    cooling_end_time = time.time()
                    cooling_time_s = cooling_end_time - cooling_start_time
                    logger.debug("MCU standby cooling started")

                    # Update timing data with cooling time for current cycle-temperature
                    cycle_key = f"cycle_{repeat_idx + 1}_temp_{int(temperature)}"
                    if cycle_key in timing_data:
                        timing_data[cycle_key]["cooling_time_s"] = cooling_time_s

                    # Update cycle timing data
                    temp_key = f"temp_{int(temperature)}"
                    if temp_key in cycle_timing_data:
                        cycle_timing_data[temp_key]["cooling_time_s"] = cooling_time_s

                    # Verify standby temperature reached
                    logger.debug("Verifying standby temperature...")
                    await self.verify_mcu_temperature(test_config.standby_temperature, test_config)
                    logger.debug("Standby temperature verification completed")

                    # Note: GUI cycle result will be sent after the complete cycle (all temperatures)

                # Save cycle data immediately if repository service is available
                if self._repository_service:
                    await self._save_cycle_measurements(
                        cycle_measurements_dict,  # Use cycle-specific measurements, not accumulated
                        repeat_idx + 1,
                        repeat_count,
                        dut_info.serial_number,
                        cycle_timing_data,  # Use cycle-specific timing data with temp_38 format
                    )

                # Create individual cycle result for this repeat
                cycle_end_time = datetime.now()
                cycle_duration = TestDuration.from_seconds((cycle_end_time - cycle_start_time).total_seconds())

                # Create cycle measurements summary
                cycle_measurements = {
                    "measurements": cycle_measurements_dict,
                    "timing_data": cycle_timing_data,
                    "cycle_number": repeat_idx + 1,
                    "total_cycles": repeat_count
                }

                # Determine if this cycle passed (all measurements within tolerance)
                cycle_passed = True  # Default to passed, will be refined based on actual criteria

                # Create CycleResult for this repeat
                cycle_result = CycleResult.create_successful(
                    cycle_number=repeat_idx + 1,
                    is_passed=cycle_passed,
                    measurements=cycle_measurements,
                    execution_duration=cycle_duration,
                    completed_at=cycle_end_time,
                    cycle_notes=f"Repeat {repeat_idx + 1}/{repeat_count} completed"
                )

                individual_cycle_results.append(cycle_result)

                logger.info(f"Cycle {repeat_idx + 1} result created: {cycle_duration.seconds:.2f}s")

                # Send individual temperature results to GUI (instead of averaged cycle result)
                logger.info(f"🔌 Hardware Facade: GUI State Manager status: {self._gui_state_manager is not None}")
                if self._gui_state_manager:
                    avg_stroke = sum(test_config.stroke_positions) / len(test_config.stroke_positions)

                    logger.info(f"🎯 Hardware Facade: Sending individual temperature results for cycle {repeat_idx + 1}/{repeat_count}")

                    # Send individual result for each temperature in this cycle
                    for temp, positions in cycle_measurements_dict.items():
                        # Calculate force average for this specific temperature
                        temp_forces = [pos_data.get('force', 0.0) for pos_data in positions.values()]
                        temp_avg_force = sum(temp_forces) / len(temp_forces) if temp_forces else 0.0

                        # Get timing data for this specific temperature
                        temp_key = f"temp_{int(float(temp))}"
                        temp_heating_time = cycle_timing_data.get(temp_key, {}).get('heating_time_s', 0)
                        temp_cooling_time = cycle_timing_data.get(temp_key, {}).get('cooling_time_s', 0)

                        logger.info(f"🌡️ Hardware Facade: Temp {temp}°C - Force: {temp_avg_force:.2f}kgf, Heating: {temp_heating_time:.1f}s, Cooling: {temp_cooling_time:.1f}s")

                        # Send individual temperature result
                        self._gui_state_manager.add_cycle_result(
                            cycle=repeat_idx + 1,
                            total_cycles=repeat_count,
                            temperature=float(temp),           # Individual temperature
                            stroke=avg_stroke,
                            force=temp_avg_force,              # Force for this specific temperature
                            heating_time=int(temp_heating_time),
                            cooling_time=int(temp_cooling_time),
                            status="PASS"  # Assuming pass for now, can be enhanced with failure detection
                        )

                    logger.info(f"✅ Hardware Facade: All {len(cycle_measurements_dict)} temperature results for cycle {repeat_idx + 1} sent to GUI State Manager")
                else:
                    logger.warning(f"⚠️ Hardware Facade: GUI State Manager not available for cycle {repeat_idx + 1} - results will not be displayed in real-time")

                # Add delay between repetitions (except for last repetition)
                if repeat_count > 1 and repeat_idx < repeat_count - 1:
                    stabilization_delay = 1.0  # 1 second between repetitions
                    logger.info(f"Stabilization delay between repetitions: {stabilization_delay}s")
                    await asyncio.sleep(stabilization_delay)

            logger.info("Force test sequence completed successfully")

            # Process measurements for repeat_count > 1: convert lists to averages
            if repeat_count > 1:
                processed_dict = {}
                for temp, positions in measurements_dict.items():
                    processed_dict[temp] = {}
                    for pos, measurements in positions.items():
                        force_data = measurements["force"]
                        if isinstance(force_data, list):
                            # Calculate average for repeated measurements
                            avg_force = sum(force_data) / len(force_data)
                            processed_dict[temp][pos] = {"force": avg_force}

                            # Log detailed repeat information
                            logger.info(
                                f"Position {pos}μm @ {temp}°C: {len(force_data)} measurements = {force_data}, average = {avg_force:.3f}N"
                            )
                        else:
                            # Single measurement, keep as is
                            processed_dict[temp][pos] = {"force": force_data}

                # Create TestMeasurements object from processed dictionary with timing data
                test_measurements = TestMeasurements.from_legacy_dict(processed_dict, timing_data)
            else:
                # Single measurement, use original dictionary with timing data
                test_measurements = TestMeasurements.from_legacy_dict(measurements_dict, timing_data)

            # Return both TestMeasurements and individual cycle results
            return test_measurements, individual_cycle_results

        except Exception as e:
            logger.debug(f"Force test sequence failed with config: {test_config.to_dict()}")
            # Local application imports
            from domain.exceptions.hardware_exceptions import (
                HardwareConnectionException,
            )

            raise HardwareConnectionException(
                f"Failed to perform force test sequence: {str(e)}",
                details={
                    "temperature_count": len(test_config.temperature_list),
                    "position_count": len(test_config.stroke_positions),
                    "repeat_count": repeat_count,
                },
            ) from e

    async def teardown_test(
        self,
        test_config: TestConfiguration,
        hardware_config: HardwareConfig,
    ) -> None:
        """Teardown test and return hardware to safe state"""
        self._log_phase_separator("TEARING DOWN TEST")
        logger.info("Tearing down test...")

        try:
            # Move robot to initial position (if not already there)
            if self._robot_state != RobotState.INITIAL_POSITION:
                logger.info(f"Moving robot to initial position: {test_config.initial_position}μm")
                self._robot_state = RobotState.MOVING
                await self._robot.move_absolute(
                    position=test_config.initial_position,
                    axis_id=hardware_config.robot.axis_id,
                    velocity=test_config.velocity,
                    acceleration=test_config.acceleration,
                    deceleration=test_config.deceleration,
                )
                await asyncio.sleep(test_config.robot_move_stabilization)
                self._robot_state = RobotState.INITIAL_POSITION
            else:
                logger.info("Robot already at initial position, skipping movement")

            # Disable power output
            await self._power.disable_output()
            logger.info("Power disabled")

            logger.info("Test teardown completed")

        except Exception as e:
            logger.error(f"Error during test teardown: {e}")
            # Continue with cleanup even if teardown fails partially

    # ============================================================================
    # Hardware Verification (Delegated to HardwareVerificationService)
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

        # Check if this is Mock environment and skip retries for faster testing
        if "Mock" in self._mcu.__class__.__name__:
            logger.info(
                f"✅ Mock environment detected - Temperature verification bypassed for {expected_temp}°C"
            )
            await asyncio.sleep(0.1)  # Short simulation delay
            return

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
                        # Local application imports
                        from domain.exceptions.eol_exceptions import (
                            HardwareOperationError,
                        )

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
                    # Local application imports
                    from domain.exceptions.hardware_exceptions import (
                        HardwareConnectionException,
                    )

                    raise HardwareConnectionException(
                        error_msg,
                        details={
                            "expected_temp": expected_temp,
                            "tolerance": test_config.temperature_tolerance,
                            "final_error": str(e),
                            "attempts_made": max_retries + 1,
                        },
                    ) from e

    # ============================================================================
    # Additional Utility Methods
    # ============================================================================

    def is_robot_homed(self) -> bool:
        """Check if robot has been homed"""
        return self._robot_homed

    def reset_robot_homing_state(self) -> None:
        """Reset robot homing state (useful for testing or re-initialization)"""
        self._robot_homed = False
        logger.debug("Robot homing state reset")

    async def _save_cycle_measurements(
        self,
        measurements_dict: Dict,
        cycle_num: int,
        total_cycles: int,
        serial_number: str,
        timing_data: Optional[Dict] = None,
    ) -> None:
        """
        Save measurements for a completed cycle immediately

        Args:
            measurements_dict: Current accumulated measurements dictionary
            cycle_num: Current cycle number (1-based)
            total_cycles: Total number of cycles
            serial_number: DUT serial number from user input
        """
        # Type guard: ensure repository service is available
        if self._repository_service is None:
            logger.warning(
                f"⚠️  Cycle {cycle_num}/{total_cycles} data not saved - Repository service not available"
            )
            return

        try:
            # measurements_dict is already cycle-specific from caller
            # No need to extract from list - just use it directly
            if measurements_dict:
                # Convert to TestMeasurements object with timing data
                cycle_test_measurements = TestMeasurements.from_legacy_dict(
                    measurements_dict, timing_data
                )

                # Save to repository with cycle identifier
                await self._repository_service.save_cycle_measurements(
                    cycle_test_measurements, cycle_num, total_cycles, serial_number, timing_data
                )

                logger.info(f"✅ Cycle {cycle_num}/{total_cycles} measurements saved to repository")

        except Exception as save_error:
            # Don't fail the test if cycle save fails, just log it
            logger.warning(
                f"Failed to save cycle {cycle_num}/{total_cycles} measurements: {save_error}"
            )
