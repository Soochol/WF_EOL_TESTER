"""
Configuration value validation.

Provides comprehensive validation for configuration values based on
predefined rules and type checking.
"""

# Standard library imports
import re
from typing import Any, Dict

# Local folder imports
from .constants import ValidationRules


class ConfigValidator:
    """Configuration value validator"""

    def __init__(self):
        """Initialize validator with rules"""
        self.rules = ValidationRules.get_rules()

    @staticmethod
    def validate_value(key: str, value: Any, rules: Dict[str, Dict[str, Any]]) -> tuple[bool, str]:
        """
        Validate a configuration value against validation rules.

        Args:
            key: Configuration key
            value: Value to validate
            rules: Validation rules dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Find matching rule
            rule = ConfigValidator._find_matching_rule(key, rules)

            if not rule:
                return True, ""  # No validation rule, assume valid

            # Type validation
            if not ConfigValidator._validate_type(value, rule):
                expected_type = rule.get("type", "unknown")
                return False, f"Must be a {expected_type}"

            # Convert value for further validation if needed
            converted_value = ConfigValidator._convert_value(value, rule)

            # Range validation
            error = ConfigValidator._validate_range(converted_value, rule)
            if error:
                return False, error

            # Allowed values validation
            error = ConfigValidator._validate_allowed_values(converted_value, rule)
            if error:
                return False, error

            # Pattern validation
            error = ConfigValidator._validate_pattern(converted_value, rule)
            if error:
                return False, error

            # String length validation
            error = ConfigValidator._validate_string_length(converted_value, rule)
            if error:
                return False, error

            return True, ""

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def _find_matching_rule(key: str, rules: Dict[str, Dict[str, Any]]) -> Dict[str, Any] | None:
        """Find matching validation rule for a key"""
        # Check for exact match first
        if key in rules:
            return rules[key]

        # Check for wildcard matches
        for rule_key in rules:
            if "*" in rule_key:
                pattern = rule_key.replace("*", ".*")
                if re.match(pattern, key):
                    return rules[rule_key]

        return None

    @staticmethod
    def _validate_type(value: Any, rule: Dict[str, Any]) -> bool:
        """Validate value type"""
        expected_type = rule.get("type")
        if not expected_type:
            return True

        if expected_type == "int":
            return isinstance(value, int) or (
                isinstance(value, str) and ConfigValidator._can_convert_to_int(value)
            )
        elif expected_type == "float":
            return isinstance(value, (int, float)) or (
                isinstance(value, str) and ConfigValidator._can_convert_to_float(value)
            )
        elif expected_type == "bool":
            return isinstance(value, bool)
        elif expected_type == "str":
            return isinstance(value, str)

        return True

    @staticmethod
    def _can_convert_to_int(value: str) -> bool:
        """Check if string can be converted to int"""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _can_convert_to_float(value: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _convert_value(value: Any, rule: Dict[str, Any]) -> Any:
        """Convert value to appropriate type for validation"""
        expected_type = rule.get("type")

        if expected_type == "int" and not isinstance(value, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        elif expected_type == "float" and not isinstance(value, (int, float)):
            try:
                return float(value)
            except (ValueError, TypeError):
                return value

        return value

    @staticmethod
    def _validate_range(value: Any, rule: Dict[str, Any]) -> str:
        """Validate numeric range"""
        if not isinstance(value, (int, float)):
            return ""

        if "min" in rule and value < rule["min"]:
            return f"Must be >= {rule['min']}"

        if "max" in rule and value > rule["max"]:
            return f"Must be <= {rule['max']}"

        return ""

    @staticmethod
    def _validate_allowed_values(value: Any, rule: Dict[str, Any]) -> str:
        """Validate against allowed values"""
        if "allowed" not in rule:
            return ""

        if value not in rule["allowed"]:
            allowed_str = ", ".join(map(str, rule["allowed"]))
            return f"Must be one of: {allowed_str}"

        return ""

    @staticmethod
    def _validate_pattern(value: Any, rule: Dict[str, Any]) -> str:
        """Validate string pattern"""
        if "pattern" not in rule or not isinstance(value, str):
            return ""

        if not re.match(rule["pattern"], value):
            return "Invalid format"

        return ""

    @staticmethod
    def _validate_string_length(value: Any, rule: Dict[str, Any]) -> str:
        """Validate string length"""
        if not isinstance(value, str):
            return ""

        if "min_length" in rule and len(value) < rule["min_length"]:
            return f"Must be at least {rule['min_length']} characters"

        if "max_length" in rule and len(value) > rule["max_length"]:
            return f"Must be no more than {rule['max_length']} characters"

        return ""

    def validate(self, key: str, value: Any) -> tuple[bool, str]:
        """
        Validate a configuration value using instance rules.

        Args:
            key: Configuration key
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.validate_value(key, value, self.rules)
