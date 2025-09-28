"""
Settings Widget

Comprehensive settings interface for editing YAML configuration files.
Features a 3-panel layout: Files Tree + Settings Tree + Properties Panel.
"""

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QVBoxLayout,
    QWidget,
)
from loguru import logger
import yaml

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class ConfigValidator:
    """Configuration value validator"""

    @staticmethod
    def get_validation_rules() -> Dict[str, Dict[str, Any]]:
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

    @staticmethod
    def validate_value(key: str, value: Any, rules: Dict[str, Dict[str, Any]]) -> tuple[bool, str]:
        """Validate a configuration value"""
        try:
            # Find matching rule
            rule = None

            # Check for exact match first
            if key in rules:
                rule = rules[key]
            else:
                # Check for wildcard matches
                for rule_key in rules:
                    if "*" in rule_key:
                        pattern = rule_key.replace("*", ".*")
                        if re.match(pattern, key):
                            rule = rules[rule_key]
                            break

            if not rule:
                return True, ""  # No validation rule, assume valid

            # Type validation
            expected_type = rule.get("type")
            if expected_type:
                if expected_type == "int" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        return False, "Must be an integer"
                elif expected_type == "float" and not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        return False, "Must be a number"
                elif expected_type == "bool" and not isinstance(value, bool):
                    return False, "Must be true or false"
                elif expected_type == "str" and not isinstance(value, str):
                    return False, "Must be a string"

            # Range validation
            if "min" in rule and isinstance(value, (int, float)):
                if value < rule["min"]:
                    return False, f"Must be >= {rule['min']}"

            if "max" in rule and isinstance(value, (int, float)):
                if value > rule["max"]:
                    return False, f"Must be <= {rule['max']}"

            # Allowed values validation
            if "allowed" in rule:
                if value not in rule["allowed"]:
                    return False, f"Must be one of: {', '.join(map(str, rule['allowed']))}"

            # Pattern validation
            if "pattern" in rule and isinstance(value, str):
                if not re.match(rule["pattern"], value):
                    return False, "Invalid format"

            # String length validation
            if "min_length" in rule and isinstance(value, str):
                if len(value) < rule["min_length"]:
                    return False, f"Must be at least {rule['min_length']} characters"

            if "max_length" in rule and isinstance(value, str):
                if len(value) > rule["max_length"]:
                    return False, f"Must be no more than {rule['max_length']} characters"

            return True, ""

        except Exception as e:
            return False, f"Validation error: {str(e)}"


@dataclass
class ConfigValue:
    """Configuration value with metadata"""

    key: str
    value: Any
    data_type: str
    description: str = ""
    category: str = ""
    file_path: str = ""
    is_modified: bool = False
    validation_rule: Optional[str] = None
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    is_valid: bool = True
    validation_error: str = ""


@dataclass
class ConfigFile:
    """Configuration file information"""

    name: str
    path: str
    description: str
    data: Dict[str, Any]
    last_loaded: Optional[datetime] = None


