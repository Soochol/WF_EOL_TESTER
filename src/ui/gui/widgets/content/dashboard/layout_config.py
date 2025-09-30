"""
Dashboard Layout Configuration

Centralized layout configuration for dashboard widgets with responsive design support.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class LayoutMetrics:
    """
    Immutable layout metrics configuration.
    
    Provides consistent spacing, sizing, and layout values across dashboard components.
    """
    
    # Spacing values (in pixels)
    spacing_xs: int = 4
    spacing_sm: int = 8 
    spacing_md: int = 12
    spacing_lg: int = 16
    spacing_xl: int = 24
    
    # Margin values (in pixels)
    margin_xs: int = 4
    margin_sm: int = 8
    margin_md: int = 12
    margin_lg: int = 16
    margin_xl: int = 24
    
    # Padding values (in pixels)
    padding_xs: int = 4
    padding_sm: int = 8
    padding_md: int = 12
    padding_lg: int = 16
    padding_xl: int = 24
    
    # Widget sizing
    min_widget_height: int = 100
    min_widget_width: int = 200
    max_widget_height: int = 600
    max_widget_width: int = 1200
    
    # Section heights (relative weights)
    hardware_section_height: int = 0  # Auto-size
    progress_section_height: int = 0  # Auto-size  
    results_section_height: int = 1   # Takes remaining space
    
    # Responsive breakpoints
    breakpoint_small: int = 600
    breakpoint_medium: int = 800
    breakpoint_large: int = 1200


@dataclass(frozen=True)
class SectionConfig:
    """
    Configuration for individual dashboard sections.
    
    Defines layout properties for hardware status, test progress, and results sections.
    """
    
    name: str
    spacing: int
    margins: Tuple[int, int, int, int]  # top, right, bottom, left
    stretch_factor: int = 0  # 0 = auto-size, >0 = relative stretch
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    visible: bool = True
    
    @property
    def margin_top(self) -> int:
        """Get top margin."""
        return self.margins[0]
        
    @property 
    def margin_right(self) -> int:
        """Get right margin."""
        return self.margins[1]
        
    @property
    def margin_bottom(self) -> int:
        """Get bottom margin."""
        return self.margins[2]
        
    @property
    def margin_left(self) -> int:
        """Get left margin."""
        return self.margins[3]


class DashboardLayoutConfig:
    """
    Centralized layout configuration for dashboard widgets.
    
    Provides flexible, responsive layout configuration with support for different
    screen sizes and user preferences.
    """
    
    def __init__(self, layout_mode: str = "default"):
        """
        Initialize layout configuration.
        
        Args:
            layout_mode: Layout mode (default, compact, expanded)
        """
        self.layout_mode = layout_mode
        self.metrics = self._get_layout_metrics()
        self.sections = self._get_section_configs()
    
    def _get_layout_metrics(self) -> LayoutMetrics:
        """
        Get layout metrics based on current mode.
        
        Returns:
            LayoutMetrics: Configured layout metrics
        """
        if self.layout_mode == "compact":
            return LayoutMetrics(
                spacing_xs=2, spacing_sm=4, spacing_md=6, spacing_lg=8, spacing_xl=12,
                margin_xs=2, margin_sm=4, margin_md=6, margin_lg=8, margin_xl=12,
                padding_xs=2, padding_sm=4, padding_md=6, padding_lg=8, padding_xl=12,
                min_widget_height=80, min_widget_width=150
            )
        elif self.layout_mode == "expanded":
            return LayoutMetrics(
                spacing_xs=6, spacing_sm=12, spacing_md=18, spacing_lg=24, spacing_xl=36,
                margin_xs=6, margin_sm=12, margin_md=18, margin_lg=24, margin_xl=36,
                padding_xs=6, padding_sm=12, padding_md=18, padding_lg=24, padding_xl=36,
                min_widget_height=120, min_widget_width=250
            )
        else:  # default
            return LayoutMetrics()
    
    def _get_section_configs(self) -> Dict[str, SectionConfig]:
        """
        Get section configurations for current layout mode.
        
        Returns:
            Dict[str, SectionConfig]: Section configurations by name
        """
        metrics = self.metrics
        
        configs = {
            "hardware_status": SectionConfig(
                name="hardware_status",
                spacing=metrics.spacing_md,
                margins=(
                    metrics.margin_md, metrics.margin_md,
                    metrics.margin_sm, metrics.margin_md
                ),
                stretch_factor=0,  # Auto-size based on content
                min_height=120 if self.layout_mode != "compact" else 100
            ),
            
            "test_progress": SectionConfig(
                name="test_progress", 
                spacing=metrics.spacing_md,
                margins=(
                    metrics.margin_sm, metrics.margin_md,
                    metrics.margin_sm, metrics.margin_md
                ),
                stretch_factor=0,  # Auto-size based on content
                min_height=80 if self.layout_mode != "compact" else 60
            ),
            
            "results_table": SectionConfig(
                name="results_table",
                spacing=metrics.spacing_md,
                margins=(
                    metrics.margin_sm, metrics.margin_md,
                    metrics.margin_md, metrics.margin_md
                ),
                stretch_factor=1,  # Takes remaining vertical space
                min_height=200 if self.layout_mode != "compact" else 150
            )
        }
        
        return configs
    
    def get_main_layout_config(self) -> Dict[str, int]:
        """
        Get main layout configuration for the dashboard widget.
        
        Returns:
            Dict[str, int]: Layout configuration with spacing and margins
        """
        return {
            "spacing": self.metrics.spacing_md,
            "margin_top": self.metrics.margin_md,
            "margin_right": self.metrics.margin_md,
            "margin_bottom": self.metrics.margin_md,
            "margin_left": self.metrics.margin_md,
        }
    
    def get_section_config(self, section_name: str) -> Optional[SectionConfig]:
        """
        Get configuration for a specific section.
        
        Args:
            section_name: Name of the section (hardware_status, test_progress, results_table)
            
        Returns:
            Optional[SectionConfig]: Section configuration or None if not found
        """
        return self.sections.get(section_name)
    
    def get_responsive_config(self, container_width: int) -> "DashboardLayoutConfig":
        """
        Get responsive layout configuration based on container width.
        
        Args:
            container_width: Width of the container in pixels
            
        Returns:
            DashboardLayoutConfig: Adjusted layout configuration
        """
        if container_width < self.metrics.breakpoint_small:
            return DashboardLayoutConfig("compact")
        elif container_width > self.metrics.breakpoint_large:
            return DashboardLayoutConfig("expanded")
        else:
            return DashboardLayoutConfig("default")
    
    def apply_to_layout(self, layout, section_name: str = "main") -> None:
        """
        Apply configuration to a Qt layout object.
        
        Args:
            layout: Qt layout object (QVBoxLayout, QHBoxLayout, etc.)
            section_name: Name of the section for specific configuration
        """
        if section_name == "main":
            config = self.get_main_layout_config()
            layout.setSpacing(config["spacing"])
            layout.setContentsMargins(
                config["margin_left"],
                config["margin_top"],
                config["margin_right"],
                config["margin_bottom"]
            )
        else:
            section_config = self.get_section_config(section_name)
            if section_config:
                layout.setSpacing(section_config.spacing)
                layout.setContentsMargins(
                    section_config.margin_left,
                    section_config.margin_top,
                    section_config.margin_right,
                    section_config.margin_bottom
                )
    
    def get_stretch_factors(self) -> Dict[str, int]:
        """
        Get stretch factors for all sections.
        
        Returns:
            Dict[str, int]: Stretch factors by section name
        """
        return {
            name: config.stretch_factor 
            for name, config in self.sections.items()
        }
    
    @classmethod
    def create_preset(cls, preset_name: str) -> "DashboardLayoutConfig":
        """
        Create a layout configuration from a preset.
        
        Args:
            preset_name: Name of the preset (minimal, standard, detailed)
            
        Returns:
            DashboardLayoutConfig: Configured layout
        """
        preset_mappings = {
            "minimal": "compact",
            "standard": "default", 
            "detailed": "expanded"
        }
        
        layout_mode = preset_mappings.get(preset_name, "default")
        return cls(layout_mode)
