"""
Settings module constants and UI definitions.

Contains all UI constants, colors, validation rules, and styling definitions
used throughout the settings module.
"""

# Standard library imports
from typing import Any, Dict


class UIConstants:
    """UI layout and styling constants"""

    # Layout dimensions
    HEADER_HEIGHT = 50
    FOOTER_HEIGHT = 50
    SEARCH_WIDTH = 250
    PROPERTY_PANEL_MIN_WIDTH = 350
    SPLITTER_SIZES = [500, 500]

    # Widget dimensions
    CHECKBOX_SIZE = 25
    MAX_TEXT_EDIT_HEIGHT = 150
    TREE_ITEM_HEIGHT = 25

    # Margins and spacing
    HEADER_MARGINS = (15, 10, 15, 10)
    FOOTER_MARGINS = (15, 10, 15, 10)
    MAIN_MARGINS = (0, 10, 0, 0)
    PROPERTY_MARGINS = (0, 0, 0, 0)
    PROPERTY_SPACING = 5


class Colors:
    """Color definitions for consistent theming"""

    # Primary colors
    BACKGROUND = "#1e1e1e"
    SECONDARY_BACKGROUND = "#2d2d2d"
    TERTIARY_BACKGROUND = "#353535"
    BORDER = "#404040"
    BORDER_HOVER = "#555555"

    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_MUTED = "#888888"
    TEXT_DISABLED = "#777777"

    # Accent colors
    PRIMARY_ACCENT = "#0078d4"
    PRIMARY_ACCENT_HOVER = "#106ebe"
    SUCCESS = "#00ff00"
    ERROR = "#ff4444"
    WARNING = "#ffaa00"

    # Button colors
    BUTTON_CHECKED = "#0078d4"
    BUTTON_UNCHECKED = "#2d2d2d"
    BUTTON_BORDER_CHECKED = "#0078d4"
    BUTTON_BORDER_UNCHECKED = "#555555"

    # Additional aliases for compatibility
    BACKGROUND_SECONDARY = SECONDARY_BACKGROUND
    BORDER_LIGHT = "#333333"
    BACKGROUND_HOVER = "#383838"

    # Tree widget specific colors
    TREE_SETTING_ITEM_BACKGROUND = "#3a3a3a"  # Brighter background for leaf setting items


class ValidationRules:
    """Configuration validation rules"""

    @staticmethod
    def get_rules() -> Dict[str, Dict[str, Any]]:
        """Get validation rules for configuration keys"""
        return {
            # Hardware limits
            "hardware.voltage": {"min": 0.0, "max": 50.0, "type": "float"},
            "hardware.current": {"min": 0.0, "max": 50.0, "type": "float"},
            "hardware.upper_current": {"min": 0.0, "max": 50.0, "type": "float"},
            "hardware.upper_temperature": {"min": 0.0, "max": 100.0, "type": "float"},
            "hardware.activation_temperature": {"min": 0.0, "max": 100.0, "type": "float"},
            "hardware.standby_temperature": {"min": 0.0, "max": 100.0, "type": "float"},
            "hardware.fan_speed": {"min": 1, "max": 10, "type": "int"},
            # Motion control
            "motion_control.velocity": {"min": 0.0, "max": 200000.0, "type": "float"},
            "motion_control.acceleration": {"min": 0.0, "max": 200000.0, "type": "float"},
            "motion_control.deceleration": {"min": 0.0, "max": 200000.0, "type": "float"},
            # Safety parameters
            "safety.max_voltage": {"min": 0.0, "max": 100.0, "type": "float"},
            "safety.max_current": {"min": 0.0, "max": 100.0, "type": "float"},
            "safety.max_stroke": {"min": 0.0, "max": 200000.0, "type": "float"},
            # Timing parameters (all should be positive)
            "timing.*": {"min": 0.0, "type": "float"},
            # Boolean validations
            "services.repository.auto_save": {"type": "bool"},
            "gui.require_serial_number_popup": {"type": "bool"},
            # String validations
            "application.environment": {
                "allowed": ["development", "production", "testing"],
                "type": "str",
            },
            "robot.model": {"allowed": ["mock", "ajinextek"], "type": "str"},
            "loadcell.model": {"allowed": ["mock", "bs205"], "type": "str"},
            "mcu.model": {"allowed": ["mock", "lma"], "type": "str"},
            "power.model": {"allowed": ["mock", "oda"], "type": "str"},
            "digital_io.model": {"allowed": ["mock", "ajinextek"], "type": "str"},
            # Port validations
            "*.port": {"pattern": r"^COM\d+$", "type": "str"},
            "*.baudrate": {"allowed": [9600, 19200, 38400, 57600, 115200], "type": "int"},
            # DUT (Device Under Test) validations
            "default.dut_id": {"type": "str", "min_length": 1, "max_length": 50},
            "default.model": {"type": "str", "min_length": 1, "max_length": 100},
            "default.operator_id": {"type": "str", "min_length": 1, "max_length": 50},
            "default.manufacturer": {"type": "str", "min_length": 1, "max_length": 100},
            "default.serial_number": {"type": "str", "min_length": 1, "max_length": 50},
            "default.part_number": {"type": "str", "min_length": 1, "max_length": 50},
        }


