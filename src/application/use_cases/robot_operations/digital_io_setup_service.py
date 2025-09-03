"""
Digital I/O Setup Service for Robot Operations

Handles Digital I/O configuration and servo brake release for robot operations.
Manages connection verification and output channel control.
"""

from loguru import logger

from application.services.hardware_facade import HardwareServiceFacade
from domain.exceptions.hardware_exceptions import HardwareConnectionException


class DigitalIOSetupService:
    """
    Digital I/O setup service for robot operations

    Manages Digital I/O service connection and configuration for robot operations,
    particularly servo brake release functionality.
    """

    def __init__(self, hardware_services: HardwareServiceFacade):
        """
        Initialize Digital I/O setup service

        Args:
            hardware_services: Hardware service facade
        """
        self._hardware_services = hardware_services

    async def setup_servo_brake_release(self, hardware_config) -> None:
        """
        Setup Digital I/O service for servo brake release

        Args:
            hardware_config: Hardware configuration containing digital I/O settings

        Raises:
            HardwareConnectionException: If Digital I/O setup fails
        """
        servo_brake_channel = hardware_config.digital_io.servo1_brake_release
        irq_no = hardware_config.robot.irq_no

        logger.info(
            f"Enabling servo brake release on Digital Output channel {servo_brake_channel} for robot homing preparation..."
        )
        logger.info(f"Checking Digital I/O service connection with irq_no={irq_no}...")

        try:
            await self._ensure_connection()
            await self._enable_brake_release(servo_brake_channel)

        except Exception as dio_error:
            self._handle_setup_error(dio_error, servo_brake_channel, irq_no)

    async def _ensure_connection(self) -> None:
        """
        Ensure Digital I/O service is connected and verified

        Raises:
            HardwareConnectionException: If connection fails
        """
        # Check if already connected, if not connect
        if not await self._hardware_services.digital_io_service.is_connected():
            await self._hardware_services.digital_io_service.connect()
            logger.info("Digital I/O service connected successfully")
        else:
            logger.info("Digital I/O service already connected")

        # Verify connection by checking status
        if not await self._hardware_services.digital_io_service.is_connected():
            raise HardwareConnectionException("Digital I/O service connection verification failed")
        logger.info("Digital I/O service connection verified")

    async def _enable_brake_release(self, servo_brake_channel: int) -> None:
        """
        Enable servo brake release on specified channel

        Args:
            servo_brake_channel: Digital output channel for brake release

        Raises:
            Exception: If brake release enable fails
        """
        await self._hardware_services.digital_io_service.write_output(servo_brake_channel, True)
        logger.info(
            f"Digital Output channel {servo_brake_channel} (servo brake release) enabled successfully"
        )

    def _handle_setup_error(
        self, dio_error: Exception, servo_brake_channel: int, irq_no: int
    ) -> None:
        """
        Handle and classify Digital I/O setup errors

        Args:
            dio_error: The original exception
            servo_brake_channel: Digital output channel that failed
            irq_no: IRQ number for context

        Raises:
            HardwareConnectionException: Classified hardware error
        """
        if "connection" in str(dio_error).lower():
            logger.error(f"Digital I/O service connection failed: {dio_error}")
            raise HardwareConnectionException(
                f"Failed to connect to Digital I/O service: {str(dio_error)}",
                details={"irq_no": irq_no, "error": str(dio_error)},
            ) from dio_error
        else:
            logger.error(
                f"Failed to enable Digital Output channel {servo_brake_channel} (servo brake release): {dio_error}"
            )
            raise HardwareConnectionException(
                f"Failed to enable servo brake release on Digital Output channel {servo_brake_channel} for robot homing: {str(dio_error)}",
                details={"dio_channel": servo_brake_channel, "dio_error": str(dio_error)},
            ) from dio_error
