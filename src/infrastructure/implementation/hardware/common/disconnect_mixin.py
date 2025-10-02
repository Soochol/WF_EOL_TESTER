"""
Hardware Disconnect Mixin

Provides robust disconnect pattern for all hardware implementations.
Guarantees resource cleanup even when errors occur during disconnection.
"""

# Standard library imports
import asyncio
from typing import Optional, Callable

# Third-party imports
from loguru import logger


class RobustDisconnectMixin:
    """
    Mixin providing robust disconnect pattern with guaranteed cleanup

    Usage:
        class MyHardware(RobustDisconnectMixin):
            async def disconnect(self) -> None:
                await self._robust_disconnect(
                    cleanup_func=self._perform_disconnect,
                    state_vars={
                        '_is_connected': False,
                        '_connection': None,
                        '_other_resource': None
                    },
                    hardware_name="MyHardware"
                )

            async def _perform_disconnect(self) -> None:
                # Actual disconnect logic here
                if self._connection:
                    await self._connection.close()
    """

    async def _robust_disconnect(
        self,
        cleanup_func: Optional[Callable] = None,
        state_vars: Optional[dict] = None,
        hardware_name: str = "Hardware",
    ) -> None:
        """
        Perform robust disconnect with guaranteed state cleanup

        Args:
            cleanup_func: Optional async function to perform actual disconnect
            state_vars: Dictionary of {attribute_name: value} to set in finally
            hardware_name: Name for logging purposes

        Example:
            await self._robust_disconnect(
                cleanup_func=lambda: self._tcp.disconnect(),
                state_vars={'_is_connected': False, '_tcp': None},
                hardware_name="ODA Power"
            )
        """
        disconnect_error = None

        try:
            if cleanup_func:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
                logger.debug(f"{hardware_name} disconnect operation completed")

        except Exception as e:
            disconnect_error = e
            logger.warning(f"Error during {hardware_name} disconnect: {e}")
            # Don't raise - continue to cleanup

        finally:
            # Always perform state cleanup to prevent resource leaks
            if state_vars:
                for attr_name, value in state_vars.items():
                    setattr(self, attr_name, value)

            if disconnect_error:
                logger.warning(f"{hardware_name} disconnected with errors: {disconnect_error}")
            else:
                logger.info(f"{hardware_name} disconnected successfully")
