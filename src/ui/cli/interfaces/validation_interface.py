"""Input Validation Interface

Defines the contract for input validation with security hardening, pattern
validation, and protection against malicious input including ReDoS attacks
and buffer overflows.

This interface enables dependency injection and flexible implementation
substitution for different validation strategies.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Optional


class IInputValidator(ABC):
    """Abstract interface for input validation with security hardening.

    Defines the contract for robust input validation with multiple layers of
    security protection including length limits, pattern validation, and ReDoS
    attack prevention. Implementations should provide comprehensive security
    measures and user-friendly error handling.

    Key Responsibilities:
    - Multi-layered validation with security hardening
    - Safe regex patterns to prevent ReDoS vulnerabilities
    - Length limits to prevent buffer overflow attacks
    - Retry mechanisms with attempt limiting
    - Comprehensive error reporting and user feedback
    """

    @abstractmethod
    def validate_input(self, user_input: str, input_type: str = "general") -> bool:
        """Validate user input against security patterns with multi-layered protection.

        Performs comprehensive validation including null checks, length validation,
        and pattern matching with ReDoS attack prevention. Uses multiple security
        layers to ensure robust input validation.

        Args:
            user_input: String to validate (can be None or empty)
            input_type: Type of input for specific validation rules

        Returns:
            True if input passes all validation checks, False otherwise
        """
        ...

    @abstractmethod
    def get_validated_input(
        self,
        prompt: str,
        input_type: str = "general",
        required: bool = False,
        max_attempts: int = 3,
    ) -> Optional[str]:
        """Get validated input from user with comprehensive security and retry logic.

        Provides a secure interface for collecting user input with validation,
        retry mechanisms, and graceful error handling. Includes protection against
        malicious input and provides clear feedback for validation failures.

        Args:
            prompt: Input prompt message to display to the user
            input_type: Type of input for specific validation rules
            required: Whether the input is mandatory (prevents empty submissions)
            max_attempts: Maximum number of retry attempts before giving up

        Returns:
            Validated input string if successful, or None if validation fails
            or user cancels the operation
        """
        ...
