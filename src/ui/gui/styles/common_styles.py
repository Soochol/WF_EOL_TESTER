"""Common UI Styles

Centralized styling definitions for consistent UI appearance.
"""

# Widget background and text colors
BACKGROUND_DARK = "#1e1e1e"
BACKGROUND_MEDIUM = "#2d2d2d"
BACKGROUND_LIGHT = "#404040"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#cccccc"
TEXT_MUTED = "#999999"

# Accent colors
ACCENT_BLUE = "#0078d4"
ACCENT_BLUE_HOVER = "#106ebe"
ACCENT_BLUE_PRESSED = "#005a9e"
ACCENT_GREEN = "#107c10"
ACCENT_RED = "#d13438"
ACCENT_ORANGE = "#ff8c00"

# Border colors
BORDER_DEFAULT = "#404040"
BORDER_FOCUS = "#0078d4"
BORDER_ERROR = "#d13438"
BORDER_SUCCESS = "#107c10"


def get_base_widget_style() -> str:
    """Get base widget styling."""
    return f"""
    QWidget {{
        background-color: {BACKGROUND_DARK};
        color: {TEXT_SECONDARY};
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
        font-size: 13px;
    }}
    """


def get_button_style() -> str:
    """Get button styling."""
    return f"""
    QPushButton {{
        background-color: {ACCENT_BLUE};
        color: {TEXT_PRIMARY};
        border: 1px solid {ACCENT_BLUE_HOVER};
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
        min-width: 80px;
        min-height: 32px;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_BLUE_HOVER};
        border-color: {ACCENT_BLUE_PRESSED};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_BLUE_PRESSED};
    }}
    QPushButton:disabled {{
        background-color: {BACKGROUND_LIGHT};
        color: {TEXT_MUTED};
        border-color: {BORDER_DEFAULT};
    }}
    """


def get_combobox_style() -> str:
    """Get combobox styling."""
    return f"""
    QComboBox {{
        background-color: {BACKGROUND_MEDIUM};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER_DEFAULT};
        border-radius: 4px;
        padding: 6px 12px;
        min-width: 100px;
        min-height: 28px;
    }}
    QComboBox:hover {{
        border-color: {BORDER_FOCUS};
    }}
    QComboBox:focus {{
        border-color: {BORDER_FOCUS};
        outline: none;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY};
        margin-right: 5px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BACKGROUND_MEDIUM};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER_DEFAULT};
        selection-background-color: {ACCENT_BLUE};
        selection-color: {TEXT_PRIMARY};
    }}
    """


def get_spinbox_style() -> str:
    """Get spinbox styling."""
    return f"""
    QSpinBox {{
        background-color: {BACKGROUND_MEDIUM};
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER_DEFAULT};
        border-radius: 4px;
        padding: 6px 8px;
        min-width: 80px;
        min-height: 28px;
    }}
    QSpinBox:hover {{
        border-color: {BORDER_FOCUS};
    }}
    QSpinBox:focus {{
        border-color: {BORDER_FOCUS};
        outline: none;
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {BACKGROUND_LIGHT};
        border: none;
        width: 16px;
    }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {ACCENT_BLUE};
    }}
    """


def get_groupbox_style() -> str:
    """Get groupbox styling."""
    return f"""
    QGroupBox {{
        font-weight: 600;
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_DEFAULT};
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: rgba(45, 45, 45, 0.3);
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {BACKGROUND_DARK};
        color: {TEXT_PRIMARY};
    }}
    """


def get_label_style() -> str:
    """Get label styling."""
    return f"""
    QLabel {{
        color: {TEXT_SECONDARY};
        background-color: transparent;
    }}
    QLabel[styleClass="title"] {{
        color: {TEXT_PRIMARY};
        font-size: 16px;
        font-weight: 600;
    }}
    QLabel[styleClass="subtitle"] {{
        color: {TEXT_SECONDARY};
        font-size: 14px;
        font-weight: 500;
    }}
    QLabel[styleClass="caption"] {{
        color: {TEXT_MUTED};
        font-size: 11px;
    }}
    """


def get_results_widget_style() -> str:
    """Get complete results widget styling."""
    return (
        get_base_widget_style() +
        get_button_style() +
        get_combobox_style() +
        get_spinbox_style() +
        get_groupbox_style() +
        get_label_style()
    )


def get_splitter_style() -> str:
    """Get splitter styling."""
    return f"""
    QSplitter::handle {{
        background-color: {BORDER_DEFAULT};
        height: 2px;
        margin: 2px 0;
    }}
    QSplitter::handle:hover {{
        background-color: {ACCENT_BLUE};
    }}
    QSplitter::handle:pressed {{
        background-color: {ACCENT_BLUE_PRESSED};
    }}
    """
