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

    async def connect_hardware(self) -> None:
        """
        Connect required hardware components

        Connects power supply, MCU, and optional power analyzer services.
        If power analyzer is configured, it will be used for power monitoring instead of power supply.
        """
        logger.info("Connecting hardware...")
        power_service = self._hardware_services.power_service
        mcu_service = self._hardware_services.mcu_service
        power_analyzer = self._hardware_services.power_analyzer_service

        # Always connect power supply (for power control)
        await power_service.connect()
        await mcu_service.connect()

        # Connect power analyzer if available
        if power_analyzer:
            logger.info("Power analyzer detected - connecting...")
            await power_analyzer.connect()
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
            if (
                hc_config.power_analyzer_line_filter
                or hc_config.power_analyzer_frequency_filter
            ):
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
            logger.warning(
                f"Failed to apply test-specific power analyzer configuration: {e}"
            )
            logger.warning(
                "Continuing with hardware config defaults. "
                "Test may proceed with non-optimal measurement settings."
            )

    async def cleanup_hardware(self) -> None:
        """
        Clean up hardware connections

        Stops power monitoring, disables power supply, and disconnects all hardware services.
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
            mcu_service = self._hardware_services.mcu_service
            power_analyzer = self._hardware_services.power_analyzer_service

            # Disable power supply output
            await power_service.disable_output()

            # Disconnect all hardware
            await power_service.disconnect()
            await mcu_service.disconnect()

            # Disconnect power analyzer if it was connected
            if power_analyzer:
                try:
                    if await power_analyzer.is_connected():
                        await power_analyzer.disconnect()
                        logger.info("Power analyzer disconnected")
                except Exception as analyzer_error:
                    logger.warning(f"Power analyzer cleanup warning: {analyzer_error}")
        except Exception as cleanup_error:
            logger.warning(f"Hardware cleanup warning: {cleanup_error}")
