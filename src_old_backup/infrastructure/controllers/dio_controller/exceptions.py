"""
DIO Controller Exceptions

All DIO controller exception definitions.
Exception-first approach with independent exception hierarchy.
"""

from typing import Optional


class DIOError(Exception):
    """Base DIO controller error - independent of common hardware exceptions"""
    
    def __init__(self, message: str, controller_type: str = "unknown", hardware_id: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.controller_type = controller_type
        self.hardware_id = hardware_id
        self.details = details
    
    def __str__(self) -> str:
        base_msg = self.message
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        
        hardware_info = f"DIO ({self.controller_type})"
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


class DIOConnectionError(DIOError):
    """Raised when DIO controller connection fails"""
    
    def __init__(self, message: str, controller_type: str = "unknown", connection_params: Optional[dict] = None, **kwargs):
        super().__init__(message, controller_type, **kwargs)
        self.connection_params = connection_params or {}
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.connection_params:
            params_str = ", ".join([f"{k}={v}" for k, v in self.connection_params.items()])
            return f"{base_msg} (Connection params: {params_str})"
        return base_msg


class DIOInitializationError(DIOError):
    """Raised when DIO controller initialization fails"""
    pass


class DIOTimeoutError(DIOError):
    """Raised when DIO operation times out"""
    
    def __init__(self, message: str, controller_type: str = "unknown", timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, controller_type, **kwargs)
        self.timeout_duration = timeout_duration
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.timeout_duration:
            return f"{base_msg} (Timeout: {self.timeout_duration}s)"
        return base_msg


class DIOCommunicationError(DIOError):
    """Raised when DIO communication fails"""
    
    def __init__(self, message: str, controller_type: str = "unknown", operation: Optional[str] = None, **kwargs):
        super().__init__(message, controller_type, **kwargs)
        self.operation = operation
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.operation:
            return f"{base_msg} (Operation: {self.operation})"
        return base_msg


# ============================================================================
# AJINEXTEK AXL DIO Specific Errors
# ============================================================================

class AXLDIOError(DIOError):
    """AJINEXTEK AXL DIO errors"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = "", **kwargs):
        super().__init__(message, "AJINEXTEK AXL", **kwargs)
        self.error_code = error_code
        self.function_name = function_name
        
    def __str__(self) -> str:
        base_msg = self.message
        if self.function_name:
            base_msg = f"{self.function_name}: {base_msg}"
        if self.error_code:
            base_msg = f"{base_msg} (Error Code: {self.error_code})"
        
        hardware_info = f"DIO ({self.controller_type})"
        if self.hardware_id:
            hardware_info += f" ({self.hardware_id})"
        return f"{hardware_info}: {base_msg}"


class AXLDIOConnectionError(DIOConnectionError):
    """AJINEXTEK AXL DIO connection errors"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = "", **kwargs):
        super().__init__(message, "AJINEXTEK AXL", **kwargs)
        self.error_code = error_code
        self.function_name = function_name


class AXLDIOInitializationError(DIOInitializationError):
    """AJINEXTEK AXL DIO initialization errors"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = "", **kwargs):
        super().__init__(message, "AJINEXTEK AXL", **kwargs)
        self.error_code = error_code
        self.function_name = function_name


class AXLDIOTimeoutError(DIOTimeoutError):
    """AJINEXTEK AXL DIO timeout errors"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = "", timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, "AJINEXTEK AXL", timeout_duration, **kwargs)
        self.error_code = error_code
        self.function_name = function_name


class AXLDIOCommunicationError(DIOCommunicationError):
    """AJINEXTEK AXL DIO communication errors"""
    
    def __init__(self, message: str, error_code: int = 0, function_name: str = "", operation: Optional[str] = None, **kwargs):
        super().__init__(message, "AJINEXTEK AXL", operation, **kwargs)
        self.error_code = error_code
        self.function_name = function_name




# ============================================================================
# Convenience functions for creating common exceptions
# ============================================================================

def create_axl_dio_error(error_code: int, function_name: str, error_message: str) -> AXLDIOError:
    """Create a standardized AXL DIO error"""
    return AXLDIOError(error_message, error_code, function_name)