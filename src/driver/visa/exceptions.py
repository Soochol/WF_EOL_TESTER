"""
VISA Communication Exceptions

Exception hierarchy for PyVISA-based instrument communication.
"""


class VISAError(Exception):
    """Base exception for VISA communication errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class VISAConnectionError(VISAError):
    """Exception raised when VISA connection fails"""

    def __init__(self, resource_string: str, message: str):
        self.resource_string = resource_string
        super().__init__(f"VISA connection failed ({resource_string}): {message}")


class VISACommunicationError(VISAError):
    """Exception raised when VISA communication fails"""

    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"VISA {operation} failed: {message}")


class VISATimeoutError(VISAError):
    """Exception raised when VISA operation times out"""

    def __init__(self, operation: str, timeout_ms: int):
        self.operation = operation
        self.timeout_ms = timeout_ms
        super().__init__(f"VISA {operation} timed out after {timeout_ms}ms")


class VISAResourceNotFoundError(VISAError):
    """Exception raised when VISA resource is not found"""

    def __init__(self, resource_pattern: str):
        self.resource_pattern = resource_pattern
        super().__init__(f"VISA resource not found: {resource_pattern}")
