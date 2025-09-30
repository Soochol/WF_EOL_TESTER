"""Color definitions for content widgets.

Provides centralized color management with theme support and semantic color naming.
Supports dark theme with accessibility considerations.
"""

from enum import Enum
from typing import Dict, NamedTuple


class ColorScheme(NamedTuple):
    """Color scheme definition for UI theming."""
    
    # Background colors
    background_primary: str
    background_secondary: str
    background_tertiary: str
    background_elevated: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_muted: str
    text_disabled: str
    
    # Accent colors
    accent_primary: str
    accent_hover: str
    accent_pressed: str
    accent_disabled: str
    
    # Status colors
    success: str
    success_light: str
    warning: str
    warning_light: str
    error: str
    error_light: str
    info: str
    info_light: str
    
    # Border colors
    border_primary: str
    border_secondary: str
    border_muted: str
    border_focus: str


class Colors:
    """Centralized color definitions for content widgets."""
    
    # Dark theme color scheme (default)
    DARK = ColorScheme(
        # Background colors
        background_primary="#1e1e1e",
        background_secondary="#2d2d2d",
        background_tertiary="#3d3d3d",
        background_elevated="#404040",
        
        # Text colors
        text_primary="#ffffff",
        text_secondary="#cccccc",
        text_muted="#888888",
        text_disabled="#666666",
        
        # Accent colors
        accent_primary="#0078d4",
        accent_hover="#106ebe",
        accent_pressed="#005a9e",
        accent_disabled="#404040",
        
        # Status colors
        success="#00ff00",
        success_light="#00cc00",
        warning="#ffaa00",
        warning_light="#ff8800",
        error="#ff4444",
        error_light="#cc0000",
        info="#4da6ff",
        info_light="#0078d4",
        
        # Border colors
        border_primary="#404040",
        border_secondary="#555555",
        border_muted="#333333",
        border_focus="#0078d4",
    )
    
    # Light theme color scheme
    LIGHT = ColorScheme(
        # Background colors
        background_primary="#ffffff",
        background_secondary="#f5f5f5",
        background_tertiary="#e5e5e5",
        background_elevated="#f0f0f0",
        
        # Text colors
        text_primary="#000000",
        text_secondary="#333333",
        text_muted="#777777",
        text_disabled="#999999",
        
        # Accent colors
        accent_primary="#0078d4",
        accent_hover="#106ebe",
        accent_pressed="#005a9e",
        accent_disabled="#cccccc",
        
        # Status colors
        success="#00aa00",
        success_light="#00cc00",
        warning="#ff8800",
        warning_light="#ffaa00",
        error="#cc0000",
        error_light="#ff4444",
        info="#0078d4",
        info_light="#4da6ff",
        
        # Border colors
        border_primary="#cccccc",
        border_secondary="#aaaaaa",
        border_muted="#e0e0e0",
        border_focus="#0078d4",
    )
    
    # High contrast theme for accessibility
    HIGH_CONTRAST = ColorScheme(
        # Background colors
        background_primary="#000000",
        background_secondary="#1a1a1a",
        background_tertiary="#2a2a2a",
        background_elevated="#333333",
        
        # Text colors
        text_primary="#ffffff",
        text_secondary="#eeeeee",
        text_muted="#bbbbbb",
        text_disabled="#777777",
        
        # Accent colors
        accent_primary="#00aaff",
        accent_hover="#3399ff",
        accent_pressed="#0088cc",
        accent_disabled="#555555",
        
        # Status colors
        success="#00ff00",
        success_light="#33ff33",
        warning="#ffff00",
        warning_light="#ffff66",
        error="#ff0000",
        error_light="#ff6666",
        info="#00ffff",
        info_light="#66ffff",
        
        # Border colors
        border_primary="#666666",
        border_secondary="#888888",
        border_muted="#444444",
        border_focus="#00aaff",
    )
    
    # Default theme
    DEFAULT = DARK


class ThemeType(Enum):
    """Available theme types."""
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"


