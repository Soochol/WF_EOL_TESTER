"""
Application Configuration Value Object

Non-hardware application settings including application metadata,
services configuration, and logging configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


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
class ServicesConfig:
    """Services configuration"""
    repository_results_path: str = "Logs/test_results/json"
    repository_auto_save: bool = True


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
class ApplicationConfig:
    """Complete application configuration (excluding hardware)"""
    application: ApplicationInfo = field(default_factory=ApplicationInfo)
    services: ServicesConfig = field(default_factory=ServicesConfig)  
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        config = {
            "application": {
                "name": self.application.name,
                "version": self.application.version,
                "environment": self.application.environment
            },
            "services": {
                "repository": {
                    "results_path": self.services.repository_results_path,
                    "auto_save": self.services.repository_auto_save
                }
            },
            "logging": {
                "level": self.logging.level
            }
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
                created_at=datetime.now().isoformat()
            ),
            services=self.services,
            logging=self.logging
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationConfig":
        """Create ApplicationConfig from dictionary"""
        app_data = data.get("application", {})
        services_data = data.get("services", {})
        logging_data = data.get("logging", {})
        
        return cls(
            application=ApplicationInfo(
                name=app_data.get("name", "WF EOL Tester"),
                version=app_data.get("version", "1.0.0"),
                environment=app_data.get("environment", "development"),
                created_at=app_data.get("created_at")
            ),
            services=ServicesConfig(
                repository_results_path=services_data.get("repository", {}).get("results_path", "Logs/test_results/json"),
                repository_auto_save=services_data.get("repository", {}).get("auto_save", True)
            ),
            logging=LoggingConfig(
                level=logging_data.get("level", "INFO")
            )
        )