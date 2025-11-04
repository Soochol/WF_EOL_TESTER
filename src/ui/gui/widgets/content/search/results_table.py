"""
Results Table

Tree widget for displaying search results from database with expandable measurement data.
"""

# Standard library imports
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHeaderView,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from loguru import logger

# Local application imports
from ui.gui.styles.common_styles import (
    ACCENT_BLUE,
    BACKGROUND_DARK,
    BACKGROUND_MEDIUM,
    BORDER_DEFAULT,
    get_groupbox_style,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class ResultsTable(QWidget):
    """
    Results table widget for displaying test results with expandable measurement data.

    Features:
    - Tree structure showing test summaries as parent items
    - Expandable child items showing individual measurement data
    - Checkbox selection on parent items only
    - On-demand loading of measurement data when expanded

    Signals:
        row_selected: Emitted when a row is selected (test_id)
        selection_changed: Emitted when checkbox selection changes (selected_count)
        measurement_load_requested: Emitted when measurement data needs to be loaded (test_id)
    """

    row_selected = Signal(str)  # test_id
    selection_changed = Signal(int)  # selected_count
    measurement_load_requested = Signal(str)  # test_id for loading measurements

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.test_results: List[Dict] = []
        self.loaded_measurements: Dict[str, List[Dict]] = {}  # Cache for loaded measurements
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the tree UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box for tree
        table_group = QGroupBox("Test Results")
        table_group.setStyleSheet(get_groupbox_style())
        group_layout = QVBoxLayout(table_group)

        # Create tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(
            ["☑", "Test ID", "Serial Number", "Created At", "Measurements", "Status"]
        )

        # Tree properties
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.MultiSelection)
        self.tree.setAlternatingRowColors(False)
        self.tree.setSortingEnabled(True)
        self.tree.setIndentation(0)  # Set to 0 to prevent checkbox from being pushed right
        self.tree.setAnimated(True)  # Smooth expand/collapse animation

        # Disable editing and focus
        self.tree.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Checkbox - Fixed width
        header.setMinimumSectionSize(70)  # Set minimum column width
        self.tree.setColumnWidth(0, 70)  # Fixed 70px width for checkbox column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Test ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Serial Number
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Created At
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Measurements
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status

        # Style
        self.tree.setStyleSheet(self._get_tree_style())

        # Connect signals
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemCollapsed.connect(self._on_item_collapsed)

        group_layout.addWidget(self.tree)
        layout.addWidget(table_group)

    def update_results(self, results: List[Dict]) -> None:
        """Update tree with new results (parent items only)"""
        self.test_results = results
        self.loaded_measurements.clear()  # Clear measurement cache
        self.tree.setSortingEnabled(False)  # Disable sorting while updating
        self.tree.clear()  # Clear existing items

        for result in results:
            # Create parent item for test summary
            parent_item = QTreeWidgetItem(self.tree)

            # Store full result data
            parent_item.setData(1, Qt.ItemDataRole.UserRole, result)

            # Test ID (Column 1)
            parent_item.setText(1, result.get("test_id", ""))

            # Serial Number (Column 2)
            parent_item.setText(2, result.get("serial_number", "N/A"))

            # Created At (Column 3)
            created_at = result.get("created_at")
            created_str = self._format_datetime(created_at) if created_at else "N/A"
            parent_item.setText(3, created_str)

            # Measurement Count (Column 4)
            measurement_count = result.get("measurement_count", 0)
            parent_item.setText(4, f"{measurement_count}")
            parent_item.setTextAlignment(4, Qt.AlignmentFlag.AlignCenter)

            # Status (Column 5)
            status = result.get("status", "N/A")
            status_text = status if status == "N/A" else self._format_status(status)
            parent_item.setText(5, status_text)
            parent_item.setTextAlignment(5, Qt.AlignmentFlag.AlignCenter)

            # Checkbox (Column 0) - Only for parent items
            checkbox = QCheckBox()
            checkbox.setStyleSheet(
                f"""
                QCheckBox {{
                    background-color: transparent;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {BORDER_DEFAULT};
                    border-radius: 3px;
                    background-color: {BACKGROUND_MEDIUM};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ACCENT_BLUE};
                    border-color: {ACCENT_BLUE};
                    image: none;
                }}
                QCheckBox::indicator:hover {{
                    border-color: {ACCENT_BLUE};
                }}
            """
            )
            checkbox.stateChanged.connect(self._on_checkbox_changed)

            # Left-align checkbox in cell with fixed size
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background-color: transparent;")  # Remove black shadow
            checkbox_widget.setFixedSize(QSize(70, 30))  # Fixed size to match column width
            checkbox_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            checkbox_layout = QVBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(
                Qt.AlignmentFlag.AlignLeft
            )  # Left align to prevent overlap
            checkbox_layout.setContentsMargins(5, 0, 0, 0)  # Small left padding for spacing
            self.tree.setItemWidget(parent_item, 0, checkbox_widget)

            # Debug logging for checkbox positioning
            logger.debug(
                f"Checkbox created for {result.get('test_id')}: "
                f"column_width={self.tree.columnWidth(0)}px, "
                f"widget_size={checkbox_widget.size()}, "
                f"indentation={self.tree.indentation()}px"
            )

            # Add placeholder child to show expand icon
            # Will be replaced with actual data when expanded
            if measurement_count > 0:
                placeholder_child = QTreeWidgetItem(parent_item)
                placeholder_child.setText(1, "Loading...")
                placeholder_child.setData(1, Qt.ItemDataRole.UserRole, {"is_placeholder": True})

        self.tree.setSortingEnabled(True)  # Re-enable sorting
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)
        self.tree.resizeColumnToContents(3)

        # Emit initial selection count (0)
        self.selection_changed.emit(0)

    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle item expansion - load measurement data"""
        # Check if this is a parent item (has UserRole data with test_id)
        result_data = item.data(1, Qt.ItemDataRole.UserRole)
        if not result_data or not isinstance(result_data, dict):
            return

        test_id = result_data.get("test_id")
        if not test_id:
            return

        # Check if children are placeholders
        if item.childCount() > 0:
            first_child_data = item.child(0).data(1, Qt.ItemDataRole.UserRole)
            if first_child_data and first_child_data.get("is_placeholder"):
                # Remove placeholder and load actual data
                logger.info(f"Loading measurements for test_id: {test_id}")
                self.measurement_load_requested.emit(test_id)

    def _on_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """Handle item collapse - optional cleanup"""
        # Currently no action needed on collapse
        pass

    def load_measurements_for_item(self, test_id: str, measurements: List[Dict]) -> None:
        """
        Load measurement data for a specific test_id and populate child items.
        Called by parent widget after fetching data from DB.
        """
        logger.info(f"Loading {len(measurements)} measurements for test_id: {test_id}")

        # Cache measurements
        self.loaded_measurements[test_id] = measurements

        # Find the parent item
        parent_item = self._find_parent_item_by_test_id(test_id)
        if not parent_item:
            logger.warning(f"Parent item not found for test_id: {test_id}")
            return

        # Remove existing children (including placeholders)
        parent_item.takeChildren()

        # If no measurements, show message
        if not measurements:
            no_data_child = QTreeWidgetItem(parent_item)
            no_data_child.setText(1, "No measurements found")
            no_data_child.setForeground(1, Qt.GlobalColor.gray)
            return

        # Sort measurements by timestamp or cycle_number
        sorted_measurements = sorted(
            measurements, key=lambda m: (m.get("cycle_number") or 0, m.get("timestamp") or "")
        )

        # Add child items for each measurement
        for idx, measurement in enumerate(sorted_measurements):
            child_item = QTreeWidgetItem(parent_item)

            # Store measurement data
            child_item.setData(1, Qt.ItemDataRole.UserRole, measurement)

            # Column 0: Empty (no checkbox for children)
            child_item.setText(0, "")

            # Column 1: Cycle number or sequence
            cycle_num = measurement.get("cycle_number")
            if cycle_num is not None:
                child_item.setText(1, f"Cycle {cycle_num}")
            else:
                child_item.setText(1, f"#{idx + 1}")

            # Column 2: Temperature
            temperature = measurement.get("temperature")
            if temperature is not None:
                child_item.setText(2, f"{temperature:.1f}°C")
            else:
                child_item.setText(2, "N/A")

            # Column 3: Position
            position = measurement.get("position")
            if position is not None:
                child_item.setText(3, f"{position:.0f} μm")
            else:
                child_item.setText(3, "N/A")

            # Column 4: Force
            force = measurement.get("force")
            if force is not None:
                child_item.setText(4, f"{force:.2f} N")
            else:
                child_item.setText(4, "N/A")

            # Column 5: Timestamp
            timestamp = measurement.get("timestamp")
            if timestamp:
                timestamp_str = self._format_datetime(timestamp)
                child_item.setText(5, timestamp_str)
            else:
                child_item.setText(5, "N/A")

            # Style child item differently
            for col in range(6):
                child_item.setForeground(col, Qt.GlobalColor.lightGray)

        logger.info(f"Loaded {len(sorted_measurements)} measurements for test_id: {test_id}")

    def _find_parent_item_by_test_id(self, test_id: str) -> Optional[QTreeWidgetItem]:
        """Find parent item by test_id"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                item_test_id = item.text(1)  # Test ID is in column 1
                if item_test_id == test_id:
                    return item
        return None

    def _on_selection_changed(self) -> None:
        """Handle row selection change"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            # Get test_id from selected item
            item = selected_items[0]

            # If child item selected, get parent's test_id
            if item.parent():
                item = item.parent()

            test_id = item.text(1)  # Column 1 is Test ID
            if test_id and test_id != "Loading...":
                self.row_selected.emit(test_id)

    def _on_checkbox_changed(self) -> None:
        """Handle checkbox state change"""
        selected_count = self.get_selected_count()
        self.selection_changed.emit(selected_count)

    def get_selected_test_ids(self) -> List[str]:
        """Get list of test IDs for checked parent items"""
        selected_ids = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                # Get checkbox widget
                checkbox_widget = self.tree.itemWidget(item, 0)
                if checkbox_widget:
                    # Find QCheckBox in the widget
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        test_id = item.text(1)  # Column 1 is Test ID
                        if test_id:
                            selected_ids.append(test_id)
        return selected_ids

    def get_selected_count(self) -> int:
        """Get count of checked parent items"""
        return len(self.get_selected_test_ids())

    def select_all(self) -> None:
        """Check all parent checkboxes"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                checkbox_widget = self.tree.itemWidget(item, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(True)

    def deselect_all(self) -> None:
        """Uncheck all parent checkboxes"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item:
                checkbox_widget = self.tree.itemWidget(item, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(False)

    def _format_status(self, status: str) -> str:
        """Format status with emoji"""
        status_map = {
            "completed": "✅ Pass",
            "failed": "❌ Fail",
            "running": "🔄 Running",
            "pending": "⏳ Pending",
        }
        return status_map.get(status.lower(), f"❓ {status}")

    def _format_datetime(self, dt) -> str:
        """Format datetime for display"""
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                return dt

        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        return str(dt)

    def _get_tree_style(self) -> str:
        """Get tree widget stylesheet"""
        return f"""
        QTreeWidget {{
            background-color: {BACKGROUND_DARK};
            color: {TEXT_SECONDARY};
            gridline-color: {BORDER_DEFAULT};
            border: 1px solid {BORDER_DEFAULT};
            border-radius: 4px;
            selection-background-color: transparent;
            selection-color: {TEXT_SECONDARY};
            outline: none;
        }}
        QTreeWidget::item {{
            padding: 8px;
            border: none;
            outline: none;
        }}
        QTreeWidget::item:selected {{
            background-color: transparent;
            color: {TEXT_SECONDARY};
        }}
        QTreeWidget::item:focus {{
            background-color: transparent;
            outline: none;
            border: none;
        }}
        QTreeWidget::item:hover {{
            background-color: rgba(0, 120, 212, 0.3);
        }}
        QTreeWidget::branch {{
            background-color: {BACKGROUND_DARK};
        }}
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: none;
        }}
        QHeaderView::section {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_PRIMARY};
            font-weight: bold;
            border: 1px solid {BORDER_DEFAULT};
            padding: 8px;
            text-align: left;
        }}
        QHeaderView::section:hover {{
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar:vertical {{
            background-color: {BACKGROUND_DARK};
            width: 14px;
            border: 1px solid {BORDER_DEFAULT};
        }}
        QScrollBar::handle:vertical {{
            background-color: {BACKGROUND_MEDIUM};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
