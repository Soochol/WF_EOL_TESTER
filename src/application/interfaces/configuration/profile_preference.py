"""
Profile Preference Interface Protocol

Defines the interface contract for profile preference implementations.
"""

from typing import Protocol, List, Optional


class ProfilePreference(Protocol):
    """Profile preference interface protocol"""
    
    async def load_last_used_profile(self) -> Optional[str]:
        """Load the last used profile name"""
        ...
    
    async def save_last_used_profile(self, profile_name: str) -> None:
        """Save the last used profile name"""
        ...
    
    async def update_usage_history(self, profile_name: str) -> None:
        """Update profile usage history"""
        ...
    
    async def get_usage_history(self) -> List[str]:
        """Get profile usage history"""
        ...
    
    async def is_available(self) -> bool:
        """Check if preference storage is available"""
        ...
    
    async def clear_preferences(self) -> None:
        """Clear all profile preferences"""
        ...