"""
Database Logger Service

Service for logging test data to database.
"""

# Standard library imports
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports
from loguru import logger

# Local application imports
from application.interfaces.repository.database_log_repository import DatabaseLogRepository
from domain.entities.eol_test import EOLTest
from domain.enums.test_status import TestStatus


class DbLoggerService:
    """Database logging service for test data"""

    def __init__(self, db_repository: DatabaseLogRepository):
        """
        Initialize database logger service

        Args:
            db_repository: Database log repository instance
        """
        self._db_repo = db_repository
        logger.info("DbLoggerService initialized")

    async def log_test_result(self, test: EOLTest) -> None:
        """
        Log test result to database - only for COMPLETED and FAILED status

        Args:
            test: EOL test entity

        Raises:
            RepositoryAccessError: If logging fails
        """
        try:
            # Only log COMPLETED or FAILED tests (not ERROR/CANCELLED)
            if test.status not in (TestStatus.COMPLETED, TestStatus.FAILED):
                logger.info(
                    f"Test {test.test_id} NOT logged to database (status: {test.status}) - "
                    f"skipping ERROR/CANCELLED tests"
                )
                return

            test_dict = test.to_dict()
            await self._db_repo.save_test_result(test_dict)
            logger.debug(f"Test result logged to database: {test.test_id}")
        except Exception as e:
            logger.error(f"Failed to log test result to database: {e}")
            # Don't raise - logging should not break the main flow
            # raise

    async def log_raw_measurement(
        self,
        test_id: str,
        serial_number: str,
        cycle_number: Optional[int],
        temperature: Optional[float],
        position: Optional[float],
        force: Optional[float],
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Log raw measurement data to database

        Args:
            test_id: Test identifier
            serial_number: Device serial number
            cycle_number: Test cycle number (optional)
            temperature: Temperature value
            position: Position value
            force: Force value
            timestamp: Measurement timestamp (defaults to now)

        Raises:
            RepositoryAccessError: If logging fails
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()

            await self._db_repo.save_raw_measurement(
                test_id=test_id,
                serial_number=serial_number,
                cycle_number=cycle_number,
                timestamp=timestamp,
                temperature=temperature,
                position=position,
                force=force,
            )
            logger.debug(
                f"Raw measurement logged: test_id={test_id}, " f"temp={temperature}, force={force}"
            )
        except Exception as e:
            logger.error(f"Failed to log raw measurement to database: {e}")
            # Don't raise - logging should not break the main flow
            # raise

    async def query_tests(
        self,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query test results from database

        Args:
            serial_number: Filter by serial number
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            status: Filter by test status
            limit: Maximum number of results

        Returns:
            List of test result dictionaries
        """
        return await self._db_repo.query_tests(
            serial_number=serial_number,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit,
        )

    async def query_raw_measurements(
        self,
        test_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Query raw measurement data from database

        Args:
            test_id: Filter by test ID
            serial_number: Filter by serial number
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            limit: Maximum number of results

        Returns:
            List of measurement dictionaries
        """
        return await self._db_repo.query_raw_measurements(
            test_id=test_id,
            serial_number=serial_number,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    async def get_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test result by ID

        Args:
            test_id: Test identifier

        Returns:
            Test result dictionary or None if not found
        """
        return await self._db_repo.get_test_by_id(test_id)

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
        return await self._db_repo.get_statistics(start_date=start_date, end_date=end_date)

    async def delete_test(self, test_id: str) -> None:
        """
        Delete test result and associated measurements

        Args:
            test_id: Test identifier

        Raises:
            ConfigurationNotFoundError: If test not found
            RepositoryAccessError: If deletion fails
        """
        await self._db_repo.delete_test(test_id)
        logger.info(f"Test deleted from database: {test_id}")
