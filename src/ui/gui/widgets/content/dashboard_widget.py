"""
Dashboard Widget

Modern dashboard with Material Design 3 styling.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtWidgets import QWidget

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.content.modern_dashboard_widget import ModernDashboardWidget


class DashboardWidget(ModernDashboardWidget):
    """
    Modern dashboard widget wrapper for backward compatibility.

    Features:
    - Beautiful card-based dashboard display
    - Statistics summary cards (Total/Pass/Fail)
    - Test progress tracking
    - Recent results table
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
        layout_mode: str = "default",
        theme: str = "dark",
    ):
        # Simply delegate to ModernDashboardWidget (ignore unused params)
        super().__init__(container, state_manager, parent)
