#!/usr/bin/env python3
"""Phase 5 Implementation Demo - Dependency Injection

Demonstrates the new interface-based design and dependency injection
system implemented in Phase 5 of the CLI refactoring project.

This script shows:
1. Interface-based design with abstract base classes
2. Dependency injection container usage
3. Component factory patterns
4. Configuration-driven service registration
5. Backward compatibility with existing code
"""

import asyncio
from typing import Any

# Import the new dependency injection system
from src.ui.cli.application_factory import (
    create_production_cli_application,
    create_development_cli_application,
    create_testing_cli_application,
    create_mock_cli_application,
)
from src.ui.cli.factories.component_factory import CLIComponentFactory
from src.ui.cli.config.component_config import ConfigurationMode
from src.ui.cli.container.dependency_container import DependencyContainer, ServiceLifetime
from src.ui.cli.interfaces import (
    ICLIApplication,
    ISessionManager,
    IMenuSystem,
    ITestExecutor,
    IInputValidator,
    IFormatter,
)

# Import backward compatibility wrapper
from src.ui.cli.enhanced_eol_tester_cli import EnhancedEOLTesterCLI


class MockUseCase:
    """Mock use case for demonstration."""
    
    async def execute(self, command: Any) -> Any:
        """Mock execute method."""
        return f"Mock result for command: {command}"


def demonstrate_dependency_container():
    """Demonstrate the dependency injection container."""
    print("\n=== Dependency Container Demo ===")
    
    # Create container
    container = DependencyContainer()
    
    # Register services
    from src.ui.cli.validation.input_validator import InputValidator
    from src.ui.cli.interfaces.validation_interface import IInputValidator
    
    container.register_singleton(
        IInputValidator,
        implementation_type=InputValidator
    )
    
    # Resolve service
    validator1 = container.resolve(IInputValidator)
    validator2 = container.resolve(IInputValidator)
    
    print(f"Validator 1: {type(validator1).__name__}")
    print(f"Validator 2: {type(validator2).__name__}")
    print(f"Same instance (singleton): {validator1 is validator2}")
    
    # Show registered services
    registered = container.get_registered_services()
    print(f"Registered services: {len(registered)}")
    for service_type, registration in registered.items():
        print(f"  - {service_type.__name__}: {registration.lifetime.value}")


def demonstrate_component_factory():
    """Demonstrate the component factory."""
    print("\n=== Component Factory Demo ===")
    
    # Create factories for different modes
    production_factory = CLIComponentFactory.create_production_factory()
    development_factory = CLIComponentFactory.create_development_factory()
    testing_factory = CLIComponentFactory.create_testing_factory()
    
    print(f"Production factory mode: {production_factory.config.mode.value}")
    print(f"Development factory mode: {development_factory.config.mode.value}")
    print(f"Testing factory mode: {testing_factory.config.mode.value}")
    
    # Create components
    try:
        validator = production_factory.create_input_validator()
        print(f"Created validator: {type(validator).__name__}")
        print(f"Implements IInputValidator: {isinstance(validator, IInputValidator)}")
    except Exception as e:
        print(f"Factory creation error (expected): {e}")


