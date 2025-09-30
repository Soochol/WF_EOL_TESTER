"""
Page Transition Effects

Smooth fade transitions between pages in QStackedWidget.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from loguru import logger
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget


class PageTransitionManager:
    """
    Manages smooth fade transitions between pages.

    Provides fade-in/fade-out effects for QStackedWidget page changes.
    """

    def __init__(self, stacked_widget: QStackedWidget):
        """
        Initialize page transition manager.

        Args:
            stacked_widget: QStackedWidget to manage transitions for
        """
        self.stacked_widget = stacked_widget
        self.current_animation: Optional[QPropertyAnimation | QParallelAnimationGroup] = None
        self.duration = 300  # Animation duration in ms

    def transition_to(self, widget: QWidget) -> None:
        """
        Transition to new widget with fade effect.

        Args:
            widget: Target widget to transition to
        """
        # Cancel any running animation
        if (
            self.current_animation
            and self.current_animation.state() == QPropertyAnimation.State.Running
        ):
            self.current_animation.stop()

        # Get current and target widgets
        current_widget = self.stacked_widget.currentWidget()
        target_widget = widget

        # If same widget or no current widget, just switch
        if current_widget is None or current_widget == target_widget:
            self.stacked_widget.setCurrentWidget(target_widget)
            return

        # Create fade out animation for current widget
        self._fade_out_then_in(current_widget, target_widget)

    def _fade_out_then_in(self, old_widget: QWidget, new_widget: QWidget) -> None:
        """Fade out current widget, then fade in new widget"""
        # Ensure opacity effects exist
        old_effect: QGraphicsOpacityEffect
        if old_widget.graphicsEffect() is None:
            old_effect = QGraphicsOpacityEffect(old_widget)
            old_widget.setGraphicsEffect(old_effect)
        else:
            effect = old_widget.graphicsEffect()
            assert isinstance(effect, QGraphicsOpacityEffect)
            old_effect = effect

        new_effect: QGraphicsOpacityEffect
        if new_widget.graphicsEffect() is None:
            new_effect = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(new_effect)
        else:
            effect = new_widget.graphicsEffect()
            assert isinstance(effect, QGraphicsOpacityEffect)
            new_effect = effect

        # Set initial states
        old_effect.setOpacity(1.0)
        new_effect.setOpacity(0.0)

        # Create fade out animation
        fade_out = QPropertyAnimation(old_effect, b"opacity")
        fade_out.setDuration(self.duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Create fade in animation
        fade_in = QPropertyAnimation(new_effect, b"opacity")
        fade_in.setDuration(self.duration // 2)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Switch widget halfway through
        def switch_widget():
            self.stacked_widget.setCurrentWidget(new_widget)
            fade_in.start()

        fade_out.finished.connect(switch_widget)

        # Clean up after fade in completes
        def cleanup():
            old_effect.setOpacity(1.0)
            new_effect.setOpacity(1.0)
            self.current_animation = None

        fade_in.finished.connect(cleanup)

        # Start fade out
        self.current_animation = fade_out
        fade_out.start()

    def cross_fade(self, old_widget: QWidget, new_widget: QWidget) -> None:
        """
        Cross-fade between widgets (simultaneous fade out/in).

        Args:
            old_widget: Widget to fade out
            new_widget: Widget to fade in
        """
        # Ensure both widgets are visible during transition
        self.stacked_widget.setCurrentWidget(new_widget)

        # Ensure opacity effects exist
        old_effect: QGraphicsOpacityEffect
        if old_widget.graphicsEffect() is None:
            old_effect = QGraphicsOpacityEffect(old_widget)
            old_widget.setGraphicsEffect(old_effect)
        else:
            effect = old_widget.graphicsEffect()
            assert isinstance(effect, QGraphicsOpacityEffect)
            old_effect = effect

        new_effect: QGraphicsOpacityEffect
        if new_widget.graphicsEffect() is None:
            new_effect = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(new_effect)
        else:
            effect = new_widget.graphicsEffect()
            assert isinstance(effect, QGraphicsOpacityEffect)
            new_effect = effect

        # Create parallel animations
        animation_group = QParallelAnimationGroup()

        # Fade out old widget
        fade_out = QPropertyAnimation(old_effect, b"opacity")
        fade_out.setDuration(self.duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation_group.addAnimation(fade_out)

        # Fade in new widget
        fade_in = QPropertyAnimation(new_effect, b"opacity")
        fade_in.setDuration(self.duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation_group.addAnimation(fade_in)

        # Cleanup
        def cleanup():
            old_effect.setOpacity(1.0)
            new_effect.setOpacity(1.0)
            self.current_animation = None

        animation_group.finished.connect(cleanup)

        # Start animations
        self.current_animation = animation_group
        animation_group.start()

    def set_duration(self, duration_ms: int) -> None:
        """
        Set transition duration.

        Args:
            duration_ms: Duration in milliseconds
        """
        self.duration = duration_ms
        logger.debug(f"Page transition duration set to {duration_ms}ms")

    def instant_switch(self, widget: QWidget) -> None:
        """
        Switch to widget instantly without animation.

        Args:
            widget: Target widget
        """
        # Cancel any running animation
        if (
            self.current_animation
            and self.current_animation.state() == QPropertyAnimation.State.Running
        ):
            self.current_animation.stop()

        self.stacked_widget.setCurrentWidget(widget)
