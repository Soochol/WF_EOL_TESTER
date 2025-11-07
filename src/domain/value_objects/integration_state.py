"""
Integration State Management (Domain Layer)

Defines integration states and state transition rules according to
Clean Architecture principles. This is part of the domain layer and
contains business logic for integration state management.
"""

# Standard library imports
from enum import Enum
from typing import Optional


class IntegrationState(Enum):
    """
    Power analyzer integration states

    State Transitions:
        IDLE → CONFIGURED (via setup_integration)
        CONFIGURED → RUNNING (via start_integration)
        RUNNING → STOPPED (via stop_integration)
        STOPPED → IDLE (via reset_integration)
        Any → IDLE (via reset_integration - force reset)
    """

    IDLE = "idle"  # Not configured, ready for setup
    CONFIGURED = "configured"  # Configured but not started
    RUNNING = "running"  # Integration actively measuring
    STOPPED = "stopped"  # Integration stopped, data available


class IntegrationStateManager:
    """
    Manages integration state transitions with validation

    Ensures all state transitions follow valid paths and prevents
    invalid operations. This is domain logic that enforces business rules.
    """

    def __init__(self, initial_state: IntegrationState = IntegrationState.IDLE):
        """
        Initialize state manager

        Args:
            initial_state: Starting state (default: IDLE)
        """
        self._state = initial_state
        self._last_error: Optional[str] = None

    @property
    def state(self) -> IntegrationState:
        """Get current state"""
        return self._state

    @property
    def last_error(self) -> Optional[str]:
        """Get last validation error"""
        return self._last_error

    def can_configure(self) -> bool:
        """
        Check if configuration is allowed in current state

        Configuration is allowed from:
        - IDLE: Initial configuration
        - CONFIGURED: Re-configuration
        - STOPPED: Re-configuration after measurement

        Returns:
            True if configuration is allowed
        """
        return self._state in [
            IntegrationState.IDLE,
            IntegrationState.CONFIGURED,
            IntegrationState.STOPPED,
        ]

    def can_start(self) -> bool:
        """
        Check if start is allowed in current state

        Start is allowed from:
        - CONFIGURED: Normal start after configuration

        Returns:
            True if start is allowed
        """
        return self._state == IntegrationState.CONFIGURED

    def can_stop(self) -> bool:
        """
        Check if stop is allowed in current state

        Stop is allowed from:
        - RUNNING: Normal stop during measurement

        Returns:
            True if stop is allowed
        """
        return self._state == IntegrationState.RUNNING

    def can_reset(self) -> bool:
        """
        Check if reset is allowed in current state

        Reset is always allowed (force reset to IDLE)

        Returns:
            True (always allowed)
        """
        return True

    def configure(self) -> bool:
        """
        Transition to CONFIGURED state

        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_configure():
            self._last_error = (
                f"Cannot configure from {self._state.value} state. "
                f"Current state must be IDLE, CONFIGURED, or STOPPED."
            )
            return False

        self._state = IntegrationState.CONFIGURED
        self._last_error = None
        return True

    def start(self) -> bool:
        """
        Transition to RUNNING state

        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_start():
            self._last_error = (
                f"Cannot start from {self._state.value} state. "
                f"Must configure integration first (state must be CONFIGURED)."
            )
            return False

        self._state = IntegrationState.RUNNING
        self._last_error = None
        return True

    def stop(self) -> bool:
        """
        Transition to STOPPED state

        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_stop():
            self._last_error = (
                f"Cannot stop from {self._state.value} state. "
                f"Integration must be running (state must be RUNNING)."
            )
            return False

        self._state = IntegrationState.STOPPED
        self._last_error = None
        return True

    def reset(self) -> bool:
        """
        Reset to IDLE state (force reset from any state)

        Returns:
            True (always succeeds)
        """
        self._state = IntegrationState.IDLE
        self._last_error = None
        return True

    def is_idle(self) -> bool:
        """Check if in IDLE state"""
        return self._state == IntegrationState.IDLE

    def is_configured(self) -> bool:
        """Check if in CONFIGURED state"""
        return self._state == IntegrationState.CONFIGURED

    def is_running(self) -> bool:
        """Check if in RUNNING state"""
        return self._state == IntegrationState.RUNNING

    def is_stopped(self) -> bool:
        """Check if in STOPPED state"""
        return self._state == IntegrationState.STOPPED

    def get_state_name(self) -> str:
        """Get human-readable state name"""
        return self._state.value.upper()

    def __repr__(self) -> str:
        """String representation"""
        return f"IntegrationStateManager(state={self._state.value})"
