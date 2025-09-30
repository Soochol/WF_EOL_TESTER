"""
Base editor widget class.

Provides common functionality for all configuration value editors.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

from ...core import ConfigValue


class BaseEditorMeta(type(QWidget), ABCMeta):
    """Metaclass to resolve conflicts between QWidget and ABC metaclasses"""
    pass


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
        pass

    @abstractmethod
    def connect_signals(self) -> None:
        """Connect signals for value changes"""
        pass

    @abstractmethod
    def get_value(self) -> Any:
        """Get the current value from the editor"""
        pass

    @abstractmethod
    def set_value(self, value: Any) -> None:
        """Set the value in the editor"""
        pass

    def on_value_changed(self) -> None:
        """Handle value change and emit signal"""
        new_value = self.get_value()
        self.value_changed_callback(new_value)