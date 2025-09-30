"""
Splash screen for WF EOL Tester application.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget


class WFEOLSplashScreen(QSplashScreen):
    """
    Custom splash screen for WF EOL Tester application.

    Shows loading progress and status messages while the main application initializes.
    """

    def __init__(self, parent=None):
        # Create a clean white background
        pixmap = QPixmap(550, 400)
        pixmap.fill(Qt.GlobalColor.white)

        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        # Disable close button and add subtle styling
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )

        # Add subtle shadow effect
        self.setStyleSheet(
            """
            QSplashScreen {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
            }
        """
        )

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        """Set up the splash screen UI elements."""
        # Create a widget to hold our custom content
        self.content_widget = QWidget(self)
        self.content_widget.setGeometry(0, 0, 550, 400)

        # Main layout
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(60, 70, 60, 60)
        layout.setSpacing(25)

        # Title label
        self.title_label = QLabel("WF EOL Tester")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                font-size: 32px;
                font-weight: 300;
                font-family: 'Segoe UI Light', 'Arial', sans-serif;
                margin-bottom: 8px;
                letter-spacing: 1px;
            }
        """
        )
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("End-of-Line Testing")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(
            """
            QLabel {
                color: #7f8c8d;
                font-size: 13px;
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                margin-bottom: 25px;
                letter-spacing: 0.5px;
            }
        """
        )
        layout.addWidget(self.subtitle_label)

        # Add some spacing
        layout.addStretch()

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #34495e;
                font-size: 11px;
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                margin-bottom: 15px;
            }
        """
        )
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 3px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Version label
        self.version_label = QLabel("Version 2.0.0")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet(
            """
            QLabel {
                color: #95a5a6;
                font-size: 9px;
                font-weight: 400;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                margin-top: 25px;
            }
        """
        )
        layout.addWidget(self.version_label)

    def _setup_animations(self):
        """Set up fade-in animation for the splash screen."""
        self.setWindowOpacity(0.0)

        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)

        # Initialize fade_out_animation to None (will be created when needed)
        self.fade_out_animation: Optional[QPropertyAnimation] = None

    def show_with_animation(self):
        """Show the splash screen with fade-in animation."""
        self.show()
        self.fade_in_animation.start()

    def update_progress(self, value: int, message: str = ""):
        """
        Update the progress bar and status message.

        Args:
            value: Progress value (0-100)
            message: Status message to display
        """
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)

        # Process events to update the display
        self.repaint()

    def update_status(self, message: str):
        """
        Update only the status message.

        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        self.repaint()

    def finish_with_fade(self, main_window):
        """
        Finish the splash screen with fade-out animation.

        Args:
            main_window: The main window to show after splash
        """
        self.fade_out_animation = QPropertyAnimation(
            self, b"windowOpacity"
        )  # pylint: disable=attribute-defined-outside-init
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)

        def on_fade_complete():
            self.finish(main_window)

        self.fade_out_animation.finished.connect(on_fade_complete)
        self.fade_out_animation.start()


class LoadingSteps:
    """Predefined loading steps for the splash screen."""

    STEPS = [
        (5, "Loading configuration..."),
        (10, "Initializing dependency injection..."),
        (15, "Creating hardware factory..."),
        (25, "Loading robot service..."),
        (35, "Loading MCU service..."),
        (40, "Loading power service..."),
        (45, "Loading loadcell service..."),
        (50, "Loading digital I/O service..."),
        (55, "Initializing hardware facade..."),
        (60, "Creating main window..."),
        (65, "Applying theme..."),
        (70, "Initializing widgets..."),
        (75, "Loading dashboard..."),
        (80, "Loading test controls..."),
        (85, "Loading hardware controls..."),
        (88, "Loading results viewer..."),
        (91, "Loading logs viewer..."),
        (94, "Loading settings..."),
        (97, "Loading about page..."),
        (100, "Ready!"),
    ]

    @classmethod
    def get_step(cls, index: int):
        """Get a loading step by index."""
        if 0 <= index < len(cls.STEPS):
            return cls.STEPS[index]
        return (100, "Complete")

    @classmethod
    def get_total_steps(cls):
        """Get the total number of loading steps."""
        return len(cls.STEPS)
