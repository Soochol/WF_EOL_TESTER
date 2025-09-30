"""
Dashboard Widget

Main dashboard page showing system overview and key information.
Refactored with separated styling and layout configuration.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.hardware_status_widget import HardwareStatusWidget
from ui.gui.widgets.results_table_widget import ResultsTableWidget
from ui.gui.widgets.test_progress_widget import TestProgressWidget

# Local folder imports
# Dashboard configuration imports
from .dashboard import DashboardLayoutConfig
from .shared.styles.dashboard_styles import DashboardStyles


class DashboardWidget(QWidget):
    """
    Enhanced dashboard widget with separated styling and layout configuration.

    Features:
    - Responsive layout with configurable spacing and margins
    - Centralized styling with theme support
    - Flexible section configuration
    - Accessibility and performance optimizations
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
        layout_mode: str = "default",
        theme: str = "dark",
    ):
        """Initialize dashboard widget with configuration options.

        Args:
            container: Application dependency injection container
            state_manager: GUI state management service
            parent: Parent widget (optional)
            layout_mode: Layout configuration mode (default, compact, expanded)
            theme: UI theme (dark, light, high_contrast)
        """
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.layout_mode = layout_mode
        self.theme = theme

        # Initialize configuration
        self.layout_config = DashboardLayoutConfig(layout_mode)
        self.styles = DashboardStyles()

        # Widget references
        self.hardware_status: Optional[HardwareStatusWidget] = None
        self.test_progress: Optional[TestProgressWidget] = None
        self.results_table: Optional[ResultsTableWidget] = None

        # Setup UI and responsive handling
        self.setup_ui()
        self.setup_responsive_updates()

    def setup_ui(self) -> None:
        """Setup the dashboard UI with configured layout and styling."""
        # Create main layout with configuration
        main_layout = QVBoxLayout(self)
        self.layout_config.apply_to_layout(main_layout, "main")

        # Create dashboard sections
        self._create_hardware_section(main_layout)
        self._create_progress_section(main_layout)
        self._create_results_section(main_layout)

        # Apply styling
        self._apply_styling()

        # Set widget properties
        self._configure_widget_properties()

    def _create_hardware_section(self, main_layout: QVBoxLayout) -> None:
        """Create hardware status section.

        Args:
            main_layout: Main dashboard layout
        """
        section_config = self.layout_config.get_section_config("hardware_status")
        if not section_config or not section_config.visible:
            return

        self.hardware_status = HardwareStatusWidget(
            container=self.container,
            state_manager=self.state_manager,
        )

        # Apply section-specific styling
        section_style = self.styles.get_section_style("hardware")
        self.hardware_status.setStyleSheet(self.hardware_status.styleSheet() + section_style)

        # Set minimum height if configured
        if section_config.min_height:
            self.hardware_status.setMinimumHeight(section_config.min_height)
        if section_config.max_height:
            self.hardware_status.setMaximumHeight(section_config.max_height)

        main_layout.addWidget(self.hardware_status, stretch=section_config.stretch_factor)

    def _create_progress_section(self, main_layout: QVBoxLayout) -> None:
        """Create test progress section.

        Args:
            main_layout: Main dashboard layout
        """
        section_config = self.layout_config.get_section_config("test_progress")
        if not section_config or not section_config.visible:
            return

        self.test_progress = TestProgressWidget(
            container=self.container,
            state_manager=self.state_manager,
        )

        # Apply section-specific styling
        section_style = self.styles.get_section_style("progress")
        self.test_progress.setStyleSheet(self.test_progress.styleSheet() + section_style)

        # Set minimum height if configured
        if section_config.min_height:
            self.test_progress.setMinimumHeight(section_config.min_height)
        if section_config.max_height:
            self.test_progress.setMaximumHeight(section_config.max_height)

        main_layout.addWidget(self.test_progress, stretch=section_config.stretch_factor)

    def _create_results_section(self, main_layout: QVBoxLayout) -> None:
        """Create results table section.

        Args:
            main_layout: Main dashboard layout
        """
        section_config = self.layout_config.get_section_config("results_table")
        if not section_config or not section_config.visible:
            return

        self.results_table = ResultsTableWidget(
            container=self.container,
            state_manager=self.state_manager,
        )

        # Apply section-specific styling
        section_style = self.styles.get_section_style("results")
        self.results_table.setStyleSheet(self.results_table.styleSheet() + section_style)

        # Set minimum height if configured
        if section_config.min_height:
            self.results_table.setMinimumHeight(section_config.min_height)
        if section_config.max_height:
            self.results_table.setMaximumHeight(section_config.max_height)

        main_layout.addWidget(self.results_table, stretch=section_config.stretch_factor)

    def _apply_styling(self) -> None:
        """Apply centralized styling to the dashboard widget."""
        # Get base dashboard styling
        base_style = self.styles.get_dashboard_widget_style()

        # Get responsive styling based on current size
        responsive_style = self.styles.get_responsive_style(self.width())

        # Combine and apply styles
        combined_style = base_style + responsive_style
        self.setStyleSheet(combined_style)

    def _configure_widget_properties(self) -> None:
        """Configure widget properties for accessibility and performance."""
        # Set object name for CSS targeting
        self.setObjectName("DashboardWidget")

        # Set minimum size based on layout configuration
        metrics = self.layout_config.metrics
        self.setMinimumSize(metrics.min_widget_width, metrics.min_widget_height)

        # Set accessibility properties
        self.setAccessibleName("EOL Test Dashboard")
        self.setAccessibleDescription(
            "Main dashboard showing hardware status, test progress, and results"
        )

    def setup_responsive_updates(self) -> None:
        """Setup responsive layout updates."""
        # Create timer for responsive updates
        self.responsive_timer = QTimer()
        self.responsive_timer.timeout.connect(self._update_responsive_layout)
        self.responsive_timer.setSingleShot(True)

        # Track last known size for optimization
        self._last_width = 0
        self._last_height = 0

    def resizeEvent(self, event) -> None:
        """Handle widget resize events for responsive layout.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        # Trigger responsive update with debouncing
        new_width = event.size().width()
        new_height = event.size().height()

        # Only update if size changed significantly
        if abs(new_width - self._last_width) > 50 or abs(new_height - self._last_height) > 50:
            self.responsive_timer.start(100)  # 100ms debounce
            self._last_width = new_width
            self._last_height = new_height

    def _update_responsive_layout(self) -> None:
        """Update layout configuration based on current widget size."""
        current_width = self.width()

        # Get responsive configuration
        new_config = self.layout_config.get_responsive_config(current_width)

        # Only update if configuration changed
        if new_config.layout_mode != self.layout_config.layout_mode:
            self.layout_config = new_config
            self._apply_styling()  # Reapply responsive styles

    def set_layout_mode(self, layout_mode: str) -> None:
        """Change layout mode dynamically.

        Args:
            layout_mode: New layout mode (default, compact, expanded)
        """
        if layout_mode != self.layout_mode:
            self.layout_mode = layout_mode
            self.layout_config = DashboardLayoutConfig(layout_mode)

            # Reapply layout configuration
            if self.layout():
                self.layout_config.apply_to_layout(self.layout(), "main")

            self._apply_styling()

    def set_theme(self, theme: str) -> None:
        """Change theme dynamically.

        Args:
            theme: New theme (dark, light, high_contrast)
        """
        if theme != self.theme:
            self.theme = theme
            # Update styles class with new theme
            self.styles.COLORS = self.styles.get_theme_style(theme)
            self._apply_styling()

    def get_layout_info(self) -> dict:
        """Get current layout information for debugging.

        Returns:
            dict: Layout configuration information
        """
        return {
            "layout_mode": self.layout_mode,
            "theme": self.theme,
            "widget_size": (self.width(), self.height()),
            "metrics": {
                "spacing": self.layout_config.metrics.spacing_md,
                "margins": (
                    self.layout_config.metrics.margin_md,
                    self.layout_config.metrics.margin_md,
                    self.layout_config.metrics.margin_md,
                    self.layout_config.metrics.margin_md,
                ),
            },
            "sections": {
                name: {
                    "visible": config.visible,
                    "stretch": config.stretch_factor,
                    "spacing": config.spacing,
                }
                for name, config in self.layout_config.sections.items()
            },
        }