class EditorTypes:
    """Editor type definitions for different configuration values"""

    # Predefined combo box options
    LOGGING_LEVELS = ["DEBUG", "INFO"]
    ENVIRONMENTS = ["development", "production", "testing"]
    ROBOT_MODELS = ["mock", "ajinextek"]
    POWER_MODELS = ["mock", "oda"]
    LOADCELL_MODELS = ["mock", "bs205"]
    MCU_MODELS = ["mock", "lma"]
    DIGITAL_IO_MODELS = ["mock", "ajinextek"]
    PARITY_OPTIONS = ["none", "even", "odd"]
    CONTACT_TYPES = ["A", "B"]
    EDGE_TYPES = ["rising", "falling"]

    @staticmethod
    def get_combo_options(key: str) -> list[str] | None:
        """Get predefined combo options for a configuration key"""
        combo_map = {
            "logging.level": EditorTypes.LOGGING_LEVELS,
            "application.environment": EditorTypes.ENVIRONMENTS,
            "robot.model": EditorTypes.ROBOT_MODELS,
            "digital_io.model": EditorTypes.DIGITAL_IO_MODELS,
            "power.model": EditorTypes.POWER_MODELS,
            "loadcell.model": EditorTypes.LOADCELL_MODELS,
            "mcu.model": EditorTypes.MCU_MODELS,
        }

        # Check for exact match
        if key in combo_map:
            return combo_map[key]

        # Check for pattern matches
        if key.endswith(".parity"):
            return EditorTypes.PARITY_OPTIONS
        elif key.endswith(".contact_type"):
            return EditorTypes.CONTACT_TYPES
        elif key.endswith(".edge_type"):
            return EditorTypes.EDGE_TYPES

        return None


class Styles:
    """UI style definitions"""

    # Main widget styles
    MAIN_WIDGET = f"""
        QWidget {{
            background-color: {Colors.BACKGROUND};
            color: {Colors.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
    """

    # Tree widget styles
    TREE_WIDGET = f"""
        QTreeWidget {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            outline: none;
            font-size: 13px;
        }}
        QTreeWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {Colors.BORDER_LIGHT};
        }}
        QTreeWidget::item:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
        }}
        QTreeWidget::item:selected {{
            background-color: {Colors.PRIMARY_ACCENT};
            color: white;
        }}
        QTreeWidget::branch:closed:has-children {{
            image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTYgNGw0IDQtNCA0VjR6Ii8+PC9zdmc+);
        }}
        QTreeWidget::branch:open:has-children {{
            image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTQgNmw0IDQgNC00SDR6Ii8+PC9zdmc+);
        }}
    """

    # Button styles
    BUTTON = f"""
        QPushButton {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            border: 2px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            color: {Colors.TEXT_PRIMARY};
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {Colors.BACKGROUND_HOVER};
            border-color: {Colors.PRIMARY_ACCENT};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY_ACCENT};
            color: white;
        }}
    """

    # Search box styles
    SEARCH_BOX = f"""
        QLineEdit {{
            border: 2px solid {Colors.BORDER};
            border-radius: 4px;
            padding: 8px;
            font-size: 13px;
            background-color: {Colors.BACKGROUND_SECONDARY};
            color: {Colors.TEXT_PRIMARY};
        }}
        QLineEdit:focus {{
            border-color: {Colors.PRIMARY_ACCENT};
        }}
        QLineEdit:hover {{
            border-color: {Colors.BORDER_HOVER};
        }}
    """

    # Splitter styles
    SPLITTER = f"""
        QSplitter::handle {{
            background-color: {Colors.BORDER};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
    """

    # Property panel styles
    PROPERTY_PANEL = f"""
        QWidget {{
            background-color: {Colors.BACKGROUND_SECONDARY};
            border: 1px solid {Colors.BORDER};
        }}
    """

    # Label styles
    LABEL_NO_BORDER = """
        QLabel {
            border: none;
            background-color: transparent;
        }
    """
