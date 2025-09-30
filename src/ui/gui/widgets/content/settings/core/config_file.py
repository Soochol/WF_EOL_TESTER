"""
Configuration data structures and models.

Contains dataclasses and models for representing configuration files,
values, and their metadata.
"""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Local application imports
from domain.value_objects.application_config import (
    CONFIG_APPLICATION_PATH,
    CONFIG_HARDWARE_PATH,
    CONFIG_HEATING_COOLING_PATH,
    CONFIG_PROFILE_PATH,
    CONFIG_DUT_DEFAULTS_PATH,
    CONFIG_TEST_PROFILES_DIR,
)


@dataclass
class ConfigValue:
    """Configuration value with metadata"""

    key: str
    value: Any
    data_type: str
    description: str = ""
    category: str = ""
    file_path: str = ""
    is_modified: bool = False
    validation_rule: Optional[str] = None
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    is_valid: bool = True
    validation_error: str = ""


@dataclass
class ConfigFile:
    """Configuration file information"""

    name: str
    path: str
    description: str
    data: Dict[str, Any]
    last_loaded: Optional[datetime] = None


class ConfigPaths:
    """Configuration file path definitions"""

    @staticmethod
    def get_default_paths() -> Dict[str, str]:
        """Get default configuration file paths"""
        return {
            "Application": str(CONFIG_APPLICATION_PATH),
            "Hardware": str(CONFIG_HARDWARE_PATH),
            "Heating/Cooling Test": str(CONFIG_HEATING_COOLING_PATH),
            "Profile Management": str(CONFIG_PROFILE_PATH),
            "DUT Defaults": str(CONFIG_DUT_DEFAULTS_PATH),
        }

    @staticmethod
    def get_test_profile_path(profile_name: str) -> str:
        """Get path for a specific test profile"""
        return str(CONFIG_TEST_PROFILES_DIR / f"{profile_name}.yaml")
