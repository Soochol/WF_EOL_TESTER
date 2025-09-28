"""
Base Domain Exceptions

Contains the base exception classes for domain-related errors.
"""

# Standard library imports
from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base exception for all domain-related errors"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize domain exception

        Args:
            message: Human-readable error message
            details: Additional context or details about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message
