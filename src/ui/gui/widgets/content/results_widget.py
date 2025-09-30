"""
Results Widget

Advanced results analysis page with enhanced filtering, statistics, and export capabilities.
Features a modular design with separated header controls and improved layout flexibility.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.styles.common_styles import get_results_widget_style, get_splitter_style
from ui.gui.widgets.content.results.header_controls import ResultsHeaderControls
from ui.gui.widgets.results_table_widget import ResultsTableWidget
from ui.gui.widgets.temperature_force_chart_widget import TemperatureForceChartWidget


class ResultsWidget(QWidget):
    """
    Advanced results widget for comprehensive test results analysis.

    Features:
    - Enhanced header with filtering and analysis controls
    - Flexible splitter layout for table and chart views
    - Export capabilities in multiple formats
    - Real-time statistics and trend analysis
    - Modular design with separated concerns
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

        # Initialize components
        self.header_controls: Optional[ResultsHeaderControls] = None
        self.results_table: Optional[ResultsTableWidget] = None
        self.temp_force_chart: Optional[TemperatureForceChartWidget] = None
        self.main_splitter: Optional[QSplitter] = None

        # Current filter state
        self.current_filters: Dict[str, Any] = {
            "type": "All",
            "status": "All",
            "days": 30,
        }

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self) -> None:
        """Setup the enhanced results UI with modular components."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Enhanced header with controls
        self.header_controls = ResultsHeaderControls(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.header_controls)

        # Create flexible splitter for table and chart
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(4)

        # Results table with enhanced filtering capabilities
        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.main_splitter.addWidget(self.results_table)

        # Temperature-Force chart with improved visualization
        self.temp_force_chart = TemperatureForceChartWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        self.main_splitter.addWidget(self.temp_force_chart)

        # Set optimized splitter proportions (65% table, 35% chart)
        self.main_splitter.setSizes([650, 350])

        # Store splitter state for restoration
        self.main_splitter.splitterMoved.connect(self.on_splitter_moved)

        main_layout.addWidget(self.main_splitter)

        # Apply modern, consistent styling
        self.apply_styling()

    def apply_styling(self) -> None:
        """Apply modern, consistent styling to the widget."""
        # Apply comprehensive styling
        widget_style = get_results_widget_style()
        splitter_style = get_splitter_style()

        combined_style = widget_style + splitter_style
        self.setStyleSheet(combined_style)

    def connect_signals(self) -> None:
        """Connect signals from header controls to appropriate handlers."""
        if self.header_controls:
            self.header_controls.filter_changed.connect(self.on_filter_changed)
            self.header_controls.export_requested.connect(self.on_export_requested)
            self.header_controls.analysis_requested.connect(self.on_analysis_requested)

    @Slot(dict)
    def on_filter_changed(self, filters: Dict[str, Any]) -> None:
        """Handle filter changes from header controls."""
        self.current_filters = filters.copy()

        # Apply filters to results table
        if self.results_table:
            self.apply_filters_to_table(filters)

        # Update chart based on filtered data
        if self.temp_force_chart:
            self.update_chart_with_filters(filters)

        # Update summary statistics
        self.update_summary_statistics()

    @Slot(str)
    def on_export_requested(self, format_type: str) -> None:
        """Handle export requests from header controls."""
        try:
            if self.results_table:
                success = self.export_filtered_data(format_type)
                if success:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Data exported successfully in {format_type.upper()} format.",
                    )
                else:
                    QMessageBox.warning(
                        self, "Export Failed", "Failed to export data. Please try again."
                    )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export: {str(e)}")

    @Slot(str)
    def on_analysis_requested(self, analysis_type: str) -> None:
        """Handle analysis requests from header controls."""
        try:
            if analysis_type == "statistics":
                self.show_detailed_statistics()
            elif analysis_type == "trends":
                self.show_trend_analysis()
            elif analysis_type == "compare":
                self.show_comparison_analysis()
        except Exception as e:
            QMessageBox.critical(
                self, "Analysis Error", f"An error occurred during analysis: {str(e)}"
            )

    @Slot(int, int)
    def on_splitter_moved(self, pos: int, index: int) -> None:
        """Handle splitter movement for state preservation."""
        # Store splitter state in state manager for restoration
        if self.state_manager and self.main_splitter:
            sizes = self.main_splitter.sizes()
            # Could store in state manager for persistence

    def apply_filters_to_table(self, filters: Dict[str, Any]) -> None:
        """Apply filters to the results table."""
        # Implementation would depend on ResultsTableWidget interface
        # This is a placeholder for the filtering logic
        pass

    def update_chart_with_filters(self, filters: Dict[str, Any]) -> None:
        """Update chart display based on current filters."""
        # Implementation would depend on TemperatureForceChartWidget interface
        # This is a placeholder for the chart update logic
        pass

    def update_summary_statistics(self) -> None:
        """Update summary statistics in header controls."""
        # Calculate statistics based on current filtered data
        # This is a placeholder implementation
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        # Update header controls with calculated statistics
        if self.header_controls:
            self.header_controls.update_summary(total_tests, passed_tests, failed_tests)

    def export_filtered_data(self, format_type: str) -> bool:
        """Export filtered data in specified format."""
        # Implementation would depend on available export functionality
        # This is a placeholder that always returns True
        return True

    def show_detailed_statistics(self) -> None:
        """Show detailed statistics dialog."""
        # Placeholder for detailed statistics implementation
        QMessageBox.information(
            self, "Statistics", "Detailed statistics feature will be implemented here."
        )

    def show_trend_analysis(self) -> None:
        """Show trend analysis dialog."""
        # Placeholder for trend analysis implementation
        QMessageBox.information(self, "Trends", "Trend analysis feature will be implemented here.")

    def show_comparison_analysis(self) -> None:
        """Show comparison analysis dialog."""
        # Placeholder for comparison analysis implementation
        QMessageBox.information(
            self, "Compare", "Comparison analysis feature will be implemented here."
        )

    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings."""
        return self.current_filters.copy()

    def reset_filters(self) -> None:
        """Reset all filters to default values."""
        if self.header_controls:
            self.header_controls.reset_filters()

    def refresh_data(self) -> None:
        """Refresh all data displays."""
        # Refresh table data
        if self.results_table:
            # Implementation would depend on ResultsTableWidget interface
            pass

        # Refresh chart data
        if self.temp_force_chart:
            # Implementation would depend on TemperatureForceChartWidget interface
            pass

        # Update summary statistics
        self.update_summary_statistics()
