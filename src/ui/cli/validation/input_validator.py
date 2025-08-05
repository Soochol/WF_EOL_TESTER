"""
Input Validation Module

Comprehensive input validation with security hardening, pattern validation,
and protection against malicious input including ReDoS attacks and buffer overflows.

Key Features:
- Multi-layered validation with security hardening
- Safe regex patterns to prevent ReDoS vulnerabilities
- Length limits to prevent buffer overflow attacks
- Retry mechanisms with attempt limiting
- Comprehensive error reporting and user feedback
"""

# Standard library imports
import re
from typing import Optional

# Local imports
from ..interfaces.validation_interface import IInputValidator


class ValidationConstants:
    """Constants for input validation and security hardening.

    These constants define security limits and validation parameters to protect
    against malicious input and ensure robust operation of the CLI interface.
    They help prevent buffer overflow attacks, ReDoS vulnerabilities, and
    provide consistent validation behavior across the application.
    """

    # Global security limits to prevent abuse and attacks
    MAX_INPUT_LENGTH = 200  # Hard limit to prevent buffer overflow attacks
    MAX_ATTEMPTS = 3  # Maximum validation attempts before failure

    # Input type specific limits for granular validation
    DUT_ID_MAX_LENGTH = 20  # Device under test identifier length limit
    MODEL_MAX_LENGTH = 50  # Model number string length limit
    SERIAL_MAX_LENGTH = 30  # Serial number string length limit
    OPERATOR_MAX_LENGTH = 30  # Operator identifier length limit
    GENERAL_MAX_LENGTH = 100  # General purpose input length limit

    # Legacy CLI validation constants for backward compatibility
    MENU_CHOICES = ["1", "2", "3", "4"]  # Valid menu choices
    FORCE_RANGE = (0.0, 1000.0)  # Valid force range (min, max)


