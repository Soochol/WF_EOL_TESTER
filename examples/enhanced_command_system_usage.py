#!/usr/bin/env python3
"""Enhanced Command System Usage Example

Demonstrates how to use the new enhanced command system with dependency
injection, middleware pipeline, and command registry.

This example shows:
1. Setting up the dependency injection container
2. Creating and configuring middleware
3. Registering commands with the enhanced registry
4. Creating a command parser with middleware pipeline
5. Executing commands through the enhanced system
"""

import asyncio
from typing import Optional

# Import the enhanced command system
from ui.cli.commands import (
    # Core interfaces and components
    ICommand,
    ICommandExecutionContext,
    CommandMetadata,
    CommandResult,
    BaseCommand,
    EnhancedCommandParser,
    CommandExecutionContext,
    EnhancedCommandRegistry,
    CommandFactory,
    
    # Middleware
    AuthenticationMiddleware,
    ValidationMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    
    # Enhanced command handlers
    TestCommandHandler,
)

# Import dependency injection
from ui.cli.container.dependency_container import DependencyContainer
from ui.cli.interfaces.formatter_interface import IFormatter
from ui.cli.interfaces.validation_interface import IInputValidator

# Import existing implementations for services
from ui.cli.implementation.formatter import RichFormatter
from ui.cli.implementation.validation import SecurityInputValidator


class ExampleCommand(BaseCommand):
    """Example command showing the enhanced command system features."""
    
    def __init__(self, formatter: Optional[IFormatter] = None):
        metadata = CommandMetadata(
            name="example",
            description="Example command demonstrating enhanced features",
            category="demo",
            aliases=["ex", "demo"],
            examples=[
                "/example - Show basic example",
                "/example advanced - Show advanced features",
            ],
            help_text="This command demonstrates the enhanced command system "
                     "with dependency injection and middleware support.",
            version="1.0.0",
            author="Enhanced Command System",
        )
        
        super().__init__(metadata)
        self._formatter = formatter
    
    async def execute(self, args: list[str], context: ICommandExecutionContext) -> CommandResult:
        """Execute the example command."""
        # Get formatter from context if not provided
        if not self._formatter:
            try:
                self._formatter = context.get_service(IFormatter)
            except ValueError:
                pass  # Use basic output
        
        if not args:
            message = (
                "Enhanced Command System Demo\n\n"
                "Features demonstrated:\n"
                "• Dependency injection integration\n"
                "• Middleware pipeline processing\n"
                "• Enhanced validation and error handling\n"
                "• Rich UI formatting support\n"
                "• Comprehensive logging and metrics\n\n"
                "Try: /example advanced"
            )
        elif args[0].lower() == "advanced":
            user_id = context.user_id or "anonymous"
            session_data = context.session_data
            config = context.configuration
            
            message = (
                f"Advanced Features Demo\n\n"
                f"Execution Context:\n"
                f"• User ID: {user_id}\n"
                f"• Session Data Keys: {list(session_data.keys())}\n"
                f"• Configuration Keys: {list(config.keys())}\n\n"
                f"Middleware Processing:\n"
                f"• Authentication: Validated user access\n"
                f"• Validation: Checked input security\n"
                f"• Logging: Recorded execution metrics\n"
                f"• Error Handling: Provided recovery guidance\n"
            )
        else:
            return CommandResult.error(
                f"Unknown subcommand: {args[0]}",
                error_details={"valid_subcommands": ["advanced"]}
            )
        
        # Use formatter if available
        if self._formatter:
            self._formatter.print_message(message, "info", "Command System Demo")
        else:
            print(message)
        
        return CommandResult.success(
            "Example command executed successfully",
            data={"mode": "advanced" if args and args[0].lower() == "advanced" else "basic"}
        )
    
    def get_subcommands(self) -> dict[str, str]:
        return {
            "": "Show basic command system features",
            "advanced": "Show advanced features with context information",
        }


