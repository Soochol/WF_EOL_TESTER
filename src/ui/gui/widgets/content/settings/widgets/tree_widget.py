"""
Settings tree widget for displaying configuration hierarchy.

Provides a tree view for browsing configuration files and settings
with search and filtering capabilities.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QWidget,
)

# Local folder imports
from ..core import Colors, ConfigFile, ConfigValue, EditorTypes, Styles


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
        self.setAlternatingRowColors(False)
        self.setStyleSheet(Styles.TREE_WIDGET)

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemExpanded.connect(self.on_item_expanded)

    def load_config_data(self, config_files: Dict[str, ConfigFile]) -> None:
        """Load configuration data into tree"""
        self.clear()
        self.config_values.clear()

        for file_name, config_file in config_files.items():
            # Create file root item
            file_item = QTreeWidgetItem(self, [file_name])
            file_item.setData(
                0, Qt.ItemDataRole.UserRole, {"type": "file", "config_file": config_file}
            )

            # Add categories and settings
            self.add_config_items(file_item, config_file.data, config_file.path, "")

            # Application and GUI-related files start expanded by default
            if file_name in ["Application", "Hardware", "Test Profile"]:
                file_item.setExpanded(True)
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

                # Determine allowed values using EditorTypes
                allowed_values = None

                # First, try to get allowed values from EditorTypes based on full key path
                allowed_values = EditorTypes.get_combo_options(item_key)

                # If not found, check for specific key patterns
                if not allowed_values:
                    if key == "model":
                        # Extract hardware type from category (e.g., "robot", "digital_io")
                        hardware_type = category_prefix.split(".")[-1] if category_prefix else None
                        if hardware_type == "robot":
                            allowed_values = ["mock", "ajinextek"]
                        elif hardware_type == "digital_io":
                            allowed_values = ["mock", "ajinextek"]
                        elif hardware_type == "power":
                            allowed_values = ["mock", "oda"]
                        elif hardware_type == "loadcell":
                            allowed_values = ["mock", "bs205"]
                        elif hardware_type == "mcu":
                            allowed_values = ["mock", "lma"]
                    elif key == "port":
                        # Get available serial ports
                        allowed_values = self._get_available_ports(value)
                    elif key == "baudrate":
                        # Common baudrate values for serial communication
                        allowed_values = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
                        # Ensure current value is in the list
                        if value and isinstance(value, int) and value not in allowed_values:
                            allowed_values.append(value)
                            allowed_values.sort()
                    elif key == "parity":
                        # Standard parity options for serial communication
                        allowed_values = ["none", "even", "odd", "mark", "space"]
                        # Handle null/None values
                        if value is None or value == "null":
                            value = "none"
                        # Ensure current value is in the list
                        if value and isinstance(value, str) and value.lower() not in allowed_values:
                            allowed_values.append(value.lower())
                            allowed_values.sort()

                # Create ConfigValue
                config_value = ConfigValue(
                    key=item_key,
                    value=value,
                    data_type=type(value).__name__,
                    file_path=file_path,
                    category=category_prefix,
                    allowed_values=allowed_values,
                )

                setting_item.setData(
                    0, Qt.ItemDataRole.UserRole, {"type": "setting", "config_value": config_value}
                )
                self.config_values[item_key] = config_value

                # Set modern glassmorphism background for setting items (leaf nodes)
                setting_item.setBackground(0, QBrush(QColor(Colors.TREE_SETTING_ITEM_BACKGROUND)))

                # Add modern tooltip
                setting_item.setToolTip(0, "✏️ Click to edit this setting")

                # Set text color based on value type for better visual distinction
                if isinstance(value, bool):
                    # Green for True, Red for False
                    setting_item.setForeground(0, QBrush(QColor("#00D9A5" if value else "#F44336")))
                elif isinstance(value, (int, float)):
                    # Blue for numbers
                    setting_item.setForeground(0, QBrush(QColor("#2196F3")))

                # Set display text based on type
                self._set_item_display_text(setting_item, key, value)

    def _set_item_display_text(self, item: QTreeWidgetItem, key: str, value: Any) -> None:
        """Set display text for tree item based on value type"""
        # Add edit icon (📝) to indicate this is an editable leaf node
        edit_icon = "📝 "

        if isinstance(value, bool):
            item.setText(0, f"{edit_icon}{key} ✓" if value else f"{edit_icon}{key} ✗")
        else:
            value_str = str(value)
            if len(value_str) > 50:
                item.setText(0, f"{edit_icon}{key}: {value_str[:50]}...")
            else:
                item.setText(0, f"{edit_icon}{key}: {value_str}")

    def on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        """Handle item click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")

        if item_type == "setting":
            # Handle setting selection
            config_value = data.get("config_value")
            if config_value:
                self.setting_selected.emit(config_value)
        elif item_type in ("category", "file"):
            # Handle expansion/collapse with single click
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
            # All items remain collapsed
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

    def _get_available_ports(self, current_value: Any) -> List[str]:
        """Get list of available serial ports"""
        try:
            import serial.tools.list_ports

            # Get available ports
            ports = serial.tools.list_ports.comports()
            available_ports = [port.device for port in ports]

            # Ensure current value is in the list (for manual entry support)
            if current_value and isinstance(current_value, str):
                if current_value not in available_ports:
                    available_ports.append(current_value)

            # Sort ports for better UX
            available_ports.sort()

            # If no ports found, provide some common defaults
            if not available_ports:
                available_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"]
                if current_value and isinstance(current_value, str) and current_value not in available_ports:
                    available_ports.append(current_value)
                    available_ports.sort()

            return available_ports

        except ImportError:
            # If pyserial is not available, return common default ports
            default_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"]
            if current_value and isinstance(current_value, str) and current_value not in default_ports:
                default_ports.append(current_value)
                default_ports.sort()
            return default_ports

    def update_item_text(self, key: str, new_value: Any) -> None:
        """Update tree item text after value change"""
        # Update the ConfigValue in our dictionary
        if key in self.config_values:
            self.config_values[key].value = new_value

        # Find and update the tree item
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.ItemDataRole.UserRole)

            if data and data.get("type") == "setting":
                config_value = data.get("config_value")
                if config_value and config_value.key == key:
                    # Update the item text
                    key_name = key.split(".")[-1]  # Get the last part of the key
                    self._set_item_display_text(item, key_name, new_value)
                    break

            iterator += 1
