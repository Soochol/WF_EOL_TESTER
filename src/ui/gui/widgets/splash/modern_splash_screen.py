"""
Modern Splash Screen with animations and effects.
"""

import random
import math
from typing import Optional, List, Tuple

from PySide6.QtCore import (
    QPropertyAnimation, Qt, QTimer, QPointF, QRectF,
    QEasingCurve, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QLinearGradient,
    QRadialGradient, QPainterPath, QFont
)
from PySide6.QtWidgets import QSplashScreen, QGraphicsBlurEffect


class Particle:
    """Floating particle for background effect"""

    def __init__(self, width: int, height: int):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.size = random.uniform(1.5, 4)  # Smaller: 2-6 → 1.5-4
        self.speed_x = random.uniform(-0.3, 0.3)  # Slower: -0.5~0.5 → -0.3~0.3
        self.speed_y = random.uniform(-0.3, 0.3)
        self.opacity = random.uniform(0.2, 0.5)  # Dimmer: 0.3-0.8 → 0.2-0.5
        self.opacity_delta = random.uniform(-0.01, 0.01)  # Slower fade: -0.02~0.02 → -0.01~0.01

    def update(self, width: int, height: int):
        """Update particle position"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.opacity += self.opacity_delta

        # Wrap around edges
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0
        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0

        # Reverse opacity direction
        if self.opacity <= 0.2 or self.opacity >= 0.5:
            self.opacity_delta *= -1


class ModernSplashScreen(QSplashScreen):
    """
    Modern splash screen with gradient background, particles, and animations.
    """

    def __init__(self, parent=None):
        # Create pixmap with dark gradient
        pixmap = QPixmap(650, 450)
        pixmap.fill(Qt.GlobalColor.transparent)

        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        # Window flags
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )

        # State
        self.progress_value = 0
        self.status_message = "Initializing..."
        self.logo_rotation = 0
        self.shimmer_position = 0

        # Particles (reduced: 50 → 15 for subtlety)
        self.particles: List[Particle] = []
        for _ in range(15):
            self.particles.append(Particle(650, 450))

        # Setup animations
        self._setup_animations()

    def mousePressEvent(self, event):
        """Override to prevent click-to-close behavior"""
        # Ignore mouse clicks - don't call super() to prevent closing
        event.ignore()

    def _setup_animations(self):
        """Setup all animations"""
        # Fade in animation
        self.setWindowOpacity(0.0)
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(800)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation (created later)
        self.fade_out_animation: Optional[QPropertyAnimation] = None

        # Logo rotation timer (slower: 30ms → 50ms)
        self.logo_timer = QTimer(self)
        self.logo_timer.timeout.connect(self._update_logo_rotation)
        self.logo_timer.start(50)  # Slower: ~20fps

        # Shimmer animation timer (slower: 20ms → 40ms)
        self.shimmer_timer = QTimer(self)
        self.shimmer_timer.timeout.connect(self._update_shimmer)
        self.shimmer_timer.start(40)  # Slower: 25fps

        # Particle animation timer (slower: 30ms → 50ms)
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self._update_particles)
        self.particle_timer.start(50)  # Slower: ~20fps

    def _update_logo_rotation(self):
        """Update logo rotation angle (slower)"""
        self.logo_rotation = (self.logo_rotation + 1) % 360  # Slower: 2 → 1
        self.update()

    def _update_shimmer(self):
        """Update shimmer position (slower)"""
        self.shimmer_position = (self.shimmer_position + 3) % (650 + 200)  # Slower: 5 → 3
        self.update()

    def _update_particles(self):
        """Update particle positions"""
        for particle in self.particles:
            particle.update(650, 450)
        self.update()

    def drawContents(self, painter: QPainter):
        """Custom painting for splash screen"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw gradient background
        self._draw_background(painter)

        # Draw particles
        self._draw_particles(painter)

        # Draw glassmorphism card
        self._draw_card(painter)

        # Draw animated logo
        self._draw_logo(painter)

        # Draw title
        self._draw_title(painter)

        # Draw progress bar with shimmer
        self._draw_progress_bar(painter)

        # Draw status message
        self._draw_status(painter)

        # Draw version
        self._draw_version(painter)

    def _draw_background(self, painter: QPainter):
        """Draw gradient background"""
        gradient = QLinearGradient(0, 0, 650, 450)
        gradient.setColorAt(0.0, QColor("#1a1a2e"))
        gradient.setColorAt(0.5, QColor("#16213e"))
        gradient.setColorAt(1.0, QColor("#0f3460"))
        painter.fillRect(0, 0, 650, 450, gradient)

    def _draw_particles(self, painter: QPainter):
        """Draw floating particles"""
        for particle in self.particles:
            color = QColor("#2196F3")
            color.setAlphaF(particle.opacity)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPointF(particle.x, particle.y),
                particle.size, particle.size
            )

    def _draw_card(self, painter: QPainter):
        """Draw glassmorphism card"""
        card_rect = QRectF(50, 80, 550, 290)

        # Card shadow
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(card_rect.adjusted(0, 5, 0, 5), 20, 20)

        # Card background with gradient
        gradient = QLinearGradient(card_rect.topLeft(), card_rect.bottomRight())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 15))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 5))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawRoundedRect(card_rect, 20, 20)

    def _draw_logo(self, painter: QPainter):
        """Draw logo - removed for minimal design"""
        # Logo removed for cleaner, minimal design
        pass

    def _draw_title(self, painter: QPainter):
        """Draw title text"""
        # Main title
        font = QFont("Segoe UI", 32, QFont.Weight.Light)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))

        title_rect = QRectF(50, 180, 550, 50)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "WF EOL Tester")

        # Subtitle (increased spacing)
        font = QFont("Segoe UI", 12, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#cccccc"))

        subtitle_rect = QRectF(50, 245, 550, 25)  # Increased gap: 240 → 245
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "End-of-Line Testing Platform")

    def _draw_progress_bar(self, painter: QPainter):
        """Draw progress bar with shimmer effect"""
        bar_rect = QRectF(100, 300, 450, 6)

        # Background
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar_rect, 3, 3)

        # Progress fill
        if self.progress_value > 0:
            progress_width = (self.progress_value / 100.0) * 450
            progress_rect = QRectF(100, 300, progress_width, 6)

            # Gradient progress
            gradient = QLinearGradient(progress_rect.topLeft(), progress_rect.topRight())
            gradient.setColorAt(0.0, QColor("#2196F3"))
            gradient.setColorAt(0.5, QColor("#00D9A5"))
            gradient.setColorAt(1.0, QColor("#2196F3"))

            painter.setBrush(gradient)
            painter.drawRoundedRect(progress_rect, 3, 3)

            # Shimmer overlay (more subtle)
            shimmer_x = self.shimmer_position - 100
            if 100 <= shimmer_x <= 100 + progress_width:
                shimmer_gradient = QLinearGradient(
                    shimmer_x - 50, 300,
                    shimmer_x + 50, 300
                )
                shimmer_gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
                shimmer_gradient.setColorAt(0.5, QColor(255, 255, 255, 40))  # Subtle: 80 → 40
                shimmer_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))

                shimmer_rect = QRectF(shimmer_x - 50, 300, 100, 6)
                painter.setBrush(shimmer_gradient)
                painter.drawRoundedRect(shimmer_rect, 3, 3)

    def _draw_status(self, painter: QPainter):
        """Draw status message"""
        font = QFont("Segoe UI", 11, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#aaaaaa"))

        status_rect = QRectF(50, 320, 550, 30)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, self.status_message)

    def _draw_version(self, painter: QPainter):
        """Draw version info"""
        font = QFont("Segoe UI", 9, QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor("#666666"))

        version_rect = QRectF(50, 390, 550, 30)
        painter.drawText(version_rect, Qt.AlignmentFlag.AlignCenter, "Version 2.0.0 • Withforce")

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
        # Stop all timers
        self.logo_timer.stop()
        self.shimmer_timer.stop()
        self.particle_timer.stop()

        # Fade out
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(500)
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