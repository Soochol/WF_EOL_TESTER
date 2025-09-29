"""
Styling Utilities

Theme management and styling utilities for the GUI application.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget


class ThemeManager(QObject):
    """
    Theme manager for the GUI application.

    Provides industrial-style themes and color schemes.
    """

    # Industrial color palette
    COLORS = {
        # Background colors
        "background_primary": "#1e1e1e",  # Main background
        "background_secondary": "#2d2d2d",  # Secondary background
        "background_tertiary": "#1a1a1a",  # Tertiary background (darker)
        # Border and separator colors
        "border_primary": "#404040",  # Primary borders
        "border_secondary": "#555555",  # Secondary borders
        "separator": "#666666",  # Separator lines
        # Text colors
        "text_primary": "#ffffff",  # Primary text (white)
        "text_secondary": "#cccccc",  # Secondary text (light gray)
        "text_tertiary": "#888888",  # Tertiary text (gray)
        "text_disabled": "#555555",  # Disabled text
        # Accent colors
        "accent_primary": "#0078d4",  # Primary accent (blue)
        "accent_hover": "#106ebe",  # Accent hover
        "accent_pressed": "#005a9e",  # Accent pressed
        # Status colors
        "status_success": "#00ff00",  # Success (green)
        "status_success_bg": "#004d00",  # Success background
        "status_warning": "#ffaa00",  # Warning (orange)
        "status_warning_bg": "#4d3300",  # Warning background
        "status_error": "#ff4444",  # Error (red)
        "status_error_bg": "#4d0000",  # Error background
        "status_info": "#4da6ff",  # Info (blue)
        "status_info_bg": "#003366",  # Info background
        # Control colors
        "control_enabled": "#0078d4",  # Enabled controls
        "control_hover": "#106ebe",  # Control hover
        "control_pressed": "#005a9e",  # Control pressed
        "control_disabled": "#404040",  # Disabled controls
        # Emergency/Critical colors
        "emergency": "#cc0000",  # Emergency red
        "emergency_hover": "#990000",  # Emergency hover
        "emergency_pressed": "#660000",  # Emergency pressed
        # Chart colors
        "chart_line": "#00ff88",  # Chart line color
        "chart_grid": "#404040",  # Chart grid color
        "chart_background": "#1a1a1a",  # Chart background
    }

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def apply_industrial_theme(self, widget: QWidget) -> None:
        """Apply industrial theme to a widget"""
        # Apply stylesheet to the specific widget
        widget.setStyleSheet(self.get_application_stylesheet())

    def get_application_stylesheet(self) -> str:
        """Get the complete application stylesheet"""
        return f"""
        /* Main Application Styling */
        QMainWindow {{
            background-color: {self.COLORS['background_primary']};
            color: {self.COLORS['text_primary']};
        }}

        /* Widget Base Styling */
        QWidget {{
            background-color: {self.COLORS['background_primary']};
            color: {self.COLORS['text_secondary']};
            font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', 'Microsoft Sans Serif', Arial, sans-serif;
            font-size: 14px;
        }}

        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {self.COLORS['border_primary']};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: {self.COLORS['text_primary']};
            font-size: 14px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}

        /* Labels */
        QLabel {{
            color: {self.COLORS['text_secondary']};
            background: transparent;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {self.COLORS['control_enabled']};
            color: {self.COLORS['text_primary']};
            border: 1px solid {self.COLORS['accent_hover']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: bold;
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {self.COLORS['control_hover']};
        }}

        QPushButton:pressed {{
            background-color: {self.COLORS['control_pressed']};
        }}

        QPushButton:disabled {{
            background-color: {self.COLORS['control_disabled']};
            color: {self.COLORS['text_disabled']};
            border-color: {self.COLORS['control_disabled']};
        }}

        QPushButton:checked {{
            background-color: {self.COLORS['accent_primary']};
            border-color: {self.COLORS['accent_hover']};
        }}

        /* Input Controls */
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_secondary']};
            border: 1px solid {self.COLORS['border_primary']};
            border-radius: 3px;
            padding: 5px;
            min-height: 20px;
        }}

        QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {self.COLORS['accent_primary']};
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {self.COLORS['accent_primary']};
            border-width: 2px;
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_secondary']};
            border: 1px solid {self.COLORS['border_primary']};
            border-radius: 3px;
            padding: 5px;
            min-height: 20px;
            min-width: 80px;
        }}

        QComboBox:hover {{
            border-color: {self.COLORS['accent_primary']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {self.COLORS['text_secondary']};
        }}

        QComboBox QAbstractItemView {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_secondary']};
            border: 1px solid {self.COLORS['border_primary']};
            selection-background-color: {self.COLORS['accent_primary']};
        }}

        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {self.COLORS['border_primary']};
            border-radius: 3px;
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_primary']};
            text-align: center;
            font-weight: bold;
        }}

        QProgressBar::chunk {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.COLORS['accent_primary']},
                stop: 1 {self.COLORS['accent_hover']});
            border-radius: 2px;
        }}

        /* Tables */
        QTableWidget {{
            background-color: {self.COLORS['background_tertiary']};
            alternate-background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_secondary']};
            border: 1px solid {self.COLORS['border_primary']};
            selection-background-color: {self.COLORS['accent_primary']};
            selection-color: {self.COLORS['text_primary']};
            gridline-color: {self.COLORS['border_primary']};
        }}

        QTableWidget::item {{
            padding: 5px;
            border-bottom: 1px solid {self.COLORS['border_primary']};
        }}

        QHeaderView::section {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_primary']};
            padding: 8px;
            border: 1px solid {self.COLORS['border_primary']};
            font-weight: bold;
        }}

        /* Text Edit (for logs) */
        QTextEdit {{
            background-color: {self.COLORS['background_tertiary']};
            color: {self.COLORS['text_secondary']};
            border: 1px solid {self.COLORS['border_primary']};
            selection-background-color: {self.COLORS['accent_primary']};
            font-family: 'D2Coding', 'Consolas', 'Malgun Gothic', '맑은 고딕', 'Courier New', monospace;
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {self.COLORS['background_secondary']};
            width: 15px;
            border-radius: 7px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.COLORS['border_secondary']};
            border-radius: 7px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.COLORS['separator']};
        }}

        QScrollBar:horizontal {{
            background-color: {self.COLORS['background_secondary']};
            height: 15px;
            border-radius: 7px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {self.COLORS['border_secondary']};
            border-radius: 7px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {self.COLORS['separator']};
        }}

        QScrollBar::add-line, QScrollBar::sub-line {{
            background: none;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_secondary']};
            border-top: 1px solid {self.COLORS['border_primary']};
        }}

        QStatusBar QLabel {{
            padding: 2px 8px;
            font-size: 14px;
        }}

        /* Separator Lines */
        QFrame[frameShape="4"], QFrame[frameShape="5"] {{ /* HLine, VLine */
            color: {self.COLORS['border_primary']};
        }}

        /* Tool Tips */
        QToolTip {{
            background-color: {self.COLORS['background_secondary']};
            color: {self.COLORS['text_primary']};
            border: 1px solid {self.COLORS['border_primary']};
            padding: 5px;
        }}
        """

    def get_log_level_color(self, level: str) -> str:
        """Get color for log level"""
        level_colors = {
            "INFO": self.COLORS["text_secondary"],
            "WARN": self.COLORS["status_warning"],
            "ERROR": self.COLORS["status_error"],
            "DEBUG": self.COLORS["status_info"],
        }
        return level_colors.get(level.upper(), self.COLORS["text_secondary"])

    def get_status_colors(self, status: str) -> tuple[str, str]:
        """Get foreground and background colors for status"""
        if status == "PASS":
            return self.COLORS["status_success"], self.COLORS["status_success_bg"]
        elif status == "FAIL":
            return self.COLORS["status_error"], self.COLORS["status_error_bg"]
        elif status == "PENDING":
            return self.COLORS["status_warning"], self.COLORS["status_warning_bg"]
        else:
            return self.COLORS["text_secondary"], "transparent"
