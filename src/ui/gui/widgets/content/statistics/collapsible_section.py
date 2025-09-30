"""Collapsible Section Widget

Provides expandable/collapsible section for organizing statistics panels.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CollapsibleSection(QGroupBox):
    """Collapsible section widget with expand/collapse functionality.

    Features:
    - Toggle button for expand/collapse
    - Dark theme styling
    - Smooth show/hide transitions
    - Optional initial collapsed state
    """

    # Signals
    toggled = Signal(bool)  # Emitted when section is expanded (True) or collapsed (False)

    def __init__(
        self,
        title: str,
        content_widget: QWidget,
        initially_collapsed: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """Initialize collapsible section.

        Args:
            title: Section title
            content_widget: Widget to show/hide when toggling
            initially_collapsed: If True, section starts collapsed
            parent: Parent widget
        """
        super().__init__(parent)
        self.content_widget = content_widget
        self.is_collapsed = initially_collapsed

        self.setup_ui(title)

        # Set initial state
        if initially_collapsed:
            self.content_widget.hide()
            self.toggle_button.setText("▶ Expand")
        else:
            self.content_widget.show()
            self.toggle_button.setText("▼ Collapse")

    def setup_ui(self, title: str) -> None:
        """Setup the collapsible section UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 20, 12, 12)

        # Toggle button
        self.toggle_button = QPushButton("▼ Collapse")
        self.toggle_button.setObjectName("toggle_button")
        self.toggle_button.setMaximumWidth(120)
        self.toggle_button.clicked.connect(self.toggle)

        # Set button font
        button_font = QFont()
        button_font.setPointSize(9)
        button_font.setBold(True)
        self.toggle_button.setFont(button_font)

        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_widget)

        # Set title
        self.setTitle(title)

        # Apply styling
        self.apply_styling()

    def apply_styling(self) -> None:
        """Apply dark theme styling to the section."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton#toggle_button {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton#toggle_button:hover {
                background-color: #505050;
                border-color: #0078d4;
            }
            QPushButton#toggle_button:pressed {
                background-color: #0078d4;
            }
        """)

    def toggle(self) -> None:
        """Toggle the section expanded/collapsed state."""
        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            self.content_widget.hide()
            self.toggle_button.setText("▶ Expand")
        else:
            self.content_widget.show()
            self.toggle_button.setText("▼ Collapse")

        # Emit signal
        self.toggled.emit(not self.is_collapsed)

    def expand(self) -> None:
        """Programmatically expand the section."""
        if self.is_collapsed:
            self.toggle()

    def collapse(self) -> None:
        """Programmatically collapse the section."""
        if not self.is_collapsed:
            self.toggle()

    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed state.

        Args:
            collapsed: True to collapse, False to expand
        """
        if collapsed != self.is_collapsed:
            self.toggle()