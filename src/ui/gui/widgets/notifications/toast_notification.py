"""Toast notification widget.

Provides a slide-down notification for test results and system messages.
"""

# Standard library imports
from enum import Enum
from typing import TYPE_CHECKING, Optional

# Third-party imports
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
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


class ToastNotification(QFrame):
    """
    Toast notification widget with slide-down animation.

    Features:
    - 4 types: SUCCESS, ERROR, WARNING, INFO
    - Icon, title, and message display
    - Auto-dismiss timer
    - Manual close button
    - Slide animations
    """

    closed = Signal()

    # Type-specific styling
    TOAST_STYLES = {
        ToastType.SUCCESS: {
            "background": "#1e3a1e",
            "border": "#4caf50",
            "icon": "✓",
            "icon_color": "#4caf50",
        },
        ToastType.ERROR: {
            "background": "#3a1e1e",
            "border": "#f44336",
            "icon": "✗",
            "icon_color": "#f44336",
        },
        ToastType.WARNING: {
            "background": "#3a2e1e",
            "border": "#ff9800",
            "icon": "⚠",
            "icon_color": "#ff9800",
        },
        ToastType.INFO: {
            "background": "#1e2a3a",
            "border": "#2196f3",
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

        # Remove QFrame default frame styling
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Plain)

        self.title = title
        self.message = message
        self.toast_type = toast_type
        self.auto_dismiss = auto_dismiss
        self.duration = duration

        # UI components
        self.icon_label: Optional[QLabel] = None
        self.title_label: Optional[QLabel] = None
        self.message_label: Optional[QLabel] = None
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
        """Setup toast UI layout as a single unified card."""
        # Set fixed width, auto height
        self.setFixedWidth(450)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Main layout - single card structure with NO margin to prevent border breaks
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top row: Icon + Title/Message + Close button (all in one horizontal line to prevent visual breaks)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(16, 12, 16, 12)
        top_layout.setSpacing(16)

        # Icon on the left
        style = self.TOAST_STYLES[self.toast_type]
        self.icon_label = QLabel(style["icon"])
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_font.setBold(True)
        self.icon_label.setFont(icon_font)
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setStyleSheet(
            f"""
            color: {style['icon_color']};
            background: transparent;
        """
        )
        top_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        # Content column: Title + Message
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)

        # Title
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #ffffff; background: transparent;")
        self.title_label.setWordWrap(True)
        content_layout.addWidget(self.title_label)

        # Message
        if self.message:
            self.message_label = QLabel(self.message)
            self.message_label.setWordWrap(True)
            message_font = QFont()
            message_font.setPointSize(10)
            self.message_label.setFont(message_font)
            self.message_label.setStyleSheet(
                "color: #e0e0e0; background: transparent;"
            )
            content_layout.addWidget(self.message_label)

        top_layout.addLayout(content_layout, stretch=1)

        # Close button on the right
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(28, 28)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #999999;
                font-size: 24px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.15);
                border-radius: 14px;
            }
        """
        )
        self.close_button.clicked.connect(self.dismiss)
        top_layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(top_layout)

    def apply_styling(self) -> None:
        """Apply type-specific styling."""
        style = self.TOAST_STYLES[self.toast_type]

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {style['background']};
                border: none;
                border-left: 4px solid {style['border']};
                border-radius: 8px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
        """
        )

        # Clear any existing graphics effects (type: ignore for None argument)
        self.setGraphicsEffect(None)  # type: ignore[arg-type]

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
