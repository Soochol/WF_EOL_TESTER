"""CLI Interfaces Package

Defines abstract base classes (interfaces) for CLI components to enable
dependency injection, improve testability, and support flexible component
substitution following SOLID principles.

Interfaces:
- ISessionManager: Session lifecycle management contract
- IMenuSystem: Menu display and navigation contract
- IInputValidator: Input validation contract
- ITestExecutor: Test execution coordination contract
- ICLIApplication: Main application contract
- IFormatter: UI formatting contract
"""

# Local folder imports
from .application_interface import ICLIApplication
from .execution_interface import ITestExecutor
from .formatter_interface import IFormatter
from .menu_interface import IMenuSystem
from .session_interface import ISessionManager
from .validation_interface import IInputValidator


__all__ = [
    "ICLIApplication",
    "ITestExecutor",
    "IFormatter",
    "IMenuSystem",
    "ISessionManager",
    "IInputValidator",
]
