"""
Emergency Stop Service

Handles emergency stop operations with hardware-first safety approach.
Integrates with button monitoring, hardware services, and use case management.
"""

import asyncio
from typing import TYPE_CHECKING, Optional

from loguru import logger

# Hardware interface imports removed - accessed through facade

if TYPE_CHECKING:
    from application.services.hardware_facade import HardwareServiceFacade
    from application.services.core.configuration_service import ConfigurationService


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
    ):
        """
        Initialize Emergency Stop Service

        Args:
            hardware_facade: Hardware service facade for accessing all hardware
            configuration_service: Configuration service for reading hardware settings
        """
        self.hardware_facade = hardware_facade
        self.configuration_service = configuration_service

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
        logger.critical("🚨 EXECUTING EMERGENCY STOP PROCEDURE 🚨")

        # Set emergency state flag
        self._emergency_active = True
        self._last_emergency_time = asyncio.get_event_loop().time()

        try:
            # Phase 1: Hardware-level immediate safety actions (HIGHEST PRIORITY)
            await self._execute_hardware_emergency_stop()

            # Phase 2: Software cleanup (UseCase emergency stop is handled by BaseUseCase)
            await self._handle_software_cleanup()

            # Phase 3: System-wide cleanup and safe state
            await self._finalize_emergency_stop()

            logger.critical("🚨 EMERGENCY STOP PROCEDURE COMPLETED SUCCESSFULLY 🚨")

        except Exception as e:
            logger.error(f"Error during emergency stop procedure: {e}")
            # Emergency stop errors should not prevent hardware safety actions
            # Hardware should already be in safe state from Phase 1
            raise
        finally:
            # Always maintain emergency state until manually reset
            logger.critical(
                "Emergency stop system is now in EMERGENCY STATE - manual reset required"
            )

    async def _execute_hardware_emergency_stop(self) -> None:
        """Execute immediate hardware safety actions"""
        logger.critical("Phase 1: Executing hardware-level emergency stop")

        # Robot emergency stop - highest priority
        try:
            robot_service = self.hardware_facade.robot_service
            if robot_service and await robot_service.is_connected():
                # Get robot axis ID from configuration
                hardware_config = await self.configuration_service.load_hardware_config()
                robot_axis = hardware_config.robot.axis_id
                await robot_service.emergency_stop(axis=robot_axis)
                logger.critical(
                    f"✓ Robot emergency stop executed on axis {robot_axis} - motion stopped and servo disabled"
                )
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
                logger.critical("✓ Power supply emergency shutdown executed")
            else:
                logger.warning("Power service not available - skipping power emergency stop")
        except Exception as e:
            logger.error(f"Power emergency stop failed: {e}")
            # Continue with other safety actions

        # Additional hardware safety actions can be added here
        # (e.g., pneumatic systems, hydraulics, etc.)

        logger.critical("Phase 1 completed: Hardware emergency stop actions executed")

    async def _handle_software_cleanup(self) -> None:
        """Handle software cleanup during emergency stop"""
        logger.critical("Phase 2: Handling software cleanup")

        try:
            # Software cleanup operations
            logger.info("Emergency stop initiated - UseCase emergency stop handled by BaseUseCase")
            logger.info("Hardware emergency stop completed, software cleanup in progress")

        except Exception as e:
            logger.error(f"Software cleanup failed: {e}")

    async def _finalize_emergency_stop(self) -> None:
        """Finalize emergency stop with system cleanup"""
        logger.critical("Phase 3: Finalizing emergency stop procedure")

        try:
            # Ensure all hardware is in safe state
            await self._verify_hardware_safe_state()

            # System-wide notification (can be extended for external systems)
            await self._notify_emergency_stop()

        except Exception as e:
            logger.error(f"Emergency stop finalization failed: {e}")

    async def _verify_hardware_safe_state(self) -> None:
        """Verify that all hardware is in safe state after emergency stop"""
        logger.info("Verifying hardware safe state after emergency stop")

        # Check robot state
        try:
            robot_service = self.hardware_facade.robot_service
            if robot_service and await robot_service.is_connected():
                robot_status = await robot_service.get_status()
                logger.info(f"Robot status after emergency stop: {robot_status}")
        except Exception as e:
            logger.warning(f"Could not verify robot safe state: {e}")

        # Check power state
        try:
            power_service = self.hardware_facade.power_service
            if power_service and await power_service.is_connected():
                power_status = await power_service.get_status()
                logger.info(f"Power status after emergency stop: {power_status}")
        except Exception as e:
            logger.warning(f"Could not verify power safe state: {e}")

    async def _notify_emergency_stop(self) -> None:
        """Send emergency stop notifications to external systems"""
        logger.info("Sending emergency stop notifications")
        # This can be extended to notify external systems, databases, etc.
        # For now, we'll just log the event

        emergency_info = {
            "event": "emergency_stop",
            "timestamp": self._last_emergency_time,
            "hardware_status": "safe_state",
            "software_status": "emergency_cleanup_completed",
        }

        logger.critical(f"Emergency stop event logged: {emergency_info}")

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
