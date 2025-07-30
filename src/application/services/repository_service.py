"""
Repository Service

Service layer that manages test result repository operations and data persistence.
Uses Exception First principles for error handling.
"""

from typing import Optional

from loguru import logger

from application.interfaces.repository.test_result_repository import (
    TestResultRepository,
)
from domain.entities.eol_test import EOLTest
from domain.exceptions import RepositoryAccessError


class RepositoryService:
    """
    Service for managing test result repository operations

    This service centralizes test result repository operations and provides
    a unified interface for test data persistence.
    """

    def __init__(
        self,
        test_repository: Optional[TestResultRepository] = None,
    ):
        self._test_repository = test_repository

    @property
    def test_repository(
        self,
    ) -> Optional[TestResultRepository]:
        """Get the test repository"""
        return self._test_repository

    async def save_test_result(self, test: EOLTest) -> None:
        """
        Save test result to repository

        Args:
            test: EOL test to save

        Raises:
            RepositoryAccessError: If saving fails
        """
        if not self._test_repository:
            logger.warning("No test repository configured, skipping test result save")
            return

        try:
            await self._test_repository.save(test)
            logger.debug("Test result saved successfully")
        except Exception as e:
            logger.error("Failed to save test result: %s", e)
            raise RepositoryAccessError(operation="save_test_result", reason=str(e)) from e

    def get_all_repositories(self) -> dict:
        """Get all repositories as a dictionary (for debugging/testing)"""
        return {"test_repository": self._test_repository}
