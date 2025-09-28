"""
Icon Manager

Utility for loading and managing icons in the GUI application.
Provides centralized icon management with fallback support.
"""

from pathlib import Path
from typing import Dict, Optional, Union
from enum import Enum
import re

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from loguru import logger


class IconSize(Enum):
    """Standard icon sizes"""
    SMALL = 16
    MEDIUM = 24
    LARGE = 32
    XLARGE = 48


class IconTheme(Enum):
    """Icon themes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class IconManager:
    """
    Centralized icon manager for the GUI application.

    Handles loading icons from files with fallback to emoji/text alternatives.
    Supports different themes and sizes.
    """

    def __init__(self, resources_path: Optional[Path] = None):
        # Default to the resources/icons directory
        if resources_path is None:
            current_file = Path(__file__)
            resources_path = current_file.parent.parent / "resources" / "icons"

        self.icons_path = Path(resources_path)
        self.current_theme = IconTheme.LIGHT
        self._icon_cache: Dict[str, QIcon] = {}

        # Emoji fallbacks for when icon files aren't available
        self.emoji_fallbacks = {
            # Navigation icons
            "dashboard": "🏠",
            "test_control": "⚡",
            "results": "📊",
            "hardware": "⚙️",
            "settings": "🔧",
            "logs": "📋",

            # Status icons
            "status_ready": "🔘",
            "status_running": "🟢",
            "status_success": "✅",
            "status_warning": "⚠️",
            "status_error": "❌",
            "status_info": "ℹ️",
            "status_loading": "🔄",
            "status_emergency": "🚨",
            "status_homing": "🏠",

            # Action icons
            "play": "▶️",
            "pause": "⏸️",
            "stop": "⏹️",
            "refresh": "🔄",
            "save": "💾",
            "export": "📤",
            "import": "📥",

            # Hardware icons
            "robot": "🤖",
            "loadcell": "⚖️",
            "power": "🔌",
            "mcu": "🎛️",
            "connection": "🔗",
            "disconnect": "❌",
        }

    def get_icon(self, name: str, size: Union[IconSize, int] = IconSize.MEDIUM,
                 theme: Optional[IconTheme] = None) -> QIcon:
        """
        Get an icon by name with specified size and theme.

        Args:
            name: Icon name (without extension)
            size: Icon size (IconSize enum or pixel size)
            theme: Icon theme (uses current theme if None)

        Returns:
            QIcon object (may be empty if not found)
        """
        # Validate icon name first
        if not self._is_valid_icon_name(name):
            # Use debug level for emoji fallbacks instead of warning
            logger.debug(f"Using fallback for icon name: '{name}' (contains emoji characters)")
            return QIcon()  # Return empty icon for invalid names

        if theme is None:
            theme = self.current_theme

        # Convert size to int
        if isinstance(size, IconSize):
            size_px = size.value
        else:
            size_px = size

        # Create cache key
        cache_key = f"{name}_{size_px}_{theme.value}"

        # Check cache first
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Try to load icon from file
        icon = self._load_icon_from_file(name, size_px, theme)

        # If no file found, try to create from emoji
        if icon.isNull():
            icon = self._create_icon_from_emoji(name, size_px)

        # Cache the result
        self._icon_cache[cache_key] = icon
        return icon

    def _load_icon_from_file(self, name: str, size: int, theme: IconTheme) -> QIcon:
        """Load icon from file system or Qt resources"""
        icon = QIcon()

        # Try Qt resources first (prefixed with :/)
        resource_paths = []
        if theme != IconTheme.AUTO:
            resource_paths.append(f":/icons/icons/{theme.value}/{name}.png")
        resource_paths.append(f":/icons/icons/{name}.png")

        for resource_path in resource_paths:
            icon = QIcon(resource_path)
            if not icon.isNull():
                logger.debug(f"Loaded icon from resources: {resource_path}")
                return icon

        # Fallback to file system
        # Supported formats
        formats = ['.png', '.svg', '.ico', '.jpg', '.jpeg']

        # Try theme-specific paths first
        if theme != IconTheme.AUTO:
            theme_path = self.icons_path / theme.value
            for fmt in formats:
                icon_file = theme_path / f"{name}{fmt}"
                if icon_file.exists():
                    icon.addFile(str(icon_file), QSize(size, size))
                    logger.debug(f"Loaded themed icon: {icon_file}")
                    return icon

        # Try general icons directory
        for fmt in formats:
            icon_file = self.icons_path / f"{name}{fmt}"
            if icon_file.exists():
                icon.addFile(str(icon_file), QSize(size, size))
                logger.debug(f"Loaded icon: {icon_file}")
                return icon

        # Only log at debug level if not in fallbacks (reduces noise)
        if name not in self.emoji_fallbacks:
            logger.debug(f"No icon file found for: {name}")
        return icon

    def _create_icon_from_emoji(self, name: str, size: int) -> QIcon:
        """Create icon from emoji fallback"""
        if name in self.emoji_fallbacks:
            # For now, return empty icon since emoji rendering as QIcon
            # would require more complex text-to-pixmap conversion
            # Only log at trace level for normal fallback usage
            logger.opt(depth=1).trace(f"Using emoji fallback for: {name} -> {self.emoji_fallbacks[name]}")

        return QIcon()  # Return empty icon for now

    def _is_valid_icon_name(self, name: str) -> bool:
        """
        Validate that the icon name is valid (not an emoji or invalid format)

        Args:
            name: Icon name to validate

        Returns:
            True if valid icon name, False otherwise
        """
        if not name or not isinstance(name, str):
            return False

        # Check if name contains emoji characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )

        if emoji_pattern.search(name):
            return False

        # Check for basic naming convention (alphanumeric, underscore, dash)
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False

        return True

    def get_emoji_fallback(self, name: str) -> str:
        """Get emoji fallback for icon name"""
        return self.emoji_fallbacks.get(name, "")

    def has_icon(self, name: str, theme: Optional[IconTheme] = None) -> bool:
        """Check if an icon exists (either as file or emoji fallback)"""
        if theme is None:
            theme = self.current_theme

        # Check for file
        if self._icon_file_exists(name, theme):
            return True

        # Check for emoji fallback
        return name in self.emoji_fallbacks

    def _icon_file_exists(self, name: str, theme: IconTheme) -> bool:
        """Check if icon file exists"""
        formats = ['.png', '.svg', '.ico', '.jpg', '.jpeg']

        # Check theme-specific path
        if theme != IconTheme.AUTO:
            theme_path = self.icons_path / theme.value
            for fmt in formats:
                if (theme_path / f"{name}{fmt}").exists():
                    return True

        # Check general path
        for fmt in formats:
            if (self.icons_path / f"{name}{fmt}").exists():
                return True

        return False

    def set_theme(self, theme: IconTheme) -> None:
        """Change the current icon theme"""
        if theme != self.current_theme:
            self.current_theme = theme
            # Clear cache to reload icons with new theme
            self._icon_cache.clear()
            logger.info(f"Icon theme changed to: {theme.value}")

    def get_available_icons(self) -> list[str]:
        """Get list of available icon names"""
        available = set()

        # Add icons from files
        if self.icons_path.exists():
            for icon_file in self.icons_path.rglob("*"):
                if icon_file.is_file() and icon_file.suffix.lower() in ['.png', '.svg', '.ico', '.jpg', '.jpeg']:
                    # Remove extension and add to set
                    available.add(icon_file.stem)

        # Add emoji fallbacks
        available.update(self.emoji_fallbacks.keys())

        return sorted(list(available))

    def clear_cache(self) -> None:
        """Clear the icon cache"""
        self._icon_cache.clear()
        logger.debug("Icon cache cleared")


# Global icon manager instance
_icon_manager: Optional[IconManager] = None


def get_icon_manager() -> IconManager:
    """Get the global icon manager instance"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


def get_icon(name: str, size: Union[IconSize, int] = IconSize.MEDIUM) -> QIcon:
    """Convenience function to get an icon"""
    return get_icon_manager().get_icon(name, size)


def get_emoji(name: str) -> str:
    """Convenience function to get emoji fallback"""
    return get_icon_manager().get_emoji_fallback(name)