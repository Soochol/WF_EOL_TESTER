"""
Test Entity Factory

Handles creation and initialization of EOL test entities.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

from datetime import datetime
from typing import Optional

from loguru import logger

from application.services.core.repository_service import RepositoryService
from domain.entities.dut import DUT
from domain.entities.eol_test import EOLTest
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.identifiers import DUTId, OperatorId, TestId
from domain.value_objects.test_configuration import TestConfiguration

from .constants import TestExecutionConstants


class TestEntityFactory:
    """Factory for creating and initializing EOL test entities"""

    def __init__(self, repository_service: RepositoryService):
        self._repository_service = repository_service

    async def create_test_entity(
        self,
        dut_info: DUTCommandInfo,
        operator_id: str,
        test_config: Optional[TestConfiguration] = None,
        session_timestamp: Optional[str] = None,
    ) -> EOLTest:
        """
        Create and initialize test entity from command data

        Args:
            dut_info: DUT command information
            operator_id: Operator identifier
            test_config: Test configuration (optional)
            session_timestamp: Session timestamp for grouping repeated tests

        Returns:
            EOLTest: Initialized test entity ready for execution
        """
        # Create DUT entity from command info
        dut = DUT(
            dut_id=DUTId(dut_info.dut_id),
            model_number=dut_info.model_number,
            serial_number=dut_info.serial_number,
            manufacturer=dut_info.manufacturer,
        )

        # Generate unique test ID with serial number and datetime
        test_id = await self._generate_unique_test_id(dut_info.serial_number)

        # Create and configure test entity
        test_entity = EOLTest(
            test_id=test_id,
            dut=dut,
            operator_id=OperatorId(operator_id),
            test_configuration=test_config.to_dict() if test_config else None,
            session_timestamp=session_timestamp,
        )

        return test_entity

    async def _generate_unique_test_id(
        self, serial_number: str, timestamp: Optional[datetime] = None
    ) -> TestId:
        """
        Generate a unique test ID, preferring no sequence number for cleaner IDs

        Args:
            serial_number: DUT serial number
            timestamp: Test timestamp (defaults to now)

        Returns:
            TestId: Unique test ID, preferring SerialNumber_YYYYMMDD_HHMMSS format (no sequence)
        """
        if timestamp is None:
            timestamp = datetime.now()

        # First, try without sequence number for cleaner ID
        try:
            test_id_no_seq = TestId.generate_from_serial_datetime_no_sequence(serial_number, timestamp)
            
            # Check if this test ID already exists
            if self._repository_service.test_repository:
                existing_test = await self._repository_service.test_repository.find_by_id(
                    str(test_id_no_seq)
                )
                if existing_test is None:
                    # ID is unique, use it without sequence
                    return test_id_no_seq
        except Exception as e:
            logger.warning(f"Failed to generate no-sequence test ID: {e}")

        # If no-sequence ID exists or failed, fall back to sequence-based generation
        sequence = TestExecutionConstants.INITIAL_SEQUENCE
        max_attempts = TestExecutionConstants.MAX_TEST_ID_ATTEMPTS

        while sequence <= max_attempts:
            test_id = TestId.generate_from_serial_datetime(serial_number, timestamp, sequence)

            # Check if this test ID already exists
            try:
                if self._repository_service.test_repository:
                    existing_test = await self._repository_service.test_repository.find_by_id(
                        str(test_id)
                    )
                    if existing_test is None:
                        # ID is unique, we can use it
                        return test_id
                    else:
                        # ID exists, try next sequence
                        sequence += 1
                else:
                    # No repository configured, assume ID is unique
                    return test_id
            except Exception as e:
                # Error checking existence, assume it doesn't exist and use the ID
                logger.warning(
                    f"Error checking test ID uniqueness for {test_id}: {e}. Using ID anyway."
                )
                return test_id

        # If we exhausted all sequences, fall back to UUID
        logger.warning(
            f"Exhausted all sequence numbers for {serial_number} at {timestamp.strftime('%Y%m%d_%H%M%S')}. Falling back to UUID format."
        )
        return TestId.generate()
