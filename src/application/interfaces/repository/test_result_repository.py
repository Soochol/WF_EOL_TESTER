"""
Test Result Repository Interface

Interface for test result data persistence.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Local application imports
from domain.entities.eol_test import EOLTest


class TestResultRepository(ABC):
    """Test result data repository interface"""

    @abstractmethod
    async def save(self, test: EOLTest) -> EOLTest:
        """
        Save test result

        Args:
            test: Test result to save

        Returns:
            Saved test result
        """
        ...

    @abstractmethod
    async def update(self, test: EOLTest) -> EOLTest:
        """
        Update test result

        Args:
            test: Test result to update

        Returns:
            Updated test result
        """
        ...

    @abstractmethod
    async def find_by_id(self, test_id: str) -> Optional[EOLTest]:
        """
        Find test result by ID

        Args:
            test_id: Test ID

        Returns:
            Found test result (None if not found)
        """
        ...

    @abstractmethod
    async def find_by_dut_id(self, dut_id: str) -> List[EOLTest]:
        """
        Find test results by DUT ID

        Args:
            dut_id: DUT ID

        Returns:
            List of test results
        """
        ...

    @abstractmethod
    async def delete(self, test_id: str) -> None:
        """
        Delete test result

        Args:
            test_id: Test ID

        Raises:
            RepositoryAccessError: If deletion fails
            ConfigurationNotFoundError: If test with given ID does not exist
        """
        ...

    @abstractmethod
    async def get_all_tests(self) -> List[Dict[str, Any]]:
        """
        Get all tests (for management purposes)

        Returns:
            List of all test dictionaries
        """
        ...

    @abstractmethod
    async def cleanup_old_tests(self, days: int = 30) -> int:
        """
        Clean up old tests

        Args:
            days: Retention period (days)

        Returns:
            Number of cleaned up tests
        """
        ...
