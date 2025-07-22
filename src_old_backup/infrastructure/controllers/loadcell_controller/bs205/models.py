"""
BS205 Loadcell Controller Data Models

Data structures and response handling for BS205 loadcell communication.
"""

import time
from typing import Optional
from dataclasses import dataclass

from loguru import logger


@dataclass
class LoadcellResponse:
    """Loadcell response data structure"""
    indicator_id: int
    value: float
    sign: str
    raw_data: str
    is_valid: bool = True
    
    def __post_init__(self):
        if self.sign not in ['+', '-']:
            self.is_valid = False


class ResponseBuffer:
    """Buffer for collecting response data"""
    
    def __init__(self, max_size: int = 1024):
        self.buffer = bytearray()
        self.max_size = max_size
    
    def add_data(self, data: bytes) -> None:
        """Add incoming data to buffer"""
        self.buffer.extend(data)
        
        # Prevent buffer overflow
        if len(self.buffer) > self.max_size:
            # Keep only the last portion of the buffer
            self.buffer = self.buffer[-self.max_size//2:]
            logger.warning("Response buffer overflow, truncated")
    
    def extract_response(self) -> Optional[bytes]:
        """
        Extract complete response from buffer
        
        Returns:
            Optional[bytes]: Complete response or None if no complete response found
        """
        STX = 0x02
        ETX = 0x03
        DATA_LENGTH_MIN = 5  # STX + ID + Sign + Digit + ETX
        
        if len(self.buffer) < DATA_LENGTH_MIN:
            return None
        
        # Find STX
        stx_index = self.buffer.find(STX)
        if stx_index == -1:
            # No STX found, clear buffer
            self.buffer.clear()
            return None
        
        # Remove data before STX
        if stx_index > 0:
            self.buffer = self.buffer[stx_index:]
        
        # Find ETX
        etx_index = self.buffer.find(ETX, 1)  # Start search after STX
        if etx_index == -1:
            # No ETX found, wait for more data
            return None
        
        # Extract response
        response = bytes(self.buffer[:etx_index + 1])
        self.buffer = self.buffer[etx_index + 1:]
        
        return response
    
    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer.clear()
    
    def __len__(self) -> int:
        """Return buffer length"""
        return len(self.buffer)