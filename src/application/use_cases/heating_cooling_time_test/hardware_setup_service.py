"""
Hardware Setup Service for Heating/Cooling Time Test

Handles hardware initialization and configuration for heating/cooling time testing.
Manages power supply, MCU configuration, and initial temperature setup.
"""

# Third-party imports
import asyncio
from loguru import logger

# Local application imports
from application.services.hardware_facade import HardwareServiceFacade
from application.services.monitoring.power_monitor import PowerMonitor
from domain.enums.mcu_enums import TestMode


class HardwareSetupService:
    """
    Hardware setup service for heating/cooling time test

    Manages the initialization and configuration of hardware components
    required for heating/cooling time testing.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize hardware setup service

        Args:
            hardware_services: Hardware service facade
        """
        self._hardware_services = hardware_services
        self._power_monitor = None

    @property
    def power_monitor(self) -> PowerMonitor:
        """Get the power monitor instance"""
        if self._power_monitor is None:
            raise RuntimeError("Power monitor not initialized. Call connect_hardware() first.")
        return self._power_monitor

    async def connect_hardware(self, hc_config) -> None:
        """
        Connect required hardware components

        Connects power supply, MCU, optional power analyzer, and robot-related services.
        If power analyzer is configured, it will be used for power monitoring instead of power supply.

        Args:
            hc_config: Heating/cooling configuration object
        """
        logger.info("Connecting hardware...")
        power_service = self._hardware_services.power_service
        mcu_service = self._hardware_services.mcu_service
        power_analyzer = self._hardware_services.power_analyzer_service

        # Basic connection tasks
        connection_tasks = [
            power_service.connect(),
            mcu_service.connect(),
        ]

        # Robot-related services (conditional)
        if hc_config.enable_robot:
            robot_service = self._hardware_services.robot_service
            loadcell_service = self._hardware_services.loadcell_service
            digital_io_service = self._hardware_services.digital_io_service

            connection_tasks.extend(
                [
                    robot_service.connect(),
                    loadcell_service.connect(),
                    digital_io_service.connect(),
                ]
            )
            logger.info("Connecting robot, loadcell, and digital I/O services...")

        # Power analyzer (optional)
        if power_analyzer:
            logger.info("Power analyzer detected - connecting...")
            connection_tasks.append(power_analyzer.connect())

        # Connect all hardware in parallel
        await asyncio.gather(*connection_tasks)
        logger.info("All hardware connected successfully")

        # Initialize power monitor
        if power_analyzer:
            # Use power analyzer for monitoring
            self._power_monitor = PowerMonitor(power_analyzer)
            logger.info("Power monitor initialized with power analyzer")
        else:
            # Use power supply for monitoring (backward compatibility)
            self._power_monitor = PowerMonitor(power_service)
            logger.info("Power monitor initialized with power supply")

    async def setup_power_supply(
        self, voltage: float, current: float, poweron_stabilization: float
    ) -> None:
        """
        Configure and enable power supply

        Args:
            voltage: Target voltage
            current: Current limit
            poweron_stabilization: Stabilization delay after power on
        """
        logger.info(f"Setting up power supply: {voltage}V, {current}A")
        power_service = self._hardware_services.power_service

        # Power off first to ensure clean state
        await power_service.disable_output()
        await asyncio.sleep(0.5)  # Brief delay after power off

        await power_service.set_voltage(voltage)
        await power_service.set_current(current)
        await power_service.enable_output()
        await asyncio.sleep(poweron_stabilization)

    async def setup_mcu(self, hc_config) -> None:
        """
        Configure MCU for heating/cooling testing

        Args:
            hc_config: Heating/cooling configuration object
        """
        mcu_service = self._hardware_services.mcu_service

        # Wait for MCU boot completion
        logger.info("Waiting for MCU boot completion...")
        await mcu_service.wait_boot_complete()
        logger.info(
            f"MCU boot complete stabilization delay: {hc_config.mcu_boot_complete_stabilization}s..."
        )
        await asyncio.sleep(hc_config.mcu_boot_complete_stabilization)

        # MCU setup
        logger.info("Setting up MCU...")
        await mcu_service.set_test_mode(TestMode.MODE_1)
        await asyncio.sleep(hc_config.mcu_command_stabilization)

        await mcu_service.set_upper_temperature(hc_config.upper_temperature)
        await asyncio.sleep(hc_config.mcu_command_stabilization)

        await mcu_service.set_fan_speed(hc_config.fan_speed)
        await asyncio.sleep(hc_config.mcu_command_stabilization)

    async def initialize_temperature(self, hc_config) -> None:
        """
        Set initial temperature to standby

        Args:
            hc_config: Heating/cooling configuration object
        """
        mcu_service = self._hardware_services.mcu_service

        # Initial temperature setup (set to standby)
        logger.info("Setting initial temperature to standby...")
        await mcu_service.start_standby_heating(
            operating_temp=hc_config.activation_temperature,
            standby_temp=hc_config.standby_temperature,
        )
        await asyncio.sleep(hc_config.mcu_command_stabilization)

        # Cool down to standby temperature
        await mcu_service.start_standby_cooling()
        logger.info(
            f"Initial cooling to standby temperature ({hc_config.standby_temperature}°C)..."
        )
        await asyncio.sleep(hc_config.mcu_temperature_stabilization)

        # Clear timing history (exclude initial setup)
        mcu_service.clear_timing_history()

    async def initialize_robot(self, hc_config, hardware_config) -> None:
        """
        Initialize robot to initial position for heating/cooling test

        Args:
            hc_config: Heating/cooling configuration object
            hardware_config: Hardware configuration object
        """
        if not hc_config.enable_robot:
            logger.info("Robot disabled in configuration, skipping robot initialization")
            return

        logger.info("Initializing robot for heating/cooling test...")

        # Access services via facade (Clean Architecture)
        robot_service = self._hardware_services.robot_service
        digital_io_service = self._hardware_services.digital_io_service

        # 1. Enable servo brake release
        await digital_io_service.write_output(hardware_config.digital_io.servo1_brake_release, True)
        logger.info("✅ Servo brake release enabled")

        # 2. Enable robot servo
        await robot_service.enable_servo(hardware_config.robot.axis_id)
        logger.info("✅ Robot servo enabled")

        # 3. Ensure robot is homed (reuse facade method)
        await self._hardware_services._ensure_robot_homed(hardware_config.robot.axis_id)
        logger.info("✅ Robot homing completed")

        # 4. Move to initial position (원점)
        await robot_service.move_absolute(
            position=hc_config.initial_position,
            axis_id=hardware_config.robot.axis_id,
            velocity=hc_config.velocity,
            acceleration=hc_config.acceleration,
            deceleration=hc_config.deceleration,
        )
        await asyncio.sleep(hc_config.robot_move_stabilization)

        logger.info(f"✅ Robot initialized at initial position: {hc_config.initial_position}μm")

    async def apply_test_specific_power_analyzer_config(self, hc_config) -> None:
        """
        Apply test-specific power analyzer configuration (overrides hardware config)

        This method allows test configurations to override hardware-level power analyzer
        settings. This is useful when different tests need different measurement ranges,
        filters, or other parameters while using the same physical hardware connection.

        Args:
            hc_config: Heating/cooling configuration object with test-specific power analyzer settings

        Note:
            - Only applies settings if power analyzer is configured and connected
            - Null/None values in test config will use hardware config defaults
            - Settings are applied AFTER hardware connection is established
        """
        power_analyzer = self._hardware_services.power_analyzer_service

        if not power_analyzer:
            logger.debug("No power analyzer configured, skipping test-specific configuration")
            return  # No power analyzer configured

        # Check if test config has any power analyzer settings
        has_test_settings = (
            hc_config.power_analyzer_voltage_range is not None
            or hc_config.power_analyzer_current_range is not None
            or hc_config.power_analyzer_auto_range is not None
            or hc_config.power_analyzer_line_filter is not None
            or hc_config.power_analyzer_frequency_filter is not None
        )

        if not has_test_settings:
            logger.debug(
                "No test-specific power analyzer settings found, using hardware config defaults"
            )
            return

        logger.info("Applying test-specific power analyzer configuration...")

        try:
            # Apply input range settings if specified
            if any(
                [
                    hc_config.power_analyzer_voltage_range,
                    hc_config.power_analyzer_current_range,
                    hc_config.power_analyzer_auto_range is not None,
                ]
            ):
                auto_range = (
                    hc_config.power_analyzer_auto_range
                    if hc_config.power_analyzer_auto_range is not None
                    else True
                )
                await power_analyzer.configure_input(
                    voltage_range=hc_config.power_analyzer_voltage_range,
                    current_range=hc_config.power_analyzer_current_range,
                    auto_range=auto_range,
                )
                logger.debug(
                    f"Power analyzer input configured - "
                    f"Voltage: {hc_config.power_analyzer_voltage_range or 'auto'}, "
                    f"Current: {hc_config.power_analyzer_current_range or 'auto'}, "
                    f"Auto-range: {auto_range}"
                )

            # Apply filter settings if specified
            if hc_config.power_analyzer_line_filter or hc_config.power_analyzer_frequency_filter:
                await power_analyzer.configure_filter(
                    line_filter=hc_config.power_analyzer_line_filter,
                    frequency_filter=hc_config.power_analyzer_frequency_filter,
                )
                logger.debug(
                    f"Power analyzer filters configured - "
                    f"Line: {hc_config.power_analyzer_line_filter or 'default'}, "
                    f"Frequency: {hc_config.power_analyzer_frequency_filter or 'default'}"
                )

            logger.info("Test-specific power analyzer configuration applied successfully")

        except Exception as e:
            logger.warning(f"Failed to apply test-specific power analyzer configuration: {e}")
            logger.warning(
                "Continuing with hardware config defaults. "
                "Test may proceed with non-optimal measurement settings."
            )

    async def cleanup_hardware(self, hc_config, hardware_config) -> None:
        """
        Clean up hardware connections

        Stops power monitoring, disables power supply, returns robot to safe position,
        and disconnects all hardware services.

        Args:
            hc_config: Heating/cooling configuration object
            hardware_config: Hardware configuration object
        """
        try:
            logger.info("Cleaning up hardware...")

            # Clean up power monitor first
            if self._power_monitor and self._power_monitor.is_monitoring():
                try:
                    logger.info("Stopping power monitor during hardware cleanup...")
                    await self._power_monitor.stop_monitoring()
                    logger.info("Power monitor stopped successfully")
                except Exception as power_monitor_error:
                    logger.warning(f"Power monitor cleanup warning: {power_monitor_error}")

            power_service = self._hardware_services.power_service

            # Robot cleanup (conditional)
            if hc_config.enable_robot:
                robot_service = self._hardware_services.robot_service

                # Return to initial position (safe position)
                if await robot_service.is_connected():
                    try:
                        current_pos = await robot_service.get_position(
                            hardware_config.robot.axis_id
                        )
                        if abs(current_pos - hc_config.initial_position) > 100:  # 100μm tolerance
                            logger.info("Returning robot to initial position...")
                            await robot_service.move_absolute(
                                position=hc_config.initial_position,
                                axis_id=hardware_config.robot.axis_id,
                                velocity=hc_config.velocity,
                                acceleration=hc_config.acceleration,
                                deceleration=hc_config.deceleration,
                            )
                            logger.info("✅ Robot returned to initial position")
                    except Exception as robot_error:
                        logger.warning(f"Robot cleanup warning: {robot_error}")

            # Disable power supply output
            await power_service.disable_output()

            # Disconnect all services
            await self._disconnect_all_services(hc_config)
            logger.info("✅ Hardware cleanup completed")

        except Exception as cleanup_error:
            logger.warning(f"Hardware cleanup warning: {cleanup_error}")

    async def _disconnect_all_services(self, hc_config) -> None:
        """
        Disconnect all hardware services

        Args:
            hc_config: Heating/cooling configuration object
        """
        disconnect_tasks = [
            self._hardware_services.power_service.disconnect(),
            self._hardware_services.mcu_service.disconnect(),
        ]

        # Robot-related services (conditional)
        if hc_config.enable_robot:
            disconnect_tasks.extend(
                [
                    self._hardware_services.robot_service.disconnect(),
                    self._hardware_services.loadcell_service.disconnect(),
                    self._hardware_services.digital_io_service.disconnect(),
                ]
            )

        # Power analyzer (optional)
        power_analyzer = self._hardware_services.power_analyzer_service
        if power_analyzer:
            disconnect_tasks.append(power_analyzer.disconnect())

        # Disconnect all in parallel, catch individual errors
        await asyncio.gather(*disconnect_tasks, return_exceptions=True)
