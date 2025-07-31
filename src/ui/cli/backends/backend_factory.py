"""
Input Backend Factory

Factory for creating the appropriate input backend based on availability.
"""

from ..input_protocols import InputBackend
from .basic_backend import BasicInputBackend


def create_input_backend() -> InputBackend:
    """
    Create the best available input backend.

    Returns:
        InputBackend: prompt_toolkit backend if available, otherwise basic backend
    """
    # Try to create prompt_toolkit backend first
    try:
        from .prompt_toolkit_backend import PromptToolkitInputBackend

        backend = PromptToolkitInputBackend()
        if backend.is_available:
            return backend
    except ImportError:
        pass

    # Fall back to basic backend
    return BasicInputBackend()


def is_prompt_toolkit_available() -> bool:
    """Check if prompt_toolkit is available"""
    try:
        from .prompt_toolkit_backend import PromptToolkitInputBackend

        return PromptToolkitInputBackend().is_available
    except ImportError:
        return False
