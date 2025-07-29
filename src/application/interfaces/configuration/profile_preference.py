"""
Profile Preference Interface

Abstract interface for profile preference persistence operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ProfilePreference(ABC):
    """
    Abstract interface for profile preference data persistence

    This interface defines the contract for storing and retrieving user preferences
    related to profile selection and usage history. It follows the Repository pattern
    to abstract away the specific storage mechanism (JSON, database, etc.).
    """

    @abstractmethod
    async def save_last_used_profile(
        self, profile_name: str
    ) -> None:
        """
        Save the last used profile name

        Args:
            profile_name: Name of the profile to save as last used

        Raises:
            RepositoryException: If saving fails
        """
        ...

    @abstractmethod
    async def load_last_used_profile(self) -> Optional[str]:
        """
        Load the last used profile name

        Returns:
            Last used profile name, or None if not found/error
        """
        ...

    @abstractmethod
    async def get_usage_history(self) -> List[str]:
        """
        Get profile usage history

        Returns:
            List of recently used profile names (most recent last)
        """
        ...

    @abstractmethod
    async def clear_preferences(self) -> None:
        """
        Clear all profile preferences

        Raises:
            RepositoryException: If clearing fails
        """
        ...

    @abstractmethod
    async def get_preference_metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Get metadata about preferences storage

        Returns:
            Dictionary with metadata information (file existence, size, etc.)
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the preference storage is available and accessible

        Returns:
            True if storage is available, False otherwise
        """
        ...
