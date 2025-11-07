"""
Heating/Cooling Time Test Input

Input object for heating/cooling time test use case.
Contains all input parameters for the test execution.
"""

# Standard library imports
from typing import Any, Dict

# Local application imports
from application.use_cases.common.command_result_patterns import BaseUseCaseInput
from domain.value_objects.dut_command_info import DUTCommandInfo


class HeatingCoolingTimeTestInput(BaseUseCaseInput):
    """
    Input for Heating/Cooling Time Test

    Contains parameters for heating/cooling time test execution including
    repeat count and operator identification.
    """

    def __init__(
        self, dut_info: DUTCommandInfo, operator_id: str = "cli_user", repeat_count: int = 1
    ):
        """
        Initialize test input

        Args:
            dut_info: DUT command information for the test
            operator_id: ID of the operator running the test
            repeat_count: Number of heating/cooling cycles to perform
        """
        super().__init__(operator_id)
        self.dut_info = dut_info
        self.repeat_count = repeat_count

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert input to dictionary representation

        Returns:
            Dictionary containing input data
        """
        return {
            "operator_id": self.operator_id,
            "dut_info": self.dut_info.to_dict() if self.dut_info else None,
            "repeat_count": self.repeat_count,
        }
