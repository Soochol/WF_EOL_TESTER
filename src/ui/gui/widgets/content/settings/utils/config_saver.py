"""
Configuration file saving utilities.

Provides functionality to save configuration changes back to YAML files
with proper formatting and backup management.
"""

import os
import shutil
from datetime import datetime
from typing import Any, Dict

import yaml

from ..core import ConfigFile, ConfigValue


class ConfigFileSaver:
    """Utility class for saving configuration files"""

    @staticmethod
    def save_config_file(config_file: ConfigFile, backup: bool = True) -> bool:
        """
        Save configuration file to disk.

        Args:
            config_file: ConfigFile object to save
            backup: Whether to create backup before saving

        Returns:
            True if save successful, False otherwise
        """
        try:
            if backup:
                ConfigFileSaver._create_backup(config_file.path)

            with open(config_file.path, "w", encoding="utf-8") as file:
                yaml.dump(
                    config_file.data,
                    file,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                )

            print(f"Configuration saved: {config_file.name}")
            return True

        except Exception as e:
            print(f"Error saving configuration file {config_file.name}: {e}")
            return False

    @staticmethod
    def save_config_value(config_value: ConfigValue, config_files: Dict[str, ConfigFile]) -> bool:
        """
        Save a specific configuration value.

        Args:
            config_value: ConfigValue to save
            config_files: Dictionary of all config files

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Find the config file containing this value
            target_file = None
            for config_file in config_files.values():
                if config_file.path == config_value.file_path:
                    target_file = config_file
                    break

            if not target_file:
                print(f"Config file not found for key: {config_value.key}")
                return False

            # Update the value in the config data
            ConfigFileSaver._update_nested_value(
                target_file.data, config_value.key, config_value.value
            )

            # Save the file
            return ConfigFileSaver.save_config_file(target_file)

        except Exception as e:
            print(f"Error saving config value {config_value.key}: {e}")
            return False

    @staticmethod
    def _update_nested_value(data: Dict[str, Any], key: str, value: Any) -> None:
        """
        Update a nested value in configuration data.

        Args:
            data: Configuration data dictionary
            key: Dot-separated key path
            value: New value to set
        """
        keys = key.split(".")
        current = data

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

    @staticmethod
    def _create_backup(file_path: str) -> None:
        """
        Create backup of configuration file.

        Args:
            file_path: Path to file to backup
        """
        if not os.path.exists(file_path):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Failed to create backup: {e}")

    @staticmethod
    def cleanup_old_backups(file_path: str, keep_count: int = 5) -> None:
        """
        Clean up old backup files, keeping only the most recent ones.

        Args:
            file_path: Original file path
            keep_count: Number of backups to keep
        """
        try:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)

            # Find all backup files for this config file
            backup_files = []
            for f in os.listdir(directory):
                if f.startswith(f"{filename}.backup_"):
                    backup_path = os.path.join(directory, f)
                    backup_files.append((backup_path, os.path.getmtime(backup_path)))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)

            # Remove old backups
            for backup_path, _ in backup_files[keep_count:]:
                try:
                    os.remove(backup_path)
                    print(f"Removed old backup: {backup_path}")
                except Exception as e:
                    print(f"Failed to remove backup {backup_path}: {e}")

        except Exception as e:
            print(f"Error during backup cleanup: {e}")