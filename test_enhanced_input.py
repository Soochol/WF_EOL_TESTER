#!/usr/bin/env python3
"""
Test script for Enhanced Input Manager Integration

Simple test script to verify that the enhanced input system works correctly
and integrates properly with the existing CLI components. This script tests
various input scenarios and provides validation of the enhancement.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from loguru import logger

from ui.cli.enhanced_input_manager import (
    EnhancedInputManager,
    is_prompt_toolkit_available
)
from ui.cli.enhanced_cli_integration import (
    EnhancedInputIntegrator,
    EnhancedMenuSystem,
    create_enhanced_cli_integrator,
    create_enhanced_menu_system
)
from ui.cli.rich_formatter import RichFormatter


async def test_enhanced_input_manager():
    """Test the enhanced input manager functionality"""
    console = Console()
    formatter = RichFormatter(console)
    
    console.print("[bold blue]Testing Enhanced Input Manager[/bold blue]\n")
    
    # Check prompt_toolkit availability
    console.print(f"prompt_toolkit available: {is_prompt_toolkit_available()}")
    
    if not is_prompt_toolkit_available():
        console.print("[yellow]Warning: prompt_toolkit not available, using fallback mode[/yellow]\n")
    
    # Create input manager
    input_manager = EnhancedInputManager(console, formatter)
    
    # Test basic input
    console.print("\n[cyan]Test 1: Basic Input[/cyan]")
    try:
        result = await input_manager.get_input(
            prompt_text="Enter test input: ",
            placeholder="Type something...",
            show_completions=False,
            enable_history=False
        )
        console.print(f"Result: {result}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    # Test validation
    console.print("\n[cyan]Test 2: Input Validation[/cyan]")
    try:
        valid, message = input_manager.validate_input_format("TEST123", "dut_id")
        console.print(f"Validation result for 'TEST123' as dut_id: {valid}")
        if not valid:
            console.print(f"Error message: {message}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    # Test completion suggestions
    console.print("\n[cyan]Test 3: Completion Suggestions[/cyan]")
    try:
        suggestions = input_manager.get_completion_suggestions("/rob")
        console.print(f"Suggestions for '/rob': {suggestions}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    # Test history stats
    console.print("\n[cyan]Test 4: History Statistics[/cyan]")
    try:
        stats = input_manager.get_history_stats()
        console.print(f"History stats: {stats}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[green]Enhanced Input Manager test completed![/green]")


async def test_cli_integration():
    """Test the CLI integration components"""
    console = Console()
    formatter = RichFormatter(console)
    
    console.print("\n[bold blue]Testing CLI Integration[/bold blue]\n")
    
    # Create integrator
    integrator = create_enhanced_cli_integrator(console, formatter)
    
    # Test validation
    console.print("[cyan]Test 1: Input Validation[/cyan]")
    try:
        result = await integrator.get_validated_input(
            "Enter DUT ID (test with 'TEST001'): ",
            input_type="dut_id",
            required=False,
            placeholder="e.g., TEST001"
        )
        console.print(f"Validated input result: {result}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    # Test confirmation
    console.print("\n[cyan]Test 2: Confirmation Dialog[/cyan]")
    try:
        confirmed = await integrator.get_confirmation("Continue with test?", default=True)
        console.print(f"Confirmation result: {confirmed}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[green]CLI Integration test completed![/green]")


async def test_menu_system():
    """Test the enhanced menu system"""
    console = Console()
    formatter = RichFormatter(console)
    
    console.print("\n[bold blue]Testing Enhanced Menu System[/bold blue]\n")
    
    # Create components
    integrator = create_enhanced_cli_integrator(console, formatter)
    menu_system = create_enhanced_menu_system(integrator)
    
    # Test statistics display
    console.print("[cyan]Test: Statistics Display[/cyan]")
    try:
        await menu_system.show_statistics_menu()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[green]Menu System test completed![/green]")


async def interactive_demo():
    """Interactive demonstration of enhanced features"""
    console = Console()
    formatter = RichFormatter(console)
    
    console.print("\n[bold blue]Interactive Demo - Enhanced Input Features[/bold blue]\n")
    
    if not is_prompt_toolkit_available():
        console.print("""[yellow]
Warning: prompt_toolkit is not available. 

To experience the full enhanced input features, please install prompt_toolkit:
    pip install prompt-toolkit>=3.0.38

Current demo will run in fallback mode with basic functionality.
[/yellow]""")
        
        proceed = input("\nContinue with basic demo? (y/N): ").lower().startswith('y')
        if not proceed:
            return
    
    integrator = create_enhanced_cli_integrator(console, formatter)
    
    console.print("""[cyan]
This demo will showcase the enhanced input features:

1. Auto-completion for commands and parameters
2. Command history with persistent storage
3. Real-time input validation
4. Syntax highlighting for slash commands
5. Professional prompt styling

Note: Press Ctrl+C at any time to exit the demo.
[/cyan]""")
    
    try:
        # Demo slash command input
        console.print("\n[bold]Demo 1: Slash Command Input[/bold]")
        console.print("Try typing: /robot connect, /mcu temp 85.0, or /help")
        
        command = await integrator.get_slash_command()
        if command:
            console.print(f"You entered: [green]{command}[/green]")
        
        # Demo DUT information collection
        console.print("\n[bold]Demo 2: DUT Information Collection[/bold]")
        console.print("This will collect DUT information with validation and auto-completion")
        
        dut_info = await integrator.get_dut_information()
        if dut_info:
            console.print(f"Collected DUT info: [green]{dut_info}[/green]")
        
        # Demo menu choice
        console.print("\n[bold]Demo 3: Enhanced Menu Choice[/bold]")
        
        custom_options = {
            "1": "Option One",
            "2": "Option Two", 
            "3": "Option Three",
            "quit": "Exit Demo"
        }
        
        choice = await integrator.get_menu_choice(
            menu_type='main_menu',
            prompt_text="Select demo option: ",
            custom_options=custom_options
        )
        
        if choice:
            console.print(f"You selected: [green]{choice}[/green] - {custom_options.get(choice, 'Unknown')}")
        
        console.print("\n[bold green]Interactive demo completed![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")


async def main():
    """Main test function"""
    console = Console()
    
    console.print("""[bold cyan]
╔══════════════════════════════════════════════════════════════════════════════╗
║                       Enhanced Input Manager Test Suite                      ║
║                                                                              ║
║  This test suite validates the prompt_toolkit integration and enhanced       ║
║  input features for the EOL Tester CLI system.                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
[/bold cyan]""")
    
    # Check Python version
    python_version = sys.version_info
    console.print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    console.print(f"prompt_toolkit available: {is_prompt_toolkit_available()}")
    
    if python_version < (3, 10):
        console.print("[red]Warning: Python 3.10+ recommended for best experience[/red]")
    
    console.print("\n" + "="*80)
    
    # Run tests
    try:
        await test_enhanced_input_manager()
        await test_cli_integration()
        await test_menu_system()
        
        # Ask if user wants interactive demo
        console.print("\n" + "="*80)
        console.print("[bold]All automated tests completed![/bold]")
        
        try:
            run_demo = input("\nRun interactive demo? (y/N): ").lower().startswith('y')
            if run_demo:
                await interactive_demo()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Demo skipped[/yellow]")
        
    except Exception as e:
        console.print(f"\n[bold red]Test suite error: {e}[/bold red]")
        logger.error(f"Test suite error: {e}")
        return 1
    
    console.print(f"\n[bold green]✓ Enhanced Input Manager test suite completed successfully![/bold green]")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)