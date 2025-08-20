"""
Application Container

Main dependency injection container for the WF EOL Tester application.
Manages all application services, use cases, and hardware dependencies.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from dependency_injector import containers, providers
from loguru import logger

# Application Layer Imports
from application.services.configuration_service import ConfigurationService
from application.services.configuration_validator import ConfigurationValidator
from application.services.exception_handler import ExceptionHandler
from application.services.hardware_service_facade import HardwareServiceFacade
from application.services.repository_service import RepositoryService
from application.services.test_result_evaluator import TestResultEvaluator
from application.use_cases.eol_force_test import EOLForceTestUseCase
from application.use_cases.robot_home import RobotHomeUseCase

# Infrastructure Layer Imports
from infrastructure.factories.hardware_factory import HardwareFactory
from infrastructure.implementation.configuration.json_profile_preference import (
    JsonProfilePreference,
)
from infrastructure.implementation.configuration.yaml_configuration import (
    YamlConfiguration,
)
from infrastructure.implementation.repositories.json_result_repository import (
    JsonResultRepository,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Main application container for dependency injection.

    Provides centralized configuration and dependency management for:
    - Configuration services
    - Hardware services
    - Repository services
    - Use cases and business logic
    """

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    config = providers.Configuration()

    # ============================================================================
    # HARDWARE LAYER
    # ============================================================================

    hardware = providers.Container(
        HardwareFactory,
        config=config.hardware
    )

    # ============================================================================
    # INFRASTRUCTURE SERVICES
    # ============================================================================

    # Configuration Infrastructure
    yaml_configuration = providers.Singleton(YamlConfiguration)

    json_profile_preference = providers.Singleton(JsonProfilePreference)

    # Repository Infrastructure
    json_result_repository = providers.Singleton(
        JsonResultRepository,
        data_dir=config.services.repository.results_path,
        auto_save=config.services.repository.auto_save,
    )

    # ============================================================================
    # APPLICATION SERVICES
    # ============================================================================

    # Configuration Services
    configuration_service = providers.Singleton(
        ConfigurationService,
        configuration=yaml_configuration,
        profile_preference=json_profile_preference,
    )

    configuration_validator = providers.Singleton(ConfigurationValidator)

    # Business Services
    repository_service = providers.Singleton(
        RepositoryService,
        test_repository=json_result_repository
    )

    exception_handler = providers.Singleton(ExceptionHandler)

    test_result_evaluator = providers.Singleton(TestResultEvaluator)

    # Hardware Service Facade
    hardware_service_facade = providers.Singleton(
        HardwareServiceFacade,
        robot_service=hardware.robot_service,
        mcu_service=hardware.mcu_service,
        loadcell_service=hardware.loadcell_service,
        power_service=hardware.power_service,
        digital_io_service=hardware.digital_io_service,
    )

    # ============================================================================
    # USE CASES
    # ============================================================================

    # EOL Force Test Use Case
    eol_force_test_use_case = providers.Singleton(
        EOLForceTestUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
        configuration_validator=configuration_validator,
        test_result_evaluator=test_result_evaluator,
        repository_service=repository_service,
        exception_handler=exception_handler,
    )

    # Robot Home Use Case
    robot_home_use_case = providers.Factory(
        RobotHomeUseCase,
        hardware_services=hardware_service_facade,
        configuration_service=configuration_service,
    )

    # ============================================================================
    # CONFIGURATION MANAGEMENT METHODS
    # ============================================================================

    @classmethod
    def load_config_safely(
        cls,
        config_path: str = "configuration/application.yaml"
    ) -> 'ApplicationContainer':
        """
        Create container and load configuration safely with fallback.

        Args:
            config_path: Path to configuration file

        Returns:
            Configured ApplicationContainer instance
        """
        # Ensure config file exists
        cls.ensure_config_exists(config_path)

        # Create container instance
        container = cls()

        # Load configuration with error handling
        config_file = Path(config_path)

        if config_file.exists():
            try:
                container.config.from_yaml(config_path)
                logger.info(f"Configuration loaded from: {config_path}")

            except Exception as e:
                logger.error(f"Failed to parse configuration from {config_path}: {e}")
                logger.info("Using in-memory default configuration due to parse error")
                cls._apply_fallback_config(container)
        else:
            logger.warning(f"Configuration file does not exist: {config_path}")
            logger.info("Using in-memory default configuration")
            cls._apply_fallback_config(container)

        return container

    @classmethod
    def ensure_config_exists(
        cls,
        config_path: str = "configuration/application.yaml"
    ) -> None:
        """
        Ensure configuration file exists, create from template if missing.

        Args:
            config_path: Path to configuration file
        """
        config_file = Path(config_path)

        if config_file.exists():
            logger.debug(f"Configuration file found: {config_path}")
            return

        logger.warning(f"Configuration file not found: {config_path}")

        try:
            # Create configuration directory
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Try to copy from template
            template_path = (
                Path(__file__).parent.parent.parent /
                "infrastructure" / "templates" / "default_application.yaml"
            )

            if template_path.exists():
                cls._create_from_template(template_path, config_file)
            else:
                logger.error(f"Template file not found: {template_path}")
                cls._create_minimal_config(config_file)

            logger.info(f"Created default configuration file: {config_path}")

        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            logger.info("Application will continue with in-memory defaults")

    @classmethod
    def _create_from_template(cls, template_path: Path, config_file: Path) -> None:
        """Create configuration file from template."""
        # Copy template to config location
        shutil.copy2(template_path, config_file)

        # Replace timestamp placeholder
        content = config_file.read_text()
        content = content.replace("${timestamp}", datetime.now().isoformat())
        config_file.write_text(content)

    @classmethod
    def _create_minimal_config(cls, config_file: Path) -> None:
        """Create minimal configuration if template is not available."""
        minimal_config = """# Minimal default configuration
application:
  name: "WF EOL Tester"
  version: "1.0.0"
  environment: "development"

hardware:
  robot:
    model: "mock"
    axis_id: 0
    irq_no: 7
  power:
    model: "mock"
    host: "localhost"
    port: 8080
    channel: 1
    timeout: 10.0
  mcu:
    model: "mock"
    port: "COM3"
    baudrate: 115200
    timeout: 5.0
    bytesize: 8
    stopbits: 1
    parity: null
  loadcell:
    model: "mock"
    port: "COM4"
    baudrate: 9600
    timeout: 3.0
    bytesize: 8
    stopbits: 1
    parity: null
    indicator_id: 1
  digital_io:
    model: "mock"

services:
  repository:
    results_path: "ResultsLog"
    auto_save: true

logging:
  level: "INFO"
"""
        try:
            config_file.write_text(minimal_config)
            logger.info(f"Created minimal configuration file: {config_file}")
        except Exception as e:
            logger.error(f"Failed to create minimal configuration: {e}")

    @classmethod
    def _apply_fallback_config(cls, container: 'ApplicationContainer') -> None:
        """Apply fallback configuration to container."""
        fallback_config = {
            "application": {
                "name": "WF EOL Tester",
                "version": "1.0.0",
                "environment": "development"
            },
            "hardware": {
                "robot": {
                    "model": "mock",
                    "axis_id": 0,
                    "irq_no": 7
                },
                "power": {
                    "model": "mock",
                    "host": "localhost",
                    "port": 8080,
                    "channel": 1,
                    "timeout": 10.0
                },
                "mcu": {
                    "model": "mock",
                    "port": "COM3",
                    "baudrate": 115200,
                    "timeout": 5.0,
                    "bytesize": 8,
                    "stopbits": 1,
                    "parity": None
                },
                "loadcell": {
                    "model": "mock",
                    "port": "COM4",
                    "baudrate": 9600,
                    "timeout": 3.0,
                    "bytesize": 8,
                    "stopbits": 1,
                    "parity": None,
                    "indicator_id": 1
                },
                "digital_io": {
                    "model": "mock"
                }
            },
            "services": {
                "repository": {
                    "results_path": "ResultsLog",
                    "auto_save": True
                }
            },
            "logging": {
                "level": "INFO"
            }
        }

        container.config.from_dict(fallback_config)
        logger.info("In-memory default configuration applied successfully")
