"""Widget-specific stylesheets for content widgets.

Provides centralized stylesheet definitions for common UI widgets including:
- Buttons with various states and types
- Group boxes with consistent styling
- Input widgets and form controls
- Status indicators and progress bars
"""

from typing import Dict, Optional
from .colors import Colors, ColorScheme, get_theme_colors, ThemeType, create_gradient
from .fonts import Fonts, get_font_css


class ButtonStyles:
    """Button stylesheet definitions."""
    
    @staticmethod
    def get_primary_button_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get primary button stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for primary buttons
        """
        return f"""
        QPushButton {{
            background-color: {colors.accent_primary};
            color: {colors.text_primary};
            border: 1px solid {colors.accent_hover};
            border-radius: 4px;
            padding: 8px 12px;
            {get_font_css(Fonts.BUTTON_NORMAL)}
            min-width: 80px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {colors.accent_hover};
        }}
        QPushButton:pressed {{
            background-color: {colors.accent_pressed};
        }}
        QPushButton:disabled {{
            background-color: {colors.accent_disabled};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """
    
    @staticmethod
    def get_secondary_button_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get secondary button stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for secondary buttons
        """
        return f"""
        QPushButton {{
            background-color: {colors.background_tertiary};
            color: {colors.text_secondary};
            border: 1px solid {colors.border_primary};
            border-radius: 4px;
            padding: 8px 12px;
            {get_font_css(Fonts.BUTTON_NORMAL)}
            min-width: 80px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {colors.background_elevated};
            border-color: {colors.border_secondary};
        }}
        QPushButton:pressed {{
            background-color: {colors.background_secondary};
        }}
        QPushButton:disabled {{
            background-color: {colors.background_secondary};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """
    
    @staticmethod
    def get_danger_button_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get danger button stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for danger buttons
        """
        return f"""
        QPushButton {{
            background-color: {colors.error};
            color: {colors.text_primary};
            border: 2px solid {colors.error_light};
            border-radius: 4px;
            padding: 8px 12px;
            {get_font_css(Fonts.BUTTON_NORMAL)}
            min-width: 80px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {colors.error_light};
        }}
        QPushButton:pressed {{
            background-color: #990000;
        }}
        QPushButton:disabled {{
            background-color: {colors.accent_disabled};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """
    
    @staticmethod
    def get_success_button_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get success button stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for success buttons
        """
        return f"""
        QPushButton {{
            background-color: {colors.success_light};
            color: {colors.text_primary};
            border: 1px solid {colors.success};
            border-radius: 4px;
            padding: 8px 12px;
            {get_font_css(Fonts.BUTTON_NORMAL)}
            min-width: 80px;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {colors.success};
        }}
        QPushButton:pressed {{
            background-color: #009900;
        }}
        QPushButton:disabled {{
            background-color: {colors.accent_disabled};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """
    
    @staticmethod
    def get_large_button_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get large button stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for large buttons
        """
        return f"""
        QPushButton {{
            background-color: {colors.accent_primary};
            color: {colors.text_primary};
            border: 1px solid {colors.accent_hover};
            border-radius: 6px;
            padding: 12px 16px;
            {get_font_css(Fonts.BUTTON_LARGE)}
            min-width: 120px;
            min-height: 45px;
        }}
        QPushButton:hover {{
            background-color: {colors.accent_hover};
        }}
        QPushButton:pressed {{
            background-color: {colors.accent_pressed};
        }}
        QPushButton:disabled {{
            background-color: {colors.accent_disabled};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """


class GroupBoxStyles:
    """Group box stylesheet definitions."""
    
    @staticmethod
    def get_standard_groupbox_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get standard group box stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for group boxes
        """
        return f"""
        QGroupBox {{
            {get_font_css(Fonts.GROUP_TITLE)}
            border: 2px solid {colors.border_primary};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: {colors.text_primary};
            background-color: {colors.background_secondary};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: {colors.background_secondary};
        }}
        """
    
    @staticmethod
    def get_elevated_groupbox_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get elevated group box stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for elevated group boxes
        """
        return f"""
        QGroupBox {{
            {get_font_css(Fonts.GROUP_TITLE)}
            border: 1px solid {colors.border_secondary};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            color: {colors.text_primary};
            background-color: {colors.background_elevated};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background-color: {colors.background_elevated};
        }}
        """


class InputStyles:
    """Input widget stylesheet definitions."""
    
    @staticmethod
    def get_line_edit_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get line edit stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for line edits
        """
        return f"""
        QLineEdit {{
            background-color: {colors.background_secondary};
            color: {colors.text_secondary};
            border: 1px solid {colors.border_primary};
            border-radius: 3px;
            padding: 5px;
            {get_font_css(Fonts.INPUT_NORMAL)}
            min-height: 20px;
        }}
        QLineEdit:hover {{
            border-color: {colors.border_focus};
        }}
        QLineEdit:focus {{
            border-color: {colors.accent_primary};
            background-color: {colors.background_tertiary};
        }}
        QLineEdit:disabled {{
            background-color: {colors.background_primary};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """
    
    @staticmethod
    def get_combo_box_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get combo box stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for combo boxes
        """
        return f"""
        QComboBox {{
            background-color: {colors.background_secondary};
            color: {colors.text_secondary};
            border: 1px solid {colors.border_primary};
            border-radius: 3px;
            padding: 5px;
            {get_font_css(Fonts.INPUT_NORMAL)}
            min-height: 25px;
        }}
        QComboBox:hover {{
            border-color: {colors.border_focus};
        }}
        QComboBox:focus {{
            border-color: {colors.accent_primary};
        }}
        QComboBox:disabled {{
            background-color: {colors.background_primary};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: {colors.border_primary};
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {colors.text_secondary};
            width: 6px;
            height: 6px;
            border-bottom: none;
            border-right: none;
            transform: rotate(45deg);
        }}
        """
    
    @staticmethod
    def get_spin_box_style(colors: ColorScheme = Colors.DARK) -> str:
        """Get spin box stylesheet.
        
        Args:
            colors: Color scheme to use
            
        Returns:
            str: CSS stylesheet for spin boxes
        """
        return f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors.background_secondary};
            color: {colors.text_secondary};
            border: 1px solid {colors.border_primary};
            border-radius: 3px;
            padding: 5px;
            {get_font_css(Fonts.INPUT_NORMAL)}
            min-height: 20px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {colors.border_focus};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {colors.accent_primary};
        }}
        QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {colors.background_primary};
            color: {colors.text_disabled};
            border-color: {colors.border_muted};
        }}
        """


class ProgressStyles:
    """Progress bar stylesheet definitions."""
    
    @staticmethod
    def get_progress_bar_style(
        colors: ColorScheme = Colors.DARK,
        status: str = "normal"
    ) -> str:
        """Get progress bar stylesheet.
        
        Args:
            colors: Color scheme to use
            status: Progress status (normal, success, error, warning)
            
        Returns:
            str: CSS stylesheet for progress bars
        """
        # Define status-specific colors
        status_colors = {
            "normal": (colors.accent_primary, colors.accent_hover),
            "success": (colors.success, colors.success_light),
            "error": (colors.error, colors.error_light),
            "warning": (colors.warning, colors.warning_light),
        }
        
        chunk_color1, chunk_color2 = status_colors.get(status, status_colors["normal"])
        
        return f"""
        QProgressBar {{
            border: 1px solid {colors.border_primary};
            border-radius: 3px;
            background-color: {colors.background_secondary};
            color: {colors.text_primary};
            text-align: center;
            {get_font_css(Fonts.STATUS_NORMAL)}
            min-height: 20px;
        }}
        QProgressBar::chunk {{
            background-color: {create_gradient(chunk_color1, chunk_color2)};
            border-radius: 2px;
        }}
        """


class StatusStyles:
    """Status display stylesheet definitions."""
    
    @staticmethod
    def get_status_label_style(
        colors: ColorScheme = Colors.DARK,
        status: str = "normal"
    ) -> str:
        """Get status label stylesheet.
        
        Args:
            colors: Color scheme to use
            status: Status type (normal, success, error, warning, info)
            
        Returns:
            str: CSS stylesheet for status labels
        """
        status_colors = {
            "normal": colors.text_secondary,
            "success": colors.success,
            "error": colors.error,
            "warning": colors.warning,
            "info": colors.info,
        }
        
        text_color = status_colors.get(status, colors.text_secondary)
        
        return f"""
        QLabel {{
            color: {text_color};
            {get_font_css(Fonts.STATUS_NORMAL)}
            padding: 4px 8px;
            border-radius: 3px;
            background-color: transparent;
        }}
        """


class WidgetStyles:
    """Combined widget stylesheet manager."""
    
    def __init__(self, theme: ThemeType = ThemeType.DARK):
        """Initialize widget styles with theme.
        
        Args:
            theme: Theme type to use
        """
        self.theme = theme
        self.colors = get_theme_colors(theme)
        self.buttons = ButtonStyles()
        self.groups = GroupBoxStyles()
        self.inputs = InputStyles()
        self.progress = ProgressStyles()
        self.status = StatusStyles()
    
    def get_base_widget_style(self) -> str:
        """Get base widget stylesheet.
        
        Returns:
            str: Base CSS stylesheet for widgets
        """
        return f"""
        QWidget {{
            background-color: {self.colors.background_primary};
            color: {self.colors.text_secondary};
            {get_font_css(Fonts.BASE)}
        }}
        
        QLabel {{
            color: {self.colors.text_secondary};
            {get_font_css(Fonts.LABEL_NORMAL)}
        }}
        
        QFrame {{
            border: 1px solid {self.colors.border_muted};
            border-radius: 3px;
        }}
        """
    
    def get_complete_stylesheet(self) -> str:
        """Get complete stylesheet combining all widget styles.
        
        Returns:
            str: Complete CSS stylesheet
        """
        components = [
            self.get_base_widget_style(),
            self.buttons.get_primary_button_style(self.colors),
            self.groups.get_standard_groupbox_style(self.colors),
            self.inputs.get_line_edit_style(self.colors),
            self.inputs.get_combo_box_style(self.colors),
            self.inputs.get_spin_box_style(self.colors),
            self.progress.get_progress_bar_style(self.colors),
        ]
        
        return "\n".join(components)
    
    def get_button_style(self, button_type: str = "primary") -> str:
        """Get button stylesheet by type.
        
        Args:
            button_type: Button type (primary, secondary, danger, success, large)
            
        Returns:
            str: CSS stylesheet for the specified button type
        """
        button_map = {
            "primary": self.buttons.get_primary_button_style,
            "secondary": self.buttons.get_secondary_button_style,
            "danger": self.buttons.get_danger_button_style,
            "success": self.buttons.get_success_button_style,
            "large": self.buttons.get_large_button_style,
        }
        
        style_func = button_map.get(button_type, self.buttons.get_primary_button_style)
        return style_func(self.colors)
    
    def get_input_style(self, input_type: str = "line_edit") -> str:
        """Get input stylesheet by type.
        
        Args:
            input_type: Input type (line_edit, combo_box, spin_box)
            
        Returns:
            str: CSS stylesheet for the specified input type
        """
        input_map = {
            "line_edit": self.inputs.get_line_edit_style,
            "combo_box": self.inputs.get_combo_box_style,
            "spin_box": self.inputs.get_spin_box_style,
        }
        
        style_func = input_map.get(input_type, self.inputs.get_line_edit_style)
        return style_func(self.colors)
    
    def set_theme(self, theme: ThemeType) -> None:
        """Change theme.
        
        Args:
            theme: New theme type
        """
        self.theme = theme
        self.colors = get_theme_colors(theme)
