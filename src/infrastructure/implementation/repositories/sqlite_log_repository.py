"""
SQLite Log Repository

SQLite implementation of database log repository.
"""

# Standard library imports
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

# Third-party imports
from loguru import logger
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from application.interfaces.repository.database_log_repository import DatabaseLogRepository
from domain.exceptions import ConfigurationNotFoundError, RepositoryAccessError
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.database.schema import RawMeasurement, TestResult


class SqliteLogRepository(DatabaseLogRepository):
    """SQLite-based log repository implementation"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository

        Args:
            db_manager: Database manager instance
        """
        self._db_manager = db_manager
        logger.info("SqliteLogRepository initialized")

    async def save_test_result(self, test_data: Dict[str, Any]) -> None:
        """Save test result to database"""
        try:
            async with self._db_manager.get_session() as session:
                # Parse datetime strings or keep datetime objects as-is
                created_at = self._ensure_datetime(test_data.get("created_at"))
                start_time = self._ensure_datetime(test_data.get("start_time"))
                end_time = self._ensure_datetime(test_data.get("end_time"))

                # Extract DUT information from nested object (EOLTest.to_dict() structure)
                # Domain model stores DUT as nested object: {"dut": {"dut_id": ..., "serial_number": ...}}
                # Repository's responsibility: Transform Domain structure → DB schema (flat structure)
                dut_data = test_data.get("dut", {})

                # Extract DUT fields with validation
                dut_id = dut_data.get("dut_id", "UNKNOWN")
                serial_number = dut_data.get("serial_number")

                # Log warning if DUT information is missing
                if not dut_data:
                    logger.warning(
                        f"DUT information missing in test_data for test_id={test_data.get('test_id')}"
                    )
                if dut_id == "UNKNOWN":
                    logger.warning(f"DUT ID is missing for test_id={test_data.get('test_id')}")
                if not serial_number:
                    logger.warning(
                        f"Serial number is missing for test_id={test_data.get('test_id')}"
                    )

                # Create TestResult model with extracted DUT information
                test_result = TestResult(
                    test_id=test_data["test_id"],
                    dut_id=dut_id,
                    serial_number=serial_number,
                    operator_id=test_data.get("operator_id", "UNKNOWN"),
                    status=test_data.get("status", "unknown"),
                    created_at=created_at,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=test_data.get("duration_seconds"),
                    error_message=test_data.get("error_message"),
                    test_configuration=test_data.get("test_configuration"),
                )

                session.add(test_result)
                await session.commit()

                logger.debug(
                    f"Test result saved to database: test_id={test_data['test_id']}, "
                    f"dut_id={dut_id}, serial_number={serial_number}"
                )

        except Exception as e:
            logger.error(f"Failed to save test result to database: {e}")
            raise RepositoryAccessError(
                "save_test_result",
                f"Failed to save test result: {str(e)}",
                file_path=None,
            ) from e

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
        """Save raw measurement data to database"""
        try:
            async with self._db_manager.get_session() as session:
                measurement = RawMeasurement(
                    test_id=test_id,
                    serial_number=serial_number,
                    cycle_number=cycle_number,
                    timestamp=timestamp,
                    temperature=temperature,
                    position=position,
                    force=force,
                )

                session.add(measurement)
                await session.commit()

                logger.debug(
                    f"Raw measurement saved: test_id={test_id}, "
                    f"temp={temperature}, force={force}"
                )

        except Exception as e:
            logger.error(f"Failed to save raw measurement to database: {e}")
            raise RepositoryAccessError(
                "save_raw_measurement",
                f"Failed to save measurement: {str(e)}",
                file_path=None,
            ) from e

    async def query_tests(
        self,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query test results"""
        try:
            async with self._db_manager.get_session() as session:
                # Build query
                query = select(TestResult)

                # Apply filters
                if serial_number:
                    query = query.where(TestResult.serial_number == serial_number)
                if start_date:
                    query = query.where(TestResult.created_at >= start_date)
                if end_date:
                    query = query.where(TestResult.created_at <= end_date)
                if status:
                    query = query.where(TestResult.status == status)

                # Order by created_at descending (newest first)
                query = query.order_by(TestResult.created_at.desc())
                query = query.limit(limit)

                # Execute query
                result = await session.execute(query)
                tests = result.scalars().all()

                # Convert to dictionaries
                return [self._test_result_to_dict(test) for test in tests]

        except Exception as e:
            logger.error(f"Failed to query tests: {e}")
            raise RepositoryAccessError("query_tests", f"Failed to query tests: {str(e)}") from e

    async def query_raw_measurements(
        self,
        test_id: Optional[str] = None,
        serial_number: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Query raw measurement data"""
        try:
            async with self._db_manager.get_session() as session:
                # Build query
                query = select(RawMeasurement)

                # Apply filters
                if test_id:
                    query = query.where(RawMeasurement.test_id == test_id)
                if serial_number:
                    query = query.where(RawMeasurement.serial_number == serial_number)
                if start_date:
                    query = query.where(RawMeasurement.timestamp >= start_date)
                if end_date:
                    query = query.where(RawMeasurement.timestamp <= end_date)

                # Order by timestamp ascending
                query = query.order_by(RawMeasurement.timestamp.asc())
                query = query.limit(limit)

                # Execute query
                result = await session.execute(query)
                measurements = result.scalars().all()

                # Convert to dictionaries
                return [self._measurement_to_dict(m) for m in measurements]

        except Exception as e:
            logger.error(f"Failed to query measurements: {e}")
            raise RepositoryAccessError(
                "query_raw_measurements", f"Failed to query measurements: {str(e)}"
            ) from e

    async def query_test_ids_from_measurements(
        self,
        serial_number: Optional[str] = None,
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query unique test IDs from raw measurements table.

        This is used when test_results table is not available or not matched.
        Returns test_id, serial_number, earliest timestamp, and measurement count.

        Args:
            serial_number: Filter by serial number (partial match)
            start_date: Filter by start date (accepts date or datetime)
            end_date: Filter by end date (accepts date or datetime)
            limit: Maximum number of test_ids to return

        Returns:
            List of dictionaries with test_id, serial_number, created_at, measurement_count
        """
        try:
            async with self._db_manager.get_session() as session:
                # Third-party imports
                from sqlalchemy import func
                # Standard library imports
                from datetime import time

                # Convert date objects to datetime for proper filtering
                # date objects are interpreted as start/end of day
                if start_date:
                    if isinstance(start_date, date) and not isinstance(start_date, datetime):
                        # Convert date to datetime at start of day (00:00:00)
                        start_date = datetime.combine(start_date, time.min)

                if end_date:
                    if isinstance(end_date, date) and not isinstance(end_date, datetime):
                        # Convert date to datetime at end of day (23:59:59.999999)
                        end_date = datetime.combine(end_date, time.max)

                # Build subquery to get test summary
                # GROUP BY test_id only to ensure one row per unique test
                # (A single test may have multiple serial_numbers during execution)
                subquery = select(
                    RawMeasurement.test_id,
                    func.min(RawMeasurement.serial_number).label("serial_number"),
                    func.min(RawMeasurement.timestamp).label("created_at"),
                    func.count(RawMeasurement.id).label("measurement_count"),
                ).group_by(RawMeasurement.test_id)

                # Apply filters to subquery
                if serial_number:
                    # Partial match on serial number
                    subquery = subquery.where(
                        RawMeasurement.serial_number.like(f"%{serial_number}%")
                    )
                if start_date:
                    subquery = subquery.where(RawMeasurement.timestamp >= start_date)
                if end_date:
                    subquery = subquery.where(RawMeasurement.timestamp <= end_date)

                # Order by created_at descending (newest first)
                subquery = subquery.order_by(func.min(RawMeasurement.timestamp).desc())
                subquery = subquery.limit(limit)

                # Execute query
                result = await session.execute(subquery)
                rows = result.all()

                # Convert to dictionaries
                test_list = []
                for row in rows:
                    test_list.append(
                        {
                            "test_id": row.test_id,
                            "serial_number": row.serial_number,
                            "created_at": row.created_at,
                            "measurement_count": row.measurement_count,
                            "status": "N/A",  # No status in raw_measurements
                            "duration_seconds": None,  # No duration in raw_measurements
                        }
                    )

                logger.debug(f"Found {len(test_list)} unique test_ids from raw_measurements")
                return test_list

        except Exception as e:
            logger.error(f"Failed to query test IDs from measurements: {e}")
            raise RepositoryAccessError(
                "query_test_ids_from_measurements",
                f"Failed to query test IDs: {str(e)}",
            ) from e

    async def get_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get test result by ID"""
        try:
            async with self._db_manager.get_session() as session:
                query = select(TestResult).where(TestResult.test_id == test_id)
                result = await session.execute(query)
                test = result.scalar_one_or_none()

                if test:
                    return self._test_result_to_dict(test)
                return None

        except Exception as e:
            logger.error(f"Failed to get test by ID: {e}")
            raise RepositoryAccessError(
                "get_test_by_id", f"Failed to get test: {str(e)}", file_path=None
            ) from e

    async def delete_test(self, test_id: str) -> None:
        """Delete test result and associated measurements"""
        try:
            async with self._db_manager.get_session() as session:
                # Check if test exists
                query = select(TestResult).where(TestResult.test_id == test_id)
                result = await session.execute(query)
                test = result.scalar_one_or_none()

                if not test:
                    raise ConfigurationNotFoundError(f"Test {test_id} not found")

                # Delete test (cascade will delete measurements)
                await session.execute(delete(TestResult).where(TestResult.test_id == test_id))
                await session.commit()

                logger.debug(f"Test deleted from database: {test_id}")

        except ConfigurationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete test: {e}")
            raise RepositoryAccessError(
                "delete_test", f"Failed to delete test: {str(e)}", file_path=None
            ) from e

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get test statistics"""
        try:
            async with self._db_manager.get_session() as session:
                # Build base query
                query = select(
                    func.count(TestResult.id).label("total_tests"),
                    func.sum(func.case((TestResult.status == "completed", 1), else_=0)).label(
                        "pass_count"
                    ),
                    func.sum(func.case((TestResult.status == "failed", 1), else_=0)).label(
                        "fail_count"
                    ),
                    func.avg(TestResult.duration_seconds).label("avg_duration"),
                )

                # Apply date filters
                if start_date:
                    query = query.where(TestResult.created_at >= start_date)
                if end_date:
                    query = query.where(TestResult.created_at <= end_date)

                # Execute query
                result = await session.execute(query)
                row = result.one()

                return {
                    "total_tests": row.total_tests or 0,
                    "pass_count": row.pass_count or 0,
                    "fail_count": row.fail_count or 0,
                    "avg_duration_seconds": float(row.avg_duration) if row.avg_duration else 0.0,
                }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise RepositoryAccessError(
                "get_statistics", f"Failed to get statistics: {str(e)}"
            ) from e

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_string:
            return None

        try:
            # Handle ISO format datetime strings
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {dt_string}")
            return None

    def _ensure_datetime(self, dt_value: Optional[Any]) -> Optional[datetime]:
        """Ensure value is a datetime object, parsing if necessary"""
        if dt_value is None:
            return None

        # Already a datetime object
        if isinstance(dt_value, datetime):
            return dt_value

        # String that needs parsing
        if isinstance(dt_value, str):
            return self._parse_datetime(dt_value)

        logger.warning(f"Unexpected datetime type: {type(dt_value)}")
        return None

    def _test_result_to_dict(self, test: TestResult) -> Dict[str, Any]:
        """Convert TestResult model to dictionary"""
        return {
            "id": test.id,
            "test_id": test.test_id,
            "dut_id": test.dut_id,
            "serial_number": test.serial_number,
            "operator_id": test.operator_id,
            "status": test.status,
            "created_at": test.created_at.isoformat() if test.created_at else None,
            "start_time": test.start_time.isoformat() if test.start_time else None,
            "end_time": test.end_time.isoformat() if test.end_time else None,
            "duration_seconds": test.duration_seconds,
            "error_message": test.error_message,
            "test_configuration": test.test_configuration,
        }

    def _measurement_to_dict(self, measurement: RawMeasurement) -> Dict[str, Any]:
        """Convert RawMeasurement model to dictionary"""
        return {
            "id": measurement.id,
            "test_id": measurement.test_id,
            "serial_number": measurement.serial_number,
            "cycle_number": measurement.cycle_number,
            "timestamp": measurement.timestamp.isoformat() if measurement.timestamp else None,
            "temperature": measurement.temperature,
            "position": measurement.position,
            "force": measurement.force,
        }
