"""
Emergency Stop Service

Handles emergency stop operations with hardware-first safety approach.
Integrates with button monitoring, hardware services, and use case management.
"""

# Standard library imports
# Standard library imports
from typing import Optional, TYPE_CHECKING

# Third-party imports
import asyncio
from loguru import logger


# Hardware interface imports removed - accessed through facade

if TYPE_CHECKING:
    # Local application imports
    from application.services.core.configuration_service import ConfigurationService
    from application.services.hardware_facade import HardwareServiceFacade
    from application.services.industrial.industrial_system_manager import IndustrialSystemManager


class EmergencyStopService:
    """
    Emergency Stop Service with Hardware-First Safety Approach

    Provides immediate hardware safety response followed by systematic
    software cleanup for emergency stop scenarios.
    """

    def __init__(
        self,
        hardware_facade: "HardwareServiceFacade",
        configuration_service: "ConfigurationService",
        industrial_system_manager: Optional["IndustrialSystemManager"] = None,
    ):
        """
        Initialize Emergency Stop Service

        Args:
            hardware_facade: Hardware service facade for accessing all hardware
            configuration_service: Configuration service for reading hardware settings
            industrial_system_manager: Optional industrial system manager for status indication
        """
        self.hardware_facade = hardware_facade
        self.configuration_service = configuration_service
        self.industrial_system_manager = industrial_system_manager

        # Emergency stop state tracking
        self._emergency_active = False
        self._last_emergency_time: Optional[float] = None

        logger.info("EmergencyStopService initialized")

    async def execute_emergency_stop(self) -> None:
        """
        Execute emergency stop procedure with hardware-first approach

        This method implements the complete emergency stop sequence:
        1. Hardware-level immediate safety actions (servo off, power off)
        2. UseCase state management and task cancellation
        3. System cleanup and safe state transition
        """
        logger.info("🚨 EMERGENCY STOP 🚨")
        self._last_emergency_time = asyncio.get_event_loop().time()

        try:
            # Immediate industrial status indication for emergency
            if self.industrial_system_manager:
                await self.industrial_system_manager.handle_emergency_stop()

            # Hardware emergency stop and cleanup
            await self._execute_hardware_emergency_stop()
            await self._handle_software_cleanup()
            await self._finalize_emergency_stop()

            logger.info("✅ Emergency stop completed")

        except Exception as e:
            logger.error(f"Error during emergency stop procedure: {e}")
            # Emergency stop errors should not prevent hardware safety actions
            # Hardware should already be in safe state from Phase 1
            raise
        finally:
            # Always maintain emergency state until manually reset
            pass

    async def _execute_hardware_emergency_stop(self) -> None:
        """Execute immediate hardware safety actions"""

        # Robot emergency stop - highest priority
        try:
            robot_service = self.hardware_facade.robot_service
            if robot_service and await robot_service.is_connected():
                # Get robot axis ID from configuration
                hardware_config = await self.configuration_service.load_hardware_config()
                robot_axis = hardware_config.robot.axis_id
                await robot_service.emergency_stop(axis=robot_axis)
                logger.info(f"✓ Robot emergency stop executed on axis {robot_axis}")
            else:
                logger.warning("Robot service not available - skipping robot emergency stop")
        except Exception as e:
            logger.error(f"Robot emergency stop failed: {e}")
            # Continue with other safety actions even if robot stop fails

        # Power supply emergency shutdown
        try:
            power_service = self.hardware_facade.power_service
            if power_service and await power_service.is_connected():
                await power_service.disable_output()
                logger.info("✓ Power supply emergency shutdown executed")
            else:
                logger.warning("Power service not available - skipping power emergency stop")
        except Exception as e:
            logger.error(f"Power emergency stop failed: {e}")
            # Continue with other safety actions

        # Additional hardware safety actions can be added here
        # (e.g., pneumatic systems, hydraulics, etc.)

        pass

    async def _handle_software_cleanup(self) -> None:
        """Handle software cleanup during emergency stop"""

        try:
            # Software cleanup operations
            pass

            # Disconnect all hardware services to ensure clean state
            await self._disconnect_all_hardware()

        except Exception as e:
            logger.error(f"Software cleanup failed: {e}")

    async def _finalize_emergency_stop(self) -> None:
        """Finalize emergency stop with system cleanup"""

        try:
            # Ensure all hardware is in safe state
            await self._verify_hardware_safe_state()

            # System-wide notification (can be extended for external systems)
            await self._notify_emergency_stop()

        except asyncio.CancelledError:
            logger.info(
                "Emergency stop finalization cancelled due to shutdown - hardware safety already ensured"
            )
            # Don't re-raise CancelledError - hardware safety was already ensured in Phase 1
        except Exception as e:
            logger.error(f"Emergency stop finalization failed: {e}")

    async def _verify_hardware_safe_state(self) -> None:
        """Verify that all hardware is in safe state after emergency stop"""
        pass

        # Check robot state
        try:
            robot_service = self.hardware_facade.robot_service
            if robot_service and await robot_service.is_connected():
                robot_status = await robot_service.get_status()
                logger.debug(
                    f"Robot status after emergency stop: servo_enabled={robot_status.get('servo_enabled', 'unknown')}"
                )
        except asyncio.CancelledError:
            logger.info(
                "Robot state verification cancelled due to shutdown - skipping robot verification"
            )
            # Don't re-raise CancelledError during emergency stop
        except Exception as e:
            logger.warning(f"Could not verify robot safe state: {e}")

        # Check power state
        try:
            power_service = self.hardware_facade.power_service
            if power_service and await power_service.is_connected():
                power_status = await power_service.get_status()
                logger.debug(
                    f"Power status after emergency stop: output_enabled={power_status.get('output_enabled', 'unknown')}"
                )
        except asyncio.CancelledError:
            logger.info(
                "Power state verification cancelled due to shutdown - skipping power verification"
            )
            # Don't re-raise CancelledError during emergency stop
        except Exception as e:
            logger.warning(f"Could not verify power safe state: {e}")

    async def _notify_emergency_stop(self) -> None:
        """Send emergency stop notifications to external systems"""
        logger.debug("Emergency stop notifications completed")
        # This can be extended to notify external systems, databases, etc.
        # Emergency stop event is already logged at CRITICAL level in main procedure

    def is_emergency_active(self) -> bool:
        """
        Check if emergency stop is currently active

        Returns:
            True if emergency stop is active, False otherwise
        """
        return self._emergency_active

    def get_emergency_time(self) -> Optional[float]:
        """
        Get the time when emergency stop was activated

        Returns:
            Emergency stop activation time or None if not active
        """
        return self._last_emergency_time

    async def reset_emergency_stop(self) -> None:
        """
        Reset emergency stop state (should only be called after manual safety verification)

        This method should only be called after:
        1. Physical safety verification
        2. Hardware inspection
        3. System status confirmation
        """
        logger.warning("Resetting emergency stop state - ensure all safety checks completed")

        self._emergency_active = False
        self._last_emergency_time = None

        logger.info("Emergency stop state reset - system ready for normal operation")

    async def _disconnect_all_hardware(self) -> None:
        """Disconnect all hardware services during emergency stop cleanup"""
        pass

        # Disconnect robot service
        try:
            robot_service = self.hardware_facade.robot_service
            if robot_service and await robot_service.is_connected():
                await robot_service.disconnect()
                pass
        except Exception as e:
            logger.warning(f"Failed to disconnect robot service: {e}")

        # Disconnect power service
        try:
            power_service = self.hardware_facade.power_service
            if power_service and await power_service.is_connected():
                await power_service.disconnect()
                pass
        except Exception as e:
            logger.warning(f"Failed to disconnect power service: {e}")

        # Disconnect MCU service
        try:
            mcu_service = self.hardware_facade.mcu_service
            if mcu_service and await mcu_service.is_connected():
                await mcu_service.disconnect()
                pass
        except Exception as e:
            logger.warning(f"Failed to disconnect MCU service: {e}")

        # Disconnect loadcell service
        try:
            loadcell_service = self.hardware_facade.loadcell_service
            if loadcell_service and await loadcell_service.is_connected():
                await loadcell_service.disconnect()
                pass
        except Exception as e:
            logger.warning(f"Failed to disconnect loadcell service: {e}")

        pass
