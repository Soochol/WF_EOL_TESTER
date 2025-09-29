"""
Splash screen for WF EOL Tester application.
"""

# Third-party imports
from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget


class WFEOLSplashScreen(QSplashScreen):
    """
    Custom splash screen for WF EOL Tester application.

    Shows loading progress and status messages while the main application initializes.
    """

    def __init__(self, parent=None):
        # Create a simple colored background since we don't have an image
        pixmap = QPixmap(500, 350)
        pixmap.fill(Qt.darkBlue)

        super().__init__(pixmap, Qt.WindowStaysOnTopHint)

        # Disable close button
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        """Set up the splash screen UI elements."""
        # Create a widget to hold our custom content
        self.content_widget = QWidget(self)
        self.content_widget.setGeometry(0, 0, 500, 350)

        # Main layout
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Title label
        self.title_label = QLabel("WF EOL Tester")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("Wafer Fabrication End-of-Line Testing")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: lightgray;
                font-size: 14px;
                margin-bottom: 30px;
            }
        """)
        layout.addWidget(self.subtitle_label)

        # Add some spacing
        layout.addStretch()

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid lightgray;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: rgba(255, 255, 255, 0.2);
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Version label
        self.version_label = QLabel("Version 0.1.0")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("""
            QLabel {
                color: lightgray;
                font-size: 10px;
                margin-top: 20px;
            }
        """)
        layout.addWidget(self.version_label)

    def _setup_animations(self):
        """Set up fade-in animation for the splash screen."""
        self.setWindowOpacity(0.0)

        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)

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
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
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
        (10, "Loading configuration..."),
        (25, "Initializing dependency injection..."),
        (40, "Setting up hardware services..."),
        (55, "Connecting to hardware..."),
        (70, "Loading user interface..."),
        (85, "Preparing main window..."),
        (100, "Ready!")
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