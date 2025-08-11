"""
Test State Manager

Handles test state persistence and measurement ID management.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

from loguru import logger

from src.application.services.repository_service import RepositoryService
from src.domain.entities.eol_test import EOLTest
from src.domain.value_objects.identifiers import MeasurementId
from src.domain.value_objects.measurements import TestMeasurements

from .constants import TestExecutionConstants


class TestStateManager:
    """Handles test state management and persistence operations"""

    def __init__(self, repository_service: RepositoryService):
        self._repository_service = repository_service

    async def save_test_state(self, test_entity: EOLTest) -> None:
        """
        Save test state to repository

        Args:
            test_entity: Test entity to save

        Note:
            Failures in saving are logged but don't fail the test execution
        """
        try:
            await self._repository_service.save_test_result(test_entity)
            logger.debug(TestExecutionConstants.LOG_TEST_STATE_SAVED, test_entity.test_id)
        except Exception as save_error:
            # Repository save failures should not fail the test
            logger.warning(TestExecutionConstants.LOG_TEST_STATE_SAVE_FAILED, save_error)

    def generate_measurement_ids(self, measurements: TestMeasurements) -> list[MeasurementId]:
        """
        Extract measurement IDs from test measurements

        Args:
            measurements: Test measurements containing temperature-position data

        Returns:
            List of measurement IDs for each measurement point
        """
        measurement_ids = []
        measurement_matrix = measurements.get_measurement_matrix()

        # Generate measurement ID for each measurement point
        for i, _ in enumerate(measurement_matrix.keys(), TestExecutionConstants.INITIAL_SEQUENCE):
            # Generate sequential ID in format M0000000001, M0000000002, etc.
            measurement_id = MeasurementId(TestExecutionConstants.MEASUREMENT_ID_FORMAT.format(i))
            measurement_ids.append(measurement_id)

        logger.debug(TestExecutionConstants.LOG_MEASUREMENT_IDS_GENERATED.format(len(measurement_ids)))
        return measurement_ids
