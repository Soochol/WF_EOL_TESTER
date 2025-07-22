"""
Execute EOL Test Command

Command object for executing EOL tests.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ...domain.value_objects.identifiers import DUTId, OperatorId
from ...domain.enums.test_types import TestType
from ...domain.exceptions.validation_exceptions import ValidationException


@dataclass(frozen=True)
class ExecuteEOLTestCommand:
    """Command for executing EOL test"""
    
    dut_id: DUTId
    test_type: TestType
    operator_id: OperatorId
    dut_model_number: str
    dut_serial_number: str
    dut_manufacturer: str = "Unknown"
    test_configuration: Optional[Dict[str, Any]] = None
    pass_criteria: Optional[Dict[str, Any]] = None
    operator_notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate command after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate command data
        
        Raises:
            ValidationException: If command data is invalid
        """
        if not isinstance(self.dut_id, DUTId):
            raise ValidationException("dut_id", self.dut_id, "DUT ID must be DUTId instance")
        
        if not isinstance(self.test_type, TestType):
            raise ValidationException("test_type", self.test_type, "Test type must be TestType enum")
        
        if not isinstance(self.operator_id, OperatorId):
            raise ValidationException("operator_id", self.operator_id, "Operator ID must be OperatorId instance")
        
        if not self.dut_model_number or not self.dut_model_number.strip():
            raise ValidationException("dut_model_number", self.dut_model_number, "DUT model number is required")
        
        if not self.dut_serial_number or not self.dut_serial_number.strip():
            raise ValidationException("dut_serial_number", self.dut_serial_number, "DUT serial number is required")
        
        if not self.dut_manufacturer or not self.dut_manufacturer.strip():
            raise ValidationException("dut_manufacturer", self.dut_manufacturer, "DUT manufacturer is required")
        
        # Validate test configuration if provided
        if self.test_configuration is not None and not isinstance(self.test_configuration, dict):
            raise ValidationException("test_configuration", self.test_configuration, "Test configuration must be a dictionary")
        
        # Validate pass criteria if provided
        if self.pass_criteria is not None and not isinstance(self.pass_criteria, dict):
            raise ValidationException("pass_criteria", self.pass_criteria, "Pass criteria must be a dictionary")
    
    def get_configuration_parameter(self, key: str, default: Any = None) -> Any:
        """Get specific configuration parameter"""
        if self.test_configuration is None:
            return default
        return self.test_configuration.get(key, default)
    
    def get_pass_criterion(self, key: str, default: Any = None) -> Any:
        """Get specific pass criterion"""
        if self.pass_criteria is None:
            return default
        return self.pass_criteria.get(key, default)
    
    def has_force_testing(self) -> bool:
        """Check if test requires force measurement"""
        return self.test_type.requires_force_measurement
    
    def has_electrical_testing(self) -> bool:
        """Check if test requires electrical measurement"""
        return self.test_type.requires_electrical_measurement
    
    def is_comprehensive_test(self) -> bool:
        """Check if this is a comprehensive test"""
        return self.test_type.is_comprehensive