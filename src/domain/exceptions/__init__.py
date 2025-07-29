"""
Domain Exceptions Package

Contains domain-specific exceptions for EOL Tester application following Exception First principles.
"""

from domain.exceptions.domain_exceptions import DomainException
from domain.exceptions.validation_exceptions import ValidationException
from domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
from domain.exceptions.robot_exceptions import (
    RobotError, RobotConnectionError, RobotMotionError,
    RobotConfigurationError, RobotSafetyError,
    AXLError, AXLConnectionError, AXLMotionError, AXLConfigurationError
)

from domain.exceptions.eol_exceptions import (
    EOLTesterError,
    ValidationError,
    ConfigurationValidationError,
    MultiConfigurationValidationError,
    TestEvaluationError,
    HardwareError,
    HardwareConnectionError,
    HardwareOperationError,
    RepositoryError,
    ConfigurationNotFoundError,
    RepositoryAccessError,
    TestExecutionError,
    TestSequenceError,
    TestSetupError,
    create_validation_error,
    create_multi_validation_error,
    create_test_evaluation_error
)

__all__ = [
    # Legacy domain exceptions
    'DomainException',
    'ValidationException',
    'BusinessRuleViolationException',
    'RobotError',
    'RobotConnectionError',
    'RobotMotionError',
    'RobotConfigurationError',
    'RobotSafetyError',
    'AXLError',
    'AXLConnectionError',
    'AXLMotionError',
    'AXLConfigurationError',

    # Exception First hierarchy
    'EOLTesterError',
    'ValidationError',
    'ConfigurationValidationError',
    'MultiConfigurationValidationError',
    'TestEvaluationError',
    'HardwareError',
    'HardwareConnectionError',
    'HardwareOperationError',
    'RepositoryError',
    'ConfigurationNotFoundError',
    'RepositoryAccessError',
    'TestExecutionError',
    'TestSequenceError',
    'TestSetupError',

    # Utility functions
    'create_validation_error',
    'create_multi_validation_error',
    'create_test_evaluation_error'
]
