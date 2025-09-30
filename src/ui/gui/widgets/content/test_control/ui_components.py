"""Test Control UI Components

Factory and builder classes for creating test control UI components.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.icon_manager import get_emoji, get_icon, IconSize
from ui.gui.utils.styling import ThemeManager
from ui.gui.widgets.log_viewer_widget import LogViewerWidget

# Local folder imports
from .event_handlers import TestControlEventHandlers
from .state_manager import TestControlState


class UIComponentFactory:
    """Factory for creating test control UI components"""

    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def create_group_font(self) -> QFont:
        """Create standardized font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def create_button_with_icon(self, text: str, icon_name: str, height: int = 38) -> QPushButton:
        """Create button with icon or emoji fallback"""
        button = QPushButton(text)

        # Try to set icon first
        icon = get_icon(icon_name, IconSize.MEDIUM)
        if not icon.isNull():
            button.setIcon(icon)
        else:
            # Fallback to emoji
            emoji = get_emoji(icon_name)
            if emoji:
                button.setText(f"{emoji} {text}")

        button.setMinimumHeight(height)
        button.setMaximumHeight(height + 10)  # Allow some flexibility
        return button

    def create_emergency_button(self) -> QPushButton:
        """Create emergency stop button with special styling"""
        button = QPushButton("EMERGENCY STOP")
        button.setMinimumHeight(45)
        button.setMaximumHeight(55)  # Allow some flexibility

        # Emergency button specific styling
        emergency_style = f"""
        QPushButton {{
            background-color: {self.theme_manager.COLORS['emergency']};
            color: white;
            font-weight: bold;
            font-size: 16px;
            border: 2px solid {self.theme_manager.COLORS['emergency_hover']};
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {self.theme_manager.COLORS['emergency_hover']};
        }}
        QPushButton:pressed {{
            background-color: {self.theme_manager.COLORS['emergency_pressed']};
        }}
        """
        button.setStyleSheet(emergency_style)
        return button

    def create_progress_bar(self) -> QProgressBar:
        """Create standardized progress bar"""
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        progress_bar.setMinimumHeight(22)
        progress_bar.setMaximumHeight(28)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat("%p% - %v/%m")
        return progress_bar

    def apply_progress_bar_style(
        self, progress_bar: QProgressBar, gradient_colors: str, text_format: str
    ) -> None:
        """Apply dynamic styling to progress bar"""
        style = f"""
        QProgressBar {{
            border: 1px solid {self.theme_manager.COLORS['border_primary']};
            border-radius: 3px;
            background-color: {self.theme_manager.COLORS['background_secondary']};
            color: {self.theme_manager.COLORS['text_primary']};
            text-align: center;
            font-weight: bold;
            font-size: 14px;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, {gradient_colors});
            border-radius: 2px;
        }}
        """
        progress_bar.setStyleSheet(style)
        progress_bar.setFormat(text_format)


class TestSequenceGroup:
    """Test sequence selection group"""

    def __init__(self, factory: UIComponentFactory, event_handlers: TestControlEventHandlers):
        self.factory = factory
        self.event_handlers = event_handlers
        self.sequence_combo: Optional[QComboBox] = None

    def create(self) -> QGroupBox:
        """Create test sequence selection group"""
        from PySide6.QtWidgets import QSizePolicy

        group = QGroupBox("Test Sequence")
        group.setFont(self.factory.create_group_font())
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(group)

        self.sequence_combo = QComboBox()
        self.sequence_combo.addItems(
            [
                "EOL Force Test",
                "Heating Cooling Time Test",
                "Simple MCU Test",
                "Custom Test Sequence",
            ]
        )
        self.sequence_combo.setMinimumHeight(30)
        self.sequence_combo.setMaximumHeight(40)

        # Connect signal
        self.sequence_combo.currentTextChanged.connect(
            lambda: (
                self.event_handlers.handle_sequence_changed(self.sequence_combo)
                if self.sequence_combo
                else None
            )
        )

        layout.addWidget(self.sequence_combo)
        return group


