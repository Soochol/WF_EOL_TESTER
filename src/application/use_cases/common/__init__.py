"""
Common Use Cases Components

Shared components, patterns, and base classes for use cases.
Promotes code reuse and consistency across all use cases.
"""

from .base_use_case import BaseUseCase
from .command_result_patterns import BaseCommand, BaseResult
from .execution_context import ExecutionContext

__all__ = [
    "BaseUseCase",
    "BaseCommand", 
    "BaseResult",
    "ExecutionContext",
]