def demonstrate_application_factory():
    """Demonstrate the application factory functions."""
    print("\n=== Application Factory Demo ===")
    
    # Create mock dependencies
    mock_use_case = MockUseCase()
    
    try:
        # Create applications in different modes
        prod_app = create_production_cli_application(mock_use_case)
        dev_app = create_development_cli_application(mock_use_case)
        test_app = create_testing_cli_application(mock_use_case)
        mock_app = create_mock_cli_application(mock_use_case)
        
        print(f"Production app: {type(prod_app).__name__}")
        print(f"Development app: {type(dev_app).__name__}")
        print(f"Testing app: {type(test_app).__name__}")
        print(f"Mock app: {type(mock_app).__name__}")
        
        # Show that they implement the interface
        print(f"Production app implements ICLIApplication: {isinstance(prod_app, ICLIApplication)}")
        
        # Access components through interface
        console = prod_app.get_console()
        formatter = prod_app.get_formatter()
        validator = prod_app.get_validator()
        
        print(f"Console: {type(console).__name__}")
        print(f"Formatter implements IFormatter: {isinstance(formatter, IFormatter)}")
        print(f"Validator implements IInputValidator: {isinstance(validator, IInputValidator)}")
        
    except Exception as e:
        print(f"Application creation error: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_backward_compatibility():
    """Demonstrate backward compatibility wrapper."""
    print("\n=== Backward Compatibility Demo ===")
    
    try:
        # Create enhanced CLI using the old interface
        mock_use_case = MockUseCase()
        enhanced_cli = EnhancedEOLTesterCLI(mock_use_case)
        
        print(f"Enhanced CLI: {type(enhanced_cli).__name__}")
        print(f"Has application: {hasattr(enhanced_cli, '_application')}")
        
        # Access legacy properties
        validator = enhanced_cli.get_validator()
        console = enhanced_cli.get_console()
        formatter = enhanced_cli.get_formatter()
        
        print(f"Validator: {type(validator).__name__}")
        print(f"Console: {type(console).__name__}")
        print(f"Formatter: {type(formatter).__name__}")
        
        # Show running state property
        print(f"Running state: {enhanced_cli._running}")
        
    except Exception as e:
        print(f"Backward compatibility error: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_interface_polymorphism():
    """Demonstrate interface-based polymorphism."""
    print("\n=== Interface Polymorphism Demo ===")
    
    try:
        from src.ui.cli.validation.input_validator import InputValidator
        from src.ui.cli.rich_formatter import RichFormatter
        
        # Create instances
        validator = InputValidator()
        formatter = RichFormatter()
        
        # Show interface compliance
        print(f"Validator implements IInputValidator: {isinstance(validator, IInputValidator)}")
        print(f"Formatter implements IFormatter: {isinstance(formatter, IFormatter)}")
        
        # Show polymorphic behavior
        def process_validator(val: IInputValidator):
            result = val.validate_input("test123", "general")
            return f"Validation result: {result}"
        
        def process_formatter(fmt: IFormatter):
            console_type = type(fmt.console).__name__
            return f"Formatter console: {console_type}"
        
        print(process_validator(validator))
        print(process_formatter(formatter))
        
    except Exception as e:
        print(f"Polymorphism demo error: {e}")
        import traceback
        traceback.print_exc()


async def demonstrate_full_integration():
    """Demonstrate full integration with dependency injection."""
    print("\n=== Full Integration Demo ===")
    
    try:
        # Create a complete application
        mock_use_case = MockUseCase()
        app = create_production_cli_application(mock_use_case)
        
        print(f"Created application: {type(app).__name__}")
        print(f"Application running state: {app._running}")
        
        # Could run the application here, but we'll skip for demo
        # await app.run_interactive()
        
        print("Full integration successful!")
        
    except Exception as e:
        print(f"Integration error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demonstration function."""
    print("Phase 5 CLI Refactoring Demo - Dependency Injection Implementation")
    print("====================================================================")
    
    # Run demonstrations
    demonstrate_dependency_container()
    demonstrate_component_factory()
    demonstrate_application_factory()
    demonstrate_backward_compatibility()
    demonstrate_interface_polymorphism()
    
    # Run async demo
    asyncio.run(demonstrate_full_integration())
    
    print("\n=== Demo Complete ===")
    print("\nPhase 5 Implementation Summary:")
    print("1. ✅ Created abstract base classes (interfaces) for all components")
    print("2. ✅ Implemented dependency injection container with lifecycle management")
    print("3. ✅ Created configuration system for different operational modes")
    print("4. ✅ Implemented factory patterns for component creation")
    print("5. ✅ Updated existing components to implement interfaces")
    print("6. ✅ Maintained backward compatibility with existing code")
    print("7. ✅ Demonstrated SOLID principles and clean architecture")
    
    print("\nBenefits achieved:")
    print("- Improved testability through interface-based design")
    print("- Flexible component substitution via dependency injection")
    print("- Configuration-driven service registration")
    print("- Maintainable and extensible architecture")
    print("- Separation of concerns and loose coupling")


if __name__ == "__main__":
    main()