class TestParametersGroup:
    """Test parameters group"""

    def __init__(self, factory: UIComponentFactory, event_handlers: TestControlEventHandlers):
        self.factory = factory
        self.event_handlers = event_handlers
        self.serial_edit: Optional[QLineEdit] = None

    def create(self) -> QGroupBox:
        """Create test parameters group"""
        from PySide6.QtWidgets import QSizePolicy

        group = QGroupBox("Test Parameters")
        group.setFont(self.factory.create_group_font())
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced top margin from 20 to 15

        # Serial Number
        layout.addWidget(QLabel("Serial Number:"))
        self.serial_edit = QLineEdit()
        self.serial_edit.setPlaceholderText("Enter serial number...")
        self.serial_edit.setText("SN123456789")
        self.serial_edit.setMinimumHeight(28)
        self.serial_edit.setMaximumHeight(38)

        # Connect signal
        self.serial_edit.textChanged.connect(
            lambda: (
                self.event_handlers.handle_serial_number_changed(self.serial_edit)
                if self.serial_edit
                else None
            )
        )

        layout.addWidget(self.serial_edit)
        layout.addStretch()

        return group


class TestControlsGroup:
    """Test controls group"""

    def __init__(self, factory: UIComponentFactory, event_handlers: TestControlEventHandlers):
        self.factory = factory
        self.event_handlers = event_handlers
        self.start_btn: Optional[QPushButton] = None
        self.home_btn: Optional[QPushButton] = None
        self.pause_btn: Optional[QPushButton] = None
        self.stop_btn: Optional[QPushButton] = None
        self.emergency_btn: Optional[QPushButton] = None

    def create(self) -> QGroupBox:
        """Create control buttons group"""
        from PySide6.QtWidgets import QSizePolicy

        group = QGroupBox("Test Controls")
        group.setFont(self.factory.create_group_font())
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)  # Reduced from 10 to 8

        # Main control buttons row
        main_controls_layout = QHBoxLayout()
        main_controls_layout.setSpacing(10)

        # Create buttons
        self.start_btn = self.factory.create_button_with_icon("START TEST", "play")
        self.home_btn = self.factory.create_button_with_icon("HOME", "dashboard")
        self.pause_btn = self.factory.create_button_with_icon("PAUSE", "pause")
        self.stop_btn = self.factory.create_button_with_icon("STOP", "stop")

        # Connect signals
        self.start_btn.clicked.connect(self.event_handlers.handle_start_test_clicked)
        self.home_btn.clicked.connect(self.event_handlers.handle_home_button_clicked)
        self.pause_btn.clicked.connect(self.event_handlers.handle_pause_test_clicked)
        self.stop_btn.clicked.connect(self.event_handlers.handle_stop_test_clicked)

        # Add to layout
        main_controls_layout.addWidget(self.start_btn)
        main_controls_layout.addWidget(self.home_btn)
        main_controls_layout.addWidget(self.pause_btn)
        main_controls_layout.addWidget(self.stop_btn)

        layout.addLayout(main_controls_layout)

        # Emergency stop button
        self.emergency_btn = self.factory.create_emergency_button()
        self.emergency_btn.clicked.connect(self.event_handlers.handle_emergency_stop_clicked)
        layout.addWidget(self.emergency_btn)

        return group

    def get_buttons(self) -> Dict[str, Optional[QPushButton]]:
        """Get button references for state management"""
        return {
            "start": self.start_btn,
            "home": self.home_btn,
            "pause": self.pause_btn,
            "stop": self.stop_btn,
            "emergency": self.emergency_btn,
        }


