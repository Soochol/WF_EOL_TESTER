"""Toast manager for managing multiple toast notifications.

Handles displaying, positioning, and animating multiple toast notifications.
"""

# Standard library imports
from typing import List

# Third-party imports
from loguru import logger
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

# Local folder imports
from .toast_animations import ToastAnimations
from .toast_notification import ToastNotification, ToastType


class ToastManager:
    """
    Manager for displaying and coordinating multiple toast notifications.

    Features:
    - Queue-based toast display
    - Maximum simultaneous toasts
    - Automatic positioning
    - Slide animations
    """

    def __init__(self, parent_widget: QWidget, max_toasts: int = 3):
        """
        Initialize toast manager.

        Args:
            parent_widget: Parent widget to display toasts on
            max_toasts: Maximum number of simultaneous toasts
        """
        self.parent_widget = parent_widget
        self.max_toasts = max_toasts

        # Active toasts list
        self.active_toasts: List[ToastNotification] = []

        # Pending toasts queue
        self.toast_queue: List[dict] = []

    def show_success(self, title: str, message: str, duration: int = 4000) -> None:
        """
        Show success toast notification.

        Args:
            title: Toast title
            message: Toast message
            duration: Auto-dismiss duration in milliseconds
        """
        self._show_toast(title, message, ToastType.SUCCESS, duration)

    def show_error(self, title: str, message: str, duration: int = 5000) -> None:
        """
        Show error toast notification.

        Args:
            title: Toast title
            message: Toast message
            duration: Auto-dismiss duration in milliseconds (longer for errors)
        """
        self._show_toast(title, message, ToastType.ERROR, duration)

    def show_warning(self, title: str, message: str, duration: int = 4000) -> None:
        """
        Show warning toast notification.

        Args:
            title: Toast title
            message: Toast message
            duration: Auto-dismiss duration in milliseconds
        """
        self._show_toast(title, message, ToastType.WARNING, duration)

    def show_info(self, title: str, message: str, duration: int = 3000) -> None:
        """
        Show info toast notification.

        Args:
            title: Toast title
            message: Toast message
            duration: Auto-dismiss duration in milliseconds
        """
        self._show_toast(title, message, ToastType.INFO, duration)

    def _show_toast(self, title: str, message: str, toast_type: ToastType, duration: int) -> None:
        """
        Internal method to show toast or queue it.

        Args:
            title: Toast title
            message: Toast message
            toast_type: Type of toast
            duration: Auto-dismiss duration in milliseconds
        """
        # If we have room, show immediately
        if len(self.active_toasts) < self.max_toasts:
            self._display_toast(title, message, toast_type, duration)
        else:
            # Queue for later
            self.toast_queue.append(
                {"title": title, "message": message, "type": toast_type, "duration": duration}
            )
            logger.debug(f"Toast queued (queue size: {len(self.toast_queue)}): {title}")

    def _display_toast(
        self, title: str, message: str, toast_type: ToastType, duration: int
    ) -> None:
        """
        Display a toast notification with animation.

        Args:
            title: Toast title
            message: Toast message
            toast_type: Type of toast
            duration: Auto-dismiss duration in milliseconds
        """
        # Create toast widget
        toast = ToastNotification(
            title=title,
            message=message,
            toast_type=toast_type,
            auto_dismiss=True,
            duration=duration,
            parent=self.parent_widget,
        )

        # Connect closed signal
        toast.closed.connect(lambda: self._on_toast_closed(toast))

        # Add to active toasts
        self.active_toasts.append(toast)

        # Show and position
        toast.show()
        toast.raise_()  # Bring to front

        # Adjust size based on content
        toast.adjustSize()

        # Create and start slide-in animation
        parent_width = self.parent_widget.width()
        animation = ToastAnimations.create_slide_in_animation(toast, parent_width, duration=300)

        # Store animation reference to prevent garbage collection
        toast._slide_in_animation = animation  # pylint: disable=protected-access

        animation.start()

        logger.debug(f"Toast displayed: {title} ({toast_type.value})")

    def _on_toast_closed(self, toast: ToastNotification) -> None:
        """
        Handle toast close event.

        Args:
            toast: Toast that was closed
        """
        # Create slide-out animation
        animation = ToastAnimations.create_slide_out_animation(toast, duration=200)

        # Store animation reference
        toast._slide_out_animation = animation  # pylint: disable=protected-access

        # When animation finishes, remove toast
        animation.finished.connect(lambda: self._remove_toast(toast))

        animation.start()

    def _remove_toast(self, toast: ToastNotification) -> None:
        """
        Remove toast from active list and display queued toast.

        Args:
            toast: Toast to remove
        """
        # Remove from active list
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)

        # Delete widget
        toast.deleteLater()

        # Process queue
        if self.toast_queue:
            # Get next toast from queue
            next_toast = self.toast_queue.pop(0)

            # Small delay before showing next toast (for smooth transition)
            QTimer.singleShot(
                100,
                lambda: self._display_toast(
                    next_toast["title"],
                    next_toast["message"],
                    next_toast["type"],
                    next_toast["duration"],
                ),
            )

    def clear_all(self) -> None:
        """Clear all active toasts and queue."""
        # Clear queue
        self.toast_queue.clear()

        # Close all active toasts
        for toast in self.active_toasts[:]:  # Copy list to avoid modification during iteration
            toast.dismiss()

        logger.debug("All toasts cleared")
