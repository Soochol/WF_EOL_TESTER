"""
Application Configuration Value Object

Non-hardware application settings including application metadata,
services configuration, and logging configuration.
"""

# Future imports
from __future__ import annotations

# Standard library imports
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# Project root path calculation (PyInstaller-aware)
def _get_project_root() -> Path:
    """
    Get project root directory with PyInstaller support.

    In development:
        Returns the actual project root (WF_EOL_TESTER/)

    In PyInstaller executable:
        Returns the directory containing the executable
        (e.g., C:/Program Files/WF_EOL_Tester/)
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        # sys.executable = C:/Program Files/WF_EOL_Tester/WF_EOL_Tester.exe
        # Return the directory containing the executable
        return Path(sys.executable).parent
    else:
        # Running as Python script (development)
        # __file__ = WF_EOL_TESTER/src/domain/value_objects/application_config.py
        return Path(__file__).parent.parent.parent.parent


PROJECT_ROOT = _get_project_root()

# Environment detection: Development vs Production
# Development: Running as Python script (sys.frozen = False)
# Production: Running as PyInstaller executable (sys.frozen = True)
IS_DEVELOPMENT = not getattr(sys, "frozen", False)

# Additional verification: If __file__ contains 'src', we're definitely in development
# This handles edge cases where sys.frozen might not be set correctly
if not IS_DEVELOPMENT:
    try:
        if __file__ and "src" in str(__file__):
            IS_DEVELOPMENT = True
            print("[WARNING] sys.frozen was True but __file__ indicates development mode. Forcing IS_DEVELOPMENT=True")
    except NameError:
        pass  # __file__ not defined (should never happen)

# Database directory selection based on environment
if IS_DEVELOPMENT:
    # Development mode: Store DB in project folder for easy access
    DATABASE_DIR = PROJECT_ROOT / "database"
    print(f"[DB CONFIG] Development mode - using database folder: {DATABASE_DIR}")
else:
    # Production mode: Store DB in LOCALAPPDATA (same location as logs)
    # Use LOCALAPPDATA instead of APPDATA to:
    # 1. Keep logs and database in the same directory
    # 2. Avoid roaming profile synchronization (local machine data only)
    localappdata = os.getenv("LOCALAPPDATA")

    if not localappdata:
        # Fallback: Use user home directory (should never happen on Windows)
        localappdata = str(Path.home() / "AppData" / "Local")

    APPDATA_DIR = Path(localappdata) / "WF EOL Tester"
    DATABASE_DIR = APPDATA_DIR
    print(f"[DB CONFIG] Production mode - using AppData folder: {DATABASE_DIR}")


# Configuration path constants (Single Source of Truth)
CONFIG_DIR = PROJECT_ROOT / "configuration"
CONFIG_TEST_PROFILES_DIR = CONFIG_DIR / "test_profiles"
CONFIG_APPLICATION_PATH = CONFIG_DIR / "application.yaml"
CONFIG_HARDWARE_PATH = CONFIG_DIR / "hardware_config.yaml"
CONFIG_PROFILE_PATH = CONFIG_DIR / "profile.yaml"
CONFIG_PROFILE_PREFERENCES_PATH = CONFIG_DIR / "profile_preferences.yaml"
CONFIG_DUT_DEFAULTS_PATH = CONFIG_DIR / "dut_defaults.yaml"
CONFIG_HEATING_COOLING_PATH = CONFIG_DIR / "heating_cooling_time_test.yaml"

# Logs path constants
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_TEST_RESULTS_JSON_DIR = LOGS_DIR / "test_results" / "json"
LOGS_EOL_RAW_DATA_DIR = LOGS_DIR / "EOL Force Test" / "raw_data"
LOGS_EOL_SUMMARY_DIR = LOGS_DIR / "EOL Force Test"


def ensure_project_directories():
    """
    Ensure all required project directories exist.

    This function runs at module load time and must not depend on logger
    as it executes before logger configuration in PyInstaller builds.
    """
    required_dirs = [
        CONFIG_DIR,
        CONFIG_TEST_PROFILES_DIR,
        LOGS_DIR,
        LOGS_TEST_RESULTS_JSON_DIR,
        LOGS_EOL_RAW_DATA_DIR,
        LOGS_EOL_SUMMARY_DIR,
        DATABASE_DIR,  # Database directory (development or AppData)
    ]

    for directory in required_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Silent fail - allow app to continue with whatever directories it can create
            pass


# Auto-create directories when module loads
ensure_project_directories()


@dataclass(frozen=True)
class ApplicationInfo:
    """Application metadata configuration"""

    name: str = "WF EOL Tester"
    version: str = "1.0.0"
    environment: str = "development"  # development, production, testing
    created_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate application info after initialization"""
        valid_environments = {"development", "production", "testing"}
        if self.environment not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")


@dataclass(frozen=True)
class ServicesConfigPaths:
    """Services configuration paths"""

    # Repository paths (absolute paths)
    repository_results_path: str = str(PROJECT_ROOT / "logs" / "test_results" / "json")
    repository_raw_data_path: str = str(PROJECT_ROOT / "logs" / "EOL Force Test" / "raw_data")
    repository_summary_path: str = str(PROJECT_ROOT / "logs" / "EOL Force Test")
    repository_summary_filename: str = "test_summary.csv"
    repository_auto_save: bool = True

    # Database path (hybrid: development=project/database, production=AppData)
    database_path: str = str(DATABASE_DIR / "test_data.db")

    # Configuration file paths (absolute paths)
    config_application_path: str = str(PROJECT_ROOT / "configuration" / "application.yaml")
    config_hardware_path: str = str(PROJECT_ROOT / "configuration" / "hardware_config.yaml")
    config_profile_preference_path: str = str(
        PROJECT_ROOT / "configuration" / "profile_preferences.yaml"
    )
    config_test_profiles_dir: str = str(PROJECT_ROOT / "configuration" / "test_profiles")
    config_heating_cooling_path: str = str(
        PROJECT_ROOT / "configuration" / "heating_cooling_time_test.yaml"
    )


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration"""

    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    def __post_init__(self) -> None:
        """Validate logging configuration"""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")


@dataclass(frozen=True)
class GUIConfig:
    """GUI configuration settings"""

    require_serial_number_popup: bool = True
    scaling_factor: float = 1.0  # UI scaling factor (0.5 ~ 2.0)

    def __post_init__(self) -> None:
        """Validate GUI configuration"""
        if not 0.5 <= self.scaling_factor <= 2.0:
            raise ValueError("scaling_factor must be between 0.5 and 2.0")


@dataclass(frozen=True)
class ApplicationConfig:
    """Complete application configuration (excluding hardware)"""

    application: ApplicationInfo = field(default_factory=ApplicationInfo)
    services: ServicesConfigPaths = field(default_factory=ServicesConfigPaths)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        config = {
            "application": {
                "name": self.application.name,
                "version": self.application.version,
                "environment": self.application.environment,
            },
            "services": {
                "repository": {
                    "results_path": self.services.repository_results_path,
                    "raw_data_path": self.services.repository_raw_data_path,
                    "summary_path": self.services.repository_summary_path,
                    "summary_filename": self.services.repository_summary_filename,
                    "auto_save": self.services.repository_auto_save,
                },
                "configuration": {
                    "application_path": self.services.config_application_path,
                    "hardware_path": self.services.config_hardware_path,
                    "profile_preference_path": self.services.config_profile_preference_path,
                    "test_profiles_dir": self.services.config_test_profiles_dir,
                    "heating_cooling_path": self.services.config_heating_cooling_path,
                },
            },
            "logging": {"level": self.logging.level},
            "gui": {
                "require_serial_number_popup": self.gui.require_serial_number_popup,
                "scaling_factor": self.gui.scaling_factor,
            },
        }

        # created_at은 있을 때만 포함
        if self.application.created_at:
            config["application"]["created_at"] = self.application.created_at

        return config

    def with_timestamp(self) -> "ApplicationConfig":
        """Return new instance with current timestamp"""
        return ApplicationConfig(
            application=ApplicationInfo(
                name=self.application.name,
                version=self.application.version,
                environment=self.application.environment,
                created_at=datetime.now().isoformat(),
            ),
            services=self.services,
            logging=self.logging,
            gui=self.gui,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationConfig":
        """Create ApplicationConfig from dictionary"""
        app_data = data.get("application", {})
        services_data = data.get("services", {})
        logging_data = data.get("logging", {})
        gui_data = data.get("gui", {})

        return cls(
            application=ApplicationInfo(
                name=app_data.get("name", "WF EOL Tester"),
                version=app_data.get("version", "1.0.0"),
                environment=app_data.get("environment", "development"),
                created_at=app_data.get("created_at"),
            ),
            services=ServicesConfigPaths(
                repository_results_path=services_data.get("repository", {}).get(
                    "results_path", str(PROJECT_ROOT / "logs" / "test_results" / "json")
                ),
                repository_raw_data_path=services_data.get("repository", {}).get(
                    "raw_data_path", str(PROJECT_ROOT / "logs" / "EOL Force Test" / "raw_data")
                ),
                repository_summary_path=services_data.get("repository", {}).get(
                    "summary_path", str(PROJECT_ROOT / "logs" / "EOL Force Test")
                ),
                repository_summary_filename=services_data.get("repository", {}).get(
                    "summary_filename", "test_summary.csv"
                ),
                repository_auto_save=services_data.get("repository", {}).get("auto_save", True),
                config_application_path=services_data.get("configuration", {}).get(
                    "application_path", str(PROJECT_ROOT / "configuration" / "application.yaml")
                ),
                config_hardware_path=services_data.get("configuration", {}).get(
                    "hardware_path", str(PROJECT_ROOT / "configuration" / "hardware_config.yaml")
                ),
                config_profile_preference_path=services_data.get("configuration", {}).get(
                    "profile_preference_path",
                    str(PROJECT_ROOT / "configuration" / "profile_preferences.yaml"),
                ),
                config_test_profiles_dir=services_data.get("configuration", {}).get(
                    "test_profiles_dir", str(PROJECT_ROOT / "configuration" / "test_profiles")
                ),
                config_heating_cooling_path=services_data.get("configuration", {}).get(
                    "heating_cooling_path",
                    str(PROJECT_ROOT / "configuration" / "heating_cooling_time_test.yaml"),
                ),
            ),
            logging=LoggingConfig(level=logging_data.get("level", "INFO")),
            gui=GUIConfig(
                require_serial_number_popup=gui_data.get("require_serial_number_popup", True),
                scaling_factor=gui_data.get("scaling_factor", 1.0),
            ),
        )