class TestStatusGroup:
    """Test status display group"""

    def __init__(self, factory: UIComponentFactory, state_manager: TestControlState):
        self.factory = factory
        self.state_manager = state_manager
        self.status_icon: Optional[QLabel] = None
        self.status_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None

    def create(self) -> QGroupBox:
        """Create test status display group"""
        from PySide6.QtWidgets import QSizePolicy

        group = QGroupBox("Test Status")
        group.setFont(self.factory.create_group_font())
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced top margin from 20 to 15
        layout.setSpacing(8)  # Reduced from 10 to 8

        # Top row: Status icon and text
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setFont(QFont("", 16))
        self.status_icon.setFixedWidth(30)
        self._update_status_icon("status_ready")
        top_layout.addWidget(self.status_icon)

        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("", 12, QFont.Weight.Bold))
        top_layout.addWidget(self.status_label)

        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Progress bar
        self.progress_bar = self.factory.create_progress_bar()
        layout.addWidget(self.progress_bar)

        # Initialize with default styling
        self._update_progress_bar_style("Ready")

        # Connect to state manager signals
        self.state_manager.status_changed.connect(self._on_status_changed)

        return group

    def _on_status_changed(self, status: str, icon: str, progress: Optional[int]) -> None:
        """Handle status change from state manager"""
        # Update status text and icon
        if self.status_label:
            self.status_label.setText(status)
        self._update_status_icon(icon)

        # Update progress bar
        if self.progress_bar and progress is not None:
            self.progress_bar.setValue(progress)

        # Update styling
        style, is_busy_mode = self.state_manager.get_status_style(status)
        if self.status_label:
            self.status_label.setStyleSheet(style)

        # Set progress bar mode
        if self.progress_bar:
            if is_busy_mode:
                self.progress_bar.setRange(0, 0)  # Busy indicator
            else:
                self.progress_bar.setRange(0, 100)  # Normal mode

                # Auto-set progress for certain states
                if "completed" in status.lower() or "success" in status.lower():
                    if progress is None:
                        self.progress_bar.setValue(100)
                elif (
                    "stopped" in status.lower()
                    or "emergency" in status.lower()
                    or "ready" in status.lower()
                ):
                    if progress is None:
                        self.progress_bar.setValue(0)

        # Update progress bar style
        self._update_progress_bar_style(status)

    def _update_status_icon(self, icon_name: str) -> None:
        """Update status icon using icon manager"""
        if not self.status_icon:
            return

        icon = get_icon(icon_name, IconSize.SMALL)

        if not icon.isNull():
            pixmap = icon.pixmap(16, 16)
            self.status_icon.setPixmap(pixmap)
            self.status_icon.setText("")  # Clear text
        else:
            # Fallback to emoji
            emoji = get_emoji(icon_name)
            if emoji:
                self.status_icon.clear()  # Clear pixmap before setting text
                self.status_icon.setText(emoji)

    def _update_progress_bar_style(self, status: str) -> None:
        """Update progress bar style based on status"""
        if not self.progress_bar:
            return

        gradient_colors, text_format = self.state_manager.get_progress_bar_style(status)
        self.factory.apply_progress_bar_style(self.progress_bar, gradient_colors, text_format)


class TestLogsGroup:
    """Test logs group"""

    def __init__(self, container: ApplicationContainer, state_manager: GUIStateManager):
        self.container = container
        self.state_manager = state_manager
        self.log_viewer: Optional[LogViewerWidget] = None

    def create(self) -> QGroupBox:
        """Create live test logs group"""
        from PySide6.QtWidgets import QSizePolicy

        group = QGroupBox("Live Test Logs")
        group.setFont(QFont("", 14, QFont.Weight.Bold))
        # Remove fixed minimum height - allow flexible sizing
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced top margin from 20 to 15

        # Add log viewer widget
        self.log_viewer = LogViewerWidget(self.container, self.state_manager)
        self.log_viewer.setMinimumHeight(150)  # Set minimum on viewer, not group
        layout.addWidget(self.log_viewer)

        return group
