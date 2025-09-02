"""
Heating/Cooling Time Test Command

Command object for heating/cooling time test use case.
Contains all input parameters for the test execution.
"""

from application.use_cases.common.command_result_patterns import BaseCommand
from typing import Any, Dict


class HeatingCoolingTimeTestCommand(BaseCommand):
    """
    Command for Heating/Cooling Time Test
    
    Contains parameters for heating/cooling time test execution including
    repeat count and operator identification.
    """

    def __init__(self, operator_id: str = "cli_user", repeat_count: int = 1):
        """
        Initialize test command

        Args:
            operator_id: ID of the operator running the test
            repeat_count: Number of heating/cooling cycles to perform
        """
        super().__init__(operator_id)
        self.repeat_count = repeat_count

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to dictionary representation
        
        Returns:
            Dictionary containing command data
        """
        return {
            "operator_id": self.operator_id,
            "repeat_count": self.repeat_count,
        }
