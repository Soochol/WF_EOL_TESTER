"""
Simple MCU Test Command

Command object for simple MCU communication test.
Contains operator identification for the test execution.
"""

from typing import Any, Dict

from application.use_cases.common.command_result_patterns import BaseCommand


class SimpleMCUTestCommand(BaseCommand):
    """
    Command for Simple MCU Communication Test
    
    Simple command containing operator identification for MCU communication testing.
    """

    def __init__(self, operator_id: str = "cli_user"):
        """
        Initialize simple MCU test command
        
        Args:
            operator_id: ID of the operator executing the command
        """
        super().__init__(operator_id)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to dictionary representation
        
        Returns:
            Dictionary containing command data
        """
        return {
            "operator_id": self.operator_id,
        }
