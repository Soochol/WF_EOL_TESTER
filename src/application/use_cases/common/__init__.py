"""
Common Use Cases Components

Shared components, patterns, and base classes for use cases.
Promotes code reuse and consistency across all use cases.
"""

from .base_use_case import BaseUseCase
from .command_result_patterns import BaseResult, BaseUseCaseInput
from .execution_context import ExecutionContext

__all__ = [
    "BaseUseCase",
    "BaseUseCaseInput",
    "BaseResult",
    "ExecutionContext",
]
