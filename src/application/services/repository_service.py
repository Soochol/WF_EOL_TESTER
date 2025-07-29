"""
Repository Service

Service layer that manages test result repository operations and data persistence.
Uses Exception First principles for error handling.
"""

from typing import Any, Dict, Optional

from loguru import logger

from application.interfaces.repository.test_result_repository import (
    TestResultRepository,
)
from domain.exceptions import RepositoryAccessError


class RepositoryService:
    """
    Service for managing test result repository operations

    This service centralizes test result repository operations and provides
    a unified interface for test data persistence.
    """

    def __init__(self, test_repository: TestResultRepository = None):
        self._test_repository = test_repository

    @property
    def test_repository(self) -> Optional[TestResultRepository]:
        """Get the test repository"""
        return self._test_repository

    async def save_test_result(self, test_data: Dict[str, Any]) -> None:
        """
        Save test result to repository

        Args:
            test_data: Test result data to save

        Raises:
            RepositoryAccessError: If saving fails
        """
        if not self._test_repository:
            logger.warning("No test repository configured, skipping test result save")
            return

        try:
            await self._test_repository.save_test_result(test_data)
            logger.debug("Test result saved successfully")
        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
            raise RepositoryAccessError(operation="save_test_result", reason=str(e))

    def get_all_repositories(self) -> dict:
        """Get all repositories as a dictionary (for debugging/testing)"""
        return {"test_repository": self._test_repository}
