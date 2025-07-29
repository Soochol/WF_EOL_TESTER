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
        self._max_history_entries = 10
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists"""
        try:
            self._preference_file.parent.mkdir(
                parents=True, exist_ok=True
            )
            logger.debug(
                f"Data directory ensured: {self._preference_file.parent}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to create data directory: {e}"
            )

    async def save_last_used_profile(
        self, profile_name: str
    ) -> None:
        """
        Save the last used profile name to JSON file

        Args:
            profile_name: Name of the profile to save as last used

        Raises:
            RepositoryException: If saving fails
        """
        if not profile_name or not isinstance(
            profile_name, str
        ):
            raise RepositoryException(
                f"Invalid profile name for saving: '{profile_name}'"
            )

        try:
            # Load existing preferences
            preferences = await self._load_preferences()

            # Update last used profile
            old_profile = preferences.get(
                "last_used_profile"
            )
            preferences["last_used_profile"] = profile_name
            preferences["last_updated"] = datetime.now(
                timezone.utc
            ).isoformat()

            # Save to file
            await self._save_preferences(preferences)

            if old_profile != profile_name:
                logger.debug(
                    f"Last used profile updated: '{old_profile}' → '{profile_name}'"
                )

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
            profile_name = preferences.get(
                "last_used_profile"
            )

            if profile_name:
                logger.debug(
                    f"Loaded last used profile: '{profile_name}'"
                )
                return profile_name

            logger.debug("No last used profile found")
            return None

        except Exception as e:
            logger.warning(
                f"Failed to load last used profile: {e}"
            )
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
            logger.warning(
                f"Failed to load usage history: {e}"
            )
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
                logger.info(
                    f"Profile preferences file deleted: {self._preference_file}"
                )
            else:
                logger.debug(
                    "Preferences file did not exist, nothing to clear"
                )

        except Exception as e:
            raise RepositoryException(
                f"Failed to clear profile preferences: {str(e)}"
            ) from e

    async def get_preference_metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Get metadata about the JSON preference file

        Returns:
            Dictionary with file metadata
        """
        try:
            metadata = {
                "preference_file": str(
                    self._preference_file
                ),
                "file_exists": self._preference_file.exists(),
                "file_size": 0,
                "last_modified": None,
                "is_readable": False,
                "is_writable": False,
            }

            if self._preference_file.exists():
                stat = self._preference_file.stat()
                metadata.update(
                    {
                        "file_size": stat.st_size,
                        "last_modified": datetime.fromtimestamp(
                            stat.st_mtime, timezone.utc
                        ).isoformat(),
                        "is_readable": os.access(
                            self._preference_file, os.R_OK
                        ),
                        "is_writable": os.access(
                            self._preference_file, os.W_OK
                        ),
                    }
                )

            return metadata

        except Exception as e:
            logger.warning(
                f"Failed to get preference metadata: {e}"
            )
            return {
                "preference_file": str(
                    self._preference_file
                ),
                "error": str(e),
            }

    async def update_usage_history(
        self, profile_name: str
    ) -> None:
        """
        Update usage history with a new profile usage

        Args:
            profile_name: Name of the profile that was used

        Raises:
            RepositoryException: If update fails
        """
        if not profile_name or not isinstance(
            profile_name, str
        ):
            raise RepositoryException(
                f"Invalid profile name for history update: '{profile_name}'"
            )

        try:
            preferences = await self._load_preferences()

            # Get current history
            history = preferences.get("usage_history", [])

            # Add new entry if not already the most recent
            if not history or history[-1] != profile_name:
                history.append(profile_name)

                # Keep only recent entries
                if len(history) > self._max_history_entries:
                    history = history[
                        -self._max_history_entries :
                    ]

                preferences["usage_history"] = history
                preferences["last_updated"] = datetime.now(
                    timezone.utc
                ).isoformat()

                await self._save_preferences(preferences)
                logger.debug(
                    f"Updated usage history with: '{profile_name}'"
                )

        except Exception as e:
            raise RepositoryException(
                f"Failed to update usage history for '{profile_name}': {str(e)}"
            ) from e

    async def is_available(self) -> bool:
        """
        Check if the JSON file storage is available and accessible

        Returns:
            True if storage is available
        """
        try:
            # Check if we can create the directory
            self._ensure_data_directory()

            # Try to access the file or its parent directory
            if self._preference_file.exists():
                return os.access(
                    self._preference_file, os.R_OK
                ) and os.access(
                    self._preference_file, os.W_OK
                )
            else:
                return os.access(
                    self._preference_file.parent, os.W_OK
                )

        except Exception as e:
            logger.warning(
                f"Repository availability check failed: {e}"
            )
            return False

    async def _load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from JSON file

        Returns:
            Dictionary with preference data
        """
        if not self._preference_file.exists():
            logger.debug(
                f"Preference file does not exist: {self._preference_file}"
            )
            return {}

        try:
            with open(
                self._preference_file, "r", encoding="utf-8"
            ) as f:
                data = json.load(f)

            # Basic validation
            if not isinstance(data, dict):
                logger.warning(
                    "Invalid preference file format, creating new"
                )
                return {}

            logger.debug(
                f"Loaded preferences from {self._preference_file}"
            )
            return data

        except json.JSONDecodeError as e:
            logger.warning(
                f"Invalid JSON in preference file, creating new: {e}"
            )
            return {}
        except Exception as e:
            logger.warning(
                f"Failed to read preference file: {e}"
            )
            return {}

    async def _save_preferences(
        self, preferences: Dict[str, Any]
    ) -> None:
        """
        Save preferences to JSON file with atomic write operation

        Args:
            preferences: Dictionary with preference data

        Raises:
            Exception: If saving fails
        """
        # Add metadata
        preferences["_metadata"] = {
            "version": "1.0",
            "created_by": "JsonProfilePreference",
            "description": "User profile preferences and usage history",
            "schema_version": "1.0",
        }

        # Write to temporary file first, then rename (atomic operation)
        temp_file = self._preference_file.with_suffix(
            ".tmp"
        )

        try:
            with open(
                temp_file, "w", encoding="utf-8"
            ) as f:
                json.dump(
                    preferences,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic rename
            temp_file.replace(self._preference_file)
            logger.debug(
                f"Saved preferences to {self._preference_file}"
            )

        except Exception as e:
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise e

    def set_max_history_entries(
        self, max_entries: int
    ) -> None:
        """
        Set the maximum number of history entries to maintain

        Args:
            max_entries: Maximum number of history entries (must be > 0)
        """
        if max_entries > 0:
            self._max_history_entries = max_entries
            logger.debug(
                f"Max history entries set to: {max_entries}"
            )
        else:
            logger.warning(
                f"Invalid max history entries: {max_entries}"
            )

    def get_file_path(self) -> Path:
        """
        Get the path to the preference file

        Returns:
            Path object for the preference file
        """
        return self._preference_file
