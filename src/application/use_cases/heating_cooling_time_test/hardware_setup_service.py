"""
Hardware Setup Service for Heating/Cooling Time Test

Handles hardware initialization and configuration for heating/cooling time testing.
Manages power supply, MCU configuration, and initial temperature setup.
"""

import asyncio

from loguru import logger

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

        Connects power supply and MCU services.
        """
        logger.info("Connecting hardware...")
        power_service = self._hardware_services.power_service
        mcu_service = self._hardware_services.mcu_service

        await power_service.connect()
        await mcu_service.connect()

        # Initialize Power Monitor
        self._power_monitor = PowerMonitor(power_service)
        logger.info("Power monitor initialized")

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

    async def cleanup_hardware(self) -> None:
        """
        Clean up hardware connections

        Disables power supply and disconnects hardware services.
        """
        try:
            logger.info("Cleaning up hardware...")
            power_service = self._hardware_services.power_service
            mcu_service = self._hardware_services.mcu_service

            await power_service.disable_output()
            await power_service.disconnect()
            await mcu_service.disconnect()
        except Exception as cleanup_error:
            logger.warning(f"Hardware cleanup warning: {cleanup_error}")
