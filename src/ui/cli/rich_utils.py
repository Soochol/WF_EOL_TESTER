"""
Rich UI Utilities Module

Comprehensive utility functions and helper classes for working with the RichFormatter
and creating consistent Rich UI components across the EOL Tester application.

This module provides high-level UI management patterns, context managers for
live displays, and utility functions that simplify common Rich UI operations
while maintaining consistent styling and behavior.
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Union

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.status import Status

from domain.enums.test_status import TestStatus
from domain.value_objects.eol_test_result import EOLTestResult

from .rich_formatter import RichFormatter


# Constants for improved maintainability and eliminating magic numbers
class UIManagerConstants:
    """Constants for UI manager operations, timing, and component categorization.

    These constants define timing parameters, categorization keywords, and
    display titles used throughout the Rich UI management system to ensure
    consistent behavior and easy maintenance.
    """

    # Timing constants for smooth user experience
    STEP_EXECUTION_DELAY = 0.5  # Seconds between execution steps for visibility
    DEMO_DELAY = 1.0  # Seconds for demonstration delays
    DEFAULT_REFRESH_RATE = 4  # Updates per second for live displays

    # Component categorization keywords for hardware organization
    POWER_KEYWORDS = ["power"]  # Power supply systems
    MEASUREMENT_KEYWORDS = ["dmm", "scope", "meter", "multimeter"]  # Measurement instruments
    COMMUNICATION_KEYWORDS = ["serial", "usb", "ethernet", "can"]  # Communication interfaces

    # Error categorization keywords for intelligent error grouping
    HARDWARE_ERROR_KEYWORDS = ["hardware", "connection", "device"]  # Hardware-related errors
    SOFTWARE_ERROR_KEYWORDS = ["software", "algorithm", "calculation"]  # Software-related errors
    COMMUNICATION_ERROR_KEYWORDS = ["communication", "timeout", "protocol"]  # Communication errors

    # Display titles for organized hardware status presentation
    POWER_SYSTEMS_TITLE = "Power Systems"  # Power supply components
    MEASUREMENT_INSTRUMENTS_TITLE = "Measurement Instruments"  # Measurement equipment
    COMMUNICATION_INTERFACES_TITLE = "Communication Interfaces"  # Communication hardware


class RichUIManager:
    """Comprehensive manager class for Rich UI operations and patterns.

    This class provides high-level methods for common UI patterns, manages
    the lifecycle of Rich UI components, and offers context managers for
    live displays and progress operations. It encapsulates complex UI
    workflows to simplify their usage throughout the application.

    Key Features:
    - Context managers for live displays and progress indication
    - Hardware dashboard with intelligent component categorization
    - Test execution flow visualization with progress tracking
    - Error analysis with automatic categorization and grouping
    - Interactive menu creation with consistent styling
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the Rich UI Manager with console and formatter configuration.

        Args:
            console: Optional Rich Console instance. If None, creates a new one
                    with default settings optimized for the EOL Tester application.
        """
        self.console = console or Console()
        self.formatter = RichFormatter(self.console)

    @contextmanager
    def live_display(
        self,
        initial_content: Any,
        title: Optional[str] = None,
        refresh_per_second: int = 4,
    ) -> Generator[Live, None, None]:
        """Context manager for live updating displays with automatic lifecycle management.

        Provides a context manager that handles the creation, configuration, and
        cleanup of Rich Live displays. Automatically wraps content in a panel
        if a title is provided, and ensures proper resource cleanup.

        Args:
            initial_content: Initial Rich object or content to display
            title: Optional display title (wraps content in titled panel if provided)
            refresh_per_second: Display refresh rate (defaults to UIManagerConstants value)

        Yields:
            Live display object for real-time content updates
        """
        if title:
            content = Panel(initial_content, title=title)
        else:
            content = initial_content

        with Live(
            content,
            console=self.console,
            refresh_per_second=refresh_per_second or UIManagerConstants.DEFAULT_REFRESH_RATE,
        ) as live:
            yield live

    @contextmanager
    def progress_context(
        self,
        task_name: str,
        total_steps: Optional[int] = None,
    ) -> Generator[Union[Progress, Status], None, None]:
        """Context manager for progress operations with automatic lifecycle management.

        Provides a context manager that creates appropriate progress indicators
        based on whether the total steps are known. Handles both deterministic
        progress bars and indeterminate status spinners.

        Args:
            task_name: Descriptive name of the task being performed
            total_steps: Total number of steps (creates progress bar if provided,
                        otherwise creates status spinner)

        Yields:
            Progress object for deterministic operations or Status object
            for indeterminate operations
        """
        progress_display = self.formatter.create_progress_display(task_name, total_steps)

        with progress_display:
            yield progress_display

    def display_test_execution_flow(
        self,
        command_info: Dict[str, Any],
        steps: List[str],
    ) -> None:
        """Display a complete test execution flow with progress visualization.

        Creates a comprehensive display showing test command information,
        configuration details, and step-by-step execution progress. Provides
        visual feedback for each execution step with timing delays.

        Args:
            command_info: Dictionary containing test command and configuration information
            steps: List of execution step descriptions to display with progress
        """
        # Display comprehensive header with test context
        self.formatter.print_header(
            "EOL Test Execution", f"DUT: {command_info.get('dut_id', 'Unknown')}"
        )

        # Show test configuration summary with details
        self.formatter.print_status("Test Configuration", "READY", details=command_info)

        # Execute steps with visual progress indication
        with self.progress_context("Executing test steps...", total_steps=len(steps)) as progress:
            if isinstance(progress, Progress) and progress.tasks:
                # Get the task ID for progress updates (Progress object)
                task_id = progress.tasks[0].id

                # Execute each step with progress feedback
                for step_index, step_description in enumerate(steps):
                    progress.update(
                        task_id,
                        completed=step_index,
                        description=f"Step {step_index+1}: {step_description}",
                    )
                    # Add visible delay for demonstration purposes
                    time.sleep(UIManagerConstants.STEP_EXECUTION_DELAY)

    def display_hardware_dashboard(
        self,
        hardware_components: Dict[str, Dict[str, Any]],
    ) -> None:
        """Display a comprehensive hardware dashboard with intelligent categorization.

        Creates an organized hardware status dashboard that automatically
        categorizes components by type (power, measurement, communication)
        and displays them in logically grouped sections for easy monitoring.

        Args:
            hardware_components: Dictionary mapping component names to their
                               status information and configuration details
        """
        # Display dashboard header with descriptive subtitle
        self.formatter.print_header("Hardware Dashboard", "Real-time Hardware Status Monitor")

        # Organize components by type for logical grouping
        categorized_components = self._categorize_hardware_components(hardware_components)

        # Display all component groups with organized formatting
        self._display_component_groups(categorized_components)

    def display_test_results_summary(
        self,
        results: List[Union[EOLTestResult, Dict[str, Any]]],
        title: str = "Test Results Summary",
        show_statistics: bool = True,
    ) -> None:
        """Display a comprehensive test results summary with optional statistics.

        Creates a complete test results display including a formatted table
        of individual results and optional statistical analysis. Handles both
        EOLTestResult objects and dictionary-based results from repositories.

        Args:
            results: List of test results in mixed formats (EOLTestResult or Dict)
            title: Summary title displayed at the top of the results
            show_statistics: Whether to calculate and display summary statistics
        """
        self.formatter.print_header(title)

        # Results table
        table = self.formatter.create_test_results_table(
            results, title=f"Test Results ({len(results)} tests)", show_details=True
        )
        self.formatter.print_table(table)

        # Statistics if requested
        if show_statistics and results:
            stats = self._calculate_results_statistics(results)
            stats_panel = self.formatter.create_statistics_display(
                {"overall": stats}, title="Summary Statistics"
            )
            self.console.print(stats_panel)

    def display_error_analysis(
        self,
        errors: List[Dict[str, Any]],
        title: str = "Error Analysis",
    ) -> None:
        """Display error analysis with intelligent categorization and grouping.

        Creates an organized error analysis display that automatically categorizes
        errors by type (hardware, software, communication, other) and presents
        them in grouped sections for easier troubleshooting and debugging.

        Args:
            errors: List of dictionaries containing error information with type and message
            title: Analysis title displayed at the top of the error summary
        """
        self.formatter.print_header(title)

        # Categorize errors using improved categorization logic
        error_categories = self._categorize_errors(errors)

        # Display categorized errors
        self._display_error_categories(error_categories)

    def create_interactive_menu(
        self,
        options: Dict[str, str],
        title: str = "Menu",
        prompt: str = "Select an option",
    ) -> Optional[str]:
        """Create an interactive menu with Rich formatting and input validation.

        Generates a beautifully formatted interactive menu with consistent styling,
        proper input validation, and graceful error handling. Supports keyboard
        interruption and provides clear feedback for invalid selections.

        Args:
            options: Dictionary mapping option keys to descriptive text
            title: Menu title displayed prominently at the top
            prompt: Input prompt text shown to the user

        Returns:
            Selected option key as string, or None if operation was cancelled
            or interrupted by user
        """
        # Create formatted menu display with consistent styling
        menu_content = []
        for key, description in options.items():
            menu_content.append(f"[bold cyan]{key}.[/bold cyan] {description}")

        menu_text = "\n".join(menu_content) + f"\n\n{prompt}:"

        # Display the menu panel with professional formatting (no icon for menus)
        from rich.panel import Panel
        from rich.text import Text
        
        # Create clean menu content without icons
        content = Text.from_markup(menu_text)
        
        menu_panel = Panel(
            content,
            title=f"🧪 {title}",
            border_style=self.formatter.COLORS["info"],
            padding=(1, 2)
        )
        self.console.print(menu_panel)

        # Handle user input with validation and error handling
        try:
            user_choice = input().strip()

            # Validate user selection against available options
            if user_choice in options:
                return user_choice

            # Provide helpful feedback for invalid selections
            self.formatter.print_message(
                f"Invalid option '{user_choice}'. Please select from: {', '.join(options.keys())}",
                message_type="warning",
            )
            return None

        except (KeyboardInterrupt, EOFError):
            # Handle user cancellation gracefully
            return None

    def _calculate_results_statistics(
        self, results: List[Union[EOLTestResult, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive statistics from test results with mixed format support.

        Analyzes a list of test results in mixed formats (EOLTestResult objects
        and dictionary-based results) to generate comprehensive statistics including
        counts by outcome and overall pass rate.

        Args:
            results: List of test results in mixed formats to analyze

        Returns:
            Dictionary containing comprehensive test statistics
        """
        total_tests = len(results)
        passed_tests = 0
        failed_tests = 0
        error_tests = 0

        # Analyze each result and categorize by outcome
        for result in results:
            if isinstance(result, EOLTestResult):
                # Handle EOLTestResult objects with detailed status analysis
                if result.is_passed:
                    passed_tests += 1
                elif result.is_failed_execution:
                    error_tests += 1
                else:
                    failed_tests += 1
            else:
                # Handle dictionary-based results from repository
                if result.get("passed", False):
                    passed_tests += 1
                else:
                    failed_tests += 1

        # Calculate pass rate with division by zero protection
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "pass_rate": pass_rate,
        }

    def _display_error_category(self, category: str, errors: List[Dict[str, Any]]) -> None:
        """Display a categorized group of errors with message aggregation.

        Creates a formatted display panel for a specific category of errors,
        aggregating duplicate messages and showing occurrence counts for
        better error analysis and troubleshooting.

        Args:
            category: Error category name for the panel title
            errors: List of error dictionaries in this category
        """
        if not errors:
            return

        # Aggregate error messages and count occurrences
        error_message_counts: Dict[str, int] = {}
        for error in errors:
            error_message = error.get("message", "Unknown error")
            current_count = error_message_counts.get(error_message, 0)
            error_message_counts[error_message] = current_count + 1

        # Format error messages with occurrence counts
        formatted_error_lines = []
        for message, occurrence_count in error_message_counts.items():
            if occurrence_count > 1:
                formatted_error_lines.append(f"• {message} (×{occurrence_count})")
            else:
                formatted_error_lines.append(f"• {message}")

        error_content = "\n".join(formatted_error_lines)

        # Create and display the error category panel
        error_panel = self.formatter.create_message_panel(
            error_content,
            message_type="error" if "error" in category.lower() else "warning",
            title=f"{category} ({len(errors)} occurrences)",
        )
        self.console.print(error_panel)

    def _categorize_hardware_components(
        self, hardware_components: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Categorize hardware components by type for organized dashboard display.

        Analyzes hardware components and groups them into logical categories
        (power, measurement, communication) based on their type information
        for better organization in the hardware dashboard.

        Args:
            hardware_components: Dictionary mapping component names to their
                               status information and configuration

        Returns:
            Dictionary with components organized by category for display
        """
        # Initialize category containers
        component_categories: Dict[str, Dict[str, Dict[str, Any]]] = {
            "power": {},
            "measurement": {},
            "communication": {},
        }

        # Categorize each component based on its type
        for component_name, component_status in hardware_components.items():
            component_type = component_status.get("type", "unknown").lower()
            determined_category = self._determine_component_category(component_type)
            component_categories[determined_category][component_name] = component_status

        return component_categories

    def _determine_component_category(self, component_type: str) -> str:
        """Determine the category of a hardware component based on its type string.

        Uses keyword matching to categorize hardware components into logical
        groups for organized display in the hardware dashboard.

        Args:
            component_type: Component type string to analyze

        Returns:
            Category string ("power", "measurement", or "communication")
        """
        # Check for power system components
        if any(keyword in component_type for keyword in UIManagerConstants.POWER_KEYWORDS):
            return "power"
        # Check for measurement instrument components
        if any(keyword in component_type for keyword in UIManagerConstants.MEASUREMENT_KEYWORDS):
            return "measurement"
        # Check for communication interface components
        if any(keyword in component_type for keyword in UIManagerConstants.COMMUNICATION_KEYWORDS):
            return "communication"
        # Default to communication category for unknown component types
        return "communication"

    def _display_component_groups(
        self, component_groups: Dict[str, Dict[str, Dict[str, Any]]]
    ) -> None:
        """Display hardware component groups with organized titles and formatting.

        Iterates through categorized hardware components and displays each
        non-empty category with appropriate titles and professional formatting.

        Args:
            component_groups: Dictionary of categorized hardware components
        """
        # Define category display configuration with consistent titles
        category_display_configs = [
            ("power", UIManagerConstants.POWER_SYSTEMS_TITLE),
            ("measurement", UIManagerConstants.MEASUREMENT_INSTRUMENTS_TITLE),
            ("communication", UIManagerConstants.COMMUNICATION_INTERFACES_TITLE),
        ]

        # Display each category that contains components
        for category_key, display_title in category_display_configs:
            category_components = component_groups.get(category_key, {})
            if category_components:
                # Create and display hardware status panel for this category
                hardware_panel = self.formatter.create_hardware_status_display(
                    category_components, title=display_title
                )
                self.console.print(hardware_panel)

    def _categorize_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize errors by type for organized analysis and display.

        Analyzes error information and groups errors into logical categories
        based on their type, making it easier to identify patterns and
        troubleshoot issues systematically.

        Args:
            errors: List of error information dictionaries with type and message

        Returns:
            Dictionary with errors organized by category for structured display
        """
        # Initialize error category containers
        error_categories: Dict[str, List[Dict[str, Any]]] = {
            "Hardware Errors": [],
            "Software Errors": [],
            "Communication Errors": [],
            "Other Errors": [],
        }

        # Categorize each error based on its type
        for error_info in errors:
            error_type = error_info.get("type", "").lower()
            determined_category = self._determine_error_category(error_type)
            error_categories[determined_category].append(error_info)

        return error_categories

    def _determine_error_category(self, error_type: str) -> str:
        """Determine the category of an error based on its type string.

        Uses keyword matching to categorize errors into logical groups
        for better organization and troubleshooting in error analysis displays.

        Args:
            error_type: Error type string to analyze for categorization

        Returns:
            Error category string for organized display
        """
        # Check for hardware-related errors
        if any(keyword in error_type for keyword in UIManagerConstants.HARDWARE_ERROR_KEYWORDS):
            return "Hardware Errors"
        # Check for software-related errors
        if any(keyword in error_type for keyword in UIManagerConstants.SOFTWARE_ERROR_KEYWORDS):
            return "Software Errors"
        # Check for communication-related errors
        if any(
            keyword in error_type for keyword in UIManagerConstants.COMMUNICATION_ERROR_KEYWORDS
        ):
            return "Communication Errors"
        # Default category for unrecognized error types
        return "Other Errors"

    def _display_error_categories(self, error_categories: Dict[str, List[Dict[str, Any]]]) -> None:
        """Display all error categories that contain errors with organized formatting.

        Iterates through error categories and displays each non-empty category
        with appropriate formatting and aggregated error information.

        Args:
            error_categories: Dictionary of categorized error lists
        """
        for category_name, category_errors in error_categories.items():
            if category_errors:
                self._display_error_category(category_name, category_errors)


# Utility functions for common Rich UI operations
def create_quick_status_display(
    console: Console,
    title: str,
    status: Union[str, TestStatus],
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Quick utility to create and display a professional status panel.

    Provides a convenient way to create and immediately display a status panel
    without needing to instantiate a RichFormatter manually. Ideal for simple
    status updates throughout the application.

    Args:
        console: Rich Console instance for output
        title: Status title describing what is being shown
        status: Status value (string or TestStatus enum)
        details: Optional dictionary of additional details to display
    """
    formatter = RichFormatter(console)
    formatter.print_status(title, status, details)


def create_quick_results_table(
    console: Console,
    results: List[Union[EOLTestResult, Dict[str, Any]]],
    title: str = "Test Results",
) -> None:
    """Quick utility to create and display a professional test results table.

    Provides a convenient way to create and immediately display a formatted
    test results table without needing to manage formatter instantiation.
    Handles mixed result formats automatically.

    Args:
        console: Rich Console instance for output
        results: List of test results in mixed formats (EOLTestResult or Dict)
        title: Table title displayed at the top
    """
    formatter = RichFormatter(console)
    results_table = formatter.create_test_results_table(results, title)
    formatter.print_table(results_table)


def create_quick_message(
    console: Console,
    message: str,
    message_type: str = "info",
    title: Optional[str] = None,
) -> None:
    """Quick utility to create and display a formatted message panel.

    Provides a convenient way to create and immediately display a message panel
    with appropriate styling and icons without needing to manage formatter
    instantiation. Supports different message types with consistent styling.

    Args:
        console: Rich Console instance for output
        message: Message text content to display
        message_type: Message category (success, error, warning, info)
        title: Optional panel title (defaults to message_type if None)
    """
    formatter = RichFormatter(console)
    formatter.print_message(message, message_type, title)


# Example integration patterns and usage documentation
def demonstrate_integration_patterns() -> str:
    """Demonstrate various integration patterns with the Rich UI system.

    Provides comprehensive examples of how to use the Rich UI utilities
    effectively throughout the EOL Tester application. These patterns
    demonstrate best practices for common UI scenarios.

    Returns:
        String containing detailed example code patterns and usage instructions
    """
    return """
# Integration Patterns for Rich UI in EOL Tester Application

## Pattern 1: Simple Status Updates
# Quick status displays for immediate feedback
from rich.console import Console
from ui.cli.rich_utils import create_quick_status_display

console = Console()
create_quick_status_display(
    console,
    "Hardware Initialization",
    "READY",
    {"Components": "5 connected", "Status": "All systems operational"}
)

## Pattern 2: Progress Tracking with Context Manager
# Managed progress indication for long-running operations
from ui.cli.rich_utils import RichUIManager

ui_manager = RichUIManager()
with ui_manager.progress_context("Running tests...", total_steps=10) as progress:
    for i in range(10):
        # Perform work step
        if hasattr(progress, 'update'):
            progress.update(progress.tasks[0].id, completed=i+1)

## Pattern 3: Live Dashboard Updates
# Real-time display updates for dynamic content
with ui_manager.live_display("Initializing...") as live:
    for step in ["Connect hardware", "Load config", "Start monitoring"]:
        live.update(ui_manager.formatter.create_message_panel(step, "info"))
        time.sleep(UIManagerConstants.DEMO_DELAY)

## Pattern 4: Interactive Menu Systems
# User-friendly menu creation with validation
options = {
    "1": "Run Test",
    "2": "Check Status",
    "3": "View Results",
    "q": "Quit"
}
user_choice = ui_manager.create_interactive_menu(options, "Main Menu")

## Pattern 5: Comprehensive Error Analysis
# Organized error display with intelligent categorization
errors = [
    {"type": "hardware", "message": "Power supply disconnected"},
    {"type": "communication", "message": "DMM timeout"},
]
ui_manager.display_error_analysis(errors, "System Errors")

## Pattern 6: Results Summary with Statistics
# Complete test results display with analytical insights
test_results = [...]  # Your test results data
ui_manager.display_test_results_summary(
    test_results,
    "Daily Test Summary",
    show_statistics=True
)

## Pattern 7: Hardware Dashboard Monitoring
# Organized hardware status monitoring
hardware_status = {
    "power_supply": {"type": "power", "connected": True, "voltage": "24V"},
    "dmm_primary": {"type": "dmm", "connected": True, "model": "34401A"}
}
ui_manager.display_hardware_dashboard(hardware_status)
"""
