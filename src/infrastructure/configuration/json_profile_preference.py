"""
Simple JSON Profile Preference Implementation

Replacement for the deleted json_profile_preference module.
Provides basic JSON file-based profile preference management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger


class JsonProfilePreference:
    """Simple JSON-based profile preference implementation"""
    
    def __init__(self, preference_file: str = "configuration/profile_preferences.json"):
        self.preference_file = Path(preference_file)
        self.preference_file.parent.mkdir(exist_ok=True)
    
    async def load_last_used_profile(self) -> Optional[str]:
        """Load the last used profile name"""
        try:
            if not self.preference_file.exists():
                return None
                
            with open(self.preference_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return data.get("last_used_profile")
            
        except Exception as e:
            logger.warning(f"Failed to load last used profile: {e}")
            return None
    
    async def save_last_used_profile(self, profile_name: str) -> None:
        """Save the last used profile name"""
        try:
            # Load existing preferences
            data = {}
            if self.preference_file.exists():
                with open(self.preference_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            # Update last used profile and timestamp
            data["last_used_profile"] = profile_name
            data["last_used_timestamp"] = datetime.now().isoformat()
            
            # Save preferences
            with open(self.preference_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved last used profile: {profile_name}")
            
        except Exception as e:
            logger.warning(f"Failed to save last used profile: {e}")
    
    async def update_usage_history(self, profile_name: str) -> None:
        """Update profile usage history"""
        try:
            # Load existing preferences
            data = {}
            if self.preference_file.exists():
                with open(self.preference_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            # Initialize usage history if not exists
            if "usage_history" not in data:
                data["usage_history"] = []
            
            # Add to history with timestamp
            history_entry = {
                "profile_name": profile_name,
                "timestamp": datetime.now().isoformat()
            }
            data["usage_history"].append(history_entry)
            
            # Keep only the last 50 entries
            data["usage_history"] = data["usage_history"][-50:]
            
            # Save preferences
            with open(self.preference_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Updated usage history for profile: {profile_name}")
            
        except Exception as e:
            logger.warning(f"Failed to update usage history: {e}")
    
    async def get_usage_history(self) -> List[str]:
        """Get profile usage history"""
        try:
            if not self.preference_file.exists():
                return []
                
            with open(self.preference_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            history = data.get("usage_history", [])
            
            # Extract profile names from history entries
            if history and isinstance(history[0], dict):
                return [entry["profile_name"] for entry in history]
            else:
                # Handle old format where history was just profile names
                return history
                
        except Exception as e:
            logger.warning(f"Failed to get usage history: {e}")
            return []
    
    async def is_available(self) -> bool:
        """Check if preference storage is available"""
        try:
            # Try to create preference file directory
            self.preference_file.parent.mkdir(exist_ok=True)
            return True
        except Exception as e:
            logger.warning(f"Profile preference storage not available: {e}")
            return False
    
    async def clear_preferences(self) -> None:
        """Clear all profile preferences"""
        try:
            if self.preference_file.exists():
                self.preference_file.unlink()
            logger.info("Profile preferences cleared")
        except Exception as e:
            logger.warning(f"Failed to clear preferences: {e}")