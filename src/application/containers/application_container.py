"""
Application Container

Main dependency injection container for the WF EOL Tester application.
Manages all application services, use cases, and hardware dependencies.
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

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
from domain.value_objects.application_config import ApplicationConfig

# Domain Layer Imports
from domain.value_objects.hardware_config import HardwareConfig

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

    hardware = providers.Container(HardwareFactory, config=config.hardware)

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
        RepositoryService, test_repository=json_result_repository
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
        application_config_path: str = "configuration/application.yaml",
        hardware_config_path: str = "configuration/hardware.yaml"
    ) -> "ApplicationContainer":
        """
        Create container and load configuration safely with fallback.

        Args:
            application_config_path: Path to application configuration file
            hardware_config_path: Path to hardware configuration file

        Returns:
            Configured ApplicationContainer instance
        """
        container = cls()

        try:
            # Ensure config files exist (create from templates if needed)
            cls._ensure_config_from_template(application_config_path, "application.template.yaml")
            cls._ensure_config_from_template(hardware_config_path, "hardware.template.yaml")

            # Load application configuration
            try:
                app_config_data = cls._load_yaml_file(application_config_path)
                container.config.from_dict(app_config_data)
                logger.info(f"Application configuration loaded from: {application_config_path}")
            except Exception as e:
                logger.error(f"Failed to load application config: {e}")
                logger.info("Using default application configuration")
                default_app = ApplicationConfig()
                container.config.from_dict(default_app.to_dict())

            # Load hardware configuration
            try:
                hw_config_data = cls._load_yaml_file(hardware_config_path)
                container.config.from_dict({"hardware": hw_config_data})
                logger.info(f"Hardware configuration loaded from: {hardware_config_path}")
            except Exception as e:
                logger.error(f"Failed to load hardware config: {e}")
                logger.info("Using default hardware configuration")
                default_hw = HardwareConfig()
                container.config.from_dict({"hardware": default_hw.to_dict()})

            logger.info("Configuration loading completed")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using in-memory default configuration")
            cls._apply_fallback_config(container)

        return container

    @classmethod
    def ensure_config_exists(
        cls, 
        application_config_path: str = "configuration/application.yaml",
        hardware_config_path: str = "configuration/hardware.yaml"
    ) -> None:
        """
        Ensure configuration files exist, create from templates if missing.

        Args:
            application_config_path: Path to application configuration file
            hardware_config_path: Path to hardware configuration file
        """
        try:
            # Create config files from templates if they don't exist
            cls._ensure_config_from_template(application_config_path, "application.template.yaml")
            cls._ensure_config_from_template(hardware_config_path, "hardware.template.yaml")
            
            logger.info("Configuration files ensured successfully")

        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")
            logger.info("Application will continue with in-memory defaults")

    @classmethod
    def _apply_fallback_config(cls, container: "ApplicationContainer") -> None:
        """Apply fallback configuration to container."""
        # Use default configurations separately
        app_config = ApplicationConfig()
        hardware_config = HardwareConfig()
        
        # Apply configurations separately
        container.config.from_dict(app_config.to_dict())
        container.config.from_dict({"hardware": hardware_config.to_dict()})
        
        logger.info("In-memory default configuration applied successfully")

    @classmethod
    def _ensure_config_from_template(cls, target_path: str, template_name: str) -> None:
        """
        Create configuration file from template if it doesn't exist.
        
        Args:
            target_path: Path where config file should be created
            template_name: Name of template file to use
        """
        target_file = Path(target_path)
        
        if target_file.exists():
            logger.debug(f"Configuration file already exists: {target_path}")
            return
            
        # Get template path
        template_path = Path(__file__).parent.parent.parent / "infrastructure" / "templates" / template_name
        
        if not template_path.exists():
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        try:
            # Create target directory
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read template content
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace timestamp placeholder
            content = content.replace("${timestamp}", datetime.now().isoformat())
            
            # Write to target file
            target_file.write_text(content, encoding='utf-8')
            logger.info(f"Created configuration from template: {target_path}")
            
        except Exception as e:
            logger.error(f"Failed to create config from template: {e}")
            raise

    @classmethod
    def _load_yaml_file(cls, file_path: str) -> dict:
        """
        Load YAML configuration file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary containing loaded configuration
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            if config_data is None:
                logger.warning(f"Empty YAML file: {file_path}")
                return {}
                
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise
