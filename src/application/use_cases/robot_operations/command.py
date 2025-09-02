"""
Robot Home Command

Command object for robot homing operation.
Contains operator identification for the homing operation.
"""

from typing import Any, Dict

from application.use_cases.common.command_result_patterns import BaseCommand


class RobotHomeCommand(BaseCommand):
    """
    Command for Robot Homing Operation
    
    Simple command containing operator identification for robot homing.
    """

    def __init__(self, operator_id: str = "system"):
        """
        Initialize robot home command
        
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