class PropertyEditorWidget(QWidget):
    """Property editor for individual configuration values"""

    value_changed = Signal(str, object)  # key, new_value

    def __init__(self, config_value: ConfigValue, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_value = config_value
        self.editor_widget = None
        self.validation_rules = ConfigValidator.get_validation_rules()
        self.setup_ui()
        self.validate_current_value()

    def setup_ui(self) -> None:
        """Setup property editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header with key name and type
        header_layout = QHBoxLayout()

        key_label = QLabel(self.config_value.key)
        key_label.setStyleSheet(
            """
            font-weight: bold;
            font-size: 14px;
            color: #ffffff;
        """
        )
        header_layout.addWidget(key_label)

        header_layout.addStretch()

        type_label = QLabel(f"({self.config_value.data_type})")
        type_label.setStyleSheet("color: #888888; font-size: 11px;")
        header_layout.addWidget(type_label)

        layout.addLayout(header_layout)

        # Description if available
        if self.config_value.description:
            desc_label = QLabel(self.config_value.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #cccccc; font-size: 11px; margin-bottom: 10px;")
            layout.addWidget(desc_label)

        # Editor widget based on type
        self.editor_widget = self.create_editor_widget()
        if self.editor_widget:
            layout.addWidget(self.editor_widget)

        # Validation status
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.validation_label)

        # File path info
        if self.config_value.file_path:
            file_label = QLabel(f"File: {os.path.basename(self.config_value.file_path)}")
            file_label.setStyleSheet("color: #777777; font-size: 11px; margin-top: 5px;")
            layout.addWidget(file_label)

        layout.addStretch()

    def create_editor_widget(self) -> Optional[QWidget]:
        """Create appropriate editor widget based on value type"""
        value = self.config_value.value
        data_type = self.config_value.data_type

        # Special handling for specific settings with predefined options
        if self.config_value.key == "logging.level":
            combo = QComboBox()
            combo.addItems(["DEBUG", "INFO"])
            combo.setCurrentText(str(value) if value is not None else "INFO")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "application.environment":
            combo = QComboBox()
            combo.addItems(["development", "production", "testing"])
            combo.setCurrentText(str(value) if value is not None else "development")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "active_profile":
            combo = QComboBox()
            # Get available profiles from test_profiles directory
            profiles = self._get_available_profiles()
            combo.addItems(profiles)
            combo.setCurrentText(str(value) if value is not None else "default")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "robot.model" or self.config_value.key == "digital_io.model":
            combo = QComboBox()
            combo.addItems(["mock", "ajinextek"])
            combo.setCurrentText(str(value) if value is not None else "mock")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "power.model":
            combo = QComboBox()
            combo.addItems(["mock", "oda"])
            combo.setCurrentText(str(value) if value is not None else "mock")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "loadcell.model":
            combo = QComboBox()
            combo.addItems(["mock", "bs205"])
            combo.setCurrentText(str(value) if value is not None else "mock")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key == "mcu.model":
            combo = QComboBox()
            combo.addItems(["mock", "lma"])
            combo.setCurrentText(str(value) if value is not None else "mock")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key.endswith(".parity"):
            combo = QComboBox()
            combo.addItems(["none", "even", "odd"])
            # Handle null value for parity
            current_value = str(value) if value is not None else "none"
            if current_value.lower() == "null":
                current_value = "none"
            combo.setCurrentText(current_value)
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key.endswith(".contact_type"):
            combo = QComboBox()
            combo.addItems(["A", "B"])
            combo.setCurrentText(str(value) if value is not None else "A")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        elif self.config_value.key.endswith(".edge_type"):
            combo = QComboBox()
            combo.addItems(["rising", "falling"])
            combo.setCurrentText(str(value) if value is not None else "rising")
            combo.currentTextChanged.connect(self.emit_value_changed)
            return combo

        if data_type == "bool":
            # Use QPushButton as reliable checkbox replacement
            checkbox_btn = QPushButton()
            checkbox_btn.setCheckable(True)
            checkbox_btn.setFixedSize(25, 25)

            # Set initial state
            checkbox_btn.blockSignals(True)
            checkbox_btn.setChecked(bool(value))
            checkbox_btn.blockSignals(False)

            # Update appearance based on state
            def update_appearance():
                if checkbox_btn.isChecked():
                    checkbox_btn.setText("✓")
                    checkbox_btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #0078d4;
                            color: #ffffff;
                            border: 2px solid #0078d4;
                            border-radius: 3px;
                            font-weight: bold;
                            font-size: 16px;
                        }
                        QPushButton:hover {
                            background-color: #106ebe;
                        }
                        QPushButton:focus {
                            outline: none;
                        }
                    """
                    )
                else:
                    checkbox_btn.setText("✗")
                    checkbox_btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #2d2d2d;
                            color: #ffffff;
                            border: 2px solid #555555;
                            border-radius: 3px;
                            font-weight: bold;
                            font-size: 16px;
                        }
                        QPushButton:hover {
                            background-color: #3d3d3d;
                            border-color: #0078d4;
                        }
                        QPushButton:focus {
                            outline: none;
                        }
                    """
                    )

            # Set initial appearance
            update_appearance()

            # Connect signals
            def on_toggle():
                update_appearance()
                self.emit_value_changed(checkbox_btn.isChecked())

            checkbox_btn.toggled.connect(on_toggle)
            logger.debug(f"🔘 Created QPushButton checkbox for {self.config_value.key}: {value}")
            return checkbox_btn

        elif data_type == "int":
            spinbox = QSpinBox()
            spinbox.setRange(-2147483648, 2147483647)
            spinbox.setValue(int(value) if value is not None else 0)
            spinbox.valueChanged.connect(self.emit_value_changed)
            return spinbox

        elif data_type == "float":
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-999999.999, 999999.999)
            spinbox.setDecimals(3)
            spinbox.setValue(float(value) if value is not None else 0.0)
            spinbox.valueChanged.connect(self.emit_value_changed)
            return spinbox

        elif data_type == "str":
            line_edit = QLineEdit()
            line_edit.setText(str(value) if value is not None else "")
            line_edit.textChanged.connect(self.emit_value_changed)
            return line_edit

        elif data_type in ["list", "dict"]:
            text_edit = QTextEdit()
            text_edit.setMaximumHeight(150)
            try:
                text_edit.setPlainText(yaml.dump(value, default_flow_style=False))
            except yaml.YAMLError:
                text_edit.setPlainText(str(value))
            text_edit.textChanged.connect(lambda: self.emit_value_changed(text_edit.toPlainText()))
            return text_edit

        else:
            # Default to line edit
            line_edit = QLineEdit()
            line_edit.setText(str(value) if value is not None else "")
            line_edit.textChanged.connect(self.emit_value_changed)
            return line_edit

    def emit_value_changed(self, new_value: Any) -> None:
        """Emit value changed signal"""
        logger.debug(
            f"🔧 emit_value_changed: {self.config_value.key} = {new_value} (type: {type(new_value).__name__})"
        )

        # For bool values, log current checkbox state
        if (
            self.config_value.data_type == "bool"
            and hasattr(self, "editor_widget")
            and isinstance(self.editor_widget, QCheckBox)
        ):
            actual_ui_state = self.editor_widget.isChecked()
            logger.debug(f"🔘 Checkbox UI state: {actual_ui_state}, new_value: {new_value}")

        # For bool values, ensure they are actually bool type
        if self.config_value.data_type == "bool" and not isinstance(new_value, bool):
            logger.warning(f"⚠️ Converting non-bool value to bool: {new_value} → {bool(new_value)}")
            new_value = bool(new_value)

        self.config_value.value = new_value
        self.config_value.is_modified = True
        self.validate_current_value()
        self.value_changed.emit(self.config_value.key, new_value)

    def validate_current_value(self) -> None:
        """Validate the current value and update UI"""
        is_valid, error_msg = ConfigValidator.validate_value(
            self.config_value.key, self.config_value.value, self.validation_rules
        )

        self.config_value.is_valid = is_valid
        self.config_value.validation_error = error_msg

        if is_valid:
            self.validation_label.setText("✓ Valid")
            self.validation_label.setStyleSheet("color: #00ff00; font-size: 11px; margin-top: 5px;")
        else:
            self.validation_label.setText(f"✗ {error_msg}")
            self.validation_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")

        # Update editor widget styling based on validation
        if self.editor_widget:
            if is_valid:
                self.editor_widget.setStyleSheet("")
            else:
                self.editor_widget.setStyleSheet(
                    "border: 1px solid #ff4444; background-color: #4d2d2d;"
                )

    def _get_available_profiles(self) -> List[str]:
        """Get available test profiles from test_profiles directory"""
        # Standard library imports
        import glob

        profiles = []
        try:
            # Get test_profiles directory path
            test_profiles_dir = "../configuration/test_profiles"
            if os.path.exists(test_profiles_dir):
                # Find all .yaml files in the directory
                yaml_files = glob.glob(os.path.join(test_profiles_dir, "*.yaml"))
                # Extract just the filename without extension
                profiles = [os.path.splitext(os.path.basename(f))[0] for f in yaml_files]
                profiles.sort()  # Sort alphabetically

            # Ensure 'default' is always available
            if not profiles or "default" not in profiles:
                profiles = ["default"] + [p for p in profiles if p != "default"]

        except Exception:
            # Fallback to default if there's any error
            profiles = ["default"]

        return profiles


class SettingsTreeWidget(QTreeWidget):
    """Tree widget for displaying configuration settings"""

    setting_selected = Signal(object)  # ConfigValue

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_values: Dict[str, ConfigValue] = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup settings tree UI"""
        self.setHeaderLabel("Settings")
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)

        self.setStyleSheet(
            """
            QTreeWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                selection-background-color: #0078d4;
                alternate-background-color: #353535;
            }
            QTreeWidget:focus {
                outline: none;
            }
            QTreeWidget::item {
                height: 25px;
                padding: 2px;
                background-color: #2d2d2d;
            }
            QTreeWidget::item:alternate {
                background-color: #353535;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
            }
        """
        )

        # Connect selection signal
        self.itemClicked.connect(self.on_item_clicked)

        # Connect expansion signal for accordion behavior
        self.itemExpanded.connect(self.on_item_expanded)

    def load_config_data(self, config_files: Dict[str, ConfigFile]) -> None:
        """Load configuration data into tree"""
        self.clear()
        self.config_values.clear()

        first_item = True
        for file_name, config_file in config_files.items():
            # Create file root item
            file_item = QTreeWidgetItem(self, [file_name])
            file_item.setData(
                0, Qt.ItemDataRole.UserRole, {"type": "file", "config_file": config_file}
            )

            # Add categories and settings (no file_name prefix to avoid duplicate keys)
            self.add_config_items(file_item, config_file.data, config_file.path, "")

            # Only expand the first item for accordion behavior
            if first_item:
                file_item.setExpanded(True)
                first_item = False
            else:
                file_item.setExpanded(False)

    def add_config_items(
        self,
        parent_item: QTreeWidgetItem,
        data: Dict[str, Any],
        file_path: str,
        category_prefix: str = "",
    ) -> None:
        """Recursively add configuration items to tree"""
        for key, value in data.items():
            if key == "metadata":
                continue  # Skip metadata sections

            item_key = f"{category_prefix}.{key}" if category_prefix else key

            if isinstance(value, dict):
                # Create category item
                category_item = QTreeWidgetItem(parent_item, [key])
                category_item.setData(
                    0, Qt.ItemDataRole.UserRole, {"type": "category", "key": item_key}
                )

                # Recursively add sub-items
                self.add_config_items(category_item, value, file_path, item_key)
                category_item.setExpanded(True)
            else:
                # Create setting item
                setting_item = QTreeWidgetItem(parent_item, [key])

                # Create ConfigValue
                config_value = ConfigValue(
                    key=item_key,
                    value=value,
                    data_type=type(value).__name__,
                    file_path=file_path,
                    category=category_prefix,
                )

                setting_item.setData(
                    0, Qt.ItemDataRole.UserRole, {"type": "setting", "config_value": config_value}
                )
                self.config_values[item_key] = config_value

                # Set icon based on type
                if isinstance(value, bool):
                    setting_item.setText(0, f"{key} ✓" if value else f"{key} ✗")
                else:
                    value_str = str(value)
                    if len(value_str) > 50:
                        setting_item.setText(0, f"{key}: {value_str[:50]}...")
                    else:
                        setting_item.setText(0, f"{key}: {value_str}")

    def on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        """Handle item click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            if data.get("type") == "setting":
                # Handle setting selection
                config_value = data.get("config_value")
                if config_value:
                    self.setting_selected.emit(config_value)
            elif data.get("type") == "category":
                # Handle category expansion/collapse with single click
                item.setExpanded(not item.isExpanded())
            elif data.get("type") == "file":
                # Handle top-level file item expansion/collapse with single click
                item.setExpanded(not item.isExpanded())

    def on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle item expansion - implement accordion behavior"""
        # Only apply accordion behavior to top-level items (file items)
        if item.parent() is None:
            # Collapse all other top-level items
            for i in range(self.topLevelItemCount()):
                top_item = self.topLevelItem(i)
                if top_item is not None and top_item != item and top_item.isExpanded():
                    top_item.setExpanded(False)

    def filter_tree(self, search_text: str) -> None:
        """Filter tree items based on search text"""
        if not search_text:
            # Show all items when search is empty
            self.show_all_items()
            self.update_status_message("")
            return

        search_text_lower = search_text.lower()
        matching_files = 0
        matching_settings = 0

        # Filter each top-level file item
        for i in range(self.topLevelItemCount()):
            file_item = self.topLevelItem(i)
            if file_item is None:
                continue
            file_name = file_item.text(0)

            # Check if file name matches
            file_matches = search_text_lower in file_name.lower()

            # Check settings within this file
            settings_match_count = self.filter_file_item(file_item, search_text_lower, file_matches)

            # Hide/show file based on matches
            has_matches = file_matches or settings_match_count > 0
            file_item.setHidden(not has_matches)

            if has_matches:
                matching_files += 1
                matching_settings += settings_match_count
                # Expand file if it has matches
                file_item.setExpanded(True)

        self.update_status_message(search_text, matching_files, matching_settings)

    def filter_file_item(
        self, file_item: QTreeWidgetItem, search_text_lower: str, file_matches: bool
    ) -> int:
        """Filter items within a file and return count of matches"""
        matching_count = 0

        for i in range(file_item.childCount()):
            child_item = file_item.child(i)
            child_matches = self.filter_item_recursive(child_item, search_text_lower, file_matches)
            if child_matches:
                matching_count += child_matches

        return matching_count

    def filter_item_recursive(
        self, item: QTreeWidgetItem, search_text_lower: str, parent_matches: bool
    ) -> int:
        """Recursively filter item and its children"""
        item_text = item.text(0).lower()
        item_matches = parent_matches or search_text_lower in item_text

        matching_count = 0

        # Check children first
        for i in range(item.childCount()):
            child_item = item.child(i)
            child_matches = self.filter_item_recursive(child_item, search_text_lower, item_matches)
            matching_count += child_matches

        # If this item or any children match, show it
        has_matches = item_matches or matching_count > 0
        item.setHidden(not has_matches)

        if has_matches:
            item.setExpanded(True)
            # Count this item as a match if it's a setting (leaf node)
            if item.childCount() == 0 and item_matches:
                matching_count += 1

        return matching_count

    def show_all_items(self) -> None:
        """Show all items in the tree"""
        for i in range(self.topLevelItemCount()):
            file_item = self.topLevelItem(i)
            if file_item is None:
                continue
            file_item.setHidden(False)
            # Only expand the first item to maintain accordion behavior
            if i == 0:
                file_item.setExpanded(True)
                self.show_all_children(file_item)
            else:
                file_item.setExpanded(False)

    def show_all_children(self, item: QTreeWidgetItem) -> None:
        """Recursively show all children of an item"""
        for i in range(item.childCount()):
            child_item = item.child(i)
            child_item.setHidden(False)
            child_item.setExpanded(True)
            self.show_all_children(child_item)

    def update_status_message(
        self, search_text: str = "", files: int = 0, settings: int = 0
    ) -> None:
        """Update status message with search results"""
        parent_widget = self.parent()
        while parent_widget is not None:
            if hasattr(parent_widget, "status_label"):
                status_label = getattr(parent_widget, "status_label", None)
                if status_label is not None:
                    if search_text:
                        if files == 0 and settings == 0:
                            status_label.setText(f"No matches found for '{search_text}'")
                        else:
                            status_label.setText(
                                f"Found {settings} settings in {files} files for '{search_text}'"
                            )
                    else:
                        status_label.setText(
                            f"Loaded {self.topLevelItemCount()} configuration files - Changes auto-save"
                        )
                    return
            parent_widget = parent_widget.parent()


