"""
Configuration Interface Protocols

Defines the interface contracts for configuration and profile preference implementations.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Protocol

# Local application imports
from domain.value_objects.hardware_config import HardwareConfig
from domain.value_objects.test_configuration import TestConfiguration


class Configuration(Protocol):
    """Configuration interface protocol"""

    async def load_profile(self, profile_name: str) -> TestConfiguration:
        """Load test configuration profile"""
        ...

    async def load_hardware_config(self) -> HardwareConfig:
        """Load hardware configuration"""
        ...

    async def list_available_profiles(self) -> List[str]:
        """List available configuration profiles"""
        ...

    async def load_dut_defaults(self, profile_name: Optional[str] = None) -> Dict[str, str]:
        """Load DUT default values"""
        ...

    async def save_profile(self, profile_name: str, test_config: TestConfiguration) -> None:
        """Save test configuration profile"""
        ...

    async def save_hardware_config(self, hardware_config: HardwareConfig) -> None:
        """Save hardware configuration"""
        ...

    async def save_dut_defaults(
        self, dut_defaults_data: Dict[str, Any], profile_name: str = "default"
    ) -> None:
        """Save DUT defaults configuration"""
        ...

    # Profile Preference Methods
    async def load_last_used_profile(self) -> Optional[str]:
        """Load the last used profile name"""
        ...

    async def save_last_used_profile(self, profile_name: str) -> None:
        """Save the last used profile name"""
        ...

    async def clear_preferences(self) -> None:
        """Clear all profile preferences"""
        ...
