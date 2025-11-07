"""
VISA Communication Driver

PyVISA-based instrument communication supporting:
- TCP/IP (SOCKET and INSTR protocols)
- USB-TMC (Test & Measurement Class)
- GPIB (IEEE 488.2)
"""

# Local application imports
from driver.visa.constants import (
    INTERFACE_GPIB,
    INTERFACE_TCP,
    INTERFACE_USB,
    WT1800E_MODEL_CODE,
    YOKOGAWA_VENDOR_ID,
)
from driver.visa.exceptions import (
    VISACommunicationError,
    VISAConnectionError,
    VISAError,
    VISAResourceNotFoundError,
    VISATimeoutError,
)
from driver.visa.visa_communication import VISACommunication


__all__ = [
    # Communication class
    "VISACommunication",
    # Interface types
    "INTERFACE_TCP",
    "INTERFACE_USB",
    "INTERFACE_GPIB",
    # Device identifiers
    "YOKOGAWA_VENDOR_ID",
    "WT1800E_MODEL_CODE",
    # Exceptions
    "VISAError",
    "VISAConnectionError",
    "VISACommunicationError",
    "VISATimeoutError",
    "VISAResourceNotFoundError",
]