class SettingsWidget(QWidget):
    """Main settings widget with 2-panel layout"""

    settings_changed = Signal()

    def __init__(
        self,
        container: Optional[SimpleReloadableContainer] = None,
        state_manager: Optional[GUIStateManager] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.config_files: Dict[str, ConfigFile] = {}
        self.current_property_editor = None

        self.setup_ui()
        self.load_configuration_files()
        self._connect_container_reload()

    def setup_ui(self) -> None:
        """Setup main settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(0)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Main content with 2-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Settings tree
        self.settings_tree = SettingsTreeWidget()
        self.settings_tree.setting_selected.connect(self.on_setting_selected)
        splitter.addWidget(self.settings_tree)

        # Right panel: Property editor
        self.property_panel = QScrollArea()
        self.property_panel.setWidgetResizable(True)
        self.property_panel.setMinimumWidth(350)
        self.property_panel.setStyleSheet(
            """
            QScrollArea {
                background-color: #2d2d2d;
                border: 1px solid #404040;
            }
        """
        )
        splitter.addWidget(self.property_panel)

        # Set splitter proportions (50% : 50%)
        splitter.setSizes([500, 500])

        layout.addWidget(splitter)

        # Footer with action buttons
        footer = self.create_footer()
        layout.addWidget(footer)

        # Apply main widget styling for consistency
        self.setStyleSheet(
            """
            SettingsWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
        """
        )

    def create_header(self) -> QWidget:
        """Create header with title and search"""
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(
            """
            QFrame {
                background-color: #1e1e1e;
            }
        """
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 10, 15, 10)

        # Title
        title = QLabel("Settings")
        title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title)

        layout.addStretch()

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search settings, files, or categories...")
        self.search_box.setFixedWidth(250)
        self.search_box.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
        """
        )
        self.search_box.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_box)

        return header

    def create_footer(self) -> QWidget:
        """Create footer with action buttons"""
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet(
            """
            QFrame {
                background-color: #404040;
                border-top: 1px solid #555555;
            }
        """
        )

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(15, 10, 15, 10)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Action buttons
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_config)
        layout.addWidget(import_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_config)
        layout.addWidget(export_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_config)
        layout.addWidget(reset_btn)

        return footer

    def load_configuration_files(self) -> None:
        """Load all configuration files"""
        base_config_paths = {
            "Application": "../configuration/application.yaml",
            "Hardware": "../configuration/hardware_config.yaml",
            "Heating/Cooling Test": "../configuration/heating_cooling_time_test.yaml",
            "Profile Management": "../configuration/profile.yaml",
            "DUT Defaults": "../configuration/dut_defaults.yaml",
        }

        self.config_files.clear()

        # Load base configuration files
        for name, rel_path in base_config_paths.items():
            try:
                full_path = Path(rel_path)
                if full_path.exists():
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}

                    config_file = ConfigFile(
                        name=name,
                        path=str(full_path),
                        description=f"Configuration file: {name}",
                        data=data,
                        last_loaded=datetime.now(),
                    )

                    self.config_files[name] = config_file

            except Exception as e:
                print(f"Failed to load {name}: {e}")

        # Load active test profile dynamically
        self.load_active_test_profile()

        # Update UI
        self.settings_tree.load_config_data(self.config_files)

        self.status_label.setText(
            f"Loaded {len(self.config_files)} configuration files - Changes auto-save"
        )

    def load_active_test_profile(self) -> None:
        """Load the currently active test profile"""
        try:
            # Read profile.yaml to get active_profile
            profile_config = self.config_files.get("Profile Management")
            if not profile_config:
                return

            active_profile = profile_config.data.get("active_profile", "default")

            # Load the active test profile
            profile_path = f"../configuration/test_profiles/{active_profile}.yaml"
            full_path = Path(profile_path)

            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                config_file = ConfigFile(
                    name=f"Active Test Profile ({active_profile})",
                    path=str(full_path),
                    description=f"Currently active test profile: {active_profile}",
                    data=data,
                    last_loaded=datetime.now(),
                )

                self.config_files[f"Active Test Profile ({active_profile})"] = config_file
                logger.info(f"📋 Loaded active test profile: {active_profile}")

            else:
                logger.warning(f"⚠️ Active test profile file not found: {profile_path}")

        except Exception as e:
            logger.error(f"❌ Failed to load active test profile: {e}")
            print(f"Failed to load active test profile: {e}")

    def on_setting_selected(self, config_value: ConfigValue) -> None:
        """Handle setting selection"""
        # Create property editor
        if self.current_property_editor:
            self.current_property_editor.deleteLater()

        self.current_property_editor = PropertyEditorWidget(config_value)
        self.current_property_editor.value_changed.connect(self.on_setting_changed)
        logger.debug(f"🔗 Connected value_changed signal for: {config_value.key}")

        self.property_panel.setWidget(self.current_property_editor)
        self.status_label.setText(f"Editing: {config_value.key}")

    def on_setting_changed(self, key: str, new_value: Any) -> None:
        """Handle setting value change with immediate auto-save"""
        logger.info(f"🔧 Setting changed: {key} = {new_value} (type: {type(new_value).__name__})")

        # Check if this is a hardware-related setting
        is_hardware_setting = self._is_hardware_related_setting(key)
        logger.info(f"🔧 Hardware-related setting: {is_hardware_setting}")

        # Find the config file and update the value
        saved_file = None
        for config_file in self.config_files.values():
            logger.debug(f"🔍 Checking file: {config_file.path}")
            if self.update_nested_dict(config_file.data, key, new_value):
                saved_file = config_file
                logger.info(f"✅ Found target file: {saved_file.path}")
                break
            else:
                logger.debug(f"❌ Key '{key}' not found in {config_file.path}")

        if saved_file:
            # Immediately save the configuration file
            try:
                logger.info(f"💾 Attempting to save file: {saved_file.path}")
                with open(saved_file.path, "w", encoding="utf-8") as f:
                    yaml.dump(saved_file.data, f, default_flow_style=False, indent=2)

                self.status_label.setText(f"Auto-saved: {key}")
                logger.info(
                    f"✅ Successfully auto-saved setting: {key} = {new_value} to {saved_file.path}"
                )

                # Check if active_profile was changed
                if key == "active_profile":
                    logger.info(f"🔄 Active profile changed to: {new_value}")
                    self.reload_active_test_profile(new_value)

            except Exception as e:
                self.status_label.setText(f"Save failed: {str(e)}")
                logger.error(f"❌ Failed to auto-save {key} to {saved_file.path}: {e}")
                QMessageBox.warning(self, "Auto-save Error", f"Failed to save {key}: {str(e)}")
        else:
            logger.warning(f"⚠️ No target file found for setting: {key}")
            self.status_label.setText("Save failed: No target file found")

        # Update tree item text immediately after successful save
        if saved_file:
            self.update_tree_item_text(key, new_value)

        # Emit signal to trigger hot-reload
        logger.info(f"🚀 Emitting settings_changed signal for: {key}")
        self.settings_changed.emit()

    def update_tree_item_text(self, key: str, new_value: Any) -> None:
        """Update tree item text after value change"""
        logger.debug(f"🔄 Updating tree item text for: {key} = {new_value}")

        # Update the ConfigValue in our dictionary
        if key in self.settings_tree.config_values:
            self.settings_tree.config_values[key].value = new_value

        # Find and update the tree item
        iterator = QTreeWidgetItemIterator(self.settings_tree)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.ItemDataRole.UserRole)

            if data and data.get("type") == "setting":
                config_value = data.get("config_value")
                if config_value and config_value.key == key:
                    # Update the item text based on type
                    key_name = key.split(".")[-1]  # Get the last part of the key
                    if isinstance(new_value, bool):
                        item.setText(0, f"{key_name} ✓" if new_value else f"{key_name} ✗")
                    else:
                        value_str = str(new_value)
                        if len(value_str) > 50:
                            item.setText(0, f"{key_name}: {value_str[:50]}...")
                        else:
                            item.setText(0, f"{key_name}: {value_str}")

                    logger.debug(f"✅ Updated tree item text for: {key}")
                    break

            iterator += 1

    def reload_active_test_profile(self, new_profile: str) -> None:
        """Reload the active test profile when profile changes"""
        try:
            # Remove old active test profile entries
            keys_to_remove = [
                k for k in self.config_files.keys() if k.startswith("Active Test Profile")
            ]
            for key in keys_to_remove:
                del self.config_files[key]

            # Load new active test profile
            self.load_active_test_profile()

            # Update the settings tree
            self.settings_tree.load_config_data(self.config_files)

            self.status_label.setText(f"Switched to test profile: {new_profile}")
            logger.info(f"🔄 Switched to active test profile: {new_profile}")

        except Exception as e:
            logger.error(f"❌ Failed to reload test profile {new_profile}: {e}")
            self.status_label.setText(f"Failed to load profile: {new_profile}")

    def on_search_changed(self, search_text: str) -> None:
        """Handle search text changes"""
        self.settings_tree.filter_tree(search_text.strip())

    def update_nested_dict(self, data: Dict[str, Any], key: str, value: Any) -> bool:
        """Update nested dictionary value by key path"""
        logger.debug(f"🔧 Updating nested dict: {key} = {value}")
        keys = key.split(".")
        current = data

        # Navigate to parent
        for i, k in enumerate(keys[:-1]):
            if k in current and isinstance(current[k], dict):
                current = current[k]
                logger.debug(f"  📂 Navigated to: {'.'.join(keys[:i+1])}")
            else:
                logger.debug(f"  ❌ Key path broken at: {'.'.join(keys[:i+1])}")
                return False

        # Update value
        final_key = keys[-1]
        if final_key in current:
            old_value = current[final_key]

            # Preserve data types, especially for booleans
            if isinstance(old_value, bool) and not isinstance(value, bool):
                logger.debug(f"  🔄 Converting to bool for consistency: {value} → {bool(value)}")
                value = bool(value)

            current[final_key] = value
            logger.debug(
                f"  ✅ Updated {final_key}: {old_value} → {value} (type: {type(value).__name__})"
            )
            return True
        else:
            logger.debug(f"  ❌ Final key '{final_key}' not found in current dict")
            return False

    def save_all_config(self) -> None:
        """Save all configuration files (used for reset functionality)"""
        saved_count = 0

        for config_file in self.config_files.values():
            try:
                with open(config_file.path, "w", encoding="utf-8") as f:
                    yaml.dump(config_file.data, f, default_flow_style=False, indent=2)

                saved_count += 1

            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Failed to save {config_file.name}: {e}")

        if saved_count > 0:
            self.status_label.setText("All configurations saved")
        else:
            self.status_label.setText("Save operation completed")

    def reset_config(self) -> None:
        """Reset all configurations"""
        reply = QMessageBox.question(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all configurations to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.load_configuration_files()
            self.status_label.setText("Configuration reset")

    def import_config(self) -> None:
        """Import configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "YAML files (*.yaml *.yml);;All files (*)"
        )

        if file_path:
            # Implementation for importing config
            self.status_label.setText("Import functionality not yet implemented")

    def export_config(self) -> None:
        """Export configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            "config_export.yaml",
            "YAML files (*.yaml *.yml);;All files (*)",
        )

        if file_path:
            # Implementation for exporting config
            self.status_label.setText("Export functionality not yet implemented")

    def _connect_container_reload(self) -> None:
        """Connect settings changes to container reload for hot-reload functionality"""
        if self.container:
            # Connect settings_changed signal to trigger container reload
            self.settings_changed.connect(self._on_settings_changed_for_reload)
            logger.info("🔗 Connected SettingsWidget to container reload for hot-reload")
        else:
            logger.warning("⚠️ Container not available - hot-reload disabled")

    def _on_settings_changed_for_reload(self) -> None:
        """Handle settings changes by triggering container reload if needed"""
        logger.info("🔔 Settings changed - evaluating hot-reload necessity...")

        if not self.container:
            logger.warning("⚠️ Container not available - hot-reload disabled")
            self.status_label.setText("⚠️ Container unavailable")
            return

        # Comprehensive debugging and method detection for dependency-injector containers
        logger.info("🔍 Starting comprehensive container analysis...")
        logger.info(f"🔍 Container type: {type(self.container)}")
        logger.info(f"🔍 Container class: {self.container.__class__}")
        logger.info(
            f"🔍 Container MRO: {[cls.__name__ for cls in self.container.__class__.__mro__]}"
        )

        # Check if container is the correct type
        if isinstance(self.container, SimpleReloadableContainer):
            logger.info("✅ Container is SimpleReloadableContainer - proceeding with direct access")
            try:
                # Direct method access since we know it's the right type
                success = self.container.reload_configuration()
                logger.info("✅ Direct method call succeeded")
            except Exception as e:
                logger.error(f"❌ Direct method call failed: {e}")
                self.status_label.setText(f"❌ Reload error: {str(e)}")
                return
        else:
            logger.info(f"🔍 Container is DynamicContainer instance: {type(self.container)}")
            logger.info("🔍 Available container methods:")
            container_methods = [
                method for method in dir(self.container) if not method.startswith("_")
            ]
            logger.info(f"🔍 Methods: {container_methods}")

            # Try multiple detection methods as fallback
            reload_method = None
            method_found = False

            # Method 1: Direct attribute access
            try:
                reload_method = self.container.reload_configuration
                method_found = True
                logger.info("✅ Method found via direct attribute access")
            except AttributeError:
                logger.warning("❌ Direct attribute access failed")

            # Method 2: getattr with default
            if not method_found:
                reload_method = getattr(self.container, "reload_configuration", None)
                if reload_method and callable(reload_method):
                    method_found = True
                    logger.info("✅ Method found via getattr")
                else:
                    logger.warning("❌ getattr method detection failed")

            if not method_found:
                logger.warning("⚠️ All method detection approaches failed")
                self.status_label.setText("⚠️ Hot-reload not supported")
                return

            # Call the found method
            logger.info("🔄 Triggering container configuration reload...")
            logger.info(f"🏭 Container instance ID: {id(self.container)}")

            try:
                if reload_method is None:
                    logger.error("❌ reload_method is None despite method detection")
                    self.status_label.setText("❌ Internal error: method is None")
                    return
                success = reload_method()
                logger.info("✅ Fallback method call succeeded")

                if success:
                    self.status_label.setText("✅ Configuration reloaded successfully")
                    logger.info("✅ Hot-reload: Configuration applied to running system")

                    # Log verification of hardware services
                    try:
                        facade = self.container.hardware_service_facade()
                        robot_service = facade.robot_service
                        robot_class = robot_service.__class__.__name__
                        logger.info(f"🤖 Active robot service: {robot_class}")

                        # Log current configuration values
                        robot_model = self.container.config.hardware.robot.model()
                        robot_axis = self.container.config.hardware.robot.axis_id()
                        logger.info(
                            f"📋 Current robot config: model={robot_model}, axis_id={robot_axis}"
                        )

                    except Exception as verification_error:
                        logger.warning(
                            f"⚠️ Could not verify hardware services: {verification_error}"
                        )

                else:
                    self.status_label.setText("❌ Configuration reload failed")
                    logger.error("❌ Hot-reload: Configuration reload failed")

            except AttributeError:
                logger.warning("⚠️ Container reload_configuration method not available")
                self.status_label.setText("⚠️ Hot-reload not supported")

            except Exception as e:
                logger.error(f"❌ Fallback method call failed: {e}")
                self.status_label.setText(f"❌ Reload error: {str(e)}")

    def _is_hardware_related_setting(self, key: str) -> bool:
        """Check if a setting key is related to hardware configuration"""
        hardware_prefixes = [
            "hardware.",
            "robot.",
            "power.",
            "loadcell.",
            "mcu.",
            "digital_io.",
        ]
        return any(key.startswith(prefix) for prefix in hardware_prefixes)
