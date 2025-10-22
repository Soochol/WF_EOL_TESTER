"""
Database Log Repository Interface

Interface for database-based test data logging.
"""

# Standard library imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


class DatabaseLogRepository(ABC):
    """Database log repository interface for test data persistence"""

    @abstractmethod
    async def save_test_result(self, test_data: Dict[str, Any]) -> None:
        """
        Save test result to database

        Args:
            test_data: Test result dictionary (from EOLTest.to_dict())

        Raises:
            RepositoryAccessError: If save fails
        """
        ...

    @abstractmethod
    async def save_raw_measurement(
        self,
        test_id: str,
        serial_number: str,
        cycle_number: Optional[int],
        timestamp: datetime,
        temperature: Optional[float],
        position: Optional[float],
        force: Optional[float],
    ) -> None:
        """
        Save raw measurement data to database

        Args:
            test_id: Test identifier
            serial_number: Device serial number
            cycle_number: Test cycle number (optional)
            timestamp: Measurement timestamp
            temperature: Temperature value
            position: Position value
            force: Force value

        Raises:
            RepositoryAccessError: If save fails
        """
        ...

    @abstractmethod
    async def query_tests(
        self,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query test results

        Args:
            serial_number: Filter by serial number
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            status: Filter by test status
            limit: Maximum number of results

        Returns:
            List of test result dictionaries
        """
        ...

    @abstractmethod
    async def query_raw_measurements(
        self,
        test_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Query raw measurement data

        Args:
            test_id: Filter by test ID
            serial_number: Filter by serial number
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            limit: Maximum number of results

        Returns:
            List of measurement dictionaries
        """
        ...

    @abstractmethod
    async def get_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test result by ID

        Args:
            test_id: Test identifier

        Returns:
            Test result dictionary or None if not found
        """
        ...

    @abstractmethod
    async def delete_test(self, test_id: str) -> None:
        """
        Delete test result and associated measurements

        Args:
            test_id: Test identifier

        Raises:
            ConfigurationNotFoundError: If test not found
            RepositoryAccessError: If deletion fails
        """
        ...

    @abstractmethod
    async def delete_measurements_by_test_ids(self, test_ids: List[str]) -> Dict[str, Any]:
        """
        Delete raw measurements by test IDs (batch delete support)

        This method deletes measurements directly from raw_measurements table
        without checking test_results table. Useful for cleaning up data
        when only raw measurements exist.

        Args:
            test_ids: List of test identifiers to delete

        Returns:
            Dictionary with deletion results:
            {
                "deleted_count": int,  # Total measurements deleted
                "deleted_tests": List[str],  # Successfully deleted test_ids
                "failed": List[str],  # Failed test_ids
                "errors": Dict[str, str]  # test_id -> error message
            }

        Raises:
            RepositoryAccessError: If critical deletion error occurs
        """
        ...

    @abstractmethod
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get test statistics

        Args:
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)

        Returns:
            Dictionary with statistics (total_tests, pass_count, fail_count, etc.)
        """
        ...
