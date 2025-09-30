"""
Common stylesheet definitions for GUI widgets.

Provides reusable styles to maintain consistency across the application.
"""

from typing import Dict


class CommonStyles:
    """
    Collection of common stylesheet definitions.
    """
    
    @staticmethod
    def get_dark_theme() -> Dict[str, str]:
        """Get dark theme color palette"""
        return {
            "background": "#1e1e1e",
            "text": "#cccccc",
            "text_light": "#ffffff",
            "border": "#404040",
            "primary": "#0078d4",
            "primary_hover": "#106ebe",
            "primary_pressed": "#005a9e",
            "warning": "#cc6600",
            "warning_dark": "#aa5500",
            "secondary": "#2d2d2d",
        }
    
    @staticmethod
    def get_widget_base_style() -> str:
        """Get base widget stylesheet"""
        colors = CommonStyles.get_dark_theme()
        return f"""
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        """
    
    @staticmethod
    def get_group_box_style() -> str:
        """Get group box stylesheet"""
        colors = CommonStyles.get_dark_theme()
        return f"""
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors['border']};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: {colors['text_light']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        """
    
    @staticmethod
    def get_label_style() -> str:
        """Get label stylesheet"""
        colors = CommonStyles.get_dark_theme()
        return f"""
        QLabel {{
            color: {colors['text']};
            font-size: 14px;
        }}
        """
    
    @staticmethod
    def get_button_style() -> str:
        """Get button stylesheet"""
        colors = CommonStyles.get_dark_theme()
        return f"""
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: 1px solid {colors['primary_hover']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 80px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {colors['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: {colors['primary_pressed']};
        }}
        QPushButton:checked {{
            background-color: {colors['warning']};
            border-color: {colors['warning_dark']};
        }}
        """
    
    @staticmethod
    def get_combo_box_style() -> str:
        """Get combo box stylesheet"""
        colors = CommonStyles.get_dark_theme()
        return f"""
        QComboBox {{
            background-color: {colors['secondary']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 3px;
            padding: 5px;
            min-width: 80px;
            min-height: 25px;
        }}
        QComboBox:hover {{
            border-color: {colors['primary']};
        }}
        """
    
    @staticmethod
    def get_complete_style() -> str:
        """Get complete stylesheet combining all components"""
        return (
            CommonStyles.get_widget_base_style() +
            CommonStyles.get_group_box_style() +
            CommonStyles.get_label_style() +
            CommonStyles.get_button_style() +
            CommonStyles.get_combo_box_style()
        )
