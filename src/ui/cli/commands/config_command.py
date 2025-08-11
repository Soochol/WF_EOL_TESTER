"""
Config Command

Handles configuration management commands.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from src.domain.exceptions.eol_exceptions import (
    ConfigurationValidationError,
    RepositoryAccessError,
)
from src.domain.value_objects.hardware_configuration import (
    HardwareConfiguration,
)
from src.ui.cli.commands.base import Command, CommandResult


class ConfigCommand(Command):
    """Command for configuration management"""

    def __init__(self) -> None:
        super().__init__(
            name="config",
            description="Configuration management",
        )
        self._config_file = "config/application/app_config.json"
        self._current_config: Optional[Dict[str, Any]] = None

    async def execute(self, args: List[str]) -> CommandResult:
        """
        Execute config command

        Args:
            args: Command arguments (subcommand and parameters)

        Returns:
            CommandResult with configuration operation results
        """
        if not args:
            return await self._show_config()

        subcommand = args[0].lower()

        if subcommand == "view":
            return await self._show_config()
        if subcommand == "hardware":
            return await self._show_hardware_config()
        if subcommand == "edit":
            return await self._edit_config()
        if subcommand == "save":
            return await self._save_config(args[1:])
        if subcommand == "load":
            return await self._load_config(args[1:])
        if subcommand == "reset":
            return await self._reset_config()
        if subcommand == "help":
            return CommandResult.info(self.get_help())
        return CommandResult.error(f"Unknown config subcommand: {subcommand}")

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands"""
        return {
            "view": "Show current configuration",
            "hardware": "Show hardware configuration details",
            "edit": "Edit configuration interactively",
            "save <name>": "Save current config with name",
            "load <name>": "Load saved configuration",
            "reset": "Reset to default configuration",
            "help": "Show config command help",
        }

    async def _show_config(self) -> CommandResult:
        """Show current configuration"""
        try:
            config = await self._get_current_config()

            config_text = "Current Configuration:\\n"
            config_text += "=" * 50 + "\\n"
            config_text += json.dumps(config, indent=2, ensure_ascii=False)

            return CommandResult.success(config_text)

        except Exception as e:
            logger.error(f"Failed to show config: {e}")
            return CommandResult.error(f"Failed to load configuration: {str(e)}")

    async def _show_hardware_config(self) -> CommandResult:
        """Show detailed hardware configuration"""
        try:
            config = await self._get_current_config()
            hardware_config = config.get("hardware", {})

            if not hardware_config:
                return CommandResult.warning("No hardware configuration found")

            # Create HardwareConfiguration object for validation and display
            try:
                hw_config = HardwareConfiguration.from_dict(hardware_config)

                config_text = "Hardware Configuration:\\n"
                config_text += "=" * 50 + "\\n"
                config_text += "├── Robot Hardware\\n"
                config_text += f"│   └── IRQ No: {hw_config.robot.irq_no}\\n"
                config_text += "├── LoadCell Hardware\\n"
                config_text += f"│   ├── Port: {hw_config.loadcell.port}\\n"
                config_text += f"│   └── Baudrate: {hw_config.loadcell.baudrate}\\n"
                config_text += "├── MCU Hardware\\n"
                config_text += f"│   ├── Port: {hw_config.mcu.port}\\n"
                config_text += f"│   └── Baudrate: {hw_config.mcu.baudrate}\\n"
                config_text += "├── Power Hardware\\n"
                config_text += f"│   ├── Host: {hw_config.power.host}\\n"
                config_text += f"│   ├── Port: {hw_config.power.port}\\n"
                config_text += f"│   └── Channel: {hw_config.power.channel}\\n"
                config_text += "└── Digital I/O Hardware\\n"
                config_text += (
                    f"    ├── Start Left: {hw_config.digital_io.operator_start_button_left}\\n"
                )
                config_text += (
                    f"    ├── Start Right: {hw_config.digital_io.operator_start_button_right}\\n"
                )
                config_text += f"    ├── Red Lamp: {hw_config.digital_io.tower_lamp_red}\\n"
                config_text += f"    ├── Yellow Lamp: {hw_config.digital_io.tower_lamp_yellow}\\n"
                config_text += f"    ├── Green Lamp: {hw_config.digital_io.tower_lamp_green}\\n"
                config_text += f"    └── Beep: {hw_config.digital_io.beep}\\n"

                return CommandResult.success(config_text)

            except Exception as validation_error:
                logger.warning(f"Hardware config validation failed: {validation_error}")
                # Fallback to raw display
                config_text = "Hardware Configuration (Raw):\\n"
                config_text += "=" * 50 + "\\n"
                config_text += json.dumps(
                    hardware_config,
                    indent=2,
                    ensure_ascii=False,
                )
                return CommandResult.warning(config_text)

        except Exception as e:
            logger.error(f"Failed to show hardware config: {e}")
            return CommandResult.error(f"Failed to load hardware configuration: {str(e)}")

    async def _edit_config(self) -> CommandResult:
        """Edit configuration interactively"""
        try:
            print("\\n" + "=" * 60)
            print("Configuration Editor")
            print("=" * 60)
            print("This feature will allow interactive configuration editing.")
            print("Currently showing current config for reference.")

            config = await self._get_current_config()
            print("\\nCurrent configuration:")
            print(json.dumps(config, indent=2, ensure_ascii=False))

            return CommandResult.info("Interactive config editor will be implemented soon")

        except Exception as e:
            logger.error(f"Config edit failed: {e}")
            return CommandResult.error(f"Failed to edit configuration: {str(e)}")

    async def _save_config(self, args: List[str]) -> CommandResult:
        """Save configuration with a name"""
        if not args:
            return CommandResult.error("Config name is required. Usage: /config save <name>")

        config_name = args[0]

        # Named config saving will be implemented in future versions
        return CommandResult.info(f"Saving config as '{config_name}' will be implemented soon")

    async def _load_config(self, args: List[str]) -> CommandResult:
        """Load saved configuration"""
        if not args:
            return CommandResult.error("Config name is required. Usage: /config load <name>")

        config_name = args[0]

        # Named config loading will be implemented in future versions
        return CommandResult.info(f"Loading config '{config_name}' will be implemented soon")

    async def _reset_config(self) -> CommandResult:
        """Reset to default configuration"""
        try:
            print("\\nResetting to default configuration...")

            # Get default config from ServiceFactory
            default_config = HardwareConfiguration().to_dict()

            # Save to file
            config_path = Path(self._config_file)

            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(
                    default_config,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            self._current_config = None  # Clear cache

            return CommandResult.success(
                f"Configuration reset to defaults and saved to {self._config_file}"
            )

        except Exception as e:
            logger.error(f"Config reset failed: {e}")
            return CommandResult.error(f"Failed to reset configuration: {str(e)}")

    async def _get_current_config(self) -> Dict[str, Any]:
        """Get current configuration (with caching)"""
        if self._current_config is not None:
            return self._current_config

        config_path = Path(self._config_file)

        if not config_path.exists():
            logger.info(f"Config file {self._config_file} not found, using default config")
            self._current_config = HardwareConfiguration().to_dict()

            # Create directory and save default config
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(
                        self._current_config,
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
                logger.info(f"Default configuration saved to {self._config_file}")
            except Exception as e:
                logger.warning(f"Failed to save default config: {e}")

        else:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._current_config = json.load(f)
                logger.debug(f"Configuration loaded from {self._config_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                raise ConfigurationValidationError([f"Invalid JSON in config file: {e}"]) from e
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
                raise RepositoryAccessError(
                    operation="load_config",
                    reason=f"Error loading config file: {e}",
                    file_path=str(config_path),
                ) from e

        # At this point, _current_config is guaranteed to be not None
        assert self._current_config is not None, "Configuration should be loaded by now"
        return self._current_config
