"""
EOL Tester Exception Hierarchy

Comprehensive exception classes for the EOL Tester application following Exception First principles.
"""

from typing import List, Dict, Any, Optional


class EOLTesterError(Exception):
    """
    Base exception for all EOL Tester application errors

    This is the root exception that all other application-specific exceptions inherit from.
    It provides common functionality and ensures consistent error handling across the application.
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize EOL Tester error

        Args:
            message: Human-readable error message
            context: Additional context information about the error
        """
        super().__init__(message)
        self.context = context or {}
        self.message = message

    def add_context(self, key: str, value: Any) -> "EOLTesterError":
        """Add context information to the exception"""
        self.context[key] = value
        return self

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information from the exception"""
        return self.context.get(key, default)


# === Validation Exceptions ===


class ValidationError(EOLTesterError):
    """Base exception for all validation errors"""

    pass


class ConfigurationValidationError(ValidationError):
    """
    Exception raised when configuration validation fails

    This exception contains detailed information about what validation rules failed
    and provides structured access to the validation errors.
    """

    def __init__(
        self,
        errors: List[str],
        config_type: str = "unknown",
        config_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize configuration validation error

        Args:
            errors: List of validation error messages
            config_type: Type of configuration that failed (e.g., 'test', 'hardware')
            config_data: The configuration data that failed validation
        """
        self.errors = errors
        self.config_type = config_type
        self.config_data = config_data

        error_summary = f"Configuration validation failed for {config_type}: {len(errors)} errors"
        super().__init__(
            error_summary,
            {"errors": errors, "config_type": config_type, "error_count": len(errors)},
        )

    def get_error_summary(self) -> str:
        """Get a formatted summary of all validation errors"""
        return "; ".join(self.errors)

    def has_error_containing(self, text: str) -> bool:
        """Check if any error message contains the specified text"""
        return any(text.lower() in error.lower() for error in self.errors)


class MultiConfigurationValidationError(ValidationError):
    """
    Exception raised when multiple configurations fail validation

    This is used when validating multiple configurations (e.g., test + hardware)
    and provides structured access to errors by configuration type.
    """

    def __init__(self, errors_by_type: Dict[str, List[str]]):
        """
        Initialize multi-configuration validation error

        Args:
            errors_by_type: Dictionary mapping configuration types to their error lists
        """
        self.errors_by_type = errors_by_type

        total_errors = sum(len(errors) for errors in errors_by_type.values())
        config_types = ", ".join(errors_by_type.keys())

        message = (
            f"Multiple configuration validation failed: {total_errors} errors across {config_types}"
        )
        super().__init__(
            message,
            {
                "errors_by_type": errors_by_type,
                "total_errors": total_errors,
                "failed_config_types": list(errors_by_type.keys()),
            },
        )

    def get_errors_for_type(self, config_type: str) -> List[str]:
        """Get validation errors for a specific configuration type"""
        return self.errors_by_type.get(config_type, [])

    def has_errors_for_type(self, config_type: str) -> bool:
        """Check if there are validation errors for a specific configuration type"""
        return config_type in self.errors_by_type and len(self.errors_by_type[config_type]) > 0


# === Test Evaluation Exceptions ===


class TestEvaluationError(EOLTesterError):
    """
    Exception raised when test evaluation fails

    This exception contains information about which test points failed
    and provides structured access to the failure details.
    """

    def __init__(self, failed_points: List[Dict[str, Any]], total_points: int = 0):
        """
        Initialize test evaluation error

        Args:
            failed_points: List of failed test points with details
            total_points: Total number of test points evaluated
        """
        self.failed_points = failed_points
        self.total_points = total_points
        self.passed_points = max(0, total_points - len(failed_points))

        message = f"Test evaluation failed: {len(failed_points)} of {total_points} points failed"
        super().__init__(
            message,
            {
                "failed_points": failed_points,
                "failed_count": len(failed_points),
                "total_points": total_points,
                "passed_count": self.passed_points,
            },
        )

    def get_failure_summary(self) -> str:
        """Get a summary of test failures"""
        if not self.failed_points:
            return "No specific failure details available"

        failure_types = {}
        for point in self.failed_points:
            error_type = point.get("error", "unknown_failure")
            failure_types[error_type] = failure_types.get(error_type, 0) + 1

        summary_parts = [f"{count} {error_type}" for error_type, count in failure_types.items()]
        return f"Failures: {', '.join(summary_parts)}"

    def get_failed_measurements(self) -> List[str]:
        """Get list of failed measurement keys"""
        return [point.get("key", "unknown") for point in self.failed_points if "key" in point]


# === Hardware Exceptions ===


class HardwareError(EOLTesterError):
    """Base exception for all hardware-related errors"""

    pass


class HardwareConnectionError(HardwareError):
    """Exception raised when hardware connection fails"""

    def __init__(self, device: str, reason: str, port: Optional[str] = None):
        self.device = device
        self.reason = reason
        self.port = port

        message = f"Failed to connect to {device}"
        if port:
            message += f" on port {port}"
        message += f": {reason}"

        super().__init__(message, {"device": device, "reason": reason, "port": port})


class HardwareOperationError(HardwareError):
    """Exception raised when hardware operation fails"""

    def __init__(self, device: str, operation: str, reason: str):
        self.device = device
        self.operation = operation
        self.reason = reason

        message = f"Hardware operation failed on {device}.{operation}: {reason}"
        super().__init__(message, {"device": device, "operation": operation, "reason": reason})


# === Repository Exceptions ===


class RepositoryError(EOLTesterError):
    """Base exception for all repository-related errors"""

    pass


class ConfigurationNotFoundError(RepositoryError):
    """Exception raised when a configuration profile is not found"""

    def __init__(self, profile_name: str, available_profiles: Optional[List[str]] = None):
        self.profile_name = profile_name
        self.available_profiles = available_profiles or []

        message = f"Configuration profile '{profile_name}' not found"
        if available_profiles:
            message += f". Available profiles: {', '.join(available_profiles)}"

        super().__init__(
            message, {"profile_name": profile_name, "available_profiles": self.available_profiles}
        )


class RepositoryAccessError(RepositoryError):
    """Exception raised when repository access fails"""

    def __init__(self, operation: str, reason: str, file_path: Optional[str] = None):
        self.operation = operation
        self.reason = reason
        self.file_path = file_path

        message = f"Repository {operation} failed: {reason}"
        if file_path:
            message += f" (file: {file_path})"

        super().__init__(
            message, {"operation": operation, "reason": reason, "file_path": file_path}
        )


# === Test Execution Exceptions ===


class TestExecutionError(EOLTesterError):
    """Base exception for test execution errors"""

    pass


class TestSequenceError(TestExecutionError):
    """Exception raised when test sequence execution fails"""

    def __init__(self, step: str, reason: str, measurements: Optional[Dict[str, Any]] = None):
        self.step = step
        self.reason = reason
        self.measurements = measurements or {}

        message = f"Test sequence failed at step '{step}': {reason}"
        super().__init__(
            message, {"step": step, "reason": reason, "measurements_count": len(self.measurements)}
        )


class TestSetupError(TestExecutionError):
    """Exception raised when test setup fails"""

    def __init__(self, component: str, reason: str):
        self.component = component
        self.reason = reason

        message = f"Test setup failed for {component}: {reason}"
        super().__init__(message, {"component": component, "reason": reason})


# === Utility Functions ===


def create_validation_error(
    errors: List[str], config_type: str = "unknown"
) -> ConfigurationValidationError:
    """Utility function to create a configuration validation error"""
    return ConfigurationValidationError(errors, config_type)


def create_multi_validation_error(
    errors_dict: Dict[str, List[str]],
) -> MultiConfigurationValidationError:
    """Utility function to create a multi-configuration validation error"""
    return MultiConfigurationValidationError(errors_dict)


def create_test_evaluation_error(
    failed_points: List[Dict[str, Any]], total: int = 0
) -> TestEvaluationError:
    """Utility function to create a test evaluation error"""
    return TestEvaluationError(failed_points, total)
