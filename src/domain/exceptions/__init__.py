"""
Domain Exceptions Package

Contains domain-specific exceptions that represent business rule violations 
and domain constraints.
"""

from domain.exceptions.domain_exceptions import DomainException
from domain.exceptions.validation_exceptions import ValidationException
from domain.exceptions.business_rule_exceptions import BusinessRuleViolationException
from domain.exceptions.robot_exceptions import (
    RobotError, RobotConnectionError, RobotMotionError, 
    RobotConfigurationError, RobotSafetyError,
    AXLError, AXLConnectionError, AXLMotionError, AXLConfigurationError
)

__all__ = [
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
    'AXLConfigurationError'
]