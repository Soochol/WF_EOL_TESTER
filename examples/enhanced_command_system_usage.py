"""
Enhanced Command System Usage Example

This module demonstrates the usage of the enhanced CLI system with proper imports
and examples of how to use the various components.
"""

# Standard library imports
import asyncio
from typing import Dict, Optional

# Third-party imports
from rich.console import Console

# Correct imports using existing modules
from ui.cli.rich_formatter import RichFormatter
from ui.cli.validation.input_validator import InputValidator

# Other CLI imports
from ui.cli.enhanced_cli_integration import (
    EnhancedInputIntegrator,
    EnhancedMenuSystem,
    create_enhanced_cli_integrator,
    create_enhanced_menu_system,
)


class EnhancedCommandSystemExample:
    """Example class demonstrating the enhanced command system usage"""

    def __init__(self):
        """Initialize the enhanced command system example"""
        # Create console and formatter
        self.console = Console(force_terminal=True, legacy_windows=False)
        self.formatter = RichFormatter(self.console)
        
        # Create validator
        self.validator = InputValidator()
        
        # Create enhanced integrator and menu system
        self.integrator = create_enhanced_cli_integrator(
            self.console, self.formatter, None  # No configuration service for example
        )
        self.menu_system = create_enhanced_menu_system(self.integrator)
        
    async def demonstrate_menu_system(self) -> None:
        """Demonstrate the enhanced menu system"""
        self.formatter.print_header(
            "Enhanced Menu System Demo",
            "Demonstrating advanced menu features with Rich formatting"
        )
        
        # Show the main menu
        choice = await self.menu_system.show_main_menu_enhanced()
        
        if choice:
            self.formatter.print_message(
                f"You selected option: {choice}",
                message_type="success",
                title="Menu Selection"
            )
        else:
            self.formatter.print_message(
                "No selection made",
                message_type="info"
            )
    
    async def demonstrate_input_validation(self) -> None:
        """Demonstrate input validation features"""
        self.formatter.print_header(
            "Input Validation Demo",
            "Demonstrating input validation with the InputValidator"
        )
        
        # Example of validated input
        try:
            result = await self.integrator.get_validated_input(
                prompt="Enter a test value: ",
                input_type="general",
                required=True,
                placeholder="Type any value to test validation"
            )
            
            if result:
                # Validate the input using the validator
                is_valid = self.validator.validate_input(result, "general")
                
                if is_valid:
                    self.formatter.print_message(
                        f"Input '{result}' is valid!",
                        message_type="success"
                    )
                else:
                    self.formatter.print_message(
                        f"Input '{result}' failed validation",
                        message_type="warning"
                    )
                    
        except Exception as e:
            self.formatter.print_message(
                f"Validation error: {e}",
                message_type="error"
            )
    
    async def demonstrate_dut_collection(self) -> None:
        """Demonstrate DUT information collection"""
        self.formatter.print_header(
            "DUT Information Collection Demo",
            "Demonstrating DUT data collection workflow"
        )
        
        # This would normally require a configuration service
        self.formatter.print_message(
            "DUT information collection requires configuration service",
            message_type="info",
            title="Configuration Required"
        )
        
        # Example of confirmation dialog
        proceed = await self.integrator.get_confirmation(
            "Would you like to continue with the demo?",
            default=True
        )
        
        if proceed:
            self.formatter.print_message(
                "Continuing with demo...",
                message_type="success"
            )
        else:
            self.formatter.print_message(
                "Demo cancelled by user",
                message_type="info"
            )
    
    async def run_complete_demo(self) -> None:
        """Run the complete demonstration"""
        self.formatter.print_header(
            "Enhanced Command System Complete Demo",
            "Full demonstration of enhanced CLI capabilities"
        )
        
        try:
            # Demonstrate menu system
            await self.demonstrate_menu_system()
            await self.integrator.wait_for_acknowledgment()
            
            # Demonstrate input validation
            await self.demonstrate_input_validation()
            await self.integrator.wait_for_acknowledgment()
            
            # Demonstrate DUT collection
            await self.demonstrate_dut_collection()
            
            self.formatter.print_message(
                "Demo completed successfully!",
                message_type="success",
                title="Demo Complete"
            )
            
        except KeyboardInterrupt:
            self.formatter.print_message(
                "Demo interrupted by user",
                message_type="info",
                title="Demo Cancelled"
            )
        except Exception as e:
            self.formatter.print_message(
                f"Demo error: {e}",
                message_type="error",
                title="Demo Error"
            )


async def main():
    """Main function to run the enhanced command system example"""
    try:
        # Create and run the example
        example = EnhancedCommandSystemExample()
        await example.run_complete_demo()
        
    except Exception as e:
        console = Console()
        console.print(f"[red]Example execution error: {e}[/red]")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())