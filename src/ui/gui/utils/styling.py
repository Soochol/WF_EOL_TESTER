"""
GUI Styling and Theme Management

Industrial theme styling with WCAG compliance for the EOL Tester GUI.
"""

from typing import Dict, Any
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject
from PySide6.QtGui import QFont, QPalette, QColor


class ThemeManager(QObject):
    """
    Theme manager for industrial GUI styling
    
    Provides consistent theming across all GUI components with
    accessibility compliance (WCAG 2.1 AA).
    """
    
    # Industrial Color Palette
    COLORS = {
        # Primary Colors
        'primary': '#2C3E50',      # Dark blue-gray
        'primary_light': '#34495E', # Lighter blue-gray
        'primary_dark': '#1B2631',  # Darker blue-gray
        
        # Accent Colors
        'accent': '#3498DB',        # Bright blue
        'accent_light': '#5DADE2',  # Light blue
        'accent_dark': '#2E86C1',   # Dark blue
        
        # Status Colors
        'success': '#27AE60',       # Green
        'warning': '#F39C12',       # Orange
        'error': '#E74C3C',         # Red
        'info': '#17A2B8',          # Cyan
        
        # Neutral Colors
        'background': '#ECF0F1',    # Light gray
        'surface': '#FFFFFF',       # White
        'text_primary': '#2C3E50',  # Dark text
        'text_secondary': '#7F8C8D', # Gray text
        'text_disabled': '#BDC3C7', # Light gray text
        
        # Industrial Terminal Colors
        'terminal_bg': '#0C0C0C',   # Black
        'terminal_green': '#00FF00', # Bright green
        'terminal_amber': '#FFBF00', # Amber
    }
    
    # Typography Settings
    FONTS = {
        'primary': 'Segoe UI',      # Windows
        'secondary': 'Roboto',      # Cross-platform
        'monospace': 'Consolas',    # Terminal/code
        'fallback': 'Arial',        # Universal fallback
    }
    
    FONT_SIZES = {
        'small': 10,
        'normal': 12,
        'medium': 14,
        'large': 16,
        'xlarge': 18,
        'title': 20,
    }
    
    def __init__(self):
        """Initialize theme manager"""
        super().__init__()
        self._current_theme = 'industrial'
        
    def apply_industrial_theme(self, widget: QWidget) -> None:
        """
        Apply industrial theme to widget and all children
        
        Args:
            widget: Root widget to apply theme to
        """
        industrial_stylesheet = self._generate_industrial_stylesheet()
        widget.setStyleSheet(industrial_stylesheet)
        
        # Set application-wide font
        font = QFont(self.FONTS['primary'], self.FONT_SIZES['normal'])
        widget.setFont(font)
        
    def apply_terminal_theme(self, widget: QWidget) -> None:
        """
        Apply terminal/console theme for hardware monitoring
        
        Args:
            widget: Widget to apply terminal theme to
        """
        terminal_stylesheet = self._generate_terminal_stylesheet()
        widget.setStyleSheet(terminal_stylesheet)
        
        # Set monospace font for terminal
        font = QFont(self.FONTS['monospace'], self.FONT_SIZES['normal'])
        widget.setFont(font)
        
    def _generate_industrial_stylesheet(self) -> str:
        """Generate complete industrial theme stylesheet"""
        return f"""
        /* === GLOBAL STYLES === */
        QWidget {{
            background-color: {self.COLORS['background']};
            color: {self.COLORS['text_primary']};
            font-family: {self.FONTS['primary']}, {self.FONTS['secondary']}, {self.FONTS['fallback']};
            font-size: {self.FONT_SIZES['normal']}px;
        }}
        
        /* === MAIN WINDOW === */
        QMainWindow {{
            background-color: {self.COLORS['background']};
        }}
        
        /* === BUTTONS === */
        QPushButton {{
            background-color: {self.COLORS['accent']};
            color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['accent']};
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: {self.FONT_SIZES['normal']}px;
            min-height: 44px;
            min-width: 100px;
        }}
        
        QPushButton:hover {{
            background-color: {self.COLORS['accent_dark']};
            border-color: {self.COLORS['accent_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.COLORS['primary_dark']};
        }}
        
        QPushButton:focus {{
            outline: 3px solid {self.COLORS['warning']};
            outline-offset: 2px;
        }}
        
        QPushButton:disabled {{
            background-color: {self.COLORS['text_disabled']};
            color: {self.COLORS['background']};
            border-color: {self.COLORS['text_disabled']};
        }}
        
        /* === PRIMARY BUTTON === */
        QPushButton.primary {{
            background-color: {self.COLORS['accent']};
            border-color: {self.COLORS['accent']};
        }}
        
        /* === SUCCESS BUTTON === */
        QPushButton.success {{
            background-color: {self.COLORS['success']};
            border-color: {self.COLORS['success']};
        }}
        
        QPushButton.success:hover {{
            background-color: #229954;
        }}
        
        /* === DANGER BUTTON === */
        QPushButton.danger {{
            background-color: {self.COLORS['error']};
            border-color: {self.COLORS['error']};
            font-weight: 700;
            min-height: 60px;
        }}
        
        QPushButton.danger:hover {{
            background-color: #CD212A;
        }}
        
        /* === WARNING BUTTON === */
        QPushButton.warning {{
            background-color: {self.COLORS['warning']};
            border-color: {self.COLORS['warning']};
            color: {self.COLORS['surface']};
        }}
        
        /* === INPUT FIELDS === */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: {self.FONT_SIZES['normal']}px;
            min-height: 44px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.COLORS['accent']};
            outline: 2px solid {self.COLORS['warning']};
            outline-offset: 1px;
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {self.COLORS['background']};
            color: {self.COLORS['text_disabled']};
        }}
        
        /* === COMBO BOXES === */
        QComboBox {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 44px;
        }}
        
        QComboBox:focus {{
            border-color: {self.COLORS['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {self.COLORS['text_primary']};
            margin-right: 10px;
        }}
        
        /* === SPIN BOXES === */
        QSpinBox, QDoubleSpinBox {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 44px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {self.COLORS['accent']};
        }}
        
        /* === LABELS === */
        QLabel {{
            color: {self.COLORS['text_primary']};
            font-weight: 500;
            font-size: {self.FONT_SIZES['normal']}px;
        }}
        
        QLabel.title {{
            font-size: {self.FONT_SIZES['title']}px;
            font-weight: 700;
            color: {self.COLORS['primary']};
        }}
        
        QLabel.subtitle {{
            font-size: {self.FONT_SIZES['medium']}px;
            font-weight: 600;
            color: {self.COLORS['primary']};
        }}
        
        QLabel.status-success {{
            color: {self.COLORS['success']};
            font-weight: 600;
        }}
        
        QLabel.status-warning {{
            color: {self.COLORS['warning']};
            font-weight: 600;
        }}
        
        QLabel.status-error {{
            color: {self.COLORS['error']};
            font-weight: 600;
        }}
        
        /* === PROGRESS BARS === */
        QProgressBar {{
            background-color: {self.COLORS['background']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            min-height: 30px;
        }}
        
        QProgressBar::chunk {{
            background-color: {self.COLORS['accent']};
            border-radius: 6px;
        }}
        
        QProgressBar.success::chunk {{
            background-color: {self.COLORS['success']};
        }}
        
        QProgressBar.warning::chunk {{
            background-color: {self.COLORS['warning']};
        }}
        
        QProgressBar.error::chunk {{
            background-color: {self.COLORS['error']};
        }}
        
        /* === GROUP BOXES === */
        QGroupBox {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
            margin-top: 20px;
            padding-top: 20px;
            font-weight: 600;
            font-size: {self.FONT_SIZES['medium']}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: {self.COLORS['primary']};
        }}
        
        /* === TABS === */
        QTabWidget::pane {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {self.COLORS['background']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-bottom: none;
            padding: 12px 24px;
            margin-right: 2px;
            font-weight: 500;
            min-height: 20px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.COLORS['surface']};
            border-color: {self.COLORS['accent']};
            border-bottom: 2px solid {self.COLORS['surface']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {self.COLORS['accent_light']};
            color: {self.COLORS['surface']};
        }}
        
        /* === LIST WIDGETS === */
        QListWidget {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
            padding: 8px;
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {self.COLORS['background']};
        }}
        
        QListWidget::item:selected {{
            background-color: {self.COLORS['accent']};
            color: {self.COLORS['surface']};
        }}
        
        QListWidget::item:hover {{
            background-color: {self.COLORS['accent_light']};
        }}
        
        /* === TREE WIDGETS === */
        QTreeWidget {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
            padding: 8px;
        }}
        
        QTreeWidget::item {{
            padding: 4px;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {self.COLORS['accent']};
            color: {self.COLORS['surface']};
        }}
        
        /* === TABLE WIDGETS === */
        QTableWidget {{
            background-color: {self.COLORS['surface']};
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 8px;
            gridline-color: {self.COLORS['background']};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {self.COLORS['background']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {self.COLORS['accent']};
            color: {self.COLORS['surface']};
        }}
        
        QHeaderView::section {{
            background-color: {self.COLORS['primary']};
            color: {self.COLORS['surface']};
            padding: 8px;
            border: none;
            font-weight: 600;
        }}
        
        /* === SCROLL BARS === */
        QScrollBar:vertical {{
            background-color: {self.COLORS['background']};
            border: none;
            width: 16px;
            border-radius: 8px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.COLORS['text_disabled']};
            border-radius: 8px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.COLORS['accent']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.COLORS['background']};
            border: none;
            height: 16px;
            border-radius: 8px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.COLORS['text_disabled']};
            border-radius: 8px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.COLORS['accent']};
        }}
        
        /* === STATUS BAR === */
        QStatusBar {{
            background-color: {self.COLORS['primary']};
            color: {self.COLORS['surface']};
            border-top: 2px solid {self.COLORS['primary_dark']};
            font-weight: 500;
        }}
        
        /* === MENU BAR === */
        QMenuBar {{
            background-color: {self.COLORS['primary']};
            color: {self.COLORS['surface']};
            border-bottom: 2px solid {self.COLORS['primary_dark']};
        }}
        
        QMenuBar::item {{
            padding: 8px 16px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.COLORS['accent']};
        }}
        
        /* === CHECKBOXES === */
        QCheckBox {{
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 4px;
            background-color: {self.COLORS['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.COLORS['accent']};
            border-color: {self.COLORS['accent']};
        }}
        
        /* === RADIO BUTTONS === */
        QRadioButton {{
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {self.COLORS['text_disabled']};
            border-radius: 10px;
            background-color: {self.COLORS['surface']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {self.COLORS['accent']};
            border-color: {self.COLORS['accent']};
        }}
        
        /* === SLIDERS === */
        QSlider::groove:horizontal {{
            background-color: {self.COLORS['background']};
            border: 1px solid {self.COLORS['text_disabled']};
            height: 8px;
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {self.COLORS['accent']};
            border: 2px solid {self.COLORS['accent_dark']};
            width: 20px;
            margin: -8px 0;
            border-radius: 10px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {self.COLORS['accent_light']};
        }}
        """
        
    def _generate_terminal_stylesheet(self) -> str:
        """Generate terminal/console theme stylesheet"""
        return f"""
        QWidget {{
            background-color: {self.COLORS['terminal_bg']};
            color: {self.COLORS['terminal_green']};
            font-family: {self.FONTS['monospace']};
            font-size: {self.FONT_SIZES['normal']}px;
        }}
        
        QTextEdit, QPlainTextEdit {{
            background-color: {self.COLORS['terminal_bg']};
            color: {self.COLORS['terminal_green']};
            border: 1px solid {self.COLORS['terminal_green']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QLabel {{
            color: {self.COLORS['terminal_green']};
        }}
        
        QLabel.warning {{
            color: {self.COLORS['terminal_amber']};
        }}
        
        QLabel.error {{
            color: {self.COLORS['error']};
        }}
        """
        
    def get_color(self, color_name: str) -> str:
        """
        Get color value by name
        
        Args:
            color_name: Name of the color from COLORS dict
            
        Returns:
            Color hex value
        """
        return self.COLORS.get(color_name, self.COLORS['text_primary'])
        
    def get_font_size(self, size_name: str) -> int:
        """
        Get font size by name
        
        Args:
            size_name: Name of the font size from FONT_SIZES dict
            
        Returns:
            Font size in pixels
        """
        return self.FONT_SIZES.get(size_name, self.FONT_SIZES['normal'])