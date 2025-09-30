"""
Dashboard Widget Styles

Centralized styling configuration for dashboard widgets following Material Design principles.
"""

# Standard library imports
from typing import Dict, Any


class DashboardStyles:
    """
    Centralized style definitions for dashboard widgets.
    
    Provides consistent styling across dashboard components with support for themes,
    responsive design, and accessibility features.
    """
    
    # Color palette - Dark theme with professional accents
    COLORS = {
        "background_primary": "#1e1e1e",
        "background_secondary": "#2d2d2d", 
        "text_primary": "#cccccc",
        "text_secondary": "#ffffff",
        "border_primary": "#404040",
        "border_secondary": "#606060",
        "accent_blue": "#0078d4",
        "success_green": "#107c10",
        "warning_orange": "#ff8c00",
        "error_red": "#d13438",
    }
    
    # Typography settings
    TYPOGRAPHY = {
        "font_family": "Segoe UI, Arial, sans-serif",
        "font_size_small": "12px",
        "font_size_normal": "14px",
        "font_size_large": "16px",
        "font_weight_normal": "normal",
        "font_weight_bold": "bold",
    }
    
    # Spacing and layout constants
    SPACING = {
        "xs": "4px",
        "sm": "8px", 
        "md": "12px",
        "lg": "16px",
        "xl": "24px",
    }
    
    # Border radius values
    BORDER_RADIUS = {
        "small": "4px",
        "medium": "6px",
        "large": "8px",
    }
    
    @classmethod
    def get_dashboard_widget_style(cls) -> str:
        """
        Get main dashboard widget stylesheet.
        
        Returns:
            str: Complete CSS stylesheet for dashboard widget
        """
        return f"""
        DashboardWidget {{
            background-color: {cls.COLORS["background_primary"]};
            color: {cls.COLORS["text_primary"]};
            font-family: {cls.TYPOGRAPHY["font_family"]};
            border-radius: {cls.BORDER_RADIUS["medium"]};
        }}
        
        DashboardWidget QWidget {{
            background-color: transparent;
        }}
        
        /* Ensure proper text rendering */
        DashboardWidget QLabel {{
            color: {cls.COLORS["text_primary"]};
            font-size: {cls.TYPOGRAPHY["font_size_normal"]};
        }}
        """
    
    @classmethod
    def get_section_style(cls, section_type: str = "default") -> str:
        """
        Get section-specific styling.
        
        Args:
            section_type: Type of section (hardware, progress, results)
            
        Returns:
            str: CSS stylesheet for the section
        """
        base_style = f"""
        QWidget {{
            background-color: transparent;
            border-radius: {cls.BORDER_RADIUS["small"]};
        }}
        """
        
        section_styles = {
            "hardware": f"""
            /* Hardware status section styling */
            QGroupBox {{
                border: 2px solid {cls.COLORS["border_primary"]};
                border-radius: {cls.BORDER_RADIUS["medium"]};
                margin-top: {cls.SPACING["md"]};
                padding-top: {cls.SPACING["md"]};
                color: {cls.COLORS["text_secondary"]};
                font-weight: {cls.TYPOGRAPHY["font_weight_bold"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {cls.SPACING["md"]};
                padding: 0 {cls.SPACING["sm"]} 0 {cls.SPACING["sm"]};
                color: {cls.COLORS["accent_blue"]};
            }}
            """,
            
            "progress": f"""
            /* Test progress section styling */
            QProgressBar {{
                border: 1px solid {cls.COLORS["border_primary"]};
                border-radius: {cls.BORDER_RADIUS["small"]};
                background-color: {cls.COLORS["background_secondary"]};
                text-align: center;
                color: {cls.COLORS["text_primary"]};
                font-weight: {cls.TYPOGRAPHY["font_weight_bold"]};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.COLORS["accent_blue"]};
                border-radius: {cls.BORDER_RADIUS["small"]};
            }}
            """,
            
            "results": f"""
            /* Results table section styling */
            QTableWidget {{
                gridline-color: {cls.COLORS["border_primary"]};
                background-color: {cls.COLORS["background_primary"]};
                color: {cls.COLORS["text_primary"]};
                border: 1px solid {cls.COLORS["border_primary"]};
                border-radius: {cls.BORDER_RADIUS["medium"]};
                selection-background-color: {cls.COLORS["accent_blue"]};
            }}
            
            QTableWidget::item {{
                padding: {cls.SPACING["sm"]};
                border-bottom: 1px solid {cls.COLORS["border_primary"]};
            }}
            
            QHeaderView::section {{
                background-color: {cls.COLORS["background_secondary"]};
                color: {cls.COLORS["text_secondary"]};
                padding: {cls.SPACING["sm"]};
                border: 1px solid {cls.COLORS["border_primary"]};
                font-weight: {cls.TYPOGRAPHY["font_weight_bold"]};
            }}
            """
        }
        
        return base_style + section_styles.get(section_type, "")
    
    @classmethod
    def get_responsive_style(cls, container_width: int) -> str:
        """
        Get responsive styling based on container width.
        
        Args:
            container_width: Width of the container in pixels
            
        Returns:
            str: Responsive CSS adjustments
        """
        if container_width < 800:
            # Compact layout for smaller screens
            return f"""
            DashboardWidget {{
                font-size: {cls.TYPOGRAPHY["font_size_small"]};
            }}
            
            QLabel {{
                font-size: {cls.TYPOGRAPHY["font_size_small"]};
                padding: {cls.SPACING["xs"]};
            }}
            """
        else:
            # Standard layout for larger screens
            return f"""
            DashboardWidget {{
                font-size: {cls.TYPOGRAPHY["font_size_normal"]};
            }}
            
            QLabel {{
                font-size: {cls.TYPOGRAPHY["font_size_normal"]};
                padding: {cls.SPACING["sm"]};
            }}
            """
    
    @classmethod
    def get_theme_style(cls, theme: str = "dark") -> Dict[str, Any]:
        """
        Get theme-specific color configuration.
        
        Args:
            theme: Theme name (dark, light, high_contrast)
            
        Returns:
            Dict[str, Any]: Theme configuration
        """
        themes = {
            "dark": cls.COLORS,
            "light": {
                "background_primary": "#ffffff",
                "background_secondary": "#f5f5f5",
                "text_primary": "#333333",
                "text_secondary": "#000000", 
                "border_primary": "#cccccc",
                "border_secondary": "#999999",
                "accent_blue": "#0078d4",
                "success_green": "#107c10",
                "warning_orange": "#ff8c00",
                "error_red": "#d13438",
            },
            "high_contrast": {
                "background_primary": "#000000",
                "background_secondary": "#1a1a1a",
                "text_primary": "#ffffff",
                "text_secondary": "#ffffff",
                "border_primary": "#ffffff", 
                "border_secondary": "#cccccc",
                "accent_blue": "#00ff00",
                "success_green": "#00ff00",
                "warning_orange": "#ffff00",
                "error_red": "#ff0000",
            }
        }
        
        return themes.get(theme, cls.COLORS)
