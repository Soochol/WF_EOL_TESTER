"""
Configuration Interface Protocol

Defines the interface contract for configuration implementations.
"""

from typing import Protocol, List, Dict, Any, Optional

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
    
    async def load_hardware_model(self) -> HardwareConfig:
        """Load hardware model configuration"""
        ...
    
    async def list_available_profiles(self) -> List[str]:
        """List available configuration profiles"""
        ...
    
    async def load_dut_defaults(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Load DUT default values"""
        ...
    
    async def save_profile(self, profile_name: str, test_config: TestConfiguration) -> None:
        """Save test configuration profile"""
        ...
    
    async def save_hardware_config(self, hardware_config: HardwareConfig) -> None:
        """Save hardware configuration"""
        ...
    
    async def save_hardware_model(self, hardware_config: HardwareConfig) -> None:
        """Save hardware model configuration"""
        ...
    
    async def save_dut_defaults(self, dut_defaults_data: Dict[str, Any], profile_name: str = "default") -> None:
        """Save DUT defaults configuration"""
        ...