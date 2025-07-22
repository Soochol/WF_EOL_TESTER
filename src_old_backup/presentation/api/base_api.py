"""
Base API

Base class for HTTP API endpoints providing common functionality.
"""

from typing import Dict, Any, Optional, Tuple
from abc import ABC
import traceback
from loguru import logger


class BaseAPI(ABC):
    """Base class for HTTP API endpoints"""
    
    def __init__(self):
        """Initialize base API"""
        self._logger = logger
    
    def create_response(
        self,
        data: Any = None,
        message: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        Create standardized HTTP response
        
        Args:
            data: Response data
            message: Response message (optional)
            status_code: HTTP status code
            headers: Response headers (optional)
            
        Returns:
            Tuple of (response_body, status_code, headers)
        """
        response_body = {
            'success': 200 <= status_code < 300,
            'status_code': status_code
        }
        
        if data is not None:
            response_body['data'] = data
        
        if message:
            response_body['message'] = message
        
        response_headers = headers or {}
        response_headers.setdefault('Content-Type', 'application/json')
        
        return response_body, status_code, response_headers
    
    def create_error_response(
        self,
        error_code: str,
        error_message: str,
        status_code: int = 400,
        error_context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        Create standardized error response
        
        Args:
            error_code: Error code for categorization
            error_message: Human-readable error message
            status_code: HTTP status code
            error_context: Additional error context (optional)
            suggestions: Suggested actions (optional)
            
        Returns:
            Tuple of (response_body, status_code, headers)
        """
        response_body = {
            'success': False,
            'status_code': status_code,
            'error': {
                'code': error_code,
                'message': error_message
            }
        }
        
        if error_context:
            response_body['error']['context'] = error_context
        
        if suggestions:
            response_body['error']['suggestions'] = suggestions
        
        headers = {'Content-Type': 'application/json'}
        
        return response_body, status_code, headers
    
    def create_validation_error_response(
        self,
        field_errors: Dict[str, str],
        general_message: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        Create validation error response
        
        Args:
            field_errors: Field-specific validation errors
            general_message: General validation message (optional)
            
        Returns:
            Tuple of (response_body, status_code, headers)
        """
        response_body = {
            'success': False,
            'status_code': 422,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': general_message or 'Input validation failed',
                'validation_errors': field_errors
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        return response_body, 422, headers
    
    def handle_controller_response(
        self,
        controller_result: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        Convert controller response to HTTP response
        
        Args:
            controller_result: Result from controller
            
        Returns:
            Tuple of (response_body, status_code, headers)
        """
        if controller_result.get('success', False):
            # Success response
            return self.create_response(
                data=controller_result,
                message=controller_result.get('message'),
                status_code=200
            )
        else:
            # Error response
            error = controller_result.get('error', {})
            error_code = error.get('code', 'UNKNOWN_ERROR')
            error_message = error.get('message', 'An unknown error occurred')
            
            # Map error codes to HTTP status codes
            status_code = self._map_error_to_status_code(error_code)
            
            return self.create_error_response(
                error_code=error_code,
                error_message=error_message,
                status_code=status_code,
                error_context=error.get('context'),
                suggestions=error.get('suggestions')
            )
    
    def handle_exception(
        self,
        exception: Exception,
        operation: str
    ) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
        """
        Handle unexpected exceptions
        
        Args:
            exception: The exception that occurred
            operation: Description of the operation that failed
            
        Returns:
            Tuple of (response_body, status_code, headers)
        """
        self._logger.error(f"API exception in {operation}: {str(exception)}")
        self._logger.error(f"Traceback: {traceback.format_exc()}")
        
        return self.create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            error_message=f"An internal error occurred during {operation}",
            status_code=500,
            error_context={
                'operation': operation,
                'exception_type': type(exception).__name__
            }
        )
    
    def _map_error_to_status_code(self, error_code: str) -> int:
        """
        Map error codes to appropriate HTTP status codes
        
        Args:
            error_code: Error code from controller
            
        Returns:
            Appropriate HTTP status code
        """
        error_mapping = {
            'VALIDATION_ERROR': 422,
            'INVALID_DUT_ID': 422,
            'INVALID_TEST_TYPE': 422,
            'INVALID_OPERATOR_ID': 422,
            'INVALID_DEVICE_TYPE': 422,
            'INVALID_PARAMETERS': 422,
            'HARDWARE_NOT_READY': 503,
            'LOADCELL_NOT_READY': 503,
            'POWER_SUPPLY_NOT_READY': 503,
            'HARDWARE_CONNECTION_FAILED': 503,
            'HARDWARE_DISCONNECTION_ERROR': 503,
            'BUSINESS_RULE_VIOLATION': 400,
            'UNSAFE_OPERATION': 400,
            'TEST_EXECUTION_ERROR': 500,
            'FORCE_MEASUREMENT_ERROR': 500,
            'POWER_MEASUREMENT_ERROR': 500,
            'AUTO_ZERO_ERROR': 500,
            'POWER_OUTPUT_ERROR': 500,
            'INTERNAL_ERROR': 500,
            'UNKNOWN_ERROR': 500
        }
        
        return error_mapping.get(error_code, 400)
    
    def log_api_request(
        self,
        method: str,
        endpoint: str,
        request_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log API request for audit purposes
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            request_data: Request data (optional)
            user_id: User identifier (optional)
        """
        log_data = {
            'api_class': self.__class__.__name__,
            'method': method,
            'endpoint': endpoint
        }
        
        if request_data:
            log_data['request_data'] = self._sanitize_for_logging(request_data)
        
        if user_id:
            log_data['user_id'] = user_id
        
        self._logger.info(f"API request: {log_data}")
    
    def _sanitize_for_logging(self, data: Any) -> Any:
        """
        Sanitize data for safe logging (remove sensitive information)
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data safe for logging
        """
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = {'password', 'token', 'secret', 'key', 'auth'}
            
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self._sanitize_for_logging(value)
            
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data]
        
        else:
            return data