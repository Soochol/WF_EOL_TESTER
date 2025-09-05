"""
Robot Home Input

Input object for robot homing operation.
Contains operator identification for the homing operation.
"""

from typing import Any, Dict

from application.use_cases.common.command_result_patterns import BaseUseCaseInput


class RobotHomeInput(BaseUseCaseInput):
    """
    Input for Robot Homing Operation
    
    Simple input containing operator identification for robot homing.
    """

    def __init__(self, operator_id: str = "system"):
        """
        Initialize robot home input
        
        Args:
            operator_id: ID of the operator executing the operation
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
