"""
File operation utilities.

Provides file system operations for configuration management
including path resolution and file validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class FileOperations:
    """Utility class for file operations"""

    @staticmethod
    def resolve_config_paths(base_paths: Dict[str, str], base_directory: Optional[str] = None) -> Dict[str, str]:
        """
        Resolve relative configuration file paths to absolute paths.

        Args:
            base_paths: Dictionary of relative paths
            base_directory: Base directory for relative paths

        Returns:
            Dictionary of resolved absolute paths
        """
        resolved_paths = {}

        if base_directory is None:
            # Get the directory of the current script
            current_file = Path(__file__).resolve()
            # Go up to the project root (assuming we're in src/ui/gui/widgets/settings/utils/)
            base_directory = str(current_file.parents[6])

        for name, relative_path in base_paths.items():
            if os.path.isabs(relative_path):
                resolved_path = relative_path
            else:
                resolved_path = os.path.join(base_directory, relative_path)

            resolved_paths[name] = os.path.normpath(resolved_path)

        return resolved_paths

    @staticmethod
    def validate_file_paths(file_paths: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate that configuration files exist.

        Args:
            file_paths: Dictionary of file paths to validate

        Returns:
            Dictionary mapping file names to existence status
        """
        validation_results = {}

        for name, path in file_paths.items():
            validation_results[name] = os.path.exists(path) and os.path.isfile(path)

        return validation_results

    @staticmethod
    def get_missing_files(file_paths: Dict[str, str]) -> List[str]:
        """
        Get list of missing configuration files.

        Args:
            file_paths: Dictionary of file paths to check

        Returns:
            List of missing file names
        """
        missing_files = []

        for name, path in file_paths.items():
            # Skip directories - they are handled separately
            if os.path.isdir(path):
                continue
            if not os.path.exists(path) or not os.path.isfile(path):
                missing_files.append(name)

        return missing_files

    @staticmethod
    def ensure_directory_exists(file_path: str) -> bool:
        """
        Ensure the directory for a file path exists.

        Args:
            file_path: Path to file

        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create directory for {file_path}: {e}")
            return False

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        info = {
            "exists": False,
            "size": 0,
            "modified": None,
            "readable": False,
            "writable": False,
        }

        try:
            if os.path.exists(file_path):
                info["exists"] = True
                stat = os.stat(file_path)
                info["size"] = stat.st_size
                info["modified"] = stat.st_mtime
                info["readable"] = os.access(file_path, os.R_OK)
                info["writable"] = os.access(file_path, os.W_OK)
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")

        return info

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize a file path for consistent handling.

        Args:
            path: File path to normalize

        Returns:
            Normalized path string
        """
        return os.path.normpath(os.path.expanduser(path))