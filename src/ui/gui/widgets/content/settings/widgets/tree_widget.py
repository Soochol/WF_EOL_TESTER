"""
Settings tree widget for displaying configuration hierarchy.

Provides a tree view for browsing configuration files and settings
with search and filtering capabilities.
"""

# Standard library imports
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QWidget,
)

# Local folder imports
from ..core import Colors, ConfigFile, ConfigValue, EditorTypes, Styles, TreeIcons
from ..core.parameter_descriptions import ParameterDescriptions


def _get_icons_path() -> Path:
    """Get the path to the icons directory"""
    # Navigate from this file to the resources/icons directory
    current_file = Path(__file__).resolve()
    # widgets/tree_widget.py -> widgets -> settings -> content -> widgets -> gui -> ui -> src
    src_dir = current_file.parents[6]
    icons_path = src_dir / "ui" / "gui" / "resources" / "icons"
    return icons_path


class SettingsTreeWidget(QTreeWidget):
    """Tree widget for displaying configuration settings"""

    setting_selected = Signal(object)  # ConfigValue

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_values: Dict[str, ConfigValue] = {}
        self.is_filtering = False  # Track if currently filtering/searching
        self._icons_path = _get_icons_path()
        self._icon_cache: Dict[str, QIcon] = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup settings tree UI"""
        self.setHeaderLabel("Settings")
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(False)
        self.setStyleSheet(Styles.TREE_WIDGET)

        # Enhanced indentation for better hierarchy visibility
        self.setIndentation(28)  # Increased from default ~20px

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemExpanded.connect(self.on_item_expanded)

    def _get_icon(self, icon_name: str) -> QIcon:
        """Get icon from cache or load it using QSvgRenderer for proper rendering"""
        if icon_name not in self._icon_cache:
            icon_path = self._icons_path / icon_name
            if icon_path.exists():
                # Use QSvgRenderer for explicit rendering with proper size
                renderer = QSvgRenderer(str(icon_path))
                pixmap = QPixmap(20, 20)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                self._icon_cache[icon_name] = QIcon(pixmap)
            else:
                # Return empty icon if file not found
                self._icon_cache[icon_name] = QIcon()
        return self._icon_cache[icon_name]

    def _get_item_depth(self, item: QTreeWidgetItem) -> int:
        """Calculate the depth of an item in the tree"""
        depth = 0
        parent = item.parent()
        while parent is not None:
            depth += 1
            parent = parent.parent()
        return depth

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

            # Apply file-level styling (top hierarchy)
            self._apply_file_styling(file_item)

            # Add categories and settings
            self.add_config_items(file_item, config_file.data, config_file.path, "")

            # All files start collapsed by default
            file_item.setExpanded(False)

    def _apply_file_styling(self, item: QTreeWidgetItem) -> None:
        """Apply styling to file-level items (root level)"""
        # Set file icon
        item.setIcon(0, self._get_icon(TreeIcons.FILE))

        # Bold font for file items
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        item.setFont(0, font)

        # White text for maximum visibility
        item.setForeground(0, QBrush(QColor(Colors.TEXT_PRIMARY)))

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

                # Apply category styling based on depth and category type
                depth = self._get_item_depth(category_item)
                self._apply_category_styling(category_item, key, item_key, depth)

                # Recursively add sub-items
                self.add_config_items(category_item, value, file_path, item_key)
                category_item.setExpanded(False)
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
                        elif hardware_type == "power_analyzer":
                            allowed_values = ["mock", "wt1800e"]
                        elif hardware_type == "loadcell":
                            allowed_values = ["mock", "bs205"]
                        elif hardware_type == "mcu":
                            allowed_values = ["mock", "lma"]
                    elif key == "interface_type":
                        # Power analyzer interface type options
                        hardware_type = category_prefix.split(".")[-1] if category_prefix else None
                        if hardware_type == "power_analyzer":
                            allowed_values = ["tcp", "usb", "gpib"]
                    elif key == "port":
                        # Determine if this is a serial port or TCP port based on parent category
                        hardware_type = category_prefix.split(".")[-1] if category_prefix else None
                        # TCP ports: power, power_analyzer, neurohub (numeric input, not combo)
                        # Serial ports: loadcell, mcu (COM port selection)
                        if hardware_type in ("power", "power_analyzer", "neurohub"):
                            # TCP port - use numeric input (no allowed_values)
                            allowed_values = None
                        else:
                            # Serial port - get available COM ports
                            allowed_values = self._get_available_ports(value)
                    elif key == "baudrate":
                        # Common baudrate values for serial communication
                        allowed_values = [
                            1200,
                            2400,
                            4800,
                            9600,
                            19200,
                            38400,
                            57600,
                            115200,
                            230400,
                            460800,
                            921600,
                        ]
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
                    description=ParameterDescriptions.get_description(item_key),
                )

                setting_item.setData(
                    0, Qt.ItemDataRole.UserRole, {"type": "setting", "config_value": config_value}
                )
                self.config_values[item_key] = config_value

                # Apply setting item styling
                self._apply_setting_styling(setting_item, key, value)

    def _apply_category_styling(
        self, item: QTreeWidgetItem, key: str, item_key: str, depth: int
    ) -> None:
        """Apply styling to category items based on depth and type"""
        # Get category-specific icon
        icon_name = TreeIcons.get_category_icon(key)
        item.setIcon(0, self._get_icon(icon_name))

        # Font styling based on depth
        font = QFont()
        if depth == 1:
            # First level category (e.g., robot, loadcell) - semi-bold
            font.setPointSize(10)
            font.setBold(True)
            item.setForeground(0, QBrush(QColor(Colors.TEXT_PRIMARY)))
        else:
            # Nested category (e.g., buttons, sensors) - medium weight
            font.setPointSize(10)
            font.setBold(False)
            item.setForeground(0, QBrush(QColor(Colors.TEXT_SECONDARY)))
        item.setFont(0, font)

        # Apply category-specific background color for first-level categories
        if depth == 1:
            bg_color = TreeIcons.get_category_color(key)
            item.setBackground(0, QBrush(QColor(bg_color)))

        # Set tooltip
        item.setToolTip(0, f"Category: {item_key}")

    def _apply_setting_styling(
        self, item: QTreeWidgetItem, key: str, value: Any
    ) -> None:
        """Apply styling to setting items (leaf nodes)"""
        # Set edit icon for setting items
        item.setIcon(0, self._get_icon(TreeIcons.EDIT))

        # Set modern glassmorphism background for setting items (leaf nodes)
        item.setBackground(0, QBrush(QColor(Colors.TREE_SETTING_ITEM_BACKGROUND)))

        # Add modern tooltip
        item.setToolTip(0, "Click to edit this setting")

        # Smaller font for leaf items
        font = QFont()
        font.setPointSize(9)
        item.setFont(0, font)

        # Set text color based on value type for better visual distinction
        if isinstance(value, bool):
            # Green for True, Red for False
            item.setForeground(0, QBrush(QColor(Colors.SUCCESS if value else Colors.ERROR)))
        elif isinstance(value, (int, float)):
            # Blue for numbers
            item.setForeground(0, QBrush(QColor(Colors.PRIMARY_ACCENT)))

        # Set display text based on type
        self._set_item_display_text(item, key, value)

    def _set_item_display_text(self, item: QTreeWidgetItem, key: str, value: Any) -> None:
        """Set display text for tree item based on value type"""
        if isinstance(value, bool):
            # Use check/cross symbols for boolean
            symbol = " [ON]" if value else " [OFF]"
            item.setText(0, f"{key}{symbol}")
        else:
            value_str = str(value)
            if len(value_str) > 40:
                item.setText(0, f"{key}: {value_str[:40]}...")
            else:
                item.setText(0, f"{key}: {value_str}")

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
        # Skip accordion behavior during filtering/search
        if self.is_filtering:
            return

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
            self.is_filtering = False  # Not filtering anymore
            self.show_all_items()
            self.update_status_message("")
            return

        self.is_filtering = True  # Start filtering
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
                if (
                    current_value
                    and isinstance(current_value, str)
                    and current_value not in available_ports
                ):
                    available_ports.append(current_value)
                    available_ports.sort()

            return available_ports

        except ImportError:
            # If pyserial is not available, return common default ports
            default_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"]
            if (
                current_value
                and isinstance(current_value, str)
                and current_value not in default_ports
            ):
                default_ports.append(current_value)
                default_ports.sort()
            return default_ports

    def update_item_text(self, key: str, new_value: Any) -> None:
        """Update tree item text and color after value change"""
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

                    # Update color based on value type
                    if isinstance(new_value, bool):
                        # Green for True, Red for False
                        color = Colors.SUCCESS if new_value else Colors.ERROR
                        item.setForeground(0, QBrush(QColor(color)))
                    elif isinstance(new_value, (int, float)):
                        # Blue for numbers
                        item.setForeground(0, QBrush(QColor(Colors.PRIMARY_ACCENT)))

                    break

            iterator += 1
