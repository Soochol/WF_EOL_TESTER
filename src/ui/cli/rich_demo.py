"""
Rich UI Demonstration

Comprehensive demonstration of the Rich UI formatting capabilities
for the EOL Tester CLI application.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Union, cast

from rich.console import Console
from rich.progress import Progress
from rich.status import Status

from domain.enums.test_status import TestStatus
from domain.value_objects.eol_test_result import EOLTestResult

from .rich_formatter import RichFormatter
from .rich_utils import RichUIManager


async def demonstrate_rich_ui() -> None:
    """
    Comprehensive demonstration of Rich UI capabilities.

    Shows all the major features and formatting options available
    in the EOL Tester Rich UI system.
    """
    console = Console()
    formatter = RichFormatter(console)
    ui_manager = RichUIManager(console)

    # 1. Header and Banner Display
    console.print(
        "\n[bold blue]═══════════════════════════════════════════════════════[/bold blue]"
    )
    console.print("[bold blue]           EOL TESTER RICH UI DEMONSTRATION            [/bold blue]")
    console.print(
        "[bold blue]═══════════════════════════════════════════════════════[/bold blue]\n"
    )

    # Professional header banner
    formatter.print_header(
        "EOL Tester Rich UI Demo", "Comprehensive demonstration of formatting capabilities"
    )

    input("\nPress Enter to continue...")

    # 2. Status Panel Demonstrations
    console.clear()
    formatter.print_header("Status Panel Demonstrations")

    # Various status types
    formatter.print_status(
        "System Initialization",
        TestStatus.PREPARING,
        details={"Components": "Loading", "Configuration": "Validated", "Hardware": "Connecting"},
    )

    formatter.print_status(
        "Test Execution",
        TestStatus.RUNNING,
        details={
            "Progress": "45%",
            "Current Step": "Voltage measurement",
            "Elapsed Time": "2.3 seconds",
        },
    )

    formatter.print_status(
        "Test Complete",
        TestStatus.COMPLETED,
        details={"Result": "PASSED", "Duration": "5.7 seconds", "Measurements": "12 collected"},
    )

    input("\nPress Enter to continue...")

    # 3. Message Panel Demonstrations
    console.clear()
    formatter.print_header("Message Panel Demonstrations")

    formatter.print_message(
        "System initialization completed successfully!",
        message_type="success",
        title="Initialization Complete",
    )

    formatter.print_message(
        "Hardware calibration is due in 3 days. Please schedule maintenance.",
        message_type="warning",
        title="Maintenance Reminder",
    )

    formatter.print_message(
        "Failed to connect to power supply. Check connections and try again.",
        message_type="error",
        title="Connection Error",
    )

    formatter.print_message(
        "Test configuration loaded from profile 'Standard_WF_2024'.",
        message_type="info",
        title="Configuration Info",
    )

    input("\nPress Enter to continue...")

    # 4. Hardware Status Display
    console.clear()
    formatter.print_header("Hardware Status Display")

    hardware_status = {
        "Power Supply Unit": {
            "connected": True,
            "voltage": "24.05V",
            "current": "2.31A",
            "temperature": "45°C",
            "status": "OPERATIONAL",
        },
        "Digital Multimeter": {
            "connected": True,
            "model": "Keysight 34461A",
            "range": "Auto",
            "accuracy": "6.5 digits",
            "status": "READY",
        },
        "Oscilloscope": {
            "connected": False,
            "last_error": "Connection timeout after 5 seconds",
            "model": "Unknown",
            "status": "DISCONNECTED",
        },
        "Signal Generator": {
            "connected": True,
            "frequency": "1.000 MHz",
            "amplitude": "5.00V",
            "waveform": "Sine",
            "status": "ACTIVE",
        },
        "Temperature Sensor": {
            "connected": True,
            "temperature": "23.5°C",
            "humidity": "45%",
            "status": "MONITORING",
        },
    }

    hardware_display = formatter.create_hardware_status_display(
        hardware_status, title="Real-time Hardware Status"
    )
    console.print(hardware_display)

    input("\nPress Enter to continue...")

    # 5. Test Results Table
    console.clear()
    formatter.print_header("Test Results Table Display")

    # Sample test results data
    test_results: List[Dict[str, Any]] = [
        {
            "test_id": "T20240730001",
            "passed": True,
            "dut": {
                "dut_id": "WF2024A001",
                "model_number": "WF-2024-A",
                "serial_number": "SN001234",
            },
            "duration": "4.2s",
            "measurement_ids": ["M001", "M002", "M003", "M004"],
            "created_at": "2024-07-30T10:15:30Z",
        },
        {
            "test_id": "T20240730002",
            "passed": False,
            "dut": {
                "dut_id": "WF2024A002",
                "model_number": "WF-2024-A",
                "serial_number": "SN001235",
            },
            "duration": "2.1s",
            "measurement_ids": ["M005", "M006"],
            "created_at": "2024-07-30T10:18:45Z",
        },
        {
            "test_id": "T20240730003",
            "passed": True,
            "dut": {
                "dut_id": "WF2024B001",
                "model_number": "WF-2024-B",
                "serial_number": "SN002001",
            },
            "duration": "6.8s",
            "measurement_ids": ["M007", "M008", "M009", "M010", "M011", "M012"],
            "created_at": "2024-07-30T10:22:10Z",
        },
    ]

    results_table = formatter.create_test_results_table(
        cast(List[Union[EOLTestResult, Dict[str, Any]]], test_results),
        title="Recent Test Results",
        show_details=True,
    )
    formatter.print_table(results_table)

    input("\nPress Enter to continue...")

    # 6. Statistics Display
    console.clear()
    formatter.print_header("Statistics Display")

    statistics = {
        "overall": {
            "total_tests": 1247,
            "passed_tests": 1156,
            "failed_tests": 91,
            "pass_rate": 92.7,
            "average_duration": 4.8,
        },
        "recent": {
            "total_tests": 45,
            "passed_tests": 43,
            "pass_rate": 95.6,
            "average_duration": 4.2,
        },
        "by_model": {
            "WF-2024-A": {
                "total": 520,
                "passed": 495,
                "pass_rate": 95.19,
            },
            "WF-2024-B": {
                "total": 380,
                "passed": 342,
                "pass_rate": 90.00,
            },
            "WF-2023-X": {
                "total": 285,
                "passed": 265,
                "pass_rate": 92.98,
            },
            "WF-2022-Legacy": {
                "total": 62,
                "passed": 54,
                "pass_rate": 87.10,
            },
        },
    }

    stats_display = formatter.create_statistics_display(
        statistics, title="Comprehensive Test Statistics"
    )
    console.print(stats_display)

    input("\nPress Enter to continue...")

    # 7. Progress Displays
    console.clear()
    formatter.print_header("Progress Display Demonstrations")

    # Progress bar demonstration
    console.print("\n[bold]Progress Bar Example:[/bold]")
    with formatter.create_progress_display(
        "Processing test data...", total_steps=10, current_step=0
    ) as progress:
        if isinstance(progress, Progress) and progress.tasks:
            task_id = progress.tasks[0].id

            steps = [
                "Initializing hardware",
                "Loading configuration",
                "Connecting to devices",
                "Calibrating instruments",
                "Starting measurements",
                "Collecting data",
                "Analyzing results",
                "Generating report",
                "Saving results",
                "Cleanup and finalization",
            ]

            for i, step in enumerate(steps):
                progress.update(task_id, completed=i + 1, description=f"Step {i+1}: {step}")
                time.sleep(0.8)

    # Spinner demonstration
    console.print("\n[bold]Spinner Example:[/bold]")
    with formatter.create_progress_display(
        "Waiting for hardware response...", show_spinner=True
    ) as status:
        for i in range(5):
            if isinstance(status, Status):
                status.update(f"Attempt {i+1}: Connecting to device...")
            time.sleep(1)

    input("\nPress Enter to continue...")

    # 8. Interactive Menu Demonstration
    console.clear()
    formatter.print_header("Interactive Menu System")

    menu_options = {
        "1": "Execute New Test",
        "2": "View Test History",
        "3": "Check Hardware Status",
        "4": "Generate Report",
        "5": "System Settings",
        "q": "Quit Demo",
    }

    console.print("\n[bold]Menu Selection Example:[/bold]")
    selected = ui_manager.create_interactive_menu(
        menu_options, title="EOL Tester Main Menu", prompt="Please select an option"
    )

    if selected:
        formatter.print_message(
            f"You selected option '{selected}': {menu_options[selected]}",
            message_type="success",
            title="Selection Confirmed",
        )
    else:
        formatter.print_message("No selection made or invalid option entered.", message_type="info")

    input("\nPress Enter to continue...")

    # 9. Live Dashboard Demonstration
    console.clear()
    formatter.print_header("Live Dashboard Demonstration")

    console.print("\n[bold]Live updating dashboard (5 seconds):[/bold]")

    dashboard_data = {
        "active_tests": 0,
        "completed_today": 23,
        "pass_rate": 95.6,
        "hardware_status": "All Connected",
        "last_update": datetime.now().strftime("%H:%M:%S"),
    }

    with ui_manager.live_display(
        formatter.create_status_panel("System Dashboard", "MONITORING", details=dashboard_data),
        title="Live Dashboard",
    ) as live:
        for i in range(5):
            # Update dashboard data
            dashboard_data["active_tests"] = i % 3
            dashboard_data["completed_today"] = cast(int, dashboard_data["completed_today"]) + 1
            dashboard_data["pass_rate"] = 95.6 + (i * 0.2)
            dashboard_data["last_update"] = datetime.now().strftime("%H:%M:%S")

            # Update display
            live.update(
                formatter.create_status_panel(
                    "System Dashboard", "MONITORING", details=dashboard_data
                )
            )
            time.sleep(1)

    input("\nPress Enter to continue...")

    # 10. Error Analysis Display
    console.clear()
    formatter.print_header("Error Analysis Display")

    sample_errors = [
        {
            "type": "hardware",
            "message": "Power supply voltage out of range",
            "timestamp": "2024-07-30T10:15:00Z",
            "severity": "high",
        },
        {
            "type": "communication",
            "message": "DMM connection timeout",
            "timestamp": "2024-07-30T10:20:00Z",
            "severity": "medium",
        },
        {
            "type": "hardware",
            "message": "Temperature sensor not responding",
            "timestamp": "2024-07-30T10:25:00Z",
            "severity": "high",
        },
        {
            "type": "software",
            "message": "Measurement algorithm convergence failure",
            "timestamp": "2024-07-30T10:30:00Z",
            "severity": "medium",
        },
        {
            "type": "communication",
            "message": "Signal generator SCPI command failed",
            "timestamp": "2024-07-30T10:35:00Z",
            "severity": "low",
        },
    ]

    ui_manager.display_error_analysis(sample_errors, title="System Error Analysis - Last 24 Hours")

    input("\nPress Enter to continue...")

    # 11. Complete Test Flow Demonstration
    console.clear()
    formatter.print_header("Complete Test Execution Flow")

    test_command_info = {
        "dut_id": "WF2024A003",
        "model": "WF-2024-A",
        "serial": "SN001236",
        "operator": "engineer1",
        "test_profile": "Standard_WF_2024",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    execution_steps = [
        "Hardware initialization",
        "Device connection verification",
        "Calibration check",
        "Power supply setup",
        "Signal generator configuration",
        "DMM range selection",
        "Test execution start",
        "Data collection phase",
        "Measurement validation",
        "Result analysis",
        "Report generation",
        "Cleanup operations",
    ]

    ui_manager.display_test_execution_flow(test_command_info, execution_steps)

    input("\nPress Enter to continue...")

    # 12. Summary and Conclusion
    console.clear()
    formatter.print_header(
        "Rich UI Demonstration Complete", "All major features have been demonstrated"
    )

    summary_info = {
        "Features Demonstrated": "12",
        "UI Components": "Status panels, tables, progress bars, menus",
        "Color Schemes": "Professional blue/teal theme",
        "Integration": "Seamless with existing EOL Tester architecture",
        "Benefits": "Enhanced UX, professional appearance, better usability",
    }

    formatter.print_status("Demonstration Summary", "COMPLETED", details=summary_info)

    formatter.print_message(
        "The Rich UI system provides a comprehensive set of tools for creating "
        "beautiful, professional terminal interfaces. All components are designed "
        "to integrate seamlessly with the existing EOL Tester architecture while "
        "providing enhanced user experience and visual appeal.",
        message_type="success",
        title="Implementation Ready",
    )

    formatter.print_message(
        "To integrate these components into your application, simply import the "
        "RichFormatter and RichUIManager classes and replace existing print "
        "statements with the appropriate Rich UI method calls.",
        message_type="info",
        title="Integration Guide",
    )

    console.print("\n[bold green]Thank you for viewing the Rich UI demonstration![/bold green]")
    console.print("[dim]Rich UI makes terminal applications beautiful and professional.[/dim]")


def run_quick_examples() -> None:
    """
    Run quick examples of individual Rich UI components.
    """
    console = Console()
    formatter = RichFormatter(console)

    # Quick status example
    formatter.print_message(
        "Quick Examples - Individual Component Demonstrations",
        message_type="info",
        title="Rich UI Quick Examples",
    )

    # Status panel
    formatter.print_status("Quick Test", TestStatus.COMPLETED, {"Result": "PASSED", "Time": "1.2s"})

    # Simple table
    quick_results: List[Dict[str, Any]] = [
        {"test_id": "Q001", "passed": True, "dut": {"dut_id": "QT001"}},
        {"test_id": "Q002", "passed": False, "dut": {"dut_id": "QT002"}},
    ]

    table = formatter.create_test_results_table(
        cast(List[Union[EOLTestResult, Dict[str, Any]]], quick_results), "Quick Test Results"
    )
    formatter.print_table(table)

    console.print("\n[bold]Quick examples complete![/bold]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_examples()
    else:
        asyncio.run(demonstrate_rich_ui())
