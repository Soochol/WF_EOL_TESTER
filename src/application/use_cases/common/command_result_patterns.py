"""
Use Case Input and Result Patterns

Base classes for input and result objects used across all use cases.
Implements consistent patterns and ensures type safety.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict

# NOTE: BaseResult has been moved to domain layer for Clean Architecture compliance
# Import from domain instead of defining here
from domain.value_objects.base_result import BaseResult  # noqa: F401


class BaseUseCaseInput(ABC):
    """
    Abstract base class for all use case input data

    Input objects encapsulate parameters for use case execution.
    They should be immutable and contain all necessary information.
    """

    def __init__(self, operator_id: str = "system"):
        """
        Initialize base use case input

        Args:
            operator_id: ID of the operator executing the use case
        """
        self._operator_id = operator_id

    @property
    def operator_id(self) -> str:
        """Get the operator ID"""
        return self._operator_id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert input to dictionary representation

        Returns:
            Dictionary containing input data
        """
        pass


# BaseResult has been moved to domain layer for Clean Architecture compliance
# Re-export here for backward compatibility with existing imports
__all__ = ["BaseUseCaseInput", "BaseResult"]
