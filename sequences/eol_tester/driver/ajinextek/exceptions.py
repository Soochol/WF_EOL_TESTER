"""
Ajinextek AXL Exceptions

Exception classes for AXL library errors.
"""

from typing import Optional


class AXLError(Exception):
    """Base AXL library error"""

    def __init__(
        self,
        message: str,
        error_code: Optional[int] = None,
        details: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self) -> str:
        base_msg = self.message
        if self.error_code is not None:
            base_msg = f"{base_msg} (Error code: {self.error_code})"
        if self.details:
            base_msg = f"{base_msg}. Details: {self.details}"
        return base_msg


class AXLMotionError(AXLError):
    """AXL motion control error"""
    pass


class AXLDIOError(AXLError):
    """AXL digital I/O error"""
    pass


class AXLConnectionError(AXLError):
    """AXL connection/initialization error"""
    pass


class AXLPlatformError(AXLError):
    """AXL platform incompatibility error (non-Windows)"""
    pass
