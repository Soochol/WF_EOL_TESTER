"""
Main Application Entry Point

Entry point for the EOL Tester application with CLI and API support.
"""

import sys
import asyncio
import argparse
from typing import Optional
from loguru import logger

from integration.application_factory import ApplicationFactory
from integration.dependency_injection import DependencyContainer


class EOLTesterApplication:
    """Main application class"""
    
    def __init__(self, container: DependencyContainer):
        """
        Initialize application
        
        Args:
            container: Dependency injection container
        """
        self._container = container
        self._running = False
    
    async def run_cli_interactive(self) -> None:
        """Run interactive CLI application"""
        logger.info("Starting EOL Tester CLI application")
        
        try:
            # Create CLI interfaces
            eol_test_cli, hardware_cli, _ = ApplicationFactory.create_cli_application()
            
            self._running = True
            
            while self._running:
                await self._show_main_menu(eol_test_cli, hardware_cli)
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self._shutdown()
    
    async def _show_main_menu(self, eol_test_cli, hardware_cli) -> None:
        """Show main menu and handle user selection"""
        print("\n" + "="*60)
        print("EOL Tester Application - Main Menu".center(60))
        print("="*60)
        print("1. Execute EOL Test")
        print("2. Hardware Management")
        print("3. System Status")
        print("4. Exit")
        print("-"*60)
        
        try:
            choice = input("Select option (1-4): ").strip()
            
            if choice == "1":
                await eol_test_cli.execute_test_interactive()
            elif choice == "2":
                await self._hardware_menu(hardware_cli)
            elif choice == "3":
                await hardware_cli.hardware_status_interactive()
            elif choice == "4":
                self._running = False
                print("Exiting application...")
            else:
                print("Invalid option. Please select 1-4.")
                
        except (KeyboardInterrupt, EOFError):
            self._running = False
            print("\nExiting application...")
    
    async def _hardware_menu(self, hardware_cli) -> None:
        """Show hardware management submenu"""
        print("\n" + "="*60)
        print("Hardware Management".center(60))
        print("="*60)
        print("1. Check Hardware Status")
        print("2. Connect Hardware")
        print("3. Disconnect Hardware")
        print("4. Read Force Measurement")
        print("5. Zero LoadCell")
        print("6. Configure Power Output")
        print("7. Measure Power Output")
        print("8. Back to Main Menu")
        print("-"*60)
        
        try:
            choice = input("Select option (1-8): ").strip()
            
            if choice == "1":
                await hardware_cli.hardware_status_interactive()
            elif choice == "2":
                await hardware_cli.connect_hardware_interactive()
            elif choice == "3":
                await hardware_cli.disconnect_hardware_interactive()
            elif choice == "4":
                await hardware_cli.read_force_interactive()
            elif choice == "5":
                await hardware_cli.zero_loadcell_interactive()
            elif choice == "6":
                await hardware_cli.set_power_output_interactive()
            elif choice == "7":
                await hardware_cli.measure_power_interactive()
            elif choice == "8":
                return  # Back to main menu
            else:
                print("Invalid option. Please select 1-8.")
                
        except (KeyboardInterrupt, EOFError):
            return  # Back to main menu
    
    async def _shutdown(self) -> None:
        """Shutdown application gracefully"""
        logger.info("Shutting down EOL Tester application")
        
        if self._container:
            self._container.shutdown()
        
        logger.info("Application shutdown complete")


def setup_logging(debug: bool = False) -> None:
    """
    Setup application logging
    
    Args:
        debug: Enable debug logging
    """
    # Remove default logger
    logger.remove()
    
    # Console logging
    log_level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # File logging
    logger.add(
        "logs/eol_tester.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="EOL Tester Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Interactive CLI mode
  python main.py --config config.json    # Use custom configuration
  python main.py --debug                 # Enable debug logging
  python main.py --generate-config dev   # Generate development config
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--generate-config",
        choices=["dev", "prod", "test"],
        help="Generate configuration file and exit"
    )
    
    parser.add_argument(
        "--config-output",
        type=str,
        default="config.json",
        help="Output path for generated configuration (default: config.json)"
    )
    
    return parser


async def main() -> None:
    """Main application entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    try:
        # Generate configuration if requested
        if args.generate_config:
            if args.generate_config == "dev":
                config = ApplicationFactory.create_development_configuration()
            elif args.generate_config == "prod":
                config = ApplicationFactory.create_production_configuration()
            else:  # test
                config = ApplicationFactory.create_test_configuration()
            
            ApplicationFactory.save_configuration(config, args.config_output)
            print(f"Configuration saved to {args.config_output}")
            return
        
        # Create application
        container = ApplicationFactory.create_application(config_file=args.config)
        
        # Run application
        app = EOLTesterApplication(container)
        await app.run_cli_interactive()
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Run application
    asyncio.run(main())