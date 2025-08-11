"""Table Creation and Formatting for CLI Rich UI Components

Specialized formatter class focused on table creation and formatting including
test results tables, statistics tables, and model-specific data displays.
This module provides methods for creating professional tables with consistent
column definitions, styling, and data formatting.

This formatter handles both EOLTestResult objects and dictionary-based results
with flexible formatting options for different display contexts.
"""

from typing import Any, Dict, List, Optional, Union

from rich.table import Table
from rich.text import Text

from src.domain.value_objects.eol_test_result import EOLTestResult

from .base_formatter import BaseFormatter


class TableFormatter(BaseFormatter):
    """Specialized formatter for table creation and data display.

    This class extends BaseFormatter to provide specialized methods for creating
    tables with consistent column definitions, professional styling, and flexible
    data formatting. It handles both EOLTestResult objects and dictionary-based
    results with configurable detail levels.

    Key Features:
    - Professional table styling with consistent column definitions
    - Support for both EOLTestResult objects and dictionary formats
    - Flexible detail levels (summary vs comprehensive views)
    - Statistics tables with model-specific breakdowns
    - Intelligent data formatting and truncation
    """

    def create_test_results_table(
        self,
        test_results: List[Union[EOLTestResult, Dict[str, Any]]],
        title: str = "Test Results",
        show_details: bool = True,
        dut_info: Optional[Dict[str, str]] = None,
    ) -> Table:
        """Create a rich table for displaying test results with flexible formatting.

        Generates a professionally formatted table that can handle both EOLTestResult
        objects and dictionary-based test results. The table automatically adjusts
        its columns based on the show_details parameter for optimal display.

        Args:
            test_results: List of test results to display (mixed types supported)
            title: Table title displayed at the top of the table
            show_details: Whether to include detailed columns (model, duration, measurements)
            dut_info: Optional DUT information dict with 'id' and 'model' keys

        Returns:
            Rich Table with formatted test results and appropriate column styling
        """
        table = self._create_base_table(title, show_details)

        # Add rows
        for result in test_results:
            if isinstance(result, EOLTestResult):
                row_data = self._format_eol_result_row(result, show_details, dut_info)
            else:  # Dict format from repository
                row_data = self._format_dict_result_row(result, show_details)

            table.add_row(*row_data)

        return table

    def create_statistics_table_by_model(self, model_stats: Dict[str, Dict[str, Any]]) -> Table:
        """Create a table for model statistics with pass rate analysis.

        Generates a comprehensive statistics table showing model-specific performance
        data including total tests, passed tests, and pass rates with intelligent
        color coding based on performance thresholds.

        Args:
            model_stats: Dictionary mapping model names to their statistics

        Returns:
            Rich Table with formatted model statistics and color-coded pass rates
        """
        table = Table(
            title="Statistics by Model",
            title_style=f"bold {self.colors.get_color('secondary')}",
            border_style=self.colors.get_color("border"),
            header_style=f"bold {self.colors.get_color('secondary')}",
            show_lines=True,
        )

        table.add_column("Model", style=self.colors.get_color("text"))
        table.add_column("Total Tests", justify="center", style=self.colors.get_color("info"))
        table.add_column("Passed", justify="center", style=self.colors.get_color("success"))
        table.add_column("Pass Rate", justify="center", style=self.colors.get_color("accent"))

        for model, stats in model_stats.items():
            pass_rate = stats.get("pass_rate", 0)
            pass_rate_color = self._get_pass_rate_color(pass_rate)

            table.add_row(
                model,
                str(stats.get("total", 0)),
                str(stats.get("passed", 0)),
                Text(f"{pass_rate:.1f}%", style=f"bold {pass_rate_color}"),
            )

        return table

    def _create_base_table(self, title: str, show_details: bool) -> Table:
        """Create base table structure with consistent column definitions.

        Establishes the foundation table structure with professional styling
        and configurable column sets based on the detail level requested.

        Args:
            title: Table title for display at the top of the table
            show_details: Whether to include detailed columns for comprehensive display

        Returns:
            Configured Rich Table with appropriate columns and professional styling
        """
        table = Table(
            title=title,
            title_style=f"bold {self.colors.get_color('primary')}",
            border_style=self.colors.get_color("border"),
            header_style=f"bold {self.colors.get_color('secondary')}",
            show_lines=True,
        )

        # Always include core columns for essential information
        self._add_core_table_columns(table)

        # Add detailed columns for comprehensive views
        if show_details:
            self._add_detail_table_columns(table)

        # Timestamp column always appears last for chronological context
        table.add_column(
            "Timestamp",
            style=self.colors.get_color("muted"),
            width=self.layout.TIMESTAMP_COLUMN_WIDTH,
        )
        return table

    def _add_core_table_columns(self, table: Table) -> None:
        """Add core table columns that are always present in test result displays.

        Args:
            table: Rich Table object to add columns to
        """
        table.add_column(
            "Status", justify="center", style="bold", width=self.layout.STATUS_COLUMN_WIDTH
        )
        table.add_column(
            "Test ID", style=self.colors.get_color("text"), width=self.layout.TEST_ID_COLUMN_WIDTH
        )
        table.add_column(
            "DUT ID", style=self.colors.get_color("text"), width=self.layout.DUT_ID_COLUMN_WIDTH
        )

    def _add_detail_table_columns(self, table: Table) -> None:
        """Add detailed table columns for comprehensive test result display.

        Args:
            table: Rich Table object to add detailed columns to
        """
        table.add_column(
            "Model", style=self.colors.get_color("muted"), width=self.layout.MODEL_COLUMN_WIDTH
        )
        table.add_column(
            "Duration",
            justify="right",
            style=self.colors.get_color("info"),
            width=self.layout.DURATION_COLUMN_WIDTH,
        )
        table.add_column(
            "Measurements",
            justify="center",
            style=self.colors.get_color("accent"),
            width=self.layout.MEASUREMENTS_COLUMN_WIDTH,
        )

    def _format_eol_result_row(self, result: EOLTestResult, show_details: bool, dut_info: Optional[Dict[str, str]] = None) -> List[Any]:
        """Format EOLTestResult into table row data with consistent styling.

        Transforms an EOLTestResult object into properly formatted table row data
        with appropriate icons, colors, and text formatting for display.

        Args:
            result: EOL test result object containing test execution data
            show_details: Whether to include detailed columns in the row
            dut_info: Optional DUT information dict with 'id' and 'model' keys

        Returns:
            List of formatted row data elements ready for table display
        """
        # Determine appropriate status styling based on test outcome
        status_icon = self._get_result_status_icon(result)
        status_color = self._get_result_status_color(result)

        # Get DUT ID from provided DUT info or default to N/A
        dut_id = dut_info.get('id', 'N/A') if dut_info else 'N/A'

        # Build core row data with essential information
        row_data = self._build_core_row_data(
            status_icon=status_icon,
            status_color=status_color,
            test_id=str(result.test_id),
            dut_id=dut_id,
        )

        # Add detailed columns if comprehensive view is requested
        if show_details:
            detail_data = self._build_eol_detail_data(result, dut_info)
            row_data.extend(detail_data)

        # Add timestamp (current time since EOLTestResult doesn't store creation time)
        timestamp = self._format_current_timestamp()
        row_data.append(timestamp)

        return row_data

    def _format_dict_result_row(self, result: Dict[str, Any], show_details: bool) -> List[Any]:
        """Format dictionary result into table row data with consistent styling.

        Transforms a dictionary-based test result into properly formatted table
        row data with appropriate icons, colors, and text formatting for display.

        Args:
            result: Dictionary containing test result data from repository
            show_details: Whether to include detailed columns in the row

        Returns:
            List of formatted row data elements ready for table display
        """
        # Determine status styling based on test outcome
        is_passed = result.get("passed", False)
        status_icon = self.icons.get_icon("check") if is_passed else self.icons.get_icon("cross")
        status_color = (
            self.colors.get_color("success") if is_passed else self.colors.get_color("error")
        )

        # Extract DUT information from nested dictionary
        dut_info = result.get("dut", {})

        # Build core row data with essential information
        row_data = self._build_core_row_data(
            status_icon=status_icon,
            status_color=status_color,
            test_id=result.get("test_id", "N/A"),
            dut_id=str(dut_info.get("dut_id", "N/A")),
        )

        # Add detailed columns if comprehensive view is requested
        if show_details:
            detail_data = self._build_dict_detail_data(result, dut_info)
            row_data.extend(detail_data)

        # Format and add timestamp with safe parsing
        timestamp = self._format_result_timestamp(result.get("created_at", ""))
        row_data.append(timestamp)

        return row_data

    def _get_result_status_icon(self, result: EOLTestResult) -> str:
        """Get appropriate icon for test result based on execution outcome.

        Args:
            result: EOLTestResult object containing test execution details

        Returns:
            Unicode icon string representing the test result visually
        """
        if result.is_passed:
            return self.icons.get_icon("check")
        if result.is_failed_execution:
            return self.icons.get_icon("error")
        return self.icons.get_icon("cross")

    def _get_result_status_color(self, result: EOLTestResult) -> str:
        """Get appropriate color for test result based on execution outcome.

        Args:
            result: EOLTestResult object containing test execution details

        Returns:
            Color string from the professional color scheme
        """
        if result.is_passed:
            return self.colors.get_color("success")
        if result.is_failed_execution:
            return self.colors.get_color("error")
        return self.colors.get_color("error")

    def _get_pass_rate_color(self, pass_rate: float) -> str:
        """Get appropriate color for pass rate based on performance thresholds.

        Args:
            pass_rate: Pass rate percentage (0-100)

        Returns:
            Color string based on performance threshold
        """
        if pass_rate >= 90:
            return self.colors.get_color("success")
        elif pass_rate >= 70:
            return self.colors.get_color("warning")
        else:
            return self.colors.get_color("error")

    def _build_core_row_data(
        self, status_icon: str, status_color: str, test_id: str, dut_id: str
    ) -> List[Any]:
        """Build core row data common to both result formats.

        Args:
            status_icon: Unicode icon representing the test status
            status_color: Color string for status styling
            test_id: Test identifier string
            dut_id: Device under test identifier string

        Returns:
            List of formatted core data elements
        """
        return [
            Text(status_icon, style=f"bold {status_color}"),
            self._truncate_text(test_id),
            self._truncate_text(dut_id),
        ]

    def _build_eol_detail_data(self, result: EOLTestResult, dut_info: Optional[Dict[str, str]] = None) -> List[str]:
        """Build detail data specific to EOLTestResult objects.

        Args:
            result: EOLTestResult object containing test execution data
            dut_info: Optional DUT information dict with 'id' and 'model' keys

        Returns:
            List of formatted detail data elements
        """
        # Get model from provided DUT info or default to N/A
        model = dut_info.get('model', 'N/A') if dut_info else 'N/A'
        
        return [
            model,
            result.format_duration(),
            str(result.measurement_count),
        ]

    def _build_dict_detail_data(
        self, result: Dict[str, Any], dut_info: Dict[str, Any]
    ) -> List[str]:
        """Build detail data specific to dictionary result objects.

        Args:
            result: Dictionary containing test result data
            dut_info: Dictionary containing DUT information

        Returns:
            List of formatted detail data elements
        """
        return [
            str(dut_info.get("model_number", "N/A")),
            str(result.get("duration", "N/A")),
            str(len(result.get("measurement_ids", []))),
        ]

    # Convenience method for console output
    def print_table(self, table: Table) -> None:
        """Print a table to the console.

        Args:
            table: Rich Table to print
        """
        self.console.print(table)
