"""Font definitions for content widgets.

Provides centralized font management with size, weight, and family configurations.
Supports responsive font sizing and accessibility features.
"""

from enum import Enum
from typing import Dict, NamedTuple
from PySide6.QtGui import QFont


class FontSize(Enum):
    """Standard font sizes."""
    TINY = 8
    SMALL = 10
    NORMAL = 12
    MEDIUM = 14
    LARGE = 16
    XLARGE = 18
    XXLARGE = 20
    HUGE = 24
    MASSIVE = 32


class FontWeight(Enum):
    """Font weight definitions."""
    THIN = QFont.Weight.Thin
    LIGHT = QFont.Weight.Light
    NORMAL = QFont.Weight.Normal
    MEDIUM = QFont.Weight.Medium
    SEMIBOLD = QFont.Weight.DemiBold
    BOLD = QFont.Weight.Bold
    EXTRABOLD = QFont.Weight.ExtraBold
    BLACK = QFont.Weight.Black


class FontFamily(Enum):
    """Font family definitions."""
    SYSTEM = ""  # Use system default
    MONOSPACE = "Consolas, 'Courier New', monospace"
    SANS_SERIF = "'Segoe UI', Arial, sans-serif"
    SERIF = "'Times New Roman', serif"


class FontConfig(NamedTuple):
    """Font configuration definition."""
    family: str
    size: int
    weight: QFont.Weight
    italic: bool = False
    underline: bool = False
    strikeout: bool = False


class Fonts:
    """Centralized font definitions for content widgets."""
    
    # Base font configurations
    BASE = FontConfig(
        family=FontFamily.SYSTEM.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.NORMAL.value
    )
    
    # Heading fonts
    HEADING_LARGE = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.XXLARGE.value,
        weight=FontWeight.BOLD.value
    )
    
    HEADING_MEDIUM = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.LARGE.value,
        weight=FontWeight.BOLD.value
    )
    
    HEADING_SMALL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.BOLD.value
    )
    
    # Body text fonts
    BODY_LARGE = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.NORMAL.value
    )
    
    BODY_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.NORMAL.value
    )
    
    BODY_SMALL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.SMALL.value,
        weight=FontWeight.NORMAL.value
    )
    
    # UI element fonts
    BUTTON_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.BOLD.value
    )
    
    BUTTON_LARGE = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.LARGE.value,
        weight=FontWeight.BOLD.value
    )
    
    LABEL_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.NORMAL.value
    )
    
    LABEL_BOLD = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.BOLD.value
    )
    
    # Input fonts
    INPUT_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.NORMAL.value
    )
    
    INPUT_MONOSPACE = FontConfig(
        family=FontFamily.MONOSPACE.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.NORMAL.value
    )
    
    # Status and indicator fonts
    STATUS_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.BOLD.value
    )
    
    STATUS_LARGE = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.BOLD.value
    )
    
    # Code and monospace fonts
    CODE_NORMAL = FontConfig(
        family=FontFamily.MONOSPACE.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.NORMAL.value
    )
    
    CODE_SMALL = FontConfig(
        family=FontFamily.MONOSPACE.value,
        size=FontSize.SMALL.value,
        weight=FontWeight.NORMAL.value
    )
    
    # Group box fonts
    GROUP_TITLE = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.MEDIUM.value,
        weight=FontWeight.BOLD.value
    )
    
    # Tab fonts
    TAB_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.MEDIUM.value
    )
    
    # Menu fonts
    MENU_NORMAL = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.NORMAL.value,
        weight=FontWeight.NORMAL.value
    )
    
    # Tooltip fonts
    TOOLTIP = FontConfig(
        family=FontFamily.SANS_SERIF.value,
        size=FontSize.SMALL.value,
        weight=FontWeight.NORMAL.value
    )


def create_qfont(config: FontConfig) -> QFont:
    """Create QFont from FontConfig.
    
    Args:
        config: Font configuration
        
    Returns:
        QFont: Configured QFont instance
    """
    font = QFont()
    
    if config.family:
        font.setFamily(config.family)
    
    font.setPointSize(config.size)
    font.setWeight(config.weight)
    font.setItalic(config.italic)
    font.setUnderline(config.underline)
    font.setStrikeOut(config.strikeout)
    
    return font


