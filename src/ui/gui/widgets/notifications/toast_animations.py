"""Toast notification animations.

Provides slide-down/up animations for toast notifications.
"""

# Third-party imports
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRect
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class ToastAnimations:
    """Animation manager for toast notifications."""

    @staticmethod
    def create_slide_in_animation(
        toast_widget: QWidget, parent_width: int, duration: int = 300
    ) -> QParallelAnimationGroup:
        """
        Create slide-down animation for toast appearing.

        Args:
            toast_widget: Toast widget to animate
            parent_width: Width of parent widget (for centering)
            duration: Animation duration in milliseconds

        Returns:
            QParallelAnimationGroup with position and opacity animations
        """
        # Calculate centered position
        toast_width = toast_widget.width()
        x_pos = (parent_width - toast_width) // 2
        margin_top = 20

        # Get current geometry
        current_geometry = toast_widget.geometry()

        # Create position animation (slide down)
        position_animation = QPropertyAnimation(toast_widget, b"geometry")
        position_animation.setDuration(duration)

        # Start from above screen (negative y)
        start_rect = QRect(
            x_pos, -current_geometry.height(), toast_width, current_geometry.height()
        )
        # End at margin_top
        end_rect = QRect(x_pos, margin_top, toast_width, current_geometry.height())

        position_animation.setStartValue(start_rect)
        position_animation.setEndValue(end_rect)
        position_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Create opacity animation (fade in)
        opacity_effect = QGraphicsOpacityEffect(toast_widget)
        toast_widget.setGraphicsEffect(opacity_effect)

        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(0.0)
        opacity_animation.setEndValue(1.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Combine animations
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(position_animation)
        animation_group.addAnimation(opacity_animation)

        return animation_group

    @staticmethod
    def create_slide_out_animation(
        toast_widget: QWidget, duration: int = 200
    ) -> QParallelAnimationGroup:
        """
        Create slide-up animation for toast disappearing.

        Args:
            toast_widget: Toast widget to animate
            duration: Animation duration in milliseconds

        Returns:
            QParallelAnimationGroup with position and opacity animations
        """
        # Get current geometry
        current_geometry = toast_widget.geometry()

        # Create position animation (slide up)
        position_animation = QPropertyAnimation(toast_widget, b"geometry")
        position_animation.setDuration(duration)

        # Start from current position
        start_rect = QRect(
            current_geometry.x(),
            current_geometry.y(),
            current_geometry.width(),
            current_geometry.height(),
        )
        # End above screen (negative y)
        end_rect = QRect(
            current_geometry.x(),
            -current_geometry.height(),
            current_geometry.width(),
            current_geometry.height(),
        )

        position_animation.setStartValue(start_rect)
        position_animation.setEndValue(end_rect)
        position_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # Create opacity animation (fade out)
        opacity_effect = toast_widget.graphicsEffect()
        if opacity_effect is None:
            opacity_effect = QGraphicsOpacityEffect(toast_widget)
            toast_widget.setGraphicsEffect(opacity_effect)

        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(1.0)
        opacity_animation.setEndValue(0.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # Combine animations
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(position_animation)
        animation_group.addAnimation(opacity_animation)

        return animation_group
