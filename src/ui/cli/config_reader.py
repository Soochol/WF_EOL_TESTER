"""
CLI Configuration Reader

Provides configuration reading capabilities for CLI slash commands.
Supports YAML and JSON formats with fallback to default values.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from loguru import logger


class CLIConfigError(Exception):
    """Exception raised for CLI configuration errors"""
    pass


class CLIConfigReader:
    """Configuration reader for CLI commands with fallback support"""
    
    # Default configuration structure that matches the expected format
    DEFAULT_CONFIG = {
        "cli_config": {
            "hardware_mode": "mock",  # Default to mock mode for safety
            "commands": {
                "robot": {
                    "connection": {
                        "axis_id": 0,
                        "irq_no": 7
                    },
                    "defaults": {
                        "velocity": 200.0,
                        "acceleration": 1000.0,
                        "deceleration": 1000.0
                    }
                },
                "mcu": {
                    "connection": {
                        "port": "/dev/ttyUSB1",
                        "baudrate": 115200,
                        "timeout": 2.0,
                        "bytesize": 8,
                        "stopbits": 1,
                        "parity": None
                    },
                    "defaults": {
                        "temperature_range": [20.0, 100.0],
                        "fan_speed_range": [0, 100]
                    }
                },
                "loadcell": {
                    "connection": {
                        "port": "/dev/ttyUSB0",
                        "baudrate": 9600,
                        "timeout": 1.0,
                        "bytesize": 8,
                        "stopbits": 1,
                        "parity": "even",
                        "indicator_id": 1
                    },
                    "defaults": {
                        "force_range": [-1000.0, 1000.0],
                        "calibration_timeout": 10.0,
                        "monitor_refresh_rate": 0.5
                    }
                },
                "power": {
                    "connection": {
                        "host": "192.168.1.100",
                        "port": 5025,
                        "timeout": 5.0,
                        "channel": 1
                    },
                    "defaults": {
                        "voltage_range": [0.0, 30.0],
                        "current_limit_range": [0.0, 5.0],
                        "output_enabled": False
                    }
                }
            },
            "preferences": {
                "auto_connect": False,
                "show_progress": True,
                "verbose_errors": True,
                "confirmation_required": True,
                "retry_attempts": 3,
                "command_timeout": 30.0
            },
            "display": {
                "refresh_rate": 2.0,
                "decimal_precision": 3,
                "show_timestamps": True,
                "color_theme": "default"
            }
        }
    }
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration reader
        
        Args:
            config_path: Path to configuration file. If None, searches standard locations
        """
        self._config_path = Path(config_path) if config_path else None
        self._config_data: Optional[Dict[str, Any]] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file with fallback to defaults"""
        config_paths = self._get_config_paths()
        
        for path in config_paths:
            try:
                if path.exists():
                    logger.info(f"Loading CLI configuration from: {path}")
                    self._config_data = self._read_config_file(path)
                    logger.info("CLI configuration loaded successfully")
                    return
            except Exception as e:
                logger.warning(f"Failed to load config from {path}: {e}")
                continue
        
        # If no config file found, use defaults
        logger.info("No CLI configuration file found, using defaults")
        self._config_data = self.DEFAULT_CONFIG.copy()
    
    def _get_config_paths(self) -> list[Path]:
        """Get ordered list of configuration file paths to try"""
        paths = []
        
        # If specific path provided, try that first
        if self._config_path:
            paths.append(self._config_path)
        
        # Standard locations
        current_dir = Path.cwd()
        config_dir = current_dir / "configuration"
        
        # Try different file names and formats
        filenames = [
            "cli_commands.yaml",
            "cli_commands.yml", 
            "cli_config.yaml",
            "cli_config.yml",
            "cli_commands.json",
            "cli_config.json"
        ]
        
        for filename in filenames:
            paths.append(config_dir / filename)
            paths.append(current_dir / filename)
        
        return paths
    
    def _read_config_file(self, path: Path) -> Dict[str, Any]:
        """Read configuration file based on extension"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    raise CLIConfigError(f"Unsupported config file format: {path.suffix}")
        except Exception as e:
            raise CLIConfigError(f"Failed to read config file {path}: {e}") from e
    
    def get_command_config(self, command: str) -> Dict[str, Any]:
        """Get configuration for a specific command
        
        Args:
            command: Command name (robot, mcu, loadcell, power)
            
        Returns:
            Command configuration dictionary
            
        Raises:
            CLIConfigError: If command not found in configuration
        """
        if not self._config_data:
            raise CLIConfigError("Configuration not loaded")
        
        cli_config = self._config_data.get("cli_config", {})
        commands = cli_config.get("commands", {})
        
        if command not in commands:
            logger.warning(f"Command '{command}' not found in configuration, using defaults")
            # Return defaults for the command if available
            default_commands = self.DEFAULT_CONFIG["cli_config"]["commands"]
            if command in default_commands:
                return default_commands[command].copy()
            else:
                raise CLIConfigError(f"No configuration available for command: {command}")
        
        return commands[command].copy()
    
    def get_connection_params(self, command: str) -> Dict[str, Any]:
        """Get connection parameters for a specific command
        
        Args:
            command: Command name (robot, mcu, loadcell, power)
            
        Returns:
            Connection parameters dictionary
        """
        command_config = self.get_command_config(command)
        return command_config.get("connection", {})
    
    def get_command_defaults(self, command: str) -> Dict[str, Any]:
        """Get default values for a specific command
        
        Args:
            command: Command name (robot, mcu, loadcell, power)
            
        Returns:
            Default values dictionary
        """
        command_config = self.get_command_config(command)
        return command_config.get("defaults", {})
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get global CLI preferences
        
        Returns:
            Preferences dictionary
        """
        if not self._config_data:
            return self.DEFAULT_CONFIG["cli_config"]["preferences"].copy()
        
        cli_config = self._config_data.get("cli_config", {})
        return cli_config.get("preferences", self.DEFAULT_CONFIG["cli_config"]["preferences"]).copy()
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get display settings
        
        Returns:
            Display settings dictionary
        """
        if not self._config_data:
            return self.DEFAULT_CONFIG["cli_config"]["display"].copy()
        
        cli_config = self._config_data.get("cli_config", {})
        return cli_config.get("display", self.DEFAULT_CONFIG["cli_config"]["display"]).copy()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value or default
        """
        preferences = self.get_preferences()
        return preferences.get(key, default)
    
    def get_display_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific display setting value
        
        Args:
            key: Display setting key
            default: Default value if key not found
            
        Returns:
            Display setting value or default
        """
        display_settings = self.get_display_settings()
        return display_settings.get(key, default)
    
    def get_hardware_mode(self) -> str:
        """Get hardware mode setting (mock or real)
        
        Returns:
            Hardware mode string ("mock" or "real")
        """
        if not self._config_data:
            return self.DEFAULT_CONFIG["cli_config"]["hardware_mode"]
        
        cli_config = self._config_data.get("cli_config", {})
        return cli_config.get("hardware_mode", self.DEFAULT_CONFIG["cli_config"]["hardware_mode"])
    
    def is_mock_mode(self) -> bool:
        """Check if mock mode is enabled
        
        Returns:
            True if mock mode is enabled, False otherwise
        """
        return self.get_hardware_mode().lower() == "mock"
    
    def reload_config(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Reload configuration from file
        
        Args:
            config_path: Optional new path to load from
        """
        if config_path:
            self._config_path = Path(config_path)
        
        self._config_data = None
        self._load_config()
        logger.info("CLI configuration reloaded")
    
    def validate_config(self) -> bool:
        """Validate the loaded configuration structure
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            if not self._config_data:
                return False
            
            # Check for required top-level structure
            cli_config = self._config_data.get("cli_config")
            if not cli_config:
                logger.error("Missing 'cli_config' section in configuration")
                return False
            
            # Check for required commands section
            commands = cli_config.get("commands")
            if not commands:
                logger.error("Missing 'commands' section in configuration")
                return False
            
            # Validate each command has required structure
            required_commands = ["robot", "mcu", "loadcell", "power"]
            for cmd in required_commands:
                if cmd not in commands:
                    logger.warning(f"Missing configuration for command: {cmd}")
                    continue
                
                cmd_config = commands[cmd]
                if "connection" not in cmd_config:
                    logger.warning(f"Missing 'connection' section for command: {cmd}")
            
            logger.info("Configuration validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get the currently loaded configuration file path"""
        return self._config_path
    
    @property
    def is_loaded(self) -> bool:
        """Check if configuration is loaded"""
        return self._config_data is not None