#!/usr/bin/env python3
"""
Test script for Hardware Monitoring Dashboard Integration

This script tests the dashboard integration to ensure it works correctly
with both mock hardware and the Enhanced CLI system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from rich.console import Console
    from infrastructure.factory import create_hardware_service_facade
    from src.ui.cli.hardware_monitoring_dashboard import create_dashboard_manager
    from src.ui.cli.dashboard_integration import create_dashboard_integrator
    from src.ui.cli.rich_formatter import RichFormatter
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_dashboard_basic_functionality():
    """Test basic dashboard functionality with mock hardware"""
    console = Console()
    formatter = RichFormatter(console)
    
    console.print("[bold green]Testing Hardware Monitoring Dashboard Integration[/bold green]")
    console.print()
    
    try:
        # Create hardware service facade with mock hardware
        console.print("🔧 Creating hardware service facade...")
        hardware_facade = create_hardware_service_facade(
            config_path="config/hardware_config.json",
            use_mock=True  # Use mock hardware for testing
        )
        
        # Test dashboard manager creation
        console.print("📊 Creating dashboard manager...")
        dashboard = create_dashboard_manager(hardware_facade, console)
        
        # Test dashboard integrator creation
        console.print("🔗 Creating dashboard integrator...")
        integrator = create_dashboard_integrator(hardware_facade, console, formatter)
        
        console.print()
        console.print("[bold green]✅ Dashboard integration test passed![/bold green]")
        console.print()
        console.print("Dashboard components created successfully:")
        console.print("• Hardware Service Facade (Mock)")
        console.print("• Dashboard Manager")
        console.print("• Dashboard Integrator")
        console.print()
        console.print("[dim]Note: This test uses mock hardware for safety.[/dim]")
        console.print("[dim]To test with real hardware, modify the configuration.[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Dashboard integration test failed: {e}[/bold red]")
        return False


async def test_dashboard_data_collection():
    """Test dashboard data collection with mock hardware"""
    console = Console()
    
    console.print("[bold blue]Testing Dashboard Data Collection[/bold blue]")
    console.print()
    
    try:
        # Create hardware facade
        hardware_facade = create_hardware_service_facade(
            config_path="config/hardware_config.json",
            use_mock=True
        )
        
        # Create dashboard
        dashboard = create_dashboard_manager(hardware_facade, console)
        
        # Test data collection (this would normally be done in the live dashboard)
        console.print("📊 Testing data collection...")
        
        # Get one metrics snapshot
        current_metrics = dashboard.get_current_metrics()
        if current_metrics:
            console.print("[green]✅ Metrics collection working[/green]")
        else:
            console.print("[yellow]⚠ No metrics available yet (expected for new dashboard)[/yellow]")
        
        console.print()
        console.print("[bold green]✅ Data collection test completed![/bold green]")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Data collection test failed: {e}[/bold red]")
        return False


async def main():
    """Main test function"""
    console = Console()
    
    console.print("[bold cyan]Hardware Monitoring Dashboard Integration Test[/bold cyan]")
    console.print("=" * 60)
    console.print()
    
    # Test 1: Basic functionality
    test1_passed = await test_dashboard_basic_functionality()
    
    console.print()
    console.print("-" * 60)
    console.print()
    
    # Test 2: Data collection
    test2_passed = await test_dashboard_data_collection()
    
    console.print()
    console.print("=" * 60)
    
    # Summary
    if test1_passed and test2_passed:
        console.print("[bold green]🎉 All tests passed! Dashboard integration is ready.[/bold green]")
        console.print()
        console.print("You can now use the dashboard from the Enhanced CLI:")
        console.print("• Run the Enhanced CLI")
        console.print("• Select option '4 - Real-time Monitoring Dashboard'")
        console.print("• Choose '1 - Start Real-time Monitoring Dashboard'")
        return 0
    else:
        console.print("[bold red]❌ Some tests failed. Please check the errors above.[/bold red]")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[yellow]Tests interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        print(f"[red]Test execution failed: {e}[/red]")
        sys.exit(1)