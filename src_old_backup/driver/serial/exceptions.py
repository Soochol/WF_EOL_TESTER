"""
Serial Communication Exceptions

Exception classes for serial communication errors following Exception First design.
These exceptions are driver-level and protocol-agnostic.
"""

from typing import Optional, Dict, Any
from ...domain.exceptions import EOLTestError


class InfrastructureError(EOLTestError):
    """Base class for infrastructure errors"""
    pass


class ErrorCategory:
    """Error category constants"""
    COMMUNICATION = "communication"
    CONFIGURATION = "configuration"
    HARDWARE = "hardware"
    SYSTEM = "system"


class SerialDriverError(InfrastructureError):
    """Base exception for serial driver errors"""
    
    def __init__(self, message: str, port: str = "", baudrate: int = 0, 
                 timeout: float = 0.0, **kwargs):
        super().__init__(message, category=ErrorCategory.COMMUNICATION, **kwargs)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.port:
            base_msg += f" [Port: {self.port}]"
        if self.baudrate > 0:
            base_msg += f" [Baud: {self.baudrate}]"
        return base_msg


class SerialConnectionError(SerialDriverError):
    """Serial connection failure (port open, configuration errors)"""
    
    def __init__(self, message: str, port: str, connection_params: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(message, port=port, **kwargs)
        self.connection_params = connection_params or {}
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.connection_params:
            params_str = ", ".join([f"{k}={v}" for k, v in self.connection_params.items()])
            base_msg += f" [Params: {params_str}]"
        return base_msg


class SerialCommunicationError(SerialDriverError):
    """Serial communication failure (send/receive, buffer errors)"""
    
    def __init__(self, message: str, port: str = "", operation: str = "", 
                 data_size: int = 0, **kwargs):
        super().__init__(message, port=port, **kwargs)
        self.operation = operation
        self.data_size = data_size
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.operation:
            base_msg += f" [Operation: {self.operation}]"
        if self.data_size > 0:
            base_msg += f" [Data Size: {self.data_size}]"
        return base_msg


class SerialTimeoutError(SerialCommunicationError):
    """Serial timeout (response wait, connection timeout)"""
    
    def __init__(self, message: str, port: str, timeout: float, operation: str = "", **kwargs):
        super().__init__(message, port=port, operation=operation, timeout=timeout, **kwargs)
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.timeout > 0:
            base_msg += f" [Timeout: {self.timeout}s]"
        return base_msg


class SerialBufferError(SerialCommunicationError):
    """Buffer errors (overflow, underflow, frame loss)"""
    
    def __init__(self, message: str, port: str = "", buffer_size: int = 0, 
                 available_space: int = 0, **kwargs):
        super().__init__(message, port=port, **kwargs)
        self.buffer_size = buffer_size
        self.available_space = available_space
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.buffer_size > 0:
            base_msg += f" [Buffer Size: {self.buffer_size}]"
        if self.available_space >= 0:
            base_msg += f" [Available: {self.available_space}]"
        return base_msg


class SerialConfigurationError(SerialConnectionError):
    """Serial configuration errors (invalid parameters)"""
    
    def __init__(self, message: str, parameter: str = "", value: Any = None, **kwargs):
        super().__init__(message, **kwargs)
        self.parameter = parameter
        self.value = value
        
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.parameter:
            base_msg += f" [Parameter: {self.parameter}]"
        if self.value is not None:
            base_msg += f" [Value: {self.value}]"
        return base_msg


# Exception Factory for common serial error scenarios
class SerialExceptionFactory:
    """Factory for creating serial communication exceptions"""
    
    @staticmethod
    def create_connection_error(port: str, error_msg: str, **params) -> SerialConnectionError:
        """Create connection error with port and parameters"""
        return SerialConnectionError(
            f"Failed to connect to port {port}: {error_msg}",
            port=port,
            connection_params=params
        )
    
    @staticmethod
    def create_timeout_error(port: str, operation: str, timeout: float) -> SerialTimeoutError:
        """Create timeout error with operation details"""
        return SerialTimeoutError(
            f"Operation '{operation}' timed out after {timeout}s",
            port=port,
            operation=operation,
            timeout=timeout
        )
    
    @staticmethod
    def create_buffer_overflow_error(port: str, buffer_size: int) -> SerialBufferError:
        """Create buffer overflow error"""
        return SerialBufferError(
            f"Buffer overflow on port {port}",
            port=port,
            buffer_size=buffer_size,
            available_space=0
        )
    
    @staticmethod
    def create_configuration_error(parameter: str, value: Any, reason: str) -> SerialConfigurationError:
        """Create configuration error"""
        return SerialConfigurationError(
            f"Invalid {parameter} value: {reason}",
            parameter=parameter,
            value=value
        )
    
    @staticmethod
    def create_communication_error(port: str, operation: str, details: str) -> SerialCommunicationError:
        """Create general communication error"""
        return SerialCommunicationError(
            f"Communication error during {operation}: {details}",
            port=port,
            operation=operation
        )