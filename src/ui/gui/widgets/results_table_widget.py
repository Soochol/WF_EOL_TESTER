"""
Results Tree Widget

Widget for displaying test results in an expandable tree format.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager, TestResult


class ResultsTableWidget(QWidget):
    """
    Results tree widget for displaying test results in expandable format.

    Shows test results with parent rows for each test and child rows for individual cycles.
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self) -> None:
        """Setup the results tree UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tree widget
        self.results_tree = QTreeWidget()
        self.setup_tree()
        main_layout.addWidget(self.results_tree)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def setup_tree(self) -> None:
        """Setup the tree widget"""
        # Set up columns
        headers = [
            "Serial / Cycle",
            "Temp(°C)",
            "Stroke(mm)",
            "Force(kgf)",
            "Heat(s)",
            "Cool(s)",
            "Status",
            "Error",  # NEW: Error column
            "Time",
        ]

        self.results_tree.setColumnCount(len(headers))
        self.results_tree.setHeaderLabels(headers)

        # Tree properties
        self.results_tree.setAlternatingRowColors(True)
        self.results_tree.setRootIsDecorated(True)  # Show expand/collapse arrows
        self.results_tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Disable keyboard focus indicator
        self.results_tree.setIndentation(20)  # Indent for child items

        # Enable single-click to expand/collapse
        self.results_tree.itemClicked.connect(self._on_item_clicked)

        # Header configuration
        header = self.results_tree.header()
        header.setStretchLastSection(True)

        # Optimize column widths
        self.results_tree.setColumnWidth(0, 140)  # Serial / Cycle
        self.results_tree.setColumnWidth(1, 100)  # Temp
        self.results_tree.setColumnWidth(2, 100)  # Stroke
        self.results_tree.setColumnWidth(3, 110)  # Force
        self.results_tree.setColumnWidth(4, 90)   # Heat
        self.results_tree.setColumnWidth(5, 90)   # Cool
        self.results_tree.setColumnWidth(6, 70)   # Status
        self.results_tree.setColumnWidth(7, 100)  # Error
        # Time column will stretch

        # Set minimum height
        self.results_tree.setMinimumHeight(200)

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        self.state_manager.test_result_added.connect(self._on_test_result_added)
        # Note: cycle_result_added signal still exists for live test updates (different from loaded results)

    def _on_test_result_added(self, result: TestResult) -> None:
        """Handle new test result"""
        self.add_test_result(result)

    def add_test_result(self, result: TestResult) -> None:
        """Add a test result with expandable cycle data to the tree"""
        # Create parent item for test
        parent_item = QTreeWidgetItem(self.results_tree)

        # Set parent item data (test-level summary)
        parent_item.setText(0, f"▶  {result.serial_number}")  # Add arrow icon with serial number
        parent_item.setText(1, "")  # Temp - show in cycles
        parent_item.setText(2, "")  # Stroke - show in cycles
        parent_item.setText(3, "")  # Force - show in cycles
        parent_item.setText(4, "")  # Heat - show in cycles
        parent_item.setText(5, "")  # Cool - show in cycles
        parent_item.setText(6, result.status)

        # Error column (index 7)
        if result.error_message:
            parent_item.setText(7, "⚠️")
            parent_item.setToolTip(7, result.error_message)
            parent_item.setForeground(7, QColor("#F44336"))  # Red color
        else:
            parent_item.setText(7, "")

        parent_item.setText(8, result.timestamp.strftime("%Y-%m-%d %H:%M"))

        # Color coding for status
        status_color = self._get_status_color(result.status)
        parent_item.setForeground(6, status_color)

        # Make parent item bold
        font = parent_item.font(0)
        font.setBold(True)
        for col in range(9):
            parent_item.setFont(col, font)

        # Store serial number for toggle
        parent_item.setData(0, Qt.ItemDataRole.UserRole, result.serial_number)

        # Add child items for each cycle
        for cycle in result.cycles:
            child_item = QTreeWidgetItem(parent_item)

            child_item.setText(0, f"Cycle {cycle.cycle}")
            child_item.setText(1, f"{cycle.temperature:.1f}°C")
            child_item.setText(2, f"{cycle.stroke / 1000.0:.1f}")  # Convert μm to mm
            child_item.setText(3, f"{cycle.force:.2f}")
            child_item.setText(4, f"{cycle.heating_time:.2f}")
            child_item.setText(5, f"{cycle.cooling_time:.2f}")
            child_item.setText(6, cycle.status)
            child_item.setText(7, "")  # No timestamp for cycles

            # Color coding for cycle status
            cycle_color = self._get_status_color(cycle.status)
            child_item.setForeground(6, cycle_color)

        # Start with parent collapsed
        parent_item.setExpanded(False)

        # Scroll to show the new item
        self.results_tree.scrollToItem(parent_item)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item click to toggle expand/collapse"""
        if item.childCount() > 0:  # Only toggle if item has children
            is_expanded = item.isExpanded()
            item.setExpanded(not is_expanded)

            # Update arrow icon
            serial_number = item.data(0, Qt.ItemDataRole.UserRole)
            if serial_number:  # Only parent items have this data
                arrow = "▼" if not is_expanded else "▶"
                item.setText(0, f"{arrow}  {serial_number}")

    def _get_status_color(self, status: str) -> QColor:
        """Get color for status text"""
        if status == "PASS":
            return QColor("#00D9A5")
        elif status in ["FAIL", "ERROR"]:
            return QColor("#F44336")
        elif status == "PENDING":
            return QColor("#FF9800")
        return QColor("#FFFFFF")

    def clear_results(self) -> None:
        """Clear all results from the tree"""
        self.results_tree.clear()


    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        ResultsTableWidget {
            background-color: transparent;
            color: #cccccc;
        }
        QTreeWidget {
            background-color: transparent;
            alternate-background-color: rgba(255, 255, 255, 0.02);
            color: #ffffff;
            border: none;
            selection-background-color: rgba(33, 150, 243, 0.3);
            selection-color: #ffffff;
        }
        QTreeWidget::item {
            padding: 8px 4px;
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        QTreeWidget::item:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }
        QTreeWidget::branch {
            background: transparent;
        }
        QTreeWidget::branch:has-children:closed {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNEwxMCA4TDYgMTJWNFoiIGZpbGw9IiNjY2NjY2MiLz4KPC9zdmc+Cg==);
        }
        QTreeWidget::branch:has-children:open {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDZINFoiIGZpbGw9IiNjY2NjY2MiLz4KPC9zdmc+Cg==);
        }
        QHeaderView::section {
            background-color: rgba(255, 255, 255, 0.05);
            color: #cccccc;
            padding: 14px 8px;
            border: none;
            border-bottom: 2px solid #2196F3;
            font-weight: 600;
            font-size: 13px;
        }
        QHeaderView::section:hover {
            background-color: rgba(255, 255, 255, 0.08);
        }
        QScrollBar:vertical {
            background-color: transparent;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """
