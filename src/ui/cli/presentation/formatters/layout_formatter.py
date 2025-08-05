"""Layout and Grid Management for CLI Rich UI Components

Specialized formatter class focused on layout creation and grid management
including statistics displays, multi-component layouts, and flexible
arrangement strategies. This module provides methods for organizing multiple
Rich components into cohesive displays with intelligent space management.

This formatter handles vertical, horizontal, and grid layouts with automatic
fallback strategies for optimal component organization.
"""

from typing import Any, Dict, List, Tuple

from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from .base_formatter import BaseFormatter


class LayoutFormatter(BaseFormatter):
    """Specialized formatter for layout creation and component organization.

    This class extends BaseFormatter to provide specialized methods for creating
    layouts, organizing multiple components, and managing grid arrangements.
    It uses the strategy pattern to support different layout types with
    intelligent fallback mechanisms for optimal display.

    Key Features:
    - Multiple layout strategies (vertical, horizontal, grid)
    - Intelligent component arrangement with automatic fallbacks
    - Statistics displays with organized sections
    - Grid layouts with optimal space utilization
    - Flexible component grouping and organization
    """

    def create_layout(
        self,
        components: Dict[str, Any],
        layout_type: str = "vertical",
    ) -> Layout:
        """Create a rich layout with multiple components using strategy pattern.

        Provides a flexible layout system that can arrange multiple Rich components
        in different patterns. Uses the strategy pattern to delegate layout creation
        to specialized methods based on the requested layout type.

        Args:
            components: Dictionary mapping component names to Rich objects for display
            layout_type: Layout arrangement type ("vertical", "horizontal", "grid")

        Returns:
            Rich Layout with components organized according to the specified type

        Raises:
            ValueError: If layout_type is not supported by the available strategies
        """
        if not components:
            return Layout()

        layout_strategies = {
            "vertical": self._create_vertical_layout,
            "horizontal": self._create_horizontal_layout,
            "grid": self._create_grid_layout,
        }

        strategy = layout_strategies.get(layout_type)
        if not strategy:
            raise ValueError(f"Unsupported layout type: {layout_type}")

        return strategy(components)

    def create_statistics_display(
        self,
        statistics: Dict[str, Any],
        title: str = "Test Statistics",
    ) -> Panel:
        """Create a comprehensive statistics display panel.

        Generates a formatted statistics panel that can display overall statistics,
        recent performance data, and model-specific breakdowns. Automatically
        formats different types of statistical data with appropriate styling.

        Args:
            statistics: Dictionary containing statistics data with keys like
                       'overall', 'recent', 'by_model' for organized display
            title: Display title for the statistics panel

        Returns:
            Rich Panel with formatted statistics and organized sections
        """
        content = []

        # Overall statistics
        if "overall" in statistics:
            overall = statistics["overall"]
            content.append(self._create_stats_section("Overall Statistics", overall))

        # Recent statistics
        if "recent" in statistics:
            recent = statistics["recent"]
            content.append(self._create_stats_section("Recent (7 days)", recent))

        # By model statistics (handled by TableFormatter if available)
        if "by_model" in statistics:
            by_model = statistics["by_model"]
            # Create a simple text display for model stats
            # (In a full implementation, this could delegate to TableFormatter)
            model_section = self._create_model_stats_section(by_model)
            content.append(model_section)

        return Panel(
            Group(*content),
            title=f"{self.icons.get_icon('report')} {title}",
            title_align="left",
            border_style=self.colors.get_color("accent"),
            padding=self.layout.DEFAULT_PANEL_PADDING,
        )

    def create_grid_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a 2x2 grid layout for up to 4 components with automatic fallback.

        Public interface for grid layout creation with intelligent component
        arrangement and automatic fallback to vertical layout for excessive components.

        Args:
            components: Dictionary of components to arrange in grid formation

        Returns:
            Layout with components arranged in a 2x2 grid, or vertical layout
            if more than 4 components are provided
        """
        return self._create_grid_layout(components)

    def _create_vertical_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a vertical layout with components stacked top to bottom.

        Args:
            components: Dictionary of components to arrange vertically

        Returns:
            Layout with components arranged in a vertical stack
        """
        layout = Layout()
        component_layouts = [Layout(comp, name=name) for name, comp in components.items()]
        layout.split_column(*component_layouts)
        return layout

    def _create_horizontal_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a horizontal layout with components arranged left to right.

        Args:
            components: Dictionary of components to arrange horizontally

        Returns:
            Layout with components arranged in a horizontal row
        """
        layout = Layout()
        component_layouts = [Layout(comp, name=name) for name, comp in components.items()]
        layout.split_row(*component_layouts)
        return layout

    def _create_grid_layout(self, components: Dict[str, Any]) -> Layout:
        """Create a 2x2 grid layout for up to 4 components with automatic fallback.

        Args:
            components: Dictionary of components to arrange in grid formation

        Returns:
            Layout with components arranged in a 2x2 grid, or vertical layout
            if more than 4 components are provided
        """
        if len(components) > self.layout.MAX_GRID_COMPONENTS:
            # Graceful fallback to vertical layout for excessive components
            return self._create_vertical_layout(components)

        layout = Layout()
        components_list = list(components.items())

        # Create main grid structure with top and bottom sections
        layout.split_column(
            Layout(name="top"),
            Layout(name="bottom"),
        )

        # Populate top row with first set of components
        self._populate_grid_row(layout["top"], components_list[: self.layout.GRID_TOP_COMPONENTS])

        # Populate bottom row with remaining components if available
        bottom_components = components_list[self.layout.GRID_TOP_COMPONENTS :]
        if bottom_components:
            self._populate_grid_row(layout["bottom"], bottom_components)

        return layout

    def _populate_grid_row(self, row_layout: Layout, components: List[Tuple[str, Any]]) -> None:
        """Populate a grid row with the provided components using optimal arrangement.

        Args:
            row_layout: Layout object representing the row to populate
            components: List of (name, component) tuples to place in the row
        """
        if len(components) == 1:
            # Single component takes full row width
            name, comp = components[0]
            row_layout.update(Layout(comp, name=name))
        elif len(components) == 2:
            # Two components split row equally
            row_layout.split_row(
                Layout(components[0][1], name=components[0][0]),
                Layout(components[1][1], name=components[1][0]),
            )

    def _create_stats_section(self, title: str, stats: Dict[str, Any]) -> Group:
        """Create a formatted statistics section with consistent styling.

        Args:
            title: Section title to display prominently
            stats: Dictionary of statistic names and values

        Returns:
            Rich Group containing the formatted statistics section
        """
        content = []

        # Create formatted section title
        title_text = Text(f"\n{title}", style=f"bold {self.colors.get_color('secondary')}")
        content.append(title_text)

        # Format each statistic with appropriate styling
        for key, value in stats.items():
            stat_text = Text()
            stat_text.append(f"  {self.icons.get_icon('bullet')} ", style=self.colors.get_color("muted"))
            stat_text.append(f"{key.replace('_', ' ').title()}: ", style="bold")

            # Apply special formatting for percentage rates
            if isinstance(value, float) and "rate" in key.lower():
                stat_text.append(f"{value:.1f}%", style=self.colors.get_color("accent"))
            else:
                stat_text.append(str(value), style=self.colors.get_color("text"))

            content.append(stat_text)

        return Group(*content)

    def _create_model_stats_section(self, model_stats: Dict[str, Dict[str, Any]]) -> Group:
        """Create a model statistics section with simplified display.

        Args:
            model_stats: Dictionary mapping model names to their statistics

        Returns:
            Rich Group with formatted model statistics
        """
        content = []

        # Section title
        title_text = Text(f"\n{self.icons.get_icon('report')} Statistics by Model",
                         style=f"bold {self.colors.get_color('secondary')}")
        content.append(title_text)

        # Format each model's statistics
        for model, stats in model_stats.items():
            model_text = Text()
            model_text.append(f"  {self.icons.get_icon('bullet')} ", style=self.colors.get_color("muted"))
            model_text.append(f"{model}: ", style="bold")

            # Format key statistics
            total = stats.get("total", 0)
            passed = stats.get("passed", 0)
            pass_rate = stats.get("pass_rate", 0)

            model_text.append(f"{passed}/{total} ", style=self.colors.get_color("text"))

            # Color-code pass rate
            if pass_rate >= 90:
                rate_color = self.colors.get_color("success")
            elif pass_rate >= 70:
                rate_color = self.colors.get_color("warning")
            else:
                rate_color = self.colors.get_color("error")

            model_text.append(f"({pass_rate:.1f}%)", style=f"bold {rate_color}")
            content.append(model_text)

        return Group(*content)

    # Utility methods for layout management
    def get_optimal_layout_type(self, component_count: int) -> str:
        """Determine optimal layout type based on component count.

        Args:
            component_count: Number of components to arrange

        Returns:
            Recommended layout type string
        """
        if component_count <= 2:
            return "horizontal"
        elif component_count <= 4:
            return "grid"
        else:
            return "vertical"

    def can_use_grid_layout(self, component_count: int) -> bool:
        """Check if grid layout is appropriate for the given component count.

        Args:
            component_count: Number of components to arrange

        Returns:
            True if grid layout is recommended, False otherwise
        """
        return 2 < component_count <= self.layout.MAX_GRID_COMPONENTS
