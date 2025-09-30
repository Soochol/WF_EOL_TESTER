"""
Configuration file loading utilities.

Provides functionality to load and parse YAML configuration files
with error handling and validation.
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

import yaml

from ..core import ConfigFile


class ConfigFileLoader:
    """Utility class for loading configuration files"""

    @staticmethod
    def load_config_file(file_path: str) -> Optional[ConfigFile]:
        """
        Load a single configuration file.

        Args:
            file_path: Path to the configuration file

        Returns:
            ConfigFile object or None if loading failed
        """
        from loguru import logger

        try:
            # Check file existence
            if not os.path.exists(file_path):
                logger.warning(f"Configuration file not found: {file_path}")
                return None

            # Check if it's a directory (for test_profiles case)
            if os.path.isdir(file_path):
                logger.debug(f"Skipping directory: {file_path}")
                return None

            # Open and read file
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}

            # Create ConfigFile object
            file_name = os.path.basename(file_path)
            description = data.get("metadata", {}).get("description", "")

            config_file = ConfigFile(
                name=file_name,
                path=file_path,
                description=description,
                data=data,
                last_loaded=datetime.now(),
            )

            logger.debug(f"Loaded configuration file: {file_path}")
            return config_file

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    @staticmethod
    def load_multiple_config_files(file_paths: Dict[str, str]) -> Dict[str, ConfigFile]:
        """
        Load multiple configuration files.

        Args:
            file_paths: Dictionary mapping display names to file paths

        Returns:
            Dictionary of loaded configuration files
        """
        from loguru import logger

        config_files = {}
        logger.debug(f"Loading {len(file_paths)} configuration files...")

        for display_name, file_path in file_paths.items():
            logger.debug(f"Loading '{display_name}' from: {file_path}")

            # Skip directories (like test_profiles)
            if os.path.isdir(file_path):
                logger.debug(f"Skipping directory '{display_name}': {file_path}")
                continue

            config_file = ConfigFileLoader.load_config_file(file_path)

            if config_file:
                logger.debug(f"'{display_name}' loaded successfully")
                # Use display name instead of file name
                config_file.name = display_name
                config_files[display_name] = config_file
            else:
                logger.error(f"Failed to load '{display_name}' from {file_path}")

        logger.debug(f"Loaded {len(config_files)}/{len(file_paths)} configuration files")
        return config_files

    @staticmethod
    def validate_config_structure(data: Dict[str, Any]) -> bool:
        """
        Validate basic configuration file structure.

        Args:
            data: Configuration data dictionary

        Returns:
            True if structure is valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        # Check for metadata section if present
        if "metadata" in data:
            metadata = data["metadata"]
            if not isinstance(metadata, dict):
                return False

        return True

    @staticmethod
    def get_config_description(data: Dict[str, Any]) -> str:
        """
        Extract description from configuration data.

        Args:
            data: Configuration data dictionary

        Returns:
            Description string or empty string
        """
        try:
            metadata = data.get("metadata", {})
            return metadata.get("description", "")
        except (AttributeError, TypeError):
            return ""