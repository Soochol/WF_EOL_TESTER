"""
NeuroHub MES Integration Service

Service for communicating with NeuroHub MES Client.
Sends START (착공) and COMPLETE (완공) messages via TCP/IP.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

# Third-party imports
from loguru import logger

# Local application imports
from domain.value_objects.neurohub_config import NeuroHubConfig
from driver.tcp.neurohub_protocol import (
    NeuroHubAck,
    NeuroHubProtocol,
)


if TYPE_CHECKING:
    from application.services.core.configuration_service import ConfigurationService


class NeuroHubService:
    """
    NeuroHub MES Integration Service

    Handles communication with NeuroHub MES Client for work order tracking.
    - START (착공): Work start notification
    - COMPLETE (완공): Work completion notification with test results

    Design principles:
    - Non-blocking: Communication failures don't stop test execution
    - Lazy initialization: Connects only when needed
    - Configurable: Can be enabled/disabled via configuration
    """

    def __init__(
        self,
        configuration_service: "ConfigurationService",
    ):
        """
        Initialize NeuroHub Service

        Args:
            configuration_service: Configuration service for loading settings
        """
        self._configuration_service = configuration_service
        self._config: Optional[NeuroHubConfig] = None
        self._protocol: Optional[NeuroHubProtocol] = None
        self._initialized = False
        self._enabled = False

        logger.info("🔗 NEUROHUB: NeuroHub Service initialized")

    async def _ensure_initialized(self) -> bool:
        """
        Ensure service is initialized and connected

        Returns:
            bool: True if service is ready, False otherwise
        """
        if self._initialized:
            return self._enabled

        try:
            # Load hardware config to get neurohub settings
            hardware_config = await self._configuration_service.load_hardware_config()
            self._config = hardware_config.neurohub
            self._enabled = self._config.enabled

            if not self._enabled:
                logger.info("🔗 NEUROHUB: Service is disabled in configuration")
                self._initialized = True
                return False

            # Create protocol instance
            self._protocol = NeuroHubProtocol(
                host=self._config.host,
                port=self._config.port,
                timeout=self._config.timeout,
            )

            self._initialized = True
            logger.info(
                f"🔗 NEUROHUB: Service enabled - {self._config.host}:{self._config.port}"
            )
            return True

        except Exception as e:
            logger.error(f"🔗 NEUROHUB: Failed to initialize: {e}")
            self._initialized = True
            self._enabled = False
            return False

    async def _connect_with_retry(self) -> Tuple[bool, str]:
        """
        Connect to NeuroHub Client with retry logic

        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self._protocol or not self._config:
            return False, "NeuroHub protocol not initialized"

        last_error = ""
        for attempt in range(self._config.retry_attempts):
            try:
                # Check if already connected and connection is valid
                if self._protocol.is_connected:
                    return True, ""

                # Attempt to connect
                logger.info(f"🔗 NEUROHUB: Connection attempt {attempt + 1}/{self._config.retry_attempts}")
                await self._protocol.connect()
                return True, ""

            except Exception as e:
                last_error = str(e)
                error_type = type(e).__name__
                logger.warning(
                    f"🔗 NEUROHUB: Connection attempt {attempt + 1}/{self._config.retry_attempts} failed: {error_type}: {e}"
                )

                # Reset protocol for next retry to ensure clean reconnection
                if attempt < self._config.retry_attempts - 1:
                    logger.info(f"🔗 NEUROHUB: Waiting {self._config.retry_delay}s before retry...")
                    import asyncio
                    await asyncio.sleep(self._config.retry_delay)
                    # Reset connection state for next attempt
                    try:
                        await self._protocol.disconnect()
                    except Exception:
                        pass  # Ignore errors during cleanup

        error_msg = f"NeuroHub connection failed: {last_error}"
        logger.error(f"🔗 NEUROHUB: {error_msg}")
        return False, error_msg

    async def send_start(self, serial_number: str) -> bool:
        """
        Send START (착공) message to NeuroHub

        Args:
            serial_number: WIP serial number

        Returns:
            bool: True if message sent successfully
        """
        if not await self._ensure_initialized():
            return False

        if not self._enabled or not self._protocol:
            logger.debug("🔗 NEUROHUB: Service disabled, skipping START")
            return True  # Return True to not block test execution

        try:
            # Connect with retry
            connected, error_msg = await self._connect_with_retry()
            if not connected:
                logger.warning(f"🔗 NEUROHUB: {error_msg}")
                return False

            # Send START message
            logger.info(f"🔗 NEUROHUB: Sending START for {serial_number}")
            ack = await self._protocol.send_start(serial_number)

            if ack.status == "OK":
                logger.info(f"🔗 NEUROHUB: START acknowledged for {serial_number}")
                return True
            else:
                logger.warning(
                    f"🔗 NEUROHUB: START failed - {ack.error_code}: {ack.message}"
                )
                return False

        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"🔗 NEUROHUB: Error sending START: {error_type}: {e}")
            return False
        finally:
            # Always disconnect after START to ensure fresh connection for COMPLETE
            await self._safe_disconnect()

    async def send_complete(
        self,
        serial_number: str,
        result: str,
        measurements: Optional[List[Dict[str, Any]]] = None,
        defects: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Send COMPLETE (완공) message to NeuroHub

        Args:
            serial_number: WIP serial number
            result: Test result ("PASS" or "FAIL")
            measurements: List of measurement data
            defects: List of defect information (for FAIL results)

        Returns:
            bool: True if message sent successfully
        """
        if not await self._ensure_initialized():
            return False

        if not self._enabled or not self._protocol:
            logger.debug("🔗 NEUROHUB: Service disabled, skipping COMPLETE")
            return True  # Return True to not block test execution

        try:
            # Connect with retry
            connected, error_msg = await self._connect_with_retry()
            if not connected:
                logger.warning(f"🔗 NEUROHUB: {error_msg}")
                return False

            # Send COMPLETE message
            logger.info(f"🔗 NEUROHUB: Sending COMPLETE ({result}) for {serial_number}")
            ack = await self._protocol.send_complete(
                serial_number=serial_number,
                result=result,
                measurements=measurements,
                defects=defects,
            )

            if ack.status == "OK":
                logger.info(
                    f"🔗 NEUROHUB: COMPLETE acknowledged for {serial_number} ({result})"
                )
                return True
            else:
                logger.warning(
                    f"🔗 NEUROHUB: COMPLETE failed - {ack.error_code}: {ack.message}"
                )
                return False

        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"🔗 NEUROHUB: Error sending COMPLETE: {error_type}: {e}")
            return False
        finally:
            # Always disconnect after COMPLETE
            await self._safe_disconnect()

    async def _safe_disconnect(self) -> None:
        """Safely disconnect from NeuroHub - guarantees connection is closed"""
        if not self._protocol:
            return

        # Always attempt to close the connection, even if errors occur
        try:
            if self._protocol.is_connected:
                logger.debug("🔗 NEUROHUB: Closing TCP connection...")
                success = await self._protocol.disconnect()
                if success:
                    logger.info("🔗 NEUROHUB: TCP connection closed successfully")
                else:
                    logger.warning("🔗 NEUROHUB: Failed to close TCP connection")
        except Exception as e:
            logger.error(f"🔗 NEUROHUB: Error during disconnect: {e}")
            # Force reset connection state even if disconnect() fails
            try:
                if self._protocol.writer:
                    self._protocol.writer.close()
                    await self._protocol.writer.wait_closed()
                self._protocol.is_connected = False
                logger.warning("🔗 NEUROHUB: Force closed TCP socket")
            except Exception as force_close_error:
                logger.error(f"🔗 NEUROHUB: Error during force close: {force_close_error}")
                # Last resort: mark as disconnected
                self._protocol.is_connected = False

    async def disconnect(self) -> None:
        """Disconnect from NeuroHub Client"""
        await self._safe_disconnect()
        logger.info("🔗 NEUROHUB: Disconnected")

    async def is_enabled(self) -> bool:
        """
        Check if NeuroHub service is enabled

        Returns:
            bool: True if service is enabled in configuration
        """
        await self._ensure_initialized()
        return self._enabled

    async def is_connected(self) -> bool:
        """
        Check if connected to NeuroHub Client

        Returns:
            bool: True if currently connected
        """
        if not self._protocol:
            return False
        return self._protocol.is_connected

    async def test_connection(self) -> bool:
        """
        Test connection to NeuroHub Client

        Returns:
            bool: True if connection test successful
        """
        if not await self._ensure_initialized():
            return False

        if not self._enabled:
            logger.info("🔗 NEUROHUB: Service disabled, connection test skipped")
            return False

        try:
            connected, error_msg = await self._connect_with_retry()
            if connected:
                logger.info("🔗 NEUROHUB: Connection test successful")
            else:
                logger.warning(f"🔗 NEUROHUB: {error_msg}")
            return connected

        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"🔗 NEUROHUB: Connection test failed: {error_type}: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """
        Get service status information

        Returns:
            Dictionary with service status
        """
        await self._ensure_initialized()

        return {
            "enabled": self._enabled,
            "connected": await self.is_connected(),
            "host": self._config.host if self._config else None,
            "port": self._config.port if self._config else None,
            "timeout": self._config.timeout if self._config else None,
        }

    async def shutdown(self) -> None:
        """Shutdown the service"""
        logger.info("🔗 NEUROHUB: Shutting down service...")
        await self.disconnect()
        self._initialized = False
        logger.info("🔗 NEUROHUB: Service shutdown complete")

    async def __aenter__(self) -> "NeuroHubService":
        """Async context manager entry"""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.shutdown()
