"""
Hardware Status Enumeration

Defines the possible states of hardware devices in the EOL testing system.
Migrated from infrastructure layer to maintain business logic in domain.
"""

from enum import Enum


class HardwareStatus(Enum):
    """Hardware connection status enumeration"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value

    @property
    def is_connected(self) -> bool:
        """Check if hardware is in connected state"""
        return self == HardwareStatus.CONNECTED

    @property
    def is_operational(self) -> bool:
        """Check if hardware can perform operations"""
        return self in (HardwareStatus.CONNECTED,)

    @property
    def requires_attention(self) -> bool:
        """Check if hardware status requires attention"""
        return self in (HardwareStatus.ERROR, HardwareStatus.UNKNOWN)
