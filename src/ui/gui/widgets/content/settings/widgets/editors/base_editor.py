"""
Base editor widget class.

Provides common functionality for all configuration value editors.
"""

# Standard library imports
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional

# Third-party imports
from PySide6.QtWidgets import QWidget

# Local folder imports
from ...core import ConfigValue


class BaseEditorMeta(ABCMeta, type(QWidget)):  # type: ignore[misc]
    """Metaclass to resolve conflicts between QWidget and ABC metaclasses"""


class BaseEditorWidget(QWidget, metaclass=BaseEditorMeta):
    """Base class for configuration value editors"""

    def __init__(
        self,
        config_value: ConfigValue,
        value_changed_callback: Callable[[Any], None],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.config_value = config_value
        self.value_changed_callback = value_changed_callback
        self.setup_ui()
        self.connect_signals()

    @abstractmethod
    def setup_ui(self) -> None:
        """Setup the editor UI"""
        ...

    @abstractmethod
    def connect_signals(self) -> None:
        """Connect signals for value changes"""
        ...

    @abstractmethod
    def get_value(self) -> Any:
        """Get the current value from the editor"""
        ...

    @abstractmethod
    def set_value(self, value: Any) -> None:
        """Set the value in the editor"""
        ...

    def on_value_changed(self) -> None:
        """Handle value change and emit signal"""
        new_value = self.get_value()
        self.value_changed_callback(new_value)
