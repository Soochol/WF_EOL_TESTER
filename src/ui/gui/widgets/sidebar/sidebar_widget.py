"""
Sidebar Widget

Main sidebar widget containing navigation menu and system information.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from .navigation_menu import NavigationMenu


class SidebarWidget(QWidget):
    """
    Main sidebar widget for the application.

    Contains navigation menu and system information display.
    """

    page_changed = Signal(str)  # Forwards navigation signals
    settings_clicked = Signal()  # Forwards settings button clicks
    collapse_toggled = Signal(bool)  # Emits collapse state

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.is_collapsed = False
        self.expanded_width = 220
        self.collapsed_width = 70
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the sidebar UI with collapse toggle"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Collapse toggle button
        self.toggle_button = self._create_toggle_button()
        layout.addWidget(self.toggle_button)

        # Navigation menu
        self.navigation_menu = NavigationMenu()
        self.navigation_menu.page_changed.connect(self.page_changed.emit)
        self.navigation_menu.settings_clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.navigation_menu)

        # Add stretcher to push navigation menu to top
        stretcher = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(stretcher)

        # Apply sidebar styling
        self.setStyleSheet(self._get_sidebar_style())
        # Set explicit fixed size
        self.setFixedWidth(self.expanded_width)
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)

        # Set size policy: fixed width, expanding height
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def _create_toggle_button(self) -> QPushButton:
        """Create sidebar collapse toggle button"""
        btn = QPushButton("☰")
        btn.setToolTip("Collapse/Expand Sidebar")
        btn.setFixedHeight(45)
        btn.clicked.connect(self.toggle_collapse)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                color: #888888;
                font-size: 20px;
                padding: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                color: #cccccc;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """)
        return btn

    def toggle_collapse(self) -> None:
        """Toggle sidebar collapse state (icon-only ↔ icon+text)"""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve

        self.is_collapsed = not self.is_collapsed
        target_width = self.collapsed_width if self.is_collapsed else self.expanded_width

        # Toggle navigation menu collapse/expand
        if hasattr(self, 'navigation_menu'):
            self.navigation_menu.toggle_collapse()

        # Animate width change
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

        # Update fixed width constraints
        self.setFixedWidth(target_width)
        self.setMaximumWidth(target_width)

        # Update toggle button icon and tooltip
        if self.is_collapsed:
            self.toggle_button.setText("→")
            self.toggle_button.setToolTip("Expand Sidebar (Show Text)")
        else:
            self.toggle_button.setText("☰")
            self.toggle_button.setToolTip("Collapse Sidebar (Icon Only)")

        # Emit signal
        self.collapse_toggled.emit(self.is_collapsed)


    def _get_sidebar_style(self) -> str:
        """Get sidebar stylesheet"""
        return """
        SidebarWidget {
            background-color: #2d2d2d;
            border-right: 1px solid #404040;
        }
        """

    def set_current_page(self, page_id: str) -> None:
        """Set the current page"""
        self.navigation_menu.set_current_page(page_id)

    def set_statistics_submenu_visible(self, visible: bool) -> None:
        """Show or hide the statistics submenu (deprecated - no longer used)"""
        # Statistics now uses internal tabs instead of submenu
        pass

