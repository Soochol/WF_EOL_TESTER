"""
Base Controller

Base class for all presentation layer controllers providing common functionality.
"""

from typing import Dict, Any, Optional
from abc import ABC
from loguru import logger


class BaseController(ABC):
    """Base class for presentation controllers"""
    
    def __init__(self):
        """Initialize base controller"""
        self._logger = logger
    
    def _create_success_response(
        self,
        data: Any,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Standardized success response
        """
        response = {
            'success': True,
            'data': data
        }
        
        if message:
            response['message'] = message
        
        if metadata:
            response['metadata'] = metadata
        
        return response
    
    def _create_error_response(
        self,
        error_code: str,
        error_message: str,
        error_context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            error_code: Error code for categorization
            error_message: Human-readable error message
            error_context: Additional error context (optional)
            suggestions: Suggested actions (optional)
            
        Returns:
            Standardized error response
        """
        response = {
            'success': False,
            'error': {
                'code': error_code,
                'message': error_message
            }
        }
        
        if error_context:
            response['error']['context'] = error_context
        
        if suggestions:
            response['error']['suggestions'] = suggestions
        
        return response
    
    def _create_validation_error_response(
        self,
        field_errors: Dict[str, str],
        general_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized validation error response
        
        Args:
            field_errors: Field-specific validation errors
            general_message: General validation message (optional)
            
        Returns:
            Standardized validation error response
        """
        response = {
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': general_message or 'Input validation failed',
                'validation_errors': field_errors
            }
        }
        
        return response
    
    def _log_controller_action(
        self,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log controller action for audit purposes
        
        Args:
            action: Action being performed
            parameters: Action parameters (optional)
            user_id: User identifier (optional)
        """
        log_data = {
            'controller': self.__class__.__name__,
            'action': action
        }
        
        if parameters:
            log_data['parameters'] = parameters
        
        if user_id:
            log_data['user_id'] = user_id
        
        self._logger.info(f"Controller action: {log_data}")
    
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