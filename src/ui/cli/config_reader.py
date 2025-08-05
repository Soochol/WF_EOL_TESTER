"""
CLI Configuration Reader

Provides configuration reading capabilities for CLI slash commands.
Supports YAML and JSON formats with fallback to default values.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger


class CLIConfigError(Exception):
    """Exception raised for CLI configuration errors"""

    ...


class CLIConfigReader:
    """Configuration reader for CLI commands with fallback support"""

    # Default configuration structure that matches the expected format
    DEFAULT_CONFIG = {
        "cli_config": {
            "hardware_mode": "mock",  # Default to mock mode for safety
            "commands": {
                "robot": {
                    "connection": {"axis_id": 0, "irq_no": 7},
                    "defaults": {"velocity": 200.0, "acceleration": 1000.0, "deceleration": 1000.0},
                },
                "mcu": {
                    "connection": {
                        "port": "/dev/ttyUSB1",
                        "baudrate": 115200,
                        "timeout": 2.0,
                        "bytesize": 8,
                        "stopbits": 1,
                        "parity": None,
                    },
                    "defaults": {"temperature_range": [20.0, 100.0], "fan_speed_range": [0, 100]},
                },
                "loadcell": {
                    "connection": {
                        "port": "/dev/ttyUSB0",
                        "baudrate": 9600,
                        "timeout": 1.0,
                        "bytesize": 8,
                        "stopbits": 1,
                        "parity": "even",
                        "indicator_id": 1,
                    },
                    "defaults": {
                        "force_range": [-1000.0, 1000.0],
                        "calibration_timeout": 10.0,
                        "monitor_refresh_rate": 0.5,
                    },
                },
                "power": {
                    "connection": {
                        "host": "192.168.1.100",
                        "port": 5025,
                        "timeout": 5.0,
                        "channel": 1,
                    },
                    "defaults": {
                        "voltage_range": [0.0, 30.0],
                        "current_limit_range": [0.0, 5.0],
                        "output_enabled": False,
                    },
                },
            },
            "preferences": {
                "auto_connect": False,
                "show_progress": True,
                "verbose_errors": True,
                "confirmation_required": True,
                "retry_attempts": 3,
                "command_timeout": 30.0,
            },
            "display": {
                "refresh_rate": 2.0,
                "decimal_precision": 3,
                "show_timestamps": True,
                "color_theme": "default",
            },
        }
    }

    # Supported hardware commands
    SUPPORTED_COMMANDS = ["robot", "mcu", "loadcell", "power"]

    # Configuration file search patterns
    CONFIG_FILENAMES = [
        "cli_commands.yaml",
        "cli_commands.yml",
        "cli_config.yaml",
        "cli_config.yml",
        "cli_commands.json",
        "cli_config.json",
    ]

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize configuration reader

        Args:
            config_path: Path to configuration file. If None, searches standard locations
        """
        self._config_path = Path(config_path) if config_path else None
        self._config_data: Dict[str, Any] = {}
        self._loaded_from: Optional[Path] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file with fallback to defaults"""
        # First, set defaults
        self._config_data = self.DEFAULT_CONFIG.copy()

        # Try to load from file
        config_paths = self._get_config_paths()

        for path in config_paths:
            if path.exists():
                try:
                    logger.info(f"Loading CLI configuration from: {path}")
                    file_config = self._read_config_file(path)

                    # Merge with defaults (file config overrides defaults)
                    self._merge_config(file_config)
                    self._loaded_from = path

                    logger.info("CLI configuration loaded successfully")
                    return

                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")
                    continue

        # If no config file found, just use defaults
        logger.info("No CLI configuration file found, using defaults")

    def _merge_config(self, file_config: Dict[str, Any]) -> None:
        """Recursively merge file configuration with defaults"""

        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value

        deep_merge(self._config_data, file_config)

    def _get_config_paths(self) -> List[Path]:
        """Get ordered list of configuration file paths to try"""
        paths: List[Path] = []

        # If specific path provided, try that first
        if self._config_path:
            paths.append(self._config_path)

        # Standard locations
        current_dir = Path.cwd()
        config_dir = current_dir / "configuration"

        # Try different locations for each filename
        for filename in self.CONFIG_FILENAMES:
            paths.extend([config_dir / filename, current_dir / filename])

        return paths

    def _read_config_file(self, path: Path) -> Dict[str, Any]:
        """Read configuration file based on extension"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == ".json":
                    return json.load(f) or {}
                else:
                    raise CLIConfigError(f"Unsupported config file format: {path.suffix}")
        except Exception as e:
            raise CLIConfigError(f"Failed to read config file {path}: {e}") from e

    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation path

        Args:
            path: Configuration path (e.g., "cli_config.hardware_mode", "commands.robot.connection.axis_id")
            default: Default value if path not found

        Returns:
            Configuration value or default

        Examples:
            config.get("cli_config.hardware_mode")
            config.get("commands.robot.connection.axis_id", 0)
            config.get("preferences.auto_connect", False)
        """
        current = self._config_data

        for key in path.split("."):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def get_command_config(self, command: str) -> Dict[str, Any]:
        """Get complete configuration for a specific command

        Args:
            command: Command name (robot, mcu, loadcell, power)

        Returns:
            Command configuration dictionary
        """
        if command not in self.SUPPORTED_COMMANDS:
            raise CLIConfigError(f"Unsupported command: {command}")

        config = self.get(f"cli_config.commands.{command}")
        if config is None:
            logger.warning(f"Command '{command}' not found in configuration, using defaults")
            # Get default configuration safely with type checking
            default_commands = self.DEFAULT_CONFIG.get("cli_config", {}).get("commands", {})
            if isinstance(default_commands, dict) and command in default_commands:
                default_config = default_commands[command]
                return default_config.copy() if isinstance(default_config, dict) else {}
            return {}

        return config.copy() if isinstance(config, dict) else {}

    def get_connection_params(self, command: str) -> Dict[str, Any]:
        """Get connection parameters for a specific command"""
        return self.get(f"cli_config.commands.{command}.connection", {})

    def get_command_defaults(self, command: str) -> Dict[str, Any]:
        """Get default values for a specific command"""
        return self.get(f"cli_config.commands.{command}.defaults", {})

    def get_preferences(self) -> Dict[str, Any]:
        """Get global CLI preferences"""
        default_prefs = self.DEFAULT_CONFIG.get("cli_config", {}).get("preferences", {})
        return self.get("cli_config.preferences", default_prefs)

    def get_display_settings(self) -> Dict[str, Any]:
        """Get display settings"""
        default_display = self.DEFAULT_CONFIG.get("cli_config", {}).get("display", {})
        return self.get("cli_config.display", default_display)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value"""
        return self.get(f"cli_config.preferences.{key}", default)

    def get_display_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific display setting value"""
        return self.get(f"cli_config.display.{key}", default)

    def get_hardware_mode(self) -> str:
        """Get hardware mode setting (mock or real)"""
        return self.get("cli_config.hardware_mode", "mock")

    def is_mock_mode(self) -> bool:
        """Check if mock mode is enabled"""
        return self.get_hardware_mode().lower() == "mock"

    def reload_config(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Reload configuration from file

        Args:
            config_path: Optional new path to load from
        """
        if config_path:
            self._config_path = Path(config_path)

        self._config_data = {}
        self._loaded_from = None
        self._load_config()
        logger.info("CLI configuration reloaded")

    def validate_config(self) -> bool:
        """Validate the loaded configuration structure

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check for required top-level structure
            cli_config = self.get("cli_config")
            if not cli_config:
                logger.error("Missing 'cli_config' section in configuration")
                return False

            # Check for required commands section
            commands = self.get("cli_config.commands")
            if not commands:
                logger.error("Missing 'commands' section in configuration")
                return False

            # Validate each command has required structure
            for cmd in self.SUPPORTED_COMMANDS:
                cmd_config = self.get(f"cli_config.commands.{cmd}")
                if not cmd_config:
                    logger.warning(f"Missing configuration for command: {cmd}")
                    continue

                if not self.get(f"cli_config.commands.{cmd}.connection"):
                    logger.warning(f"Missing 'connection' section for command: {cmd}")

            logger.info("Configuration validation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_supported_commands(self) -> List[str]:
        """Get list of supported hardware commands"""
        return self.SUPPORTED_COMMANDS.copy()

    def has_command_config(self, command: str) -> bool:
        """Check if configuration exists for a specific command"""
        return self.get(f"cli_config.commands.{command}") is not None

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "loaded_from": str(self._loaded_from) if self._loaded_from else "defaults",
            "hardware_mode": self.get_hardware_mode(),
            "supported_commands": self.get_supported_commands(),
            "configured_commands": [
                cmd for cmd in self.SUPPORTED_COMMANDS if self.has_command_config(cmd)
            ],
            "preferences": {
                "auto_connect": self.get_preference("auto_connect"),
                "show_progress": self.get_preference("show_progress"),
                "verbose_errors": self.get_preference("verbose_errors"),
            },
        }

    @property
    def config_path(self) -> Optional[Path]:
        """Get the currently loaded configuration file path"""
        return self._loaded_from

    @property
    def is_loaded(self) -> bool:
        """Check if configuration is loaded"""
        return bool(self._config_data)