def get_font_config(font_type: str) -> FontConfig:
    """Get font configuration by type name.
    
    Args:
        font_type: Font type name (e.g., 'heading_large', 'body_normal')
        
    Returns:
        FontConfig: Font configuration for the specified type
    """
    font_map = {
        "base": Fonts.BASE,
        "heading_large": Fonts.HEADING_LARGE,
        "heading_medium": Fonts.HEADING_MEDIUM,
        "heading_small": Fonts.HEADING_SMALL,
        "body_large": Fonts.BODY_LARGE,
        "body_normal": Fonts.BODY_NORMAL,
        "body_small": Fonts.BODY_SMALL,
        "button_normal": Fonts.BUTTON_NORMAL,
        "button_large": Fonts.BUTTON_LARGE,
        "label_normal": Fonts.LABEL_NORMAL,
        "label_bold": Fonts.LABEL_BOLD,
        "input_normal": Fonts.INPUT_NORMAL,
        "input_monospace": Fonts.INPUT_MONOSPACE,
        "status_normal": Fonts.STATUS_NORMAL,
        "status_large": Fonts.STATUS_LARGE,
        "code_normal": Fonts.CODE_NORMAL,
        "code_small": Fonts.CODE_SMALL,
        "group_title": Fonts.GROUP_TITLE,
        "tab_normal": Fonts.TAB_NORMAL,
        "menu_normal": Fonts.MENU_NORMAL,
        "tooltip": Fonts.TOOLTIP,
    }
    
    return font_map.get(font_type.lower(), Fonts.BASE)


def create_font(font_type: str) -> QFont:
    """Create QFont by type name.
    
    Args:
        font_type: Font type name
        
    Returns:
        QFont: Configured QFont instance
    """
    config = get_font_config(font_type)
    return create_qfont(config)


def get_font_css(config: FontConfig) -> str:
    """Generate CSS font definition from FontConfig.
    
    Args:
        config: Font configuration
        
    Returns:
        str: CSS font definition
    """
    weight_map = {
        QFont.Weight.Thin: "100",
        QFont.Weight.Light: "300",
        QFont.Weight.Normal: "400",
        QFont.Weight.Medium: "500",
        QFont.Weight.DemiBold: "600",
        QFont.Weight.Bold: "700",
        QFont.Weight.ExtraBold: "800",
        QFont.Weight.Black: "900",
    }
    
    css_parts = []
    
    if config.family:
        css_parts.append(f"font-family: {config.family};")
    
    css_parts.append(f"font-size: {config.size}px;")
    css_parts.append(f"font-weight: {weight_map.get(config.weight, '400')};")
    
    if config.italic:
        css_parts.append("font-style: italic;")
    
    if config.underline:
        css_parts.append("text-decoration: underline;")
    
    if config.strikeout:
        css_parts.append("text-decoration: line-through;")
    
    return " ".join(css_parts)


def get_responsive_font_size(base_size: int, scale_factor: float = 1.0) -> int:
    """Calculate responsive font size.
    
    Args:
        base_size: Base font size
        scale_factor: Scaling factor based on screen size/density
        
    Returns:
        int: Scaled font size
    """
    scaled_size = int(base_size * scale_factor)
    return max(FontSize.TINY.value, min(FontSize.MASSIVE.value, scaled_size))


def create_responsive_font_config(
    base_config: FontConfig, 
    scale_factor: float = 1.0
) -> FontConfig:
    """Create responsive font configuration.
    
    Args:
        base_config: Base font configuration
        scale_factor: Scaling factor
        
    Returns:
        FontConfig: Scaled font configuration
    """
    return FontConfig(
        family=base_config.family,
        size=get_responsive_font_size(base_config.size, scale_factor),
        weight=base_config.weight,
        italic=base_config.italic,
        underline=base_config.underline,
        strikeout=base_config.strikeout,
    )


def get_font_metrics_info(font: QFont) -> Dict[str, int]:
    """Get font metrics information.
    
    Args:
        font: QFont instance
        
    Returns:
        Dict[str, int]: Font metrics information
    """
    from PySide6.QtGui import QFontMetrics
    
    metrics = QFontMetrics(font)
    
    return {
        "height": metrics.height(),
        "ascent": metrics.ascent(),
        "descent": metrics.descent(),
        "leading": metrics.leading(),
        "line_spacing": metrics.lineSpacing(),
        "max_width": metrics.maxWidth(),
        "average_char_width": metrics.averageCharWidth(),
    }
