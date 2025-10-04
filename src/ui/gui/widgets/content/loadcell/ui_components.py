"""Loadcell UI Components - Modern Design

Factory and builder classes for creating modern loadcell control UI components.
Uses Material Design 3 components for consistent styling.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtWidgets import (
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
# Local folder imports - use robot's modern components
from ..robot.modern_components import ModernButton, ModernCard, StatusPill
from .event_handlers import LoadcellEventHandlers
from .state_manager import LoadcellControlState


class StatusDisplayGroup:
    """Status display group with StatusPills"""

    def __init__(self, state: LoadcellControlState):
        self.state = state
        self.connection_pill: Optional[StatusPill] = None
        self.force_pill: Optional[StatusPill] = None
        self.hold_pill: Optional[StatusPill] = None

    def create(self) -> ModernCard:
        """Create status display card with pills"""
        card = ModernCard("📊 Loadcell Status")

        # Pills layout
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(12)

        # Connection status pill
        self.connection_pill = StatusPill("Connection:")
        self.connection_pill.set_status("Disconnected", "#FF5722")
        pills_layout.addWidget(self.connection_pill)

        # Force status pill
        self.force_pill = StatusPill("Force:")
        self.force_pill.set_status("0.000 N", "#cccccc")
        pills_layout.addWidget(self.force_pill)

        # Hold status pill
        self.hold_pill = StatusPill("Hold:")
        self.hold_pill.set_status("Released", "#FFC107")
        pills_layout.addWidget(self.hold_pill)

        pills_widget = QWidget()
        pills_widget.setLayout(pills_layout)
        card.add_widget(pills_widget)

        # Connect to state changes
        self.state.connection_changed.connect(self._on_connection_changed)
        self.state.force_changed.connect(self._on_force_changed)
        self.state.hold_changed.connect(self._on_hold_changed)

        return card

    def _on_connection_changed(self, connected: bool) -> None:
        """Update connection status pill"""
        if self.connection_pill:
            if connected:
                self.connection_pill.set_status("Connected", "#00D9A5")
            else:
                self.connection_pill.set_status("Disconnected", "#FF5722")

    def _on_force_changed(self, force: float) -> None:
        """Update force pill"""
        if self.force_pill:
            self.force_pill.set_status(f"{force:.3f} N", "#2196F3")

    def _on_hold_changed(self, held: bool) -> None:
        """Update hold status pill"""
        if self.hold_pill:
            if held:
                self.hold_pill.set_status("Held", "#00D9A5")
            else:
                self.hold_pill.set_status("Released", "#FFC107")


class ConnectionGroup:
    """Connection control group"""

    def __init__(self, event_handlers: LoadcellEventHandlers):
        self.event_handlers = event_handlers
        self.connect_btn: Optional[QPushButton] = None
        self.disconnect_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create connection control card"""
        card = ModernCard("🔌 Connection")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)

        self.connect_btn = ModernButton("Connect", "play", "success")
        self.disconnect_btn = ModernButton("Disconnect", "stop", "danger")

        self.connect_btn.clicked.connect(self.event_handlers.on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.event_handlers.on_disconnect_clicked)

        main_layout.addWidget(self.connect_btn)
        main_layout.addWidget(self.disconnect_btn)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references for state management"""
        return {
            "connect": self.connect_btn,
            "disconnect": self.disconnect_btn,
        }


class MeasurementGroup:
    """Measurement control group"""

    def __init__(self, event_handlers: LoadcellEventHandlers):
        self.event_handlers = event_handlers
        self.zero_calibration_btn: Optional[QPushButton] = None
        self.read_force_btn: Optional[QPushButton] = None
        self.read_peak_force_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create measurement control card"""
        card = ModernCard("📏 Measurement")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Zero calibration button
        self.zero_calibration_btn = ModernButton("Zero Calibration", "refresh-cw", "primary")
        self.zero_calibration_btn.clicked.connect(self.event_handlers.on_zero_calibration_clicked)
        main_layout.addWidget(self.zero_calibration_btn)

        # Read force buttons
        read_layout = QHBoxLayout()
        read_layout.setSpacing(8)

        self.read_force_btn = ModernButton("Read Force", "activity", "primary")
        self.read_peak_force_btn = ModernButton("Peak Force", "trending-up", "success")

        self.read_force_btn.clicked.connect(self.event_handlers.on_read_force_clicked)
        self.read_peak_force_btn.clicked.connect(
            lambda: self.event_handlers.on_read_peak_force_clicked(1000, 200)
        )

        read_layout.addWidget(self.read_force_btn)
        read_layout.addWidget(self.read_peak_force_btn)
        main_layout.addLayout(read_layout)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references for state management"""
        return {
            "zero_calibration": self.zero_calibration_btn,
            "read_force": self.read_force_btn,
            "read_peak_force": self.read_peak_force_btn,
        }


class HoldControlGroup:
    """Hold control group"""

    def __init__(self, event_handlers: LoadcellEventHandlers):
        self.event_handlers = event_handlers
        self.hold_btn: Optional[QPushButton] = None
        self.hold_release_btn: Optional[QPushButton] = None

    def create(self) -> ModernCard:
        """Create hold control card"""
        card = ModernCard("🔒 Hold Control")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)

        self.hold_btn = ModernButton("Hold", "lock", "warning")
        self.hold_release_btn = ModernButton("Release", "unlock", "success")

        self.hold_btn.clicked.connect(self.event_handlers.on_hold_clicked)
        self.hold_release_btn.clicked.connect(self.event_handlers.on_hold_release_clicked)

        main_layout.addWidget(self.hold_btn)
        main_layout.addWidget(self.hold_release_btn)

        container = QWidget()
        container.setLayout(main_layout)
        card.add_widget(container)

        return card

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references for state management"""
        return {
            "hold": self.hold_btn,
            "hold_release": self.hold_release_btn,
        }


def create_modern_progress_bar() -> QProgressBar:
    """Create a modern styled progress bar"""
    progress = QProgressBar()
    progress.setRange(0, 0)  # Indeterminate progress
    progress.setTextVisible(False)
    progress.setFixedHeight(4)
    progress.setStyleSheet(
        """
        QProgressBar {
            border: none;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 2px;
        }
    """
    )
    return progress