def get_theme_colors(theme: ThemeType = ThemeType.DARK) -> ColorScheme:
    """Get color scheme for specified theme.
    
    Args:
        theme: Theme type to retrieve colors for
        
    Returns:
        ColorScheme: Color scheme for the specified theme
    """
    theme_map = {
        ThemeType.DARK: Colors.DARK,
        ThemeType.LIGHT: Colors.LIGHT,
        ThemeType.HIGH_CONTRAST: Colors.HIGH_CONTRAST,
    }
    
    return theme_map.get(theme, Colors.DEFAULT)


def get_status_color(status: str, theme: ThemeType = ThemeType.DARK, light: bool = False) -> str:
    """Get status-specific color.
    
    Args:
        status: Status type (success, error, warning, info)
        theme: Theme type
        light: Whether to use light variant of the color
        
    Returns:
        str: Hex color code for the status
    """
    colors = get_theme_colors(theme)
    
    status_map = {
        "success": colors.success_light if light else colors.success,
        "error": colors.error_light if light else colors.error,
        "warning": colors.warning_light if light else colors.warning,
        "info": colors.info_light if light else colors.info,
    }
    
    return status_map.get(status.lower(), colors.text_muted)


def get_semantic_colors() -> Dict[str, str]:
    """Get semantic color mappings for common UI states.
    
    Returns:
        Dict[str, str]: Mapping of semantic names to hex colors
    """
    colors = Colors.DEFAULT
    
    return {
        # States
        "ready": colors.text_secondary,
        "running": colors.warning,
        "completed": colors.success,
        "failed": colors.error,
        "paused": colors.info,
        "stopped": colors.warning_light,
        "emergency": colors.error_light,
        
        # Hardware states
        "connected": colors.success,
        "disconnected": colors.text_muted,
        "connecting": colors.warning,
        "error_hw": colors.error,
        
        # Button states
        "primary": colors.accent_primary,
        "secondary": colors.background_tertiary,
        "danger": colors.error,
        "success_btn": colors.success,
        "warning_btn": colors.warning,
    }


def create_gradient(color1: str, color2: str, direction: str = "horizontal") -> str:
    """Create CSS gradient string.
    
    Args:
        color1: Start color (hex)
        color2: End color (hex)
        direction: Gradient direction (horizontal, vertical, diagonal)
        
    Returns:
        str: CSS gradient definition
    """
    direction_map = {
        "horizontal": "x1: 0, y1: 0, x2: 1, y2: 0",
        "vertical": "x1: 0, y1: 0, x2: 0, y2: 1",
        "diagonal": "x1: 0, y1: 0, x2: 1, y2: 1",
    }
    
    coords = direction_map.get(direction, direction_map["horizontal"])
    
    return f"qlineargradient({coords}, stop: 0 {color1}, stop: 1 {color2})"


def adjust_opacity(color: str, opacity: float) -> str:
    """Adjust color opacity.
    
    Args:
        color: Hex color code
        opacity: Opacity value (0.0 to 1.0)
        
    Returns:
        str: Color with adjusted opacity
    """
    # Convert hex to RGB
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Return RGBA format
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"


def lighten_color(color: str, factor: float = 0.2) -> str:
    """Lighten a color by a given factor.
    
    Args:
        color: Hex color code
        factor: Lightening factor (0.0 to 1.0)
        
    Returns:
        str: Lightened color
    """
    color = color.lstrip('#')
    rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
    
    # Lighten each component
    for i in range(3):
        rgb[i] = min(255, int(rgb[i] + (255 - rgb[i]) * factor))
    
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def darken_color(color: str, factor: float = 0.2) -> str:
    """Darken a color by a given factor.
    
    Args:
        color: Hex color code
        factor: Darkening factor (0.0 to 1.0)
        
    Returns:
        str: Darkened color
    """
    color = color.lstrip('#')
    rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
    
    # Darken each component
    for i in range(3):
        rgb[i] = max(0, int(rgb[i] * (1 - factor)))
    
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
