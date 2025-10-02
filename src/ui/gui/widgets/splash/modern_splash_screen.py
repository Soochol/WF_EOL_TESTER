"""
Simple and Clean Splash Screen.
"""

from typing import Optional

from PySide6.QtCore import QPropertyAnimation, Qt, QRectF, QEasingCurve
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont
from PySide6.QtWidgets import QSplashScreen


class ModernSplashScreen(QSplashScreen):
    """
    Simple and clean splash screen without distracting animations.
    """

    def __init__(self, parent=None):
        # Create clean white pixmap (reduced size: 650x450 → 500x300)
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.GlobalColor.white)

        # Remove WindowStaysOnTopHint to not block other windows
        super().__init__(pixmap)

        # Window flags - removed WindowStaysOnTopHint
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
        )

        # Add subtle border
        self.setStyleSheet(
            """
            QSplashScreen {
                border: 1px solid #d0d0d0;
            }
        """
        )

        # State
        self.progress_value = 0
        self.status_message = "Initializing..."

        # Setup animations (fade only)
        self._setup_animations()

    def mousePressEvent(self, event):
        """Override to prevent click-to-close behavior"""
        event.ignore()

    def _setup_animations(self):
        """Setup fade animations only"""
        # Fade in animation
        self.setWindowOpacity(0.0)
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(400)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation (created later)
        self.fade_out_animation: Optional[QPropertyAnimation] = None

    def drawContents(self, painter: QPainter):
        """Simple clean painting"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw title
        self._draw_title(painter)

        # Draw progress bar
        self._draw_progress_bar(painter)

        # Draw status message
        self._draw_status(painter)

        # Draw version
        self._draw_version(painter)

    def _draw_title(self, painter: QPainter):
        """Draw title text"""
        # Main title
        font = QFont("Segoe UI Light", 28, QFont.Weight.Light)
        painter.setFont(font)
        painter.setPen(QColor("#2c3e50"))

        title_rect = QRectF(0, 60, 500, 40)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "WF EOL Tester")

        # Subtitle
        font = QFont("Segoe UI", 11, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#7f8c8d"))

        subtitle_rect = QRectF(0, 105, 500, 25)
        painter.drawText(
            subtitle_rect, Qt.AlignmentFlag.AlignCenter, "End-of-Line Testing"
        )

    def _draw_progress_bar(self, painter: QPainter):
        """Draw simple progress bar"""
        bar_rect = QRectF(100, 170, 300, 5)

        # Background
        painter.setBrush(QColor("#ecf0f1"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar_rect, 2.5, 2.5)

        # Progress fill
        if self.progress_value > 0:
            progress_width = (self.progress_value / 100.0) * 300
            progress_rect = QRectF(100, 170, progress_width, 5)

            # Blue gradient
            gradient = QLinearGradient(progress_rect.topLeft(), progress_rect.topRight())
            gradient.setColorAt(0.0, QColor("#3498db"))
            gradient.setColorAt(1.0, QColor("#2980b9"))

            painter.setBrush(gradient)
            painter.drawRoundedRect(progress_rect, 2.5, 2.5)

    def _draw_status(self, painter: QPainter):
        """Draw status message"""
        font = QFont("Segoe UI", 10, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#95a5a6"))

        status_rect = QRectF(0, 190, 500, 25)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, self.status_message)

    def _draw_version(self, painter: QPainter):
        """Draw version info"""
        font = QFont("Segoe UI", 9, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#bdc3c7"))

        version_rect = QRectF(0, 260, 500, 25)
        painter.drawText(
            version_rect, Qt.AlignmentFlag.AlignCenter, "Version 2.0.0 • Withforce"
        )

    def show_with_animation(self):
        """Show splash with fade-in animation"""
        self.show()
        self.fade_in_animation.start()

    def update_progress(self, value: int, message: str = ""):
        """Update progress and status"""
        self.progress_value = value
        if message:
            self.status_message = message
        self.update()

    def update_status(self, message: str):
        """Update status message only"""
        self.status_message = message
        self.update()

    def finish_with_fade(self, main_window):
        """Finish with fade-out animation"""
        # Fade out
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        def on_fade_complete():
            self.close()
            main_window.show()

        self.fade_out_animation.finished.connect(on_fade_complete)
        self.fade_out_animation.start()


class LoadingSteps:
    """Predefined loading steps for splash screen"""

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
        """Get loading step by index"""
        if 0 <= index < len(cls.STEPS):
            return cls.STEPS[index]
        return (100, "Complete")

    @classmethod
    def get_total_steps(cls):
        """Get total number of steps"""
        return len(cls.STEPS)
