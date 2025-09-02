"""
Hardware Connection Manager

Manages hardware connections, status monitoring, and shutdown operations.
Extracted from HardwareServiceFacade for single responsibility compliance.
"""

import asyncio
from typing import Dict, Optional

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService
from application.interfaces.hardware.loadcell import LoadCellService
from application.interfaces.hardware.mcu import MCUService
from application.interfaces.hardware.power import PowerService
from application.interfaces.hardware.robot import RobotService
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.hardware_config import HardwareConfig


class HardwareConnectionManager:
    """
    Manages hardware connection lifecycle operations

    Handles connecting, monitoring status, and safely shutting down all hardware services.
    """

    def __init__(
        self,
        robot_service: RobotService,
        mcu_service: MCUService,
        loadcell_service: LoadCellService,
        power_service: PowerService,
        digital_io_service: DigitalIOService,
    ):
        self._robot = robot_service
        self._mcu = mcu_service
        self._loadcell = loadcell_service
        self._power = power_service
        self._digital_io = digital_io_service

    async def connect_all_hardware(self, hardware_config: HardwareConfig) -> None:
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

        # Digital I/O connection (if connect method is available)
        if not await self._digital_io.is_connected():
            if hasattr(self._digital_io, "connect") and callable(
                getattr(self._digital_io, "connect")
            ):
                try:
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

    async def shutdown_hardware(self, hardware_config: Optional[HardwareConfig] = None) -> None:
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
