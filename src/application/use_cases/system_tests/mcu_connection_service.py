"""
MCU Connection Service for System Tests

Handles MCU connection setup, boot completion waiting, and cleanup.
Manages the hardware connection lifecycle for MCU testing.
"""

import asyncio
from loguru import logger

from application.services.hardware_service_facade import HardwareServiceFacade


class MCUConnectionService:
    """
    MCU connection service for system tests
    
    Manages MCU connection lifecycle including connection setup,
    boot completion waiting, and proper disconnection cleanup.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize MCU connection service
        
        Args:
            hardware_services: Hardware service facade
        """
        self._hardware_services = hardware_services
        self._mcu_service = None

    async def connect_and_initialize(self, hardware_config) -> None:
        """
        Connect to MCU and wait for initialization
        
        Args:
            hardware_config: Hardware configuration containing MCU settings
            
        Raises:
            RuntimeError: If MCU service is not available
            Exception: If connection or initialization fails
        """
        # Get MCU service using public property
        self._mcu_service = self._hardware_services.mcu_service
        if not self._mcu_service:
            raise RuntimeError("MCU service not available")

        # Connect to MCU using configuration values
        logger.info(
            f"Connecting to MCU - Port: {hardware_config.mcu.port}, Baudrate: {hardware_config.mcu.baudrate}"
        )
        await self._mcu_service.connect()

        # Wait for boot complete
        logger.info("Waiting for MCU boot complete...")
        await self._mcu_service.wait_boot_complete()

        # Add stabilization delay after boot complete
        logger.info("Boot complete confirmed, waiting 2 seconds for stabilization...")
        await asyncio.sleep(2.0)
        
        logger.info("MCU connection and initialization completed")

    async def disconnect(self) -> None:
        """
        Disconnect from MCU with proper cleanup
        
        Handles disconnection gracefully even if already disconnected.
        """
        if self._mcu_service:
            try:
                await self._mcu_service.disconnect()
                logger.info("MCU disconnected successfully")
            except Exception as disconnect_error:
                logger.warning(f"Failed to disconnect MCU: {disconnect_error}")
        else:
            logger.warning("MCU service not available for disconnection")

    async def cleanup_on_error(self) -> None:
        """
        Clean up MCU connection when an error occurs
        
        Attempts to disconnect MCU service safely during error conditions.
        """
        try:
            if self._mcu_service:
                await self._mcu_service.disconnect()
                logger.info("MCU disconnected during error cleanup")
        except Exception as cleanup_error:
            logger.warning(f"Failed to disconnect MCU during error cleanup: {cleanup_error}")
