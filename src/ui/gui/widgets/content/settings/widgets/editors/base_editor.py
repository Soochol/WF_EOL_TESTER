"""
Base editor widget class.

Provides common functionality for all configuration value editors.
Implements VS Code-style save behavior:
- Boolean/Combo: Save immediately on change
- Text/Numeric: Save on focus lost or window close
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

    # Override in subclasses: True for immediate save (Boolean, Combo)
    # False for deferred save on focus lost (Text, Numeric)
    IMMEDIATE_SAVE: bool = False

    def __init__(
        self,
        config_value: ConfigValue,
        value_changed_callback: Callable[[Any], None],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.config_value = config_value
        self.value_changed_callback = value_changed_callback
        self._has_pending_changes: bool = False
        self._original_value: Any = config_value.value
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
        """Handle value change - immediate or deferred based on IMMEDIATE_SAVE"""
        new_value = self.get_value()

        if self.IMMEDIATE_SAVE:
            # Boolean/Combo: Save immediately
            self.value_changed_callback(new_value)
            self._original_value = new_value
            self._has_pending_changes = False
        else:
            # Text/Numeric: Mark as pending, save on focus lost
            self._has_pending_changes = (new_value != self._original_value)

    def commit_pending_changes(self) -> bool:
        """
        Commit pending changes (called on focus lost or window close).

        Returns:
            True if changes were committed, False if no pending changes
        """
        if self._has_pending_changes:
            new_value = self.get_value()
            self.value_changed_callback(new_value)
            self._original_value = new_value
            self._has_pending_changes = False
            return True
        return False

    def has_pending_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        return self._has_pending_changes

    def discard_pending_changes(self) -> None:
        """Discard pending changes and restore original value"""
        if self._has_pending_changes:
            self.set_value(self._original_value)
            self._has_pending_changes = False
