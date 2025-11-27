"""Toast notification widget.

Provides a slide-down notification for test results and system messages.
"""

# Standard library imports
from enum import Enum
from typing import TYPE_CHECKING, Optional

# Third-party imports
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)

if TYPE_CHECKING:
    # Third-party imports
    from PySide6.QtCore import QParallelAnimationGroup


class ToastType(Enum):
    """Toast notification types."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ToastNotification(QWidget):
    """
    Minimalist toast notification widget with slide-down animation.

    Features:
    - 4 types: SUCCESS, ERROR, WARNING, INFO
    - Simple icon + text display
    - Auto-dismiss timer
    - Manual close button
    - Slide animations
    """

    closed = Signal()

    # Type-specific styling
    TOAST_STYLES = {
        ToastType.SUCCESS: {
            "background": "#1e3a1e",
            "border_color": "#4caf50",
            "icon": "✓",
            "icon_color": "#4caf50",
        },
        ToastType.ERROR: {
            "background": "#3a1e1e",
            "border_color": "#f44336",
            "icon": "✗",
            "icon_color": "#f44336",
        },
        ToastType.WARNING: {
            "background": "#3a2e1e",
            "border_color": "#ff9800",
            "icon": "⚠",
            "icon_color": "#ff9800",
        },
        ToastType.INFO: {
            "background": "#1e2a3a",
            "border_color": "#2196f3",
            "icon": "ℹ",
            "icon_color": "#2196f3",
        },
    }

    def __init__(
        self,
        title: str,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        *,
        auto_dismiss: bool = True,
        duration: int = 4000,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize toast notification.

        Args:
            title: Toast title
            message: Toast message
            toast_type: Type of toast (SUCCESS, ERROR, WARNING, INFO)
            auto_dismiss: Whether to auto-dismiss after duration
            duration: Auto-dismiss duration in milliseconds
            parent: Parent widget
        """
        super().__init__(parent)

        self.title = title
        self.message = message
        self.toast_type = toast_type
        self.auto_dismiss = auto_dismiss
        self.duration = duration

        # UI components
        self.icon_label: Optional[QLabel] = None
        self.text_label: Optional[QLabel] = None
        self.close_button: Optional[QPushButton] = None

        # Auto-dismiss timer
        self.dismiss_timer: Optional[QTimer] = None

        # Animation references (set by ToastManager to prevent garbage collection)
        self._slide_in_animation: Optional["QParallelAnimationGroup"] = None
        self._slide_out_animation: Optional["QParallelAnimationGroup"] = None

        self.setup_ui()
        self.apply_styling()

        # Start auto-dismiss timer if enabled
        if self.auto_dismiss:
            self.start_dismiss_timer()

    def setup_ui(self) -> None:
        """Setup toast UI - simple and clean design."""
        # Set fixed width, auto height
        self.setFixedWidth(420)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Main layout - simple vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar: colored line
        style = self.TOAST_STYLES[self.toast_type]
        bar_widget = QWidget()
        bar_widget.setFixedHeight(4)
        bar_widget.setStyleSheet(f"background-color: {style['border_color']};")
        main_layout.addWidget(bar_widget)

        # Content area: icon + text + close button
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(16, 12, 12, 12)
        content_layout.setSpacing(0)

        # Text container (icon + message + close button)
        from PySide6.QtWidgets import QHBoxLayout
        text_container = QHBoxLayout()
        text_container.setContentsMargins(0, 0, 0, 0)
        text_container.setSpacing(12)

        # Icon
        self.icon_label = QLabel(style["icon"])
        self.icon_label.setStyleSheet(f"color: {style['icon_color']}; font-size: 20px; font-weight: bold;")
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_container.addWidget(self.icon_label)

        # Message text
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        # Combine title and message if message exists
        if self.message:
            text_content = f"{self.title}\n{self.message}"
        else:
            text_content = self.title
        self.text_label.setText(text_content)
        self.text_label.setStyleSheet(
            "color: #ffffff; font-size: 11px; background-color: transparent;"
        )
        text_container.addWidget(self.text_label, stretch=1)

        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """
        )
        self.close_button.clicked.connect(self.dismiss)
        text_container.addWidget(self.close_button)

        content_layout.addLayout(text_container)
        main_layout.addLayout(content_layout)

    def apply_styling(self) -> None:
        """Apply type-specific styling."""
        style = self.TOAST_STYLES[self.toast_type]

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {style['background']};
                border-radius: 6px;
            }}
        """
        )

    def start_dismiss_timer(self) -> None:
        """Start auto-dismiss timer."""
        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self.dismiss)
        self.dismiss_timer.start(self.duration)

    def dismiss(self) -> None:
        """Dismiss the toast notification."""
        # Stop timer if running
        if self.dismiss_timer and self.dismiss_timer.isActive():
            self.dismiss_timer.stop()

        # Emit closed signal
        self.closed.emit()

    def enterEvent(self, event) -> None:
        """Pause auto-dismiss on mouse hover."""
        if self.dismiss_timer and self.dismiss_timer.isActive():
            self.dismiss_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Resume auto-dismiss on mouse leave."""
        if self.auto_dismiss and (not self.dismiss_timer or not self.dismiss_timer.isActive()):
            remaining_time = self.duration // 2  # Resume with half duration
            self.dismiss_timer = QTimer(self)
            self.dismiss_timer.setSingleShot(True)
            self.dismiss_timer.timeout.connect(self.dismiss)
            self.dismiss_timer.start(remaining_time)
        super().leaveEvent(event)
