"""
JSON Profile Preference

JSON file-based implementation of ProfilePreferenceRepository.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from application.interfaces.configuration.profile_preference import (
    ProfilePreference,
)
from domain.exceptions import (
    RepositoryError as RepositoryException,
)

# Constants
DEFAULT_MAX_HISTORY_ENTRIES = 10
FILE_ENCODING = "utf-8"
JSON_INDENT_SPACES = 2


class JsonProfilePreference(ProfilePreference):
    """
    JSON file-based implementation of profile preference storage

    This repository stores profile preferences in a JSON file, providing
    persistence across application restarts. It handles file I/O operations,
    data validation, and error recovery.
    """

    def __init__(
        self,
        preference_file: str = "configuration/last_used_profile.json",
    ):
        """
        Initialize JSON profile preference repository

        Args:
            preference_file: Path to the JSON preference storage file
        """
        self._preference_file = Path(preference_file)
        self._max_history_entries = DEFAULT_MAX_HISTORY_ENTRIES
        self._ensure_data_directory()


    def _ensure_data_directory(self) -> None:
        """
        Create the data directory if it doesn't exist.

        Ensures the parent directory of the preference file exists with
        appropriate permissions for reading and writing.
        """
        try:
            self._preference_file.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Data directory ensured: {self._preference_file.parent}")
        except Exception as e:
            logger.warning(f"Failed to create data directory: {e}")

    async def save_last_used_profile(self, profile_name: str) -> None:
        """
        Save the last used profile name to JSON file

        Args:
            profile_name: Name of the profile to save as last used

        Raises:
            RepositoryException: If saving fails
        """
        self._validate_profile_name(profile_name, "saving")

        try:
            existing_preferences = await self._load_preferences()
            updated_preferences = self._update_last_used_profile(existing_preferences, profile_name)
            await self._save_preferences(updated_preferences)

            self._log_profile_change(existing_preferences.get("last_used_profile"), profile_name)

        except Exception as e:
            raise RepositoryException(
                f"Failed to save last used profile '{profile_name}': {str(e)}"
            ) from e

    async def load_last_used_profile(self) -> Optional[str]:
        """
        Load the last used profile name from JSON file

        Returns:
            Last used profile name, or None if not found
        """
        try:
            preferences = await self._load_preferences()
            last_used_profile = preferences.get("last_used_profile")

            if last_used_profile:
                logger.debug(f"Loaded last used profile: '{last_used_profile}'")
                return last_used_profile

            logger.debug("No last used profile found")
            return None

        except Exception as e:
            logger.warning(f"Failed to load last used profile: {e}")
            return None

    async def get_usage_history(self) -> List[str]:
        """
        Get profile usage history from JSON file

        Returns:
            List of recently used profile names (most recent last)
        """
        try:
            preferences = await self._load_preferences()
            return preferences.get("usage_history", [])
        except Exception as e:
            logger.warning(f"Failed to load usage history: {e}")
            return []

    async def clear_preferences(self) -> None:
        """
        Clear all profile preferences by removing the JSON file

        Raises:
            RepositoryException: If clearing fails
        """
        try:
            if self._preference_file.exists():
                self._preference_file.unlink()
                logger.info(f"Profile preferences file deleted: {self._preference_file}")
            else:
                logger.debug("Preferences file did not exist, nothing to clear")

        except Exception as e:
            raise RepositoryException(f"Failed to clear profile preferences: {str(e)}") from e

    async def get_preference_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the JSON preference file

        Returns:
            Dictionary with basic file information
        """
        try:
            return {
                "preference_file": str(self._preference_file),
                "file_exists": self._preference_file.exists(),
                "is_readable": os.access(self._preference_file, os.R_OK) if self._preference_file.exists() else False,
                "is_writable": os.access(self._preference_file, os.W_OK) if self._preference_file.exists() else os.access(self._preference_file.parent, os.W_OK),
            }

        except Exception as e:
            logger.warning(f"Failed to get preference metadata: {e}")
            return {
                "preference_file": str(self._preference_file),
                "error": str(e),
            }

    async def update_usage_history(self, profile_name: str) -> None:
        """
        Update usage history with a new profile usage

        Args:
            profile_name: Name of the profile that was used

        Raises:
            RepositoryException: If update fails
        """
        self._validate_profile_name(profile_name, "history update")

        try:
            current_preferences = await self._load_preferences()
            updated_preferences = self._update_profile_history(current_preferences, profile_name)

            # Only save if history was actually updated
            if updated_preferences != current_preferences:
                await self._save_preferences(updated_preferences)
                logger.debug(f"Updated usage history with: '{profile_name}'")

        except Exception as e:
            raise RepositoryException(
                f"Failed to update usage history for '{profile_name}': {str(e)}"
            ) from e

    async def is_available(self) -> bool:
        """
        Check if the JSON file storage is available and accessible

        Returns:
            True if storage is available for reading and writing
        """
        try:
            # Ensure directory structure exists
            self._ensure_data_directory()

            # Check file or directory accessibility
            if self._preference_file.exists():
                return self._check_file_permissions()
            return self._check_directory_permissions()

        except Exception as e:
            logger.warning(f"Repository availability check failed: {e}")
            return False

    async def _load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from JSON file with validation

        Returns:
            Dictionary with preference data, empty dict if file doesn't exist
            or contains invalid data
        """
        if not self._preference_file.exists():
            logger.debug(f"Preference file does not exist: {self._preference_file}")
            return {}

        try:
            loaded_data = self._read_json_file()
            validated_data = self._validate_preferences_data(loaded_data)

            logger.debug(f"Loaded preferences from {self._preference_file}")
            return validated_data

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in preference file, creating new: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Failed to read preference file: {e}")
            return {}

    async def _save_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Save preferences to JSON file

        Args:
            preferences: Dictionary with preference data

        Raises:
            Exception: If saving fails
        """
        try:
            with open(self._preference_file, "w", encoding=FILE_ENCODING) as file:
                json.dump(
                    preferences,
                    file,
                    indent=JSON_INDENT_SPACES,
                    ensure_ascii=False,
                )
            logger.debug(f"Saved preferences to {self._preference_file}")

        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            raise e


    # Helper methods for improved readability and maintainability

    def _validate_profile_name(self, profile_name: str, operation: str) -> None:
        """
        Validate profile name for repository operations

        Args:
            profile_name: Name to validate
            operation: Description of the operation for error messages

        Raises:
            RepositoryException: If profile name is invalid
        """
        if not profile_name or not isinstance(profile_name, str):
            raise RepositoryException(f"Invalid profile name for {operation}: '{profile_name}'")

    def _update_last_used_profile(
        self, preferences: Dict[str, Any], profile_name: str
    ) -> Dict[str, Any]:
        """
        Update preferences with new last used profile

        Args:
            preferences: Current preferences dictionary
            profile_name: New profile name to set

        Returns:
            Updated preferences dictionary
        """
        preferences["last_used_profile"] = profile_name
        preferences["last_updated"] = datetime.now(timezone.utc).isoformat()
        return preferences

    def _log_profile_change(self, old_profile: Optional[str], new_profile: str) -> None:
        """
        Log profile changes for debugging

        Args:
            old_profile: Previously used profile name
            new_profile: Newly set profile name
        """
        if old_profile != new_profile:
            logger.debug(f"Last used profile updated: '{old_profile}' → '{new_profile}'")


    def _update_profile_history(
        self, preferences: Dict[str, Any], profile_name: str
    ) -> Dict[str, Any]:
        """
        Update usage history with new profile entry

        Args:
            preferences: Current preferences dictionary
            profile_name: Profile name to add to history

        Returns:
            Updated preferences dictionary
        """
        current_history = preferences.get("usage_history", [])

        # Only update if this isn't already the most recent entry
        if not current_history or current_history[-1] != profile_name:
            updated_history = self._add_profile_to_history(current_history, profile_name)
            preferences["usage_history"] = updated_history
            preferences["last_updated"] = datetime.now(timezone.utc).isoformat()

        return preferences

    def _add_profile_to_history(self, history: List[str], profile_name: str) -> List[str]:
        """
        Add profile to history list, maintaining size limit

        Args:
            history: Current history list
            profile_name: Profile name to add

        Returns:
            Updated history list with size constraint applied
        """
        updated_history = history + [profile_name]

        # Trim to maximum allowed entries
        if len(updated_history) > self._max_history_entries:
            updated_history = updated_history[-self._max_history_entries :]

        return updated_history

    def _check_file_permissions(self) -> bool:
        """
        Check if existing preference file has read/write permissions

        Returns:
            True if file is readable and writable
        """
        return os.access(self._preference_file, os.R_OK) and os.access(
            self._preference_file, os.W_OK
        )

    def _check_directory_permissions(self) -> bool:
        """
        Check if parent directory has write permissions for new file creation

        Returns:
            True if directory is writable
        """
        return os.access(self._preference_file.parent, os.W_OK)

    def _read_json_file(self) -> Dict[str, Any]:
        """
        Read and parse JSON data from preference file

        Returns:
            Parsed JSON data as dictionary

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
            Exception: If file cannot be read
        """
        with open(self._preference_file, "r", encoding=FILE_ENCODING) as file:
            return json.load(file)

    def _validate_preferences_data(self, data: Any) -> Dict[str, Any]:
        """
        Validate loaded preferences data structure

        Args:
            data: Raw data loaded from JSON file

        Returns:
            Valid preferences dictionary or empty dict if invalid
        """
        if not isinstance(data, dict):
            logger.warning("Invalid preference file format, creating new")
            return {}
        return data



