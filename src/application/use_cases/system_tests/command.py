"""
Simple MCU Test Input

Input object for simple MCU communication test.
Contains operator identification for the test execution.
"""

from typing import Any, Dict

from application.use_cases.common.command_result_patterns import BaseUseCaseInput


class SimpleMCUTestInput(BaseUseCaseInput):
    """
    Input for Simple MCU Communication Test

    Simple input containing operator identification for MCU communication testing.
    """

    def __init__(self, operator_id: str = "cli_user"):
        """
        Initialize simple MCU test input

        Args:
            operator_id: ID of the operator executing the test
        """
        super().__init__(operator_id)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert input to dictionary representation

        Returns:
            Dictionary containing input data
        """
        return {
            "operator_id": self.operator_id,
        }