async def setup_enhanced_command_system():
    """Set up the enhanced command system with all components."""
    
    print("Setting up Enhanced Command System...")
    
    # 1. Create dependency injection container
    container = DependencyContainer()
    
    # 2. Register services with the container
    container.register_singleton(IFormatter, RichFormatter)
    container.register_singleton(IInputValidator, SecurityInputValidator)
    
    # 3. Create command factory
    factory = CommandFactory(container)
    
    # 4. Create command registry
    registry = EnhancedCommandRegistry()
    
    # 5. Create and register middleware (in priority order)
    auth_middleware = AuthenticationMiddleware(
        require_authentication=False,  # Disabled for demo
        guest_allowed_commands={"example", "help", "exit"}
    )
    
    validation_middleware = ValidationMiddleware(enable_strict_validation=True)
    
    logging_middleware = LoggingMiddleware(
        log_level="INFO",
        include_args=True,
        include_performance=True,
        include_user_context=True
    )
    
    error_middleware = ErrorHandlingMiddleware(
        include_stack_trace=False,
        enable_recovery_suggestions=True
    )
    
    # Register global middleware
    registry.register_middleware(auth_middleware)
    registry.register_middleware(validation_middleware)
    registry.register_middleware(logging_middleware)
    registry.register_middleware(error_middleware)
    
    # 6. Create and register commands
    example_command = factory.create_command(ExampleCommand)
    registry.register_command(example_command)
    
    # Create test command handler with DI
    test_command = factory.create_command(TestCommandHandler)
    registry.register_command(test_command)
    
    # 7. Create enhanced command parser with registry
    parser = EnhancedCommandParser()
    
    # Register commands with parser
    for command_name, command in registry.get_all_commands().items():
        middleware = registry.get_middleware_for_command(command_name)
        parser.register_command(command, middleware)
    
    # Register global middleware with parser
    for middleware in [auth_middleware, validation_middleware, logging_middleware, error_middleware]:
        parser.register_global_middleware(middleware)
    
    print(f"Enhanced Command System Ready!")
    print(f"• Commands registered: {len(registry.get_all_commands())}")
    print(f"• Middleware registered: {registry.get_registry_statistics()['total_global_middleware']}")
    print(f"• Categories: {', '.join(registry.get_all_categories())}")
    
    return parser, container, registry


async def demo_command_execution(parser: EnhancedCommandParser, container: DependencyContainer):
    """Demonstrate command execution with the enhanced system."""
    
    print("\n" + "=" * 60)
    print("ENHANCED COMMAND SYSTEM DEMO")
    print("=" * 60)
    
    # Create execution context
    context = CommandExecutionContext(
        container=container,
        user_id="demo_user",
        session_data={"session_id": "demo_session_123", "role": "user"},
        configuration={"demo_mode": True, "log_level": "INFO"}
    )
    
    # Demo commands to execute
    demo_commands = [
        "/example",
        "/example advanced",
        "/test help",  # This will show help for test command
        "/invalid_command",  # This will demonstrate error handling
        "/example invalid_sub",  # This will demonstrate validation
    ]
    
    for i, command_input in enumerate(demo_commands, 1):
        print(f"\n[{i}] Executing: {command_input}")
        print("-" * 40)
        
        # Execute command through enhanced parser
        result = await parser.execute_command(command_input, context)
        
        # Display result
        status_icon = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }.get(result.status.value, "❓")
        
        print(f"Result: {status_icon} {result.status.value.upper()}")
        print(f"Message: {result.message}")
        
        if result.execution_time_ms:
            print(f"Execution Time: {result.execution_time_ms:.2f}ms")
        
        if result.data:
            print(f"Data: {result.data}")
        
        if result.error_details:
            print(f"Error Details: {result.error_details}")
        
        if result.middleware_data:
            print(f"Middleware Data: {result.middleware_data}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


async def main():
    """Main demo function."""
    try:
        # Set up the enhanced command system
        parser, container, registry = await setup_enhanced_command_system()
        
        # Run the demo
        await demo_command_execution(parser, container)
        
        # Show registry statistics
        stats = registry.get_registry_statistics()
        print(f"\nRegistry Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
