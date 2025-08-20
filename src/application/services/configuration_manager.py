"""
Configuration Manager

Centralized configuration management service that handles loading and 
validation of application and hardware configuration files.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from loguru import logger

from domain.value_objects.application_config import ApplicationConfig
from domain.value_objects.hardware_config import HardwareConfig


class ConfigPaths:
    """Configuration file paths constants"""

    # Default configuration file paths
    DEFAULT_APPLICATION_CONFIG = "configuration/application.yaml"
    DEFAULT_HARDWARE_CONFIG = "configuration/hardware.yaml"

    # Template file paths
    APPLICATION_TEMPLATE = "application.template.yaml"
    HARDWARE_TEMPLATE = "hardware.template.yaml"

    # Template directory path relative to this file
    TEMPLATE_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "templates"


class ConfigurationManager:
    """
    Centralized configuration management service.
    
    Handles loading, validation, and fallback for application and hardware configurations.
    Separates configuration loading concerns from the dependency injection container.
    """

    def __init__(
        self,
        application_config_path: Optional[str] = None,
        hardware_config_path: Optional[str] = None,
    ) -> None:
        """
        Initialize ConfigurationManager with optional custom paths.
        
        Args:
            application_config_path: Custom path to application config file
            hardware_config_path: Custom path to hardware config file
        """
        self.application_config_path = application_config_path or ConfigPaths.DEFAULT_APPLICATION_CONFIG
        self.hardware_config_path = hardware_config_path or ConfigPaths.DEFAULT_HARDWARE_CONFIG

    def load_all_configurations(self) -> Dict[str, Any]:
        """
        Load all configuration files and return combined configuration dictionary.
        
        Returns:
            Dictionary containing all loaded configurations
        """
        try:
            # Ensure config files exist
            self._ensure_config_files_exist()
            
            # Load application configuration
            app_config = self._load_application_config()
            
            # Load hardware configuration  
            hardware_config = self._load_hardware_config()
            
            # Combine configurations
            combined_config = app_config.copy()
            combined_config["hardware"] = hardware_config
            
            logger.info("All configurations loaded successfully")
            return combined_config
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
            logger.info("Using fallback default configurations")
            return self._get_fallback_configuration()

    def _load_application_config(self) -> Dict[str, Any]:
        """Load application configuration from file."""
        try:
            config_data = self._load_yaml_file(self.application_config_path)
            logger.info(f"Application configuration loaded from: {self.application_config_path}")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load application config: {e}")
            logger.info("Using default application configuration")
            return ApplicationConfig().to_dict()

    def _load_hardware_config(self) -> Dict[str, Any]:
        """Load hardware configuration from file."""
        try:
            config_data = self._load_yaml_file(self.hardware_config_path)
            logger.info(f"Hardware configuration loaded from: {self.hardware_config_path}")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load hardware config: {e}")
            logger.info("Using default hardware configuration")
            return HardwareConfig().to_dict()

    def _ensure_config_files_exist(self) -> None:
        """Ensure configuration files exist, create from templates if missing."""
        try:
            self._ensure_config_from_template(
                self.application_config_path, 
                ConfigPaths.APPLICATION_TEMPLATE
            )
            self._ensure_config_from_template(
                self.hardware_config_path,
                ConfigPaths.HARDWARE_TEMPLATE
            )
            logger.debug("Configuration files existence verified")
            
        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")
            raise

    def _ensure_config_from_template(self, target_path: str, template_name: str) -> None:
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

        template_path = ConfigPaths.TEMPLATE_DIR / template_name
        
        if not template_path.exists():
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")

        try:
            # Create target directory
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Read template content
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace timestamp placeholder
            content = content.replace("${timestamp}", datetime.now().isoformat())

            # Write to target file
            target_file.write_text(content, encoding="utf-8")
            logger.info(f"Created configuration from template: {target_path}")

        except Exception as e:
            logger.error(f"Failed to create config from template: {e}")
            raise

    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary containing loaded configuration
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if config_data is None:
                logger.warning(f"Empty YAML file: {file_path}")
                return {}

            return config_data

        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise

    def _get_fallback_configuration(self) -> Dict[str, Any]:
        """Get fallback configuration using in-memory defaults."""
        app_config = ApplicationConfig()
        hardware_config = HardwareConfig()
        
        combined_config = app_config.to_dict()
        combined_config["hardware"] = hardware_config.to_dict()
        
        logger.info("Fallback default configuration created")
        return combined_config

    @classmethod
    def create_default(cls) -> "ConfigurationManager":
        """Create ConfigurationManager with default paths."""
        return cls()

    @classmethod
    def create_with_paths(
        cls, 
        application_path: str, 
        hardware_path: str
    ) -> "ConfigurationManager":
        """
        Create ConfigurationManager with custom paths.
        
        Args:
            application_path: Custom application config path
            hardware_path: Custom hardware config path
            
        Returns:
            ConfigurationManager instance
        """
        return cls(application_path, hardware_path)

    def ensure_configurations_exist(self) -> None:
        """Public method to ensure configuration files exist."""
        try:
            self._ensure_config_files_exist()
            logger.info("Configuration files ensured successfully")

        except Exception as e:
            logger.error(f"Failed to ensure configuration files exist: {e}")
            logger.info("Application will continue with in-memory defaults")
