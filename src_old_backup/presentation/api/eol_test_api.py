"""
EOL Test API

HTTP API endpoints for EOL test operations.
"""

from typing import Dict, Any, Optional, Tuple
from loguru import logger

from ..controllers.eol_test_controller import EOLTestController
from .base_api import BaseAPI


class EOLTestAPI(BaseAPI):
    """HTTP API for EOL test operations"""
    
    def __init__(self, eol_test_controller: EOLTestController):
        """
        Initialize API with controller
        
        Args:
            eol_test_controller: EOL test controller
        """
        super().__init__()
        self._controller = eol_test_controller
    
    async def execute_test(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/tests/execute
        Execute EOL test
        
        Args:
            request_data: Request payload containing test parameters
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", "/api/v1/tests/execute", request_data)
        
        try:
            # Validate required fields
            validation_errors = self._validate_execute_test_request(request_data)
            if validation_errors:
                return self.create_validation_error_response(validation_errors)
            
            # Extract parameters
            dut_id = request_data['dut_id']
            test_type = request_data['test_type']
            operator_id = request_data['operator_id']
            dut_model_number = request_data.get('dut_model_number')
            dut_serial_number = request_data.get('dut_serial_number')
            dut_manufacturer = request_data.get('dut_manufacturer')
            test_configuration = request_data.get('test_configuration')
            pass_criteria = request_data.get('pass_criteria')
            operator_notes = request_data.get('operator_notes')
            
            # Execute test through controller
            result = await self._controller.execute_test(
                dut_id=dut_id,
                test_type=test_type,
                operator_id=operator_id,
                dut_model_number=dut_model_number,
                dut_serial_number=dut_serial_number,
                dut_manufacturer=dut_manufacturer,
                test_configuration=test_configuration,
                pass_criteria=pass_criteria,
                operator_notes=operator_notes
            )
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "test execution")
    
    async def get_test_status(self, test_id: str) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        GET /api/v1/tests/{test_id}/status
        Get test status
        
        Args:
            test_id: Test identifier
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("GET", f"/api/v1/tests/{test_id}/status")
        
        try:
            # Validate test ID
            if not test_id or not test_id.strip():
                return self.create_validation_error_response(
                    {'test_id': 'Test ID is required'}
                )
            
            # Get status through controller
            result = await self._controller.get_test_status(test_id.strip())
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "get test status")
    
    async def cancel_test(self, test_id: str, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        POST /api/v1/tests/{test_id}/cancel
        Cancel running test
        
        Args:
            test_id: Test identifier
            request_data: Request payload containing cancellation reason
            
        Returns:
            HTTP response tuple (body, status_code, headers)
        """
        self.log_api_request("POST", f"/api/v1/tests/{test_id}/cancel", request_data)
        
        try:
            # Validate test ID
            if not test_id or not test_id.strip():
                return self.create_validation_error_response(
                    {'test_id': 'Test ID is required'}
                )
            
            # Extract cancellation reason
            reason = request_data.get('reason')
            
            # Cancel test through controller
            result = await self._controller.cancel_test(test_id.strip(), reason)
            
            # Convert controller response to HTTP response
            return self.handle_controller_response(result)
            
        except Exception as e:
            return self.handle_exception(e, "test cancellation")
    
    def _validate_execute_test_request(self, request_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate execute test request data
        
        Args:
            request_data: Request payload
            
        Returns:
            Dictionary of field validation errors (empty if valid)
        """
        errors = {}
        
        # Required fields
        if not request_data.get('dut_id', '').strip():
            errors['dut_id'] = 'DUT ID is required'
        
        if not request_data.get('test_type', '').strip():
            errors['test_type'] = 'Test type is required'
        
        if not request_data.get('operator_id', '').strip():
            errors['operator_id'] = 'Operator ID is required'
        
        # Optional field validation
        test_configuration = request_data.get('test_configuration')
        if test_configuration is not None and not isinstance(test_configuration, dict):
            errors['test_configuration'] = 'Test configuration must be a valid object'
        
        pass_criteria = request_data.get('pass_criteria')
        if pass_criteria is not None and not isinstance(pass_criteria, dict):
            errors['pass_criteria'] = 'Pass criteria must be a valid object'
        
        # String length limits
        if len(request_data.get('dut_id', '')) > 100:
            errors['dut_id'] = 'DUT ID must be 100 characters or less'
        
        if len(request_data.get('operator_id', '')) > 50:
            errors['operator_id'] = 'Operator ID must be 50 characters or less'
        
        if request_data.get('operator_notes') and len(request_data['operator_notes']) > 1000:
            errors['operator_notes'] = 'Operator notes must be 1000 characters or less'
        
        return errors