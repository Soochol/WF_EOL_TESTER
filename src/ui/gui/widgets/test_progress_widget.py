"""
Test Progress Widget

Widget for displaying test progress and current status.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager, TestProgress


class TestProgressWidget(QWidget):
    """
    Test progress widget for displaying current test status.

    Shows test name, progress percentage, elapsed time, and estimated completion.
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.setup_ui()
        self.connect_signals()
        self.setup_update_timer()

    def setup_ui(self) -> None:
        """Setup the test progress UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create progress group
        self.progress_group = QGroupBox("Test Progress & Data")
        self.progress_group.setFont(self._get_group_font())
        main_layout.addWidget(self.progress_group)

        # Content layout
        content_layout = QVBoxLayout(self.progress_group)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(15, 20, 15, 15)

        # Top row: Test info and progress
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        # Left side: Test info
        left_layout = QVBoxLayout()
        self.current_test_label = QLabel("Current: EOL Force Test")
        self.status_label = QLabel("Status: Running...")
        left_layout.addWidget(self.current_test_label)
        left_layout.addWidget(self.status_label)
        info_layout.addLayout(left_layout)

        # Right side: Progress and timing
        right_layout = QVBoxLayout()
        self.progress_label = QLabel("Progress: 60% (6/10)")
        self.timing_label = QLabel("Elapsed: 02:34 | ETA: 01:42")
        right_layout.addWidget(self.progress_label)
        right_layout.addWidget(self.timing_label)
        info_layout.addLayout(right_layout)

        content_layout.addLayout(info_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(60)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        content_layout.addWidget(self.progress_bar)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

        # Initialize display
        self._update_display()

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        self.state_manager.test_progress_updated.connect(self._on_test_progress_updated)

    def setup_update_timer(self) -> None:
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second

    def _on_test_progress_updated(self, progress: TestProgress) -> None:
        """Handle test progress update"""
        self._update_display(progress)

    def _update_display(self, progress: Optional[TestProgress] = None) -> None:
        """Update the display with current test progress"""
        if progress is None:
            progress = self.state_manager.get_test_progress()

        # Update labels
        current_test = progress.current_test if progress.current_test else "No active test"
        self.current_test_label.setText(f"Current: {current_test}")
        self.status_label.setText(f"Status: {progress.status}")

        # Update progress
        if progress.total_cycles > 0:
            progress_text = f"Progress: {progress.progress_percent}% ({progress.current_cycle}/{progress.total_cycles})"
        else:
            progress_text = f"Progress: {progress.progress_percent}%"
        self.progress_label.setText(progress_text)

        # Update timing
        timing_text = f"Elapsed: {progress.elapsed_time} | ETA: {progress.estimated_remaining}"
        self.timing_label.setText(timing_text)

        # Update progress bar
        self.progress_bar.setValue(progress.progress_percent)

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        TestProgressWidget {
            background-color: #1e1e1e;
            color: #cccccc;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #404040;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLabel {
            color: #cccccc;
            font-size: 14px;
            padding: 2px;
        }
        QProgressBar {
            border: 1px solid #404040;
            border-radius: 3px;
            background-color: #2d2d2d;
            color: #ffffff;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #0078d4, stop: 1 #106ebe);
            border-radius: 2px;
        }
        """
