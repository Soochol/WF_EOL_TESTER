"""
Execution Context

Contains contextual information about use case execution including timing,
identification, and operator information.
"""

from typing import Any, Dict, Optional

from domain.value_objects.identifiers import TestId
from domain.value_objects.time_values import Timestamp


class ExecutionContext:
    """
    Execution context for use case operations

    Contains all contextual information needed during use case execution
    including timing, identification, and metadata.
    """

    def __init__(
        self,
        test_id: TestId,
        use_case_name: str,
        operator_id: str,
        start_time: Timestamp,
        end_time: Optional[Timestamp] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize execution context

        Args:
            test_id: Unique identifier for this execution
            use_case_name: Name of the use case being executed
            operator_id: ID of the operator running the use case
            start_time: When execution started
            end_time: When execution ended (set later)
            metadata: Additional context metadata
        """
        self.test_id = test_id
        self.use_case_name = use_case_name
        self.operator_id = operator_id
        self.start_time = start_time
        self.end_time = end_time
        self.metadata = metadata or {}

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the execution context

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata from the execution context

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary representation

        Returns:
            Dictionary containing context data
        """
        return {
            "test_id": self.test_id.value,
            "use_case_name": self.use_case_name,
            "operator_id": self.operator_id,
            "start_time": self.start_time.to_iso(),
            "end_time": self.end_time.to_iso() if self.end_time else None,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        """String representation of execution context"""
        return (
            f"ExecutionContext("
            f"test_id={self.test_id.value}, "
            f"use_case={self.use_case_name}, "
            f"operator={self.operator_id})"
        )