class InputValidator(IInputValidator):
    """Enhanced input validation utility with comprehensive security hardening.

    This class provides robust input validation with multiple layers of security
    protection including length limits, pattern validation, and ReDoS attack
    prevention. It offers a secure interface for collecting user input with
    appropriate error handling and retry mechanisms.

    Security Features:
    - Hard length limits to prevent buffer overflow attacks
    - Safe regex patterns to prevent ReDoS vulnerabilities
    - Input sanitization with null value handling
    - Retry limits to prevent brute force attempts
    - Comprehensive error reporting for debugging
    """

    # Simplified, safer regex patterns designed to prevent ReDoS attacks
    PATTERNS = {
        "dut_id": r"^[A-Z0-9_-]{1,20}$",  # Device IDs: uppercase alphanumeric with separators
        "model": (
            r"^[A-Za-z0-9_\-\s\.]{1,50}$"
        ),  # Model numbers: alphanumeric with common separators
        "serial": (
            r"^[A-Za-z0-9_\-]{1,30}$"
        ),  # Serial numbers: alphanumeric with hyphens/underscores
        "operator": (
            r"^[A-Za-z0-9_\-\s]{1,30}$"
        ),  # Operator IDs: alphanumeric with spaces and separators
        "general": (
            r"^[A-Za-z0-9_\-\s\.]{1,100}$"  # General input: broader character set with length limit
        ),
    }

    # Length limits corresponding to validation patterns for consistent enforcement
    MAX_LENGTHS = {
        "dut_id": ValidationConstants.DUT_ID_MAX_LENGTH,  # Device ID length limit
        "model": ValidationConstants.MODEL_MAX_LENGTH,  # Model number length limit
        "serial": ValidationConstants.SERIAL_MAX_LENGTH,  # Serial number length limit
        "operator": ValidationConstants.OPERATOR_MAX_LENGTH,  # Operator ID length limit
        "general": ValidationConstants.GENERAL_MAX_LENGTH,  # General input length limit
    }

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
        # First layer: null and empty string validation
        if not user_input or len(user_input.strip()) == 0:
            return False

        # Second layer: global security length limit to prevent buffer overflow
        if len(user_input) > ValidationConstants.MAX_INPUT_LENGTH:
            return False

        # Third layer: type-specific length validation
        type_max_length = self.MAX_LENGTHS.get(input_type, ValidationConstants.GENERAL_MAX_LENGTH)
        if len(user_input.strip()) > type_max_length:
            return False

        # Fourth layer: pattern validation with ReDoS protection
        validation_pattern = self.PATTERNS.get(input_type, self.PATTERNS["general"])
        try:
            # Use safe regex matching to prevent ReDoS attacks
            return self._safe_regex_match(validation_pattern, user_input.strip())
        except Exception:
            # Security-first approach: reject input if validation fails for any reason
            return False

    def _safe_regex_match(self, pattern: str, text: str) -> bool:
        """Safely match regex with comprehensive protection against ReDoS attacks.

        Implements safe regex matching by using simple patterns and pre-validation
        length checks. Python's re module doesn't have built-in timeout protection,
        so we rely on pattern simplicity and length limits for security.

        Args:
            pattern: Compiled regex pattern string to match against
            text: Input text to validate (should be pre-validated for length)

        Returns:
            True if pattern matches safely, False otherwise or on any error
        """
        # Pre-validation: ensure text length is within safe limits
        if len(text) > ValidationConstants.MAX_INPUT_LENGTH:
            return False

        # Perform safe regex matching with simple patterns
        return bool(re.match(pattern, text))

    def get_validated_input(
        self,
        prompt: str,
        input_type: str = "general",
        required: bool = False,
        max_attempts: int = ValidationConstants.MAX_ATTEMPTS,
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
        validation_attempts = 0

        # Retry loop with attempt limiting for security
        while validation_attempts < max_attempts:
            try:
                # Securely collect user input with protection
                user_input = self._get_safe_input(prompt)

                # Handle user cancellation gracefully
                if user_input is None:
                    return None

                # Handle optional empty input (non-required fields)
                if not user_input and not required:
                    return None

                # Validate required input presence
                if not user_input and required:
                    print("  ⚠️ Input is required. Please try again.")
                    validation_attempts += 1
                    continue

                # Perform comprehensive input validation
                if self.validate_input(user_input, input_type):
                    return user_input

                # Provide specific error feedback for validation failure
                self._display_validation_error(input_type)
                validation_attempts += 1

            except (KeyboardInterrupt, EOFError):
                # Handle user interruption gracefully
                return None

        # Maximum attempts exceeded - provide clear feedback
        self._display_max_attempts_error(max_attempts)
        return None

    def _get_safe_input(self, prompt: str) -> Optional[str]:
        """Safely collect user input with comprehensive protection and validation.

        Implements secure input collection with immediate length validation
        and graceful handling of user interruption scenarios.

        Args:
            prompt: Input prompt string to display to the user

        Returns:
            Stripped user input string, empty string for invalid input,
            or None if user cancels
        """
        try:
            # Collect and sanitize user input
            user_input = input(prompt).strip()

            # Immediate security check: reject excessively long inputs
            if len(user_input) > ValidationConstants.MAX_INPUT_LENGTH:
                print(
                    f"  ⚠️ Input too long (max {ValidationConstants.MAX_INPUT_LENGTH} characters)."
                )
                return ""  # Return empty string to trigger validation retry

            return user_input

        except (KeyboardInterrupt, EOFError):
            # Handle user cancellation (Ctrl+C or Ctrl+D) gracefully
            return None

    def _display_validation_error(self, input_type: str) -> None:
        """Display contextual validation error message with helpful guidance.

        Args:
            input_type: Type of input that failed validation for specific messaging
        """
        type_max_length = self.MAX_LENGTHS.get(input_type, ValidationConstants.GENERAL_MAX_LENGTH)
        print(f"  ⚠️ Invalid {input_type} format. Max length: {type_max_length} characters.")

    def _display_max_attempts_error(self, max_attempts: int) -> None:
        """Display maximum attempts exceeded error with clear feedback.

        Args:
            max_attempts: Number of attempts that were allowed before failure
        """
        print(f"  ❌ Maximum attempts ({max_attempts}) exceeded.")

    # Legacy validation methods for backward compatibility
    def is_valid_menu_choice(self, choice: str) -> bool:
        """Validate menu choice selection.

        Args:
            choice: Menu choice string to validate

        Returns:
            True if choice is valid, False otherwise
        """
        if not choice:
            return False
        return choice.strip() in ValidationConstants.MENU_CHOICES

    def is_valid_force_value(self, force_str: str) -> bool:
        """Validate force value input.

        Args:
            force_str: Force value string to validate

        Returns:
            True if force value is valid, False otherwise
        """
        if not force_str:
            return False

        try:
            force_val = float(force_str.strip())
            min_force, max_force = ValidationConstants.FORCE_RANGE
            return min_force <= force_val <= max_force
        except (ValueError, TypeError):
            return False
