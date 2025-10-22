"""
Test Entity Factory

Handles creation and initialization of EOL test entities.
Extracted from EOLForceTestUseCase for better separation of concerns.
"""

# Standard library imports
from typing import Optional

# Local application imports
from application.services.core.repository_service import RepositoryService
from domain.entities.dut import DUT
from domain.entities.eol_test import EOLTest
from domain.value_objects.dut_command_info import DUTCommandInfo
from domain.value_objects.identifiers import DUTId, OperatorId, TestId
from domain.value_objects.test_configuration import TestConfiguration


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

        # Generate unique test ID using UUID format
        test_id = await self._generate_unique_test_id()

        # Create and configure test entity
        test_entity = EOLTest(
            test_id=test_id,
            dut=dut,
            operator_id=OperatorId(operator_id),
            test_configuration=test_config.to_dict() if test_config else None,
            session_timestamp=session_timestamp,
        )

        return test_entity

    async def _generate_unique_test_id(self) -> TestId:
        """
        Generate a unique test ID using UUID format.

        UUID provides guaranteed uniqueness without requiring duplicate checks,
        sequence management, or database queries. This simplifies the code and
        eliminates the possibility of ID collisions.

        Returns:
            TestId: Unique UUID-format test ID

        Note:
            Serial number and timestamp information is preserved in separate
            database fields (dut.serial_number, created_at) so no information
            is lost by using UUID.
        """
        return TestId.generate()  # UUID format - always unique
