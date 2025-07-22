"""
Application Factory

Factory class for creating and configuring the complete application.
"""

import json
import os
from typing import Dict, Any, Optional
from loguru import logger

from .dependency_injection import DependencyContainer
from ..presentation.cli.eol_test_cli import EOLTestCLI
from ..presentation.cli.hardware_cli import HardwareCLI
from ..presentation.api.eol_test_api import EOLTestAPI
from ..presentation.api.hardware_api import HardwareAPI


class ApplicationFactory:
    """Factory for creating and configuring the EOL Tester application"""
    
    @staticmethod
    def create_application(
        config_file: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None
    ) -> DependencyContainer:
        """
        Create and configure complete application
        
        Args:
            config_file: Path to configuration file (optional)
            config_dict: Configuration dictionary (optional)
            
        Returns:
            Configured dependency container
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        logger.info("Creating EOL Tester application")
        
        # Load configuration
        configuration = ApplicationFactory._load_configuration(config_file, config_dict)
        
        # Create and initialize dependency container
        container = DependencyContainer(configuration)
        container.initialize_all_layers()
        
        logger.info("EOL Tester application created successfully")
        return container
    
    @staticmethod
    def create_cli_application(
        config_file: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Create CLI application with all CLI interfaces
        
        Args:
            config_file: Path to configuration file (optional)
            config_dict: Configuration dictionary (optional)
            
        Returns:
            Tuple of (eol_test_cli, hardware_cli, container)
        """
        logger.info("Creating CLI application")
        
        container = ApplicationFactory.create_application(config_file, config_dict)
        
        # Create CLI interfaces
        eol_test_cli = container.resolve(EOLTestCLI)
        hardware_cli = container.resolve(HardwareCLI)
        
        logger.info("CLI application created successfully")
        return eol_test_cli, hardware_cli, container
    
    @staticmethod
    def create_api_application(
        config_file: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Create API application with all API interfaces
        
        Args:
            config_file: Path to configuration file (optional)
            config_dict: Configuration dictionary (optional)
            
        Returns:
            Tuple of (eol_test_api, hardware_api, container)
        """
        logger.info("Creating API application")
        
        container = ApplicationFactory.create_application(config_file, config_dict)
        
        # Create API interfaces
        eol_test_api = container.resolve(EOLTestAPI)
        hardware_api = container.resolve(HardwareAPI)
        
        logger.info("API application created successfully")
        return eol_test_api, hardware_api, container
    
    @staticmethod
    def _load_configuration(
        config_file: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load application configuration
        
        Args:
            config_file: Path to configuration file (optional)
            config_dict: Configuration dictionary (optional)
            
        Returns:
            Merged configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        configuration = {}
        
        # Load from file if provided
        if config_file:
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                configuration.update(file_config)
                logger.info(f"Loaded configuration from {config_file}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in configuration file: {e}")
            except Exception as e:
                raise ValueError(f"Error loading configuration file: {e}")
        
        # Merge with dictionary config
        if config_dict:
            configuration.update(config_dict)
            logger.info("Merged configuration from dictionary")
        
        # Load from environment variables
        env_config = ApplicationFactory._load_environment_configuration()
        if env_config:
            ApplicationFactory._deep_merge(configuration, env_config)
            logger.info("Merged configuration from environment variables")
        
        return configuration
    
    @staticmethod
    def _load_environment_configuration() -> Dict[str, Any]:
        """
        Load configuration from environment variables
        
        Returns:
            Configuration dictionary from environment
        """
        env_config = {}
        
        # Hardware configuration
        if os.getenv('EOL_LOADCELL_PORT'):
            env_config.setdefault('hardware', {}).setdefault('loadcell', {}).setdefault('connection', {})['port'] = os.getenv('EOL_LOADCELL_PORT')
        
        if os.getenv('EOL_LOADCELL_BAUDRATE'):
            try:
                baudrate = int(os.getenv('EOL_LOADCELL_BAUDRATE'))
                env_config.setdefault('hardware', {}).setdefault('loadcell', {}).setdefault('connection', {})['baudrate'] = baudrate
            except ValueError:
                logger.warning(f"Invalid baudrate in environment: {os.getenv('EOL_LOADCELL_BAUDRATE')}")
        
        if os.getenv('EOL_POWER_HOST'):
            env_config.setdefault('hardware', {}).setdefault('power_supply', {}).setdefault('connection', {})['host'] = os.getenv('EOL_POWER_HOST')
        
        if os.getenv('EOL_POWER_PORT'):
            try:
                port = int(os.getenv('EOL_POWER_PORT'))
                env_config.setdefault('hardware', {}).setdefault('power_supply', {}).setdefault('connection', {})['port'] = port
            except ValueError:
                logger.warning(f"Invalid power port in environment: {os.getenv('EOL_POWER_PORT')}")
        
        # Application configuration
        if os.getenv('EOL_TEST_TIMEOUT'):
            try:
                timeout = int(os.getenv('EOL_TEST_TIMEOUT'))
                env_config.setdefault('application', {})['test_timeout'] = timeout
            except ValueError:
                logger.warning(f"Invalid test timeout in environment: {os.getenv('EOL_TEST_TIMEOUT')}")
        
        if os.getenv('EOL_AUTO_SAVE'):
            auto_save = os.getenv('EOL_AUTO_SAVE').lower() in ('true', '1', 'yes', 'on')
            env_config.setdefault('application', {})['auto_save'] = auto_save
        
        return env_config
    
    @staticmethod
    def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge source dictionary into target dictionary
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                ApplicationFactory._deep_merge(target[key], value)
            else:
                target[key] = value
    
    @staticmethod
    def create_development_configuration() -> Dict[str, Any]:
        """
        Create development configuration
        
        Returns:
            Development configuration dictionary
        """
        return {
            'hardware': {
                'loadcell': {
                    'type': 'bs205',
                    'connection': {
                        'port': 'COM3',
                        'baudrate': 9600,
                        'timeout': 2.0
                    }
                },
                'power_supply': {
                    'type': 'oda',
                    'connection': {
                        'host': '192.168.1.100',
                        'port': 8080,
                        'timeout': 10.0
                    }
                }
            },
            'application': {
                'test_timeout': 600,  # Longer timeout for development
                'measurement_precision': 4,  # Higher precision for development
                'auto_save': True,
                'debug_mode': True
            },
            'logging': {
                'level': 'DEBUG',
                'file_logging': True,
                'console_logging': True
            }
        }
    
    @staticmethod
    def create_production_configuration() -> Dict[str, Any]:
        """
        Create production configuration
        
        Returns:
            Production configuration dictionary
        """
        return {
            'hardware': {
                'loadcell': {
                    'type': 'bs205',
                    'connection': {
                        'port': 'COM1',
                        'baudrate': 9600,
                        'timeout': 1.0
                    }
                },
                'power_supply': {
                    'type': 'oda',
                    'connection': {
                        'host': '192.168.1.10',
                        'port': 8080,
                        'timeout': 5.0
                    }
                }
            },
            'application': {
                'test_timeout': 300,
                'measurement_precision': 3,
                'auto_save': True,
                'debug_mode': False
            },
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'console_logging': False
            }
        }
    
    @staticmethod
    def create_test_configuration() -> Dict[str, Any]:
        """
        Create test configuration with mock hardware
        
        Returns:
            Test configuration dictionary
        """
        return {
            'hardware': {
                'loadcell': {
                    'type': 'mock',
                    'connection': {
                        'mock_values': [10.5, 10.6, 10.4, 10.7, 10.3]
                    }
                },
                'power_supply': {
                    'type': 'mock',
                    'connection': {
                        'mock_voltage': 12.0,
                        'mock_current': 1.5
                    }
                }
            },
            'application': {
                'test_timeout': 60,  # Shorter timeout for tests
                'measurement_precision': 2,
                'auto_save': False,
                'debug_mode': True
            },
            'logging': {
                'level': 'WARNING',
                'file_logging': False,
                'console_logging': True
            }
        }
    
    @staticmethod
    def save_configuration(config: Dict[str, Any], file_path: str) -> None:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary
            file_path: Path to save configuration file
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise IOError(f"Cannot save configuration to {file_path}: {e}")