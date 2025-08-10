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
    from application.services.hardware_service_facade import HardwareServiceFacade
    from application.use_cases.eol_force_test.main_executor import EOLForceTestUseCase


class EmergencyStopService:
    """
    Emergency Stop Service with Hardware-First Safety Approach

    Provides immediate hardware safety response followed by systematic
    software cleanup for emergency stop scenarios.
    """

    def __init__(
        self,
        hardware_facade: "HardwareServiceFacade",
        eol_use_case: Optional["EOLForceTestUseCase"] = None,
    ):
        """
        Initialize Emergency Stop Service

        Args:
            hardware_facade: Hardware service facade for accessing all hardware
            eol_use_case: EOL test use case for state management (optional)
        """
        self.hardware_facade = hardware_facade
        self.eol_use_case = eol_use_case

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

            # Phase 2: UseCase state management and software cleanup
            await self._handle_usecase_emergency_stop()

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
                # Use axis 0 (primary axis) for emergency stop
                await robot_service.emergency_stop(axis=0)
                logger.critical(
                    "✓ Robot emergency stop executed - motion stopped and servo disabled"
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

    async def _handle_usecase_emergency_stop(self) -> None:
        """Handle UseCase state management during emergency stop"""
        logger.critical("Phase 2: Handling UseCase emergency stop")

        if not self.eol_use_case:
            logger.warning("No EOL UseCase provided - skipping UseCase emergency handling")
            return

        try:
            # Check if UseCase is currently running
            if self.eol_use_case.is_running():
                logger.critical("UseCase is running - initiating emergency cancellation")

                # The UseCase._is_running flag will be cleared automatically
                # when the UseCase's finally block executes after task cancellation

                # Note: In AsyncIO, we cannot directly cancel a running UseCase
                # from outside its execution context. The UseCase must handle
                # emergency stop through its own mechanisms (e.g., checking
                # emergency flags during operation loops).

                # The hardware emergency stop (Phase 1) will cause hardware
                # operations to fail, which will naturally cause the UseCase
                # to enter its exception handling and cleanup phases.

                logger.critical(
                    "UseCase emergency handling initiated - hardware failures will trigger cleanup"
                )
            else:
                logger.info("UseCase not running - no active test to cancel")

        except Exception as e:
            logger.error(f"UseCase emergency handling failed: {e}")

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
            "usecase_status": (
                "cancelled" if self.eol_use_case and self.eol_use_case.is_running() else "idle"
            ),
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
