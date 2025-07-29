"""
Configuration Domain Exceptions

Contains exceptions related to configuration business rules and constraints.
"""

from typing import Dict, Any, Optional, List
from domain.exceptions.domain_exceptions import DomainException


class ConfigurationException(DomainException):
    """Base exception for configuration-related business rule violations"""

    def __init__(self, message: str, config_source: str = None, details: Dict[str, Any] = None):
        """
        Initialize configuration exception

        Args:
            message: Human-readable error message
            config_source: Source of configuration (e.g., 'default.yaml', 'runtime_override')
            details: Additional context about the configuration error
        """
        super().__init__(message, details)
        self.config_source = config_source


class InvalidConfigurationException(ConfigurationException):
    """Exception raised when configuration values violate business rules"""

    def __init__(
        self,
        parameter_name: str,
        invalid_value: Any,
        validation_rule: str,
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize invalid configuration exception

        Args:
            parameter_name: Name of the configuration parameter
            invalid_value: The invalid value that violated rules
            validation_rule: Description of the validation rule that was violated
            config_source: Source of the configuration
            details: Additional validation context
        """
        message = f"Invalid configuration parameter '{parameter_name}': {invalid_value}. Rule: {validation_rule}"

        exception_details = details or {}
        exception_details.update(
            {
                "parameter_name": parameter_name,
                "invalid_value": invalid_value,
                "validation_rule": validation_rule,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.parameter_name = parameter_name
        self.invalid_value = invalid_value
        self.validation_rule = validation_rule


class MissingConfigurationException(ConfigurationException):
    """Exception raised when required configuration is missing violating business rules"""

    def __init__(
        self,
        missing_parameters: List[str],
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize missing configuration exception

        Args:
            missing_parameters: List of missing required parameters
            config_source: Source where parameters were expected
            details: Additional missing parameter context
        """
        if len(missing_parameters) == 1:
            message = f"Missing required configuration parameter: '{missing_parameters[0]}'"
        else:
            params_str = "', '".join(missing_parameters)
            message = f"Missing required configuration parameters: '{params_str}'"

        exception_details = details or {}
        exception_details.update({"missing_parameters": missing_parameters})

        super().__init__(message, config_source, exception_details)
        self.missing_parameters = missing_parameters


class ConfigurationConflictException(ConfigurationException):
    """Exception raised when configuration values conflict violating business rules"""

    def __init__(
        self,
        conflicting_parameters: Dict[str, Any],
        conflict_description: str,
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize configuration conflict exception

        Args:
            conflicting_parameters: Dictionary of conflicting parameter names and values
            conflict_description: Description of why these parameters conflict
            config_source: Source of the conflicting configuration
            details: Additional conflict context
        """
        params_str = ", ".join(f"{k}={v}" for k, v in conflicting_parameters.items())
        message = (
            f"Configuration conflict: {conflict_description}. Conflicting parameters: {params_str}"
        )

        exception_details = details or {}
        exception_details.update(
            {
                "conflicting_parameters": conflicting_parameters,
                "conflict_description": conflict_description,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.conflicting_parameters = conflicting_parameters
        self.conflict_description = conflict_description


class ConfigurationVersionException(ConfigurationException):
    """Exception raised when configuration version violates business rules"""

    def __init__(
        self,
        current_version: str,
        required_version: str,
        compatibility_issue: str,
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize configuration version exception

        Args:
            current_version: Current configuration version
            required_version: Required configuration version
            compatibility_issue: Description of compatibility issue
            config_source: Source of the configuration
            details: Additional version context
        """
        message = f"Configuration version incompatibility: {compatibility_issue}. Current: {current_version}, Required: {required_version}"

        exception_details = details or {}
        exception_details.update(
            {
                "current_version": current_version,
                "required_version": required_version,
                "compatibility_issue": compatibility_issue,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.current_version = current_version
        self.required_version = required_version
        self.compatibility_issue = compatibility_issue


class ConfigurationRangeException(ConfigurationException):
    """Exception raised when configuration values are outside allowed ranges violating business rules"""

    def __init__(
        self,
        parameter_name: str,
        actual_value: float,
        allowed_range: Dict[str, float],
        range_type: str = "numeric",
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize configuration range exception

        Args:
            parameter_name: Name of the parameter outside range
            actual_value: Actual value that is outside range
            allowed_range: Dictionary with 'min' and/or 'max' keys
            range_type: Type of range violation (e.g., 'numeric', 'count', 'duration')
            config_source: Source of the configuration
            details: Additional range context
        """
        min_val = allowed_range.get("min", "-∞")
        max_val = allowed_range.get("max", "+∞")
        message = f"Configuration parameter '{parameter_name}' value {actual_value} is outside allowed {range_type} range [{min_val}, {max_val}]"

        exception_details = details or {}
        exception_details.update(
            {
                "parameter_name": parameter_name,
                "actual_value": actual_value,
                "allowed_range": allowed_range,
                "range_type": range_type,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.parameter_name = parameter_name
        self.actual_value = actual_value
        self.allowed_range = allowed_range
        self.range_type = range_type


class ConfigurationFormatException(ConfigurationException):
    """Exception raised when configuration format violates business rules"""

    def __init__(
        self,
        parameter_name: str,
        invalid_format: str,
        expected_format: str,
        format_example: str = None,
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize configuration format exception

        Args:
            parameter_name: Name of the parameter with format issue
            invalid_format: The invalid format that was provided
            expected_format: Description of expected format
            format_example: Example of correct format
            config_source: Source of the configuration
            details: Additional format context
        """
        message = f"Configuration parameter '{parameter_name}' has invalid format: '{invalid_format}'. Expected: {expected_format}"

        if format_example:
            message += f". Example: {format_example}"

        exception_details = details or {}
        exception_details.update(
            {
                "parameter_name": parameter_name,
                "invalid_format": invalid_format,
                "expected_format": expected_format,
                "format_example": format_example,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.parameter_name = parameter_name
        self.invalid_format = invalid_format
        self.expected_format = expected_format
        self.format_example = format_example


class ConfigurationSecurityException(ConfigurationException):
    """Exception raised when configuration violates security business rules"""

    def __init__(
        self,
        security_violation: str,
        affected_parameters: List[str] = None,
        risk_level: str = "medium",
        config_source: str = None,
        details: Dict[str, Any] = None,
    ):
        """
        Initialize configuration security exception

        Args:
            security_violation: Description of security violation
            affected_parameters: List of parameters that violate security
            risk_level: Risk level (e.g., 'low', 'medium', 'high', 'critical')
            config_source: Source of the configuration
            details: Additional security context
        """
        message = f"Configuration security violation ({risk_level} risk): {security_violation}"

        if affected_parameters:
            params_str = "', '".join(affected_parameters)
            message += f". Affected parameters: '{params_str}'"

        exception_details = details or {}
        exception_details.update(
            {
                "security_violation": security_violation,
                "affected_parameters": affected_parameters,
                "risk_level": risk_level,
            }
        )

        super().__init__(message, config_source, exception_details)
        self.security_violation = security_violation
        self.affected_parameters = affected_parameters
        self.risk_level = risk_level
