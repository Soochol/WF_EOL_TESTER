"""
Search Widget

Main database search and visualization widget.
"""

# Standard library imports
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from loguru import logger

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.styles.common_styles import BACKGROUND_DARK, get_button_style
from ui.gui.widgets.content.search import GraphPanel, ResultsTable, SearchFiltersPanel


class SearchWidget(QWidget):
    """
    Database search and visualization widget.

    Features:
    - Search filters (serial number, date range, status)
    - Results table view
    - Force vs Temperature graphs grouped by serial number
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

        # Get DB repository
        self.db_repo = container.sqlite_log_repository()

        # Initialize components
        self.filters_panel: Optional[SearchFiltersPanel] = None
        self.results_table: Optional[ResultsTable] = None
        self.graph_panel: Optional[GraphPanel] = None
        self.splitter: Optional[QSplitter] = None
        self.show_graph_btn: Optional[QPushButton] = None
        self.select_all_btn: Optional[QPushButton] = None
        self.deselect_all_btn: Optional[QPushButton] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the search UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark background
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {BACKGROUND_DARK};
            }}
        """
        )

        # Search filters panel
        self.filters_panel = SearchFiltersPanel()
        self.filters_panel.search_requested.connect(self._on_search_requested)
        self.filters_panel.filters_cleared.connect(self._on_filters_cleared)
        main_layout.addWidget(self.filters_panel)

        # Results table
        self.results_table = ResultsTable()
        self.results_table.row_selected.connect(self._on_row_selected)
        self.results_table.selection_changed.connect(self._on_selection_changed)
        main_layout.addWidget(self.results_table)

        # Button toolbar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Select All button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setStyleSheet(get_button_style())
        self.select_all_btn.clicked.connect(self._on_select_all)
        button_layout.addWidget(self.select_all_btn)

        # Deselect All button
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.setStyleSheet(get_button_style())
        self.deselect_all_btn.clicked.connect(self._on_deselect_all)
        button_layout.addWidget(self.deselect_all_btn)

        button_layout.addStretch()

        # Show Graph button
        self.show_graph_btn = QPushButton("📊 Show Graph (0 selected)")
        self.show_graph_btn.setStyleSheet(get_button_style())
        self.show_graph_btn.setEnabled(False)
        self.show_graph_btn.clicked.connect(self._on_show_graph)
        button_layout.addWidget(self.show_graph_btn)

        main_layout.addLayout(button_layout)

        # Splitter for graphs
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(8)
        self.splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                margin: 4px 0;
            }
            QSplitter::handle:hover {
                background-color: rgba(33, 150, 243, 0.3);
            }
        """
        )

        # Graph panel
        self.graph_panel = GraphPanel()
        self.splitter.addWidget(self.graph_panel)

        main_layout.addWidget(self.splitter)

        logger.info("SearchWidget initialized")

    def _on_search_requested(self, filters: Dict) -> None:
        """Handle search request"""
        logger.info(f"Search requested with filters: {filters}")

        # Run async search using QTimer for proper Qt-asyncio integration
        # Third-party imports
        from PySide6.QtCore import QTimer

        # Use QTimer.singleShot to avoid event loop issues
        QTimer.singleShot(0, lambda: self._run_search_async(filters))

    def _on_filters_cleared(self) -> None:
        """Handle filters clear"""
        logger.info("Filters cleared")
        if self.results_table:
            self.results_table.update_results([])
        if self.graph_panel:
            self.graph_panel.clear_graphs()

    def _on_row_selected(self, test_id: str) -> None:
        """Handle row selection"""
        logger.info(f"Row selected: {test_id}")
        # Future: Highlight corresponding graph

    def _on_selection_changed(self, selected_count: int) -> None:
        """Handle checkbox selection change"""
        logger.debug(f"Selection changed: {selected_count} items selected")

        # Update Show Graph button
        if self.show_graph_btn:
            if selected_count == 0:
                self.show_graph_btn.setText("📊 Show Graph (0 selected)")
                self.show_graph_btn.setEnabled(False)
            else:
                self.show_graph_btn.setText(f"📊 Show Graph ({selected_count} selected)")
                self.show_graph_btn.setEnabled(True)

    def _on_select_all(self) -> None:
        """Handle Select All button click"""
        logger.info("Select All clicked")
        if self.results_table:
            self.results_table.select_all()

    def _on_deselect_all(self) -> None:
        """Handle Deselect All button click"""
        logger.info("Deselect All clicked")
        if self.results_table:
            self.results_table.deselect_all()

    def _on_show_graph(self) -> None:
        """Handle Show Graph button click"""
        if not self.results_table:
            return

        selected_ids = self.results_table.get_selected_test_ids()
        logger.info(f"Show Graph clicked: {len(selected_ids)} test IDs selected")

        if not selected_ids:
            logger.warning("No tests selected for graphing")
            return

        # Run async graph update using QTimer for proper Qt-asyncio integration
        # Third-party imports
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, lambda: self._run_graph_update_async(selected_ids))

    def _run_graph_update_async(self, selected_test_ids: List[str]) -> None:
        """Run async graph update using new event loop"""
        # Third-party imports
        import asyncio

        try:
            # Create new event loop for this operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._update_graphs_for_selected(selected_test_ids))
            loop.close()
        except Exception as e:
            logger.error(f"Graph update execution failed: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()

    async def _update_graphs_for_selected(self, selected_test_ids: List[str]) -> None:
        """Update graphs for selected test IDs only"""
        try:
            logger.info(f"Updating graphs for {len(selected_test_ids)} selected tests")

            # Collect all test data in a single group (no serial number grouping)
            all_tests_data: Dict[str, List[Dict]] = {}

            # Get test results from table to extract serial numbers for display
            if not self.results_table:
                return

            for test_id in selected_test_ids:
                # Find the test result in the table
                test_result = None
                for result in self.results_table.test_results:
                    if result.get("test_id") == test_id:
                        test_result = result
                        break

                if not test_result:
                    logger.warning(f"Test result not found for test_id: {test_id}")
                    continue

                serial_number = test_result.get("serial_number", "Unknown")

                # Query raw measurements for this test
                logger.debug(f"Querying measurements for test_id: {test_id}")
                measurements = await self.db_repo.query_raw_measurements(
                    test_id=test_id,
                    limit=1000,
                )

                logger.debug(
                    f"Found {len(measurements)} measurements for test_id: {test_id}, "
                    f"serial: {serial_number}"
                )

                if measurements:
                    # Add serial number to each measurement for legend display
                    for m in measurements:
                        m["serial_number"] = serial_number
                    all_tests_data[test_id] = measurements
                else:
                    logger.warning(f"No measurements found for test_id: {test_id}")

            logger.info(f"Collected data: {len(all_tests_data)} tests total")

            # Create single-group structure for graph panel
            # Key: "All Selected Tests", Value: {test_id: measurements}
            grouped_data = {"All Selected Tests": all_tests_data}

            # Update graph panel
            if self.graph_panel:
                self.graph_panel.update_graphs(grouped_data)
                logger.info("Graph panel updated successfully")

        except Exception as e:
            logger.error(f"Failed to update graphs for selected items: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()

    def _run_search_async(self, filters: Dict) -> None:
        """Run async search using new event loop"""
        # Third-party imports
        import asyncio

        try:
            # Create new event loop for this operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._perform_search(filters))
            loop.close()
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()

    async def _perform_search(self, filters: Dict) -> None:
        """Perform database search using raw_measurements directly"""
        try:
            logger.info("Performing database search from raw_measurements...")

            # Query test IDs directly from raw_measurements table
            # This bypasses test_results table which may not have matching test_ids
            results = await self.db_repo.query_test_ids_from_measurements(
                serial_number=filters.get("serial_number"),
                start_date=filters.get("start_date"),
                end_date=filters.get("end_date"),
                limit=500,  # Increased from 100 to support more test data
            )

            logger.info(f"Found {len(results)} unique test IDs from raw_measurements")

            # Update table
            if self.results_table:
                self.results_table.update_results(results)

            # Clear graphs - user needs to select items and click "Show Graph"
            if self.graph_panel:
                self.graph_panel.clear_graphs()

            logger.info("Search completed. Select items and click 'Show Graph' to visualize.")

        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Standard library imports
            import traceback

            traceback.print_exc()
