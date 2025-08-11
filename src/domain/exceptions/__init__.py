"""
Domain Exceptions Package

Contains domain-specific exceptions for EOL Tester application following Exception First principles.
"""

from src.domain.exceptions.domain_exceptions import (
    DomainException,
)
from src.domain.exceptions.eol_exceptions import (
    ConfigurationNotFoundError,
    ConfigurationValidationError,
    create_multi_validation_error,
    create_test_evaluation_error,
    create_validation_error,
    EOLTesterError,
    HardwareConnectionError,
    HardwareError,
    HardwareOperationError,
    MultiConfigurationValidationError,
    RepositoryAccessError,
    RepositoryError,
    TestEvaluationError,
    TestExecutionError,
    TestSequenceError,
    TestSetupError,
    ValidationError,
)
from src.domain.exceptions.robot_exceptions import (
    AXLConfigurationError,
    AXLConnectionError,
    AXLError,
    AXLMotionError,
    RobotConfigurationError,
    RobotConnectionError,
    RobotError,
    RobotMotionError,
    RobotSafetyError,
)
from src.domain.exceptions.validation_exceptions import (
    ValidationException,
)

__all__ = [
    # Legacy domain exceptions
    "DomainException",
    "ValidationException",
    "RobotError",
    "RobotConnectionError",
    "RobotMotionError",
    "RobotConfigurationError",
    "RobotSafetyError",
    "AXLError",
    "AXLConnectionError",
    "AXLMotionError",
    "AXLConfigurationError",
    # Exception First hierarchy
    "EOLTesterError",
    "ValidationError",
    "ConfigurationValidationError",
    "MultiConfigurationValidationError",
    "TestEvaluationError",
    "HardwareError",
    "HardwareConnectionError",
    "HardwareOperationError",
    "RepositoryError",
    "ConfigurationNotFoundError",
    "RepositoryAccessError",
    "TestExecutionError",
    "TestSequenceError",
    "TestSetupError",
    # Utility functions
    "create_validation_error",
    "create_multi_validation_error",
    "create_test_evaluation_error",
]
