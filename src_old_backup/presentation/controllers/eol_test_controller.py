"""
EOL Test Controller

Presentation layer controller for handling EOL test operations.
Coordinates between user interface and application use cases.
"""

from typing import Dict, Any, Optional
from loguru import logger

from ...application.use_cases.execute_eol_test_use_case import ExecuteEOLTestUseCase
from ...application.commands.execute_eol_test_command import ExecuteEOLTestCommand
from ...application.results.eol_test_result import EOLTestResult

from ...domain.value_objects.identifiers import DUTId, OperatorId
from ...domain.enums.test_types import TestType
from ...domain.exceptions.business_rule_exceptions import (
    BusinessRuleViolationException,
    HardwareNotReadyException,
    ValidationException
)

from .base_controller import BaseController


class EOLTestController(BaseController):
    """Controller for EOL test operations"""
    
    def __init__(self, execute_eol_test_use_case: ExecuteEOLTestUseCase):
        """
        Initialize controller with required use cases
        
        Args:
            execute_eol_test_use_case: Use case for EOL test execution
        """
        super().__init__()
        self._execute_eol_test_use_case = execute_eol_test_use_case
    
    async def execute_test(
        self,
        dut_id: str,
        test_type: str,
        operator_id: str,
        dut_model_number: Optional[str] = None,
        dut_serial_number: Optional[str] = None,
        dut_manufacturer: Optional[str] = None,
        test_configuration: Optional[Dict[str, Any]] = None,
        pass_criteria: Optional[Dict[str, Any]] = None,
        operator_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute EOL test
        
        Args:
            dut_id: Device Under Test identifier
            test_type: Type of test to execute
            operator_id: Operator identifier
            dut_model_number: DUT model number (optional)
            dut_serial_number: DUT serial number (optional) 
            dut_manufacturer: DUT manufacturer (optional)
            test_configuration: Test configuration parameters (optional)
            pass_criteria: Test pass criteria (optional)
            operator_notes: Operator notes (optional)
            
        Returns:
            Test execution result as dictionary
            
        Raises:
            BusinessRuleViolationException: If test execution fails
            ValidationException: If input validation fails
        """
        logger.info(f"EOL test execution requested for DUT {dut_id}")
        
        try:
            # Validate and convert inputs
            validated_inputs = self._validate_test_inputs(
                dut_id, test_type, operator_id, dut_model_number,
                dut_serial_number, dut_manufacturer, test_configuration,
                pass_criteria, operator_notes
            )
            
            # Create command
            command = ExecuteEOLTestCommand(
                dut_id=validated_inputs['dut_id'],
                test_type=validated_inputs['test_type'],
                operator_id=validated_inputs['operator_id'],
                dut_model_number=validated_inputs['dut_model_number'],
                dut_serial_number=validated_inputs['dut_serial_number'],
                dut_manufacturer=validated_inputs['dut_manufacturer'],
                test_configuration=validated_inputs['test_configuration'],
                pass_criteria=validated_inputs['pass_criteria'],
                operator_notes=validated_inputs['operator_notes']
            )
            
            # Execute use case
            result = await self._execute_eol_test_use_case.execute(command)
            
            # Convert to presentation format
            return self._format_test_result(result)
            
        except ValidationException as e:
            logger.error(f"Input validation failed: {e}")
            return self._create_error_response(
                "VALIDATION_ERROR",
                f"Input validation failed: {str(e)}",
                {"validation_errors": e.context}
            )
        except HardwareNotReadyException as e:
            logger.error(f"Hardware not ready: {e}")
            return self._create_error_response(
                "HARDWARE_NOT_READY",
                f"Hardware not ready: {str(e)}",
                {"hardware_status": e.context}
            )
        except BusinessRuleViolationException as e:
            logger.error(f"Business rule violation: {e}")
            return self._create_error_response(
                "BUSINESS_RULE_VIOLATION",
                str(e),
                e.context
            )
        except Exception as e:
            logger.error(f"Unexpected error during test execution: {e}")
            return self._create_error_response(
                "INTERNAL_ERROR",
                f"Unexpected error: {str(e)}",
                {"dut_id": dut_id, "test_type": test_type}
            )
    
    def _validate_test_inputs(
        self,
        dut_id: str,
        test_type: str,
        operator_id: str,
        dut_model_number: Optional[str],
        dut_serial_number: Optional[str],
        dut_manufacturer: Optional[str],
        test_configuration: Optional[Dict[str, Any]],
        pass_criteria: Optional[Dict[str, Any]],
        operator_notes: Optional[str]
    ) -> Dict[str, Any]:
        """Validate and convert input parameters"""
        
        # Validate required fields
        if not dut_id or not dut_id.strip():
            raise ValidationException(
                "DUT_ID_REQUIRED",
                "DUT ID is required and cannot be empty",
                {"field": "dut_id", "value": dut_id}
            )
        
        if not test_type or not test_type.strip():
            raise ValidationException(
                "TEST_TYPE_REQUIRED", 
                "Test type is required and cannot be empty",
                {"field": "test_type", "value": test_type}
            )
        
        if not operator_id or not operator_id.strip():
            raise ValidationException(
                "OPERATOR_ID_REQUIRED",
                "Operator ID is required and cannot be empty", 
                {"field": "operator_id", "value": operator_id}
            )
        
        # Convert and validate DUT ID
        try:
            dut_id_obj = DUTId(dut_id.strip())
        except Exception as e:
            raise ValidationException(
                "INVALID_DUT_ID",
                f"Invalid DUT ID format: {str(e)}",
                {"field": "dut_id", "value": dut_id}
            )
        
        # Convert and validate test type
        try:
            test_type_obj = TestType.from_string(test_type.strip().upper())
        except Exception as e:
            raise ValidationException(
                "INVALID_TEST_TYPE",
                f"Invalid test type: {str(e)}",
                {"field": "test_type", "value": test_type, "valid_types": [t.value for t in TestType]}
            )
        
        # Convert and validate operator ID
        try:
            operator_id_obj = OperatorId(operator_id.strip())
        except Exception as e:
            raise ValidationException(
                "INVALID_OPERATOR_ID",
                f"Invalid operator ID format: {str(e)}",
                {"field": "operator_id", "value": operator_id}
            )
        
        # Validate optional string fields
        validated_model = dut_model_number.strip() if dut_model_number else None
        validated_serial = dut_serial_number.strip() if dut_serial_number else None
        validated_manufacturer = dut_manufacturer.strip() if dut_manufacturer else None
        validated_notes = operator_notes.strip() if operator_notes else None
        
        # Validate configuration and criteria
        validated_config = test_configuration if test_configuration else {}
        validated_criteria = pass_criteria if pass_criteria else {}
        
        return {
            'dut_id': dut_id_obj,
            'test_type': test_type_obj,
            'operator_id': operator_id_obj,
            'dut_model_number': validated_model,
            'dut_serial_number': validated_serial,
            'dut_manufacturer': validated_manufacturer,
            'test_configuration': validated_config,
            'pass_criteria': validated_criteria,
            'operator_notes': validated_notes
        }
    
    def _format_test_result(self, result: EOLTestResult) -> Dict[str, Any]:
        """Format use case result for presentation"""
        return {
            'success': True,
            'test_id': str(result.test_id),
            'test_type': result.test_type.value,
            'status': result.test_status.value,
            'passed': result.is_passed,
            'execution_duration_ms': result.execution_duration.total_seconds() * 1000 if result.execution_duration else 0,
            'measurement_count': len(result.measurement_ids),
            'measurement_ids': [str(mid) for mid in result.measurement_ids],
            'test_summary': result.test_summary,
            'error_message': result.error_message,
            'operator_notes': result.operator_notes,
            'timestamp': result.test_id.created_at.isoformat() if hasattr(result.test_id, 'created_at') else None
        }
    
    async def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """
        Get status of a specific test
        
        Args:
            test_id: Test identifier
            
        Returns:
            Test status information
        """
        logger.info(f"Test status requested for test {test_id}")
        
        try:
            # This would typically use a query use case
            # For now, return a placeholder response
            return {
                'success': True,
                'test_id': test_id,
                'message': 'Test status query not yet implemented'
            }
            
        except Exception as e:
            logger.error(f"Error getting test status: {e}")
            return self._create_error_response(
                "STATUS_QUERY_ERROR",
                f"Failed to get test status: {str(e)}",
                {"test_id": test_id}
            )
    
    async def cancel_test(self, test_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel a running test
        
        Args:
            test_id: Test identifier
            reason: Cancellation reason (optional)
            
        Returns:
            Cancellation result
        """
        logger.info(f"Test cancellation requested for test {test_id}")
        
        try:
            # This would typically use a cancel test use case
            # For now, return a placeholder response
            return {
                'success': True,
                'test_id': test_id,
                'message': 'Test cancellation not yet implemented',
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error cancelling test: {e}")
            return self._create_error_response(
                "CANCELLATION_ERROR",
                f"Failed to cancel test: {str(e)}",
                {"test_id": test_id, "reason": reason}
            )