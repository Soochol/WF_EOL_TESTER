"""Animation manager for About widget"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QWidget


class AboutAnimationManager:
    """Manages animations for About widget"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self.fade_animation = None
        self._setup_initial_state()

    def _setup_initial_state(self) -> None:
        """Setup initial animation state"""
        self.widget.setStyleSheet("background-color: #1e1e1e;")
        # Initially hide the widget for fade-in effect
        self.widget.setWindowOpacity(0.0)

    def start_fade_in_animation(self, duration: int = 800, delay: int = 100) -> None:
        """Start fade-in animation with customizable duration and delay"""
        self.fade_animation = QPropertyAnimation(self.widget, b"windowOpacity")
        self.fade_animation.setDuration(duration)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start animation with a slight delay
        QTimer.singleShot(delay, self.fade_animation.start)

    def start_fade_out_animation(self, duration: int = 400) -> None:
        """Start fade-out animation"""
        if self.fade_animation:
            self.fade_animation.stop()

        self.fade_animation = QPropertyAnimation(self.widget, b"windowOpacity")
        self.fade_animation.setDuration(duration)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.start()

    def stop_animations(self) -> None:
        """Stop all running animations"""
        if self.fade_animation:
            self.fade_animation.stop()
            self.fade_animation = None

    def is_animation_running(self) -> bool:
        """Check if any animation is currently running"""
        return self.fade_animation is not None and self.fade_animation.state() == QPropertyAnimation.State.Running
