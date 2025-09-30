"""
SVG Icon Provider

Advanced SVG icon rendering with color theming support.
Provides high-quality 24x24px icons with customizable colors.
"""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from loguru import logger


class SVGIconProvider:
    """
    SVG icon provider with theme-based color rendering.

    Renders SVG icons at high quality with customizable stroke colors.
    Supports caching for performance.
    """

    def __init__(self, icons_path: Optional[Path] = None):
        """
        Initialize SVG icon provider.

        Args:
            icons_path: Path to icons directory (auto-detected if None)
        """
        if icons_path is None:
            current_file = Path(__file__)
            icons_path = current_file.parent.parent / "resources" / "icons"

        self.icons_path = Path(icons_path)
        self._icon_cache = {}

        # Default colors for different states
        self.colors = {
            "default": "#cccccc",
            "hover": "#ffffff",
            "active": "#63b3ed",
            "disabled": "#666666",
        }

    def get_icon(
        self,
        name: str,
        size: int = 24,
        color: Optional[str] = None,
        state: str = "default"
    ) -> QIcon:
        """
        Get SVG icon with specified size and color.

        Args:
            name: Icon name (without .svg extension)
            size: Icon size in pixels (default: 24)
            color: Custom color hex (overrides state color)
            state: Icon state - default, hover, active, disabled

        Returns:
            QIcon object
        """
        # Determine color
        if color is None:
            color = self.colors.get(state, self.colors["default"])

        # Create cache key
        cache_key = f"{name}_{size}_{color}"

        # Check cache
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Load and render SVG
        icon = self._render_svg_icon(name, size, color)

        # Cache result
        self._icon_cache[cache_key] = icon
        return icon

    def _render_svg_icon(self, name: str, size: int, color: str) -> QIcon:
        """Render SVG icon with specified color"""
        svg_path = self.icons_path / f"{name}.svg"

        if not svg_path.exists():
            logger.debug(f"SVG icon not found: {svg_path}")
            return QIcon()

        try:
            # Read SVG content
            svg_content = svg_path.read_text(encoding='utf-8')

            # Replace currentColor with specified color
            svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
            svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')

            # Create SVG renderer
            renderer = QSvgRenderer()
            if not renderer.load(svg_content.encode('utf-8')):
                logger.error(f"Failed to load SVG: {name}")
                return QIcon()

            # Create pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            # Render SVG to pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()

            # Create icon
            icon = QIcon(pixmap)
            return icon

        except Exception as e:
            logger.error(f"Error rendering SVG icon {name}: {e}")
            return QIcon()

    def get_multi_state_icon(self, name: str, size: int = 24) -> QIcon:
        """
        Create icon with multiple states (normal, hover, pressed, disabled).

        Args:
            name: Icon name
            size: Icon size

        Returns:
            QIcon with multiple states
        """
        icon = QIcon()

        # Normal state
        normal_pixmap = self._render_svg_to_pixmap(name, size, self.colors["default"])
        if not normal_pixmap.isNull():
            icon.addPixmap(normal_pixmap, QIcon.Mode.Normal, QIcon.State.Off)

        # Active state
        active_pixmap = self._render_svg_to_pixmap(name, size, self.colors["active"])
        if not active_pixmap.isNull():
            icon.addPixmap(active_pixmap, QIcon.Mode.Normal, QIcon.State.On)
            icon.addPixmap(active_pixmap, QIcon.Mode.Selected)

        # Disabled state
        disabled_pixmap = self._render_svg_to_pixmap(name, size, self.colors["disabled"])
        if not disabled_pixmap.isNull():
            icon.addPixmap(disabled_pixmap, QIcon.Mode.Disabled)

        return icon

    def _render_svg_to_pixmap(self, name: str, size: int, color: str) -> QPixmap:
        """Helper to render SVG to pixmap"""
        svg_path = self.icons_path / f"{name}.svg"

        if not svg_path.exists():
            return QPixmap()

        try:
            svg_content = svg_path.read_text(encoding='utf-8')
            svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
            svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')

            renderer = QSvgRenderer()
            if not renderer.load(svg_content.encode('utf-8')):
                return QPixmap()

            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()

            return pixmap

        except Exception as e:
            logger.error(f"Error rendering SVG to pixmap {name}: {e}")
            return QPixmap()

    def set_color_theme(
        self,
        default: Optional[str] = None,
        hover: Optional[str] = None,
        active: Optional[str] = None,
        disabled: Optional[str] = None
    ):
        """
        Update color theme for icons.

        Args:
            default: Default icon color
            hover: Hover state color
            active: Active/selected state color
            disabled: Disabled state color
        """
        if default:
            self.colors["default"] = default
        if hover:
            self.colors["hover"] = hover
        if active:
            self.colors["active"] = active
        if disabled:
            self.colors["disabled"] = disabled

        # Clear cache to re-render with new colors
        self._icon_cache.clear()
        logger.info("Icon color theme updated")

    def clear_cache(self):
        """Clear icon cache"""
        self._icon_cache.clear()
        logger.debug("SVG icon cache cleared")


# Global instance
_svg_icon_provider: Optional[SVGIconProvider] = None


def get_svg_icon_provider() -> SVGIconProvider:
    """Get global SVG icon provider instance"""
    global _svg_icon_provider
    if _svg_icon_provider is None:
        _svg_icon_provider = SVGIconProvider()
    return _svg_icon_provider


def get_svg_icon(name: str, size: int = 24, color: Optional[str] = None) -> QIcon:
    """Convenience function to get SVG icon"""
    return get_svg_icon_provider().get_icon(name, size, color)