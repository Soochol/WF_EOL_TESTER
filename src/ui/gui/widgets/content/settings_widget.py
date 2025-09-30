"""
Settings Widget - Refactored Entry Point

This file now uses the new modular settings architecture.
The original 1,419-line monolithic implementation has been replaced
with a clean, modular structure for better maintainability.

Architecture:
- Core logic separated into core/ module
- Widgets organized in widgets/ module
- Editors specialized in widgets/editors/
- Utilities extracted to utils/ module

Migration from 1,419 lines to ~50 lines with improved:
- Separation of concerns
- Code reusability
- Maintainability
- Type safety
- Error handling
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtWidgets import QWidget

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.services.gui_state_manager import GUIStateManager

# Local folder imports
# Import the new modular settings widget
from .settings import SettingsWidget as ModularSettingsWidget


class SettingsWidget(ModularSettingsWidget):
    """
    Settings widget using the new modular architecture.

    This class maintains compatibility with the existing interface
    while using the new modular structure underneath.
    """

    def __init__(self, parent: Optional[QWidget] = None, container=None, state_manager=None):
        """
        Initialize the settings widget.

        Args:
            parent: Parent widget
            container: Dependency injection container
            state_manager: GUI state manager
        """
        super().__init__(parent, container=container, state_manager=state_manager)

        # Maintain compatibility with existing container integration
        self._container: Optional[SimpleReloadableContainer] = container
        self._state_manager: Optional[GUIStateManager] = state_manager

        # Connect to existing signals if needed
        self.settings_changed.connect(self._handle_settings_change)

    def set_container(self, container: SimpleReloadableContainer) -> None:
        """
        Set the dependency injection container.

        Args:
            container: The container instance
        """
        self._container = container

    def set_state_manager(self, state_manager: GUIStateManager) -> None:
        """
        Set the GUI state manager.

        Args:
            state_manager: The state manager instance
        """
        self._state_manager = state_manager

    def _handle_settings_change(self) -> None:
        """Handle settings changes for container integration"""
        if self._container:
            try:
                # Trigger container reload if configuration changed
                self._container.reload_configuration()
            except Exception as e:
                print(f"Error reloading container configuration: {e}")


# Legacy compatibility exports
__all__ = ["SettingsWidget"]
