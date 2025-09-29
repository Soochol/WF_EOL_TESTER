"""
Test Control Widget

Refactored test control page with modular architecture.
Imports the new modular TestControlWidget implementation.
"""

# Local folder imports
# Re-export the refactored TestControlWidget from the new modular structure
from .test_control.test_control_widget import TestControlWidget


__all__ = ["TestControlWidget"]

# This file now imports from the refactored modular structure
# All functionality has been moved to the test_control package
