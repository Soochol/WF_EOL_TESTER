"""
Application Configuration Value Object

Non-hardware application settings including application metadata,
services configuration, and logging configuration.
"""

# Future imports
from __future__ import annotations

# Standard library imports
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


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

    # Repository paths
    repository_results_path: str = "Logs/test_results/json"
    repository_raw_data_path: str = "Logs/EOL Force Test/raw_data"
    repository_summary_path: str = "Logs/EOL Force Test"
    repository_summary_filename: str = "test_summary.csv"
    repository_auto_save: bool = True

    # Configuration file paths
    config_application_path: str = "configuration/application.yaml"
    config_hardware_path: str = "configuration/hardware_config.yaml"
    config_profile_preference_path: str = "configuration/profile_preferences.json"
    config_test_profiles_dir: str = "configuration/test_profiles"
    config_heating_cooling_path: str = "configuration/heating_cooling_time_test.yaml"


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
            "gui": {"require_serial_number_popup": self.gui.require_serial_number_popup},
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
                    "results_path", "Logs/test_results/json"
                ),
                repository_raw_data_path=services_data.get("repository", {}).get(
                    "raw_data_path", "Logs/EOL Force Test/raw_data"
                ),
                repository_summary_path=services_data.get("repository", {}).get(
                    "summary_path", "Logs/EOL Force Test"
                ),
                repository_summary_filename=services_data.get("repository", {}).get(
                    "summary_filename", "test_summary.csv"
                ),
                repository_auto_save=services_data.get("repository", {}).get("auto_save", True),
                config_application_path=services_data.get("configuration", {}).get(
                    "application_path", "configuration/application.yaml"
                ),
                config_hardware_path=services_data.get("configuration", {}).get(
                    "hardware_path", "configuration/hardware_config.yaml"
                ),
                config_profile_preference_path=services_data.get("configuration", {}).get(
                    "profile_preference_path", "configuration/profile_preferences.json"
                ),
                config_test_profiles_dir=services_data.get("configuration", {}).get(
                    "test_profiles_dir", "configuration/test_profiles"
                ),
                config_heating_cooling_path=services_data.get("configuration", {}).get(
                    "heating_cooling_path", "configuration/heating_cooling_time_test.yaml"
                ),
            ),
            logging=LoggingConfig(level=logging_data.get("level", "INFO")),
            gui=GUIConfig(
                require_serial_number_popup=gui_data.get("require_serial_number_popup", True)
            ),
        )
