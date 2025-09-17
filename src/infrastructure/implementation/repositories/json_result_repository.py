"""
JSON Result Repository

Simple file-based test result data persistence using JSON format.
"""

# Standard library imports
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
from loguru import logger

# Local application imports
from application.interfaces.repository.test_result_repository import (
    TestResultRepository,
)
from domain.entities.eol_test import EOLTest
from domain.exceptions import (
    ConfigurationNotFoundError,
    RepositoryAccessError,
)


class JsonResultRepository(TestResultRepository):
    """JSON file-based test result repository"""

    def __init__(
        self,
        data_dir: str,
        auto_save: bool = True,
    ):
        """
        Initialize the repository

        Args:
            data_dir: Data storage directory
            auto_save: Enable automatic saving
        """
        self._data_dir = Path(data_dir)
        self._auto_save = auto_save
        self._tests_cache: Dict[str, Dict[str, Any]] = {}

        # Create directory
        self._data_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"JsonResultRepository initialized at {self._data_dir}")

    async def save(self, test: EOLTest) -> EOLTest:
        """
        Save test

        Args:
            test: Test to save

        Returns:
            Saved test
        """
        test_dict = await self._test_to_dict(test)
        test_id = str(test.test_id)

        # Save to cache
        self._tests_cache[test_id] = test_dict

        if self._auto_save:
            await self._save_to_file(test_id, test_dict)

        logger.debug(f"Test {test_id} saved to repository")
        return test

    async def update(self, test: EOLTest) -> EOLTest:
        """
        Update test

        Args:
            test: Test to update

        Returns:
            Updated test
        """
        return await self.save(test)  # In JSON, save and update are identical

    async def find_by_id(self, test_id: str) -> Optional[EOLTest]:
        """
        Find test by ID

        Args:
            test_id: Test ID

        Returns:
            Found test (None if not found)
        """
        # Check cache first
        if test_id in self._tests_cache:
            test_dict = self._tests_cache[test_id]
            return await self._dict_to_test(test_dict)

        # Load from file
        loaded_test_dict: Optional[Dict[str, Any]] = await self._load_from_file(test_id)
        if loaded_test_dict is not None:
            self._tests_cache[test_id] = loaded_test_dict
            return await self._dict_to_test(loaded_test_dict)

        return None

    async def find_by_dut_id(self, dut_id: str) -> List[EOLTest]:
        """
        Find tests by DUT ID

        Args:
            dut_id: DUT ID

        Returns:
            List of tests
        """
        tests = []

        # Scan all test files
        await self._load_all_tests()

        for test_dict in self._tests_cache.values():
            if test_dict.get("dut", {}).get("dut_id") == dut_id:
                test = await self._dict_to_test(test_dict)
                tests.append(test)

        # Sort by creation time (newest first)
        tests.sort(key=lambda t: t.created_at, reverse=True)

        logger.debug(f"Found {len(tests)} tests for DUT {dut_id}")
        return tests

    async def delete(self, test_id: str) -> None:
        """
        Delete test

        Args:
            test_id: Test ID

        Raises:
            ConfigurationNotFoundError: If test does not exist
            RepositoryAccessError: If deletion fails
        """
        try:
            # Check if test exists
            file_path = self._get_test_file_path(test_id)
            if not file_path.exists() and test_id not in self._tests_cache:
                raise ConfigurationNotFoundError(f"Test {test_id} not found")

            # Remove from cache
            if test_id in self._tests_cache:
                del self._tests_cache[test_id]

            # Delete file
            if file_path.exists():
                file_path.unlink()

            logger.debug(f"Test {test_id} deleted from repository")

        except ConfigurationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete test {test_id}: {e}")
            raise RepositoryAccessError(
                "delete",
                f"Failed to delete test {test_id}: {str(e)}",
                file_path=str(self._get_test_file_path(test_id)),
            ) from e

    async def _test_to_dict(self, test: EOLTest) -> Dict[str, Any]:
        """Convert test entity to dictionary"""
        try:
            # Use EOLTest's built-in to_dict method for complete serialization
            return test.to_dict()
        except Exception as e:
            logger.error(f"Failed to convert EOLTest to dict: {e}")
            logger.debug(f"Test: {test}")
            raise

    async def _dict_to_test(self, test_dict: Dict[str, Any]) -> EOLTest:
        """Convert dictionary to test entity"""
        try:
            # Use EOLTest's from_dict class method for complete entity restoration
            return EOLTest.from_dict(test_dict)
        except Exception as e:
            logger.error(f"Failed to convert dict to EOLTest: {e}")
            logger.debug(f"Test dict: {test_dict}")
            raise

    async def _save_to_file(self, test_id: str, test_dict: Dict[str, Any]) -> None:
        """Save test data to file"""
        file_path = self._get_test_file_path(test_id)

        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as JSON file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    test_dict,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.debug(f"Test {test_id} saved to file {file_path}")

        except Exception as e:
            logger.error(f"Failed to save test {test_id} to file: {e}")
            raise

    async def _load_from_file(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Load test data from file"""
        file_path = self._get_test_file_path(test_id)

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                test_dict: Dict[str, Any] = json.load(f)

            logger.debug(
                "Test %s loaded from file %s",
                test_id,
                file_path,
            )
            return test_dict

        except Exception as e:
            logger.error(
                "Failed to load test %s from file: %s",
                test_id,
                e,
            )
            return None

    async def _load_all_tests(self) -> None:
        """Load all test files into cache"""
        if not self._data_dir.exists():
            return

        for file_path in self._data_dir.glob("*.json"):
            test_id = file_path.stem

            if test_id not in self._tests_cache:
                test_dict = await self._load_from_file(test_id)
                if test_dict is not None:
                    self._tests_cache[test_id] = test_dict

    def _get_test_file_path(self, test_id: str) -> Path:
        """Return file path for test ID"""
        return self._data_dir / f"{test_id}.json"

    async def get_all_tests(self) -> List[Dict[str, Any]]:
        """
        Get all tests (for management)

        Returns:
            List of all test dictionaries
        """
        await self._load_all_tests()
        return list(self._tests_cache.values())

    async def cleanup_old_tests(self, days: int = 30) -> int:
        """
        Clean up old tests

        Args:
            days: Retention period (days)

        Returns:
            Number of cleaned up tests
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0

        await self._load_all_tests()

        for test_id, test_dict in list(self._tests_cache.items()):
            created_at = test_dict.get("created_at")
            if created_at:
                try:
                    test_date = datetime.fromisoformat(created_at).timestamp()
                    if test_date < cutoff_date:
                        try:
                            await self.delete(test_id)
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(
                                "Failed to delete old test %s: %s",
                                test_id,
                                e,
                            )
                except Exception as e:
                    logger.warning(
                        "Failed to parse date for test %s: %s",
                        test_id,
                        e,
                    )

        logger.info(
            "Cleaned up %d old tests (older than %d days)",
            deleted_count,
            days,
        )
        return deleted_count
