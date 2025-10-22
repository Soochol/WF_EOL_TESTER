"""Toast notification widget.

Provides a slide-down notification for test results and system messages.
"""

# Standard library imports
from enum import Enum
from typing import Optional

# Third-party imports
from PySide6.QtCore import QTimer, Qt, Signal
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

        self.setup_ui()
        self.apply_styling()

        # Start auto-dismiss timer if enabled
        if self.auto_dismiss:
            self.start_dismiss_timer()

    def setup_ui(self) -> None:
        """Setup toast UI layout."""
        # Set fixed width, auto height
        self.setFixedWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Header layout (icon + title + close button)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icon
        style = self.TOAST_STYLES[self.toast_type]
        self.icon_label = QLabel(style["icon"])
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_font.setBold(True)
        self.icon_label.setFont(icon_font)
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setStyleSheet(
            f"""
            color: {style['icon_color']};
            background: transparent;
        """
        )
        header_layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #ffffff; background: transparent;")
        header_layout.addWidget(self.title_label, stretch=1)

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #999999;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """
        )
        self.close_button.clicked.connect(self.dismiss)
        header_layout.addWidget(self.close_button)

        main_layout.addLayout(header_layout)

        # Message
        if self.message:
            self.message_label = QLabel(self.message)
            self.message_label.setWordWrap(True)
            message_font = QFont()
            message_font.setPointSize(9)
            self.message_label.setFont(message_font)
            self.message_label.setStyleSheet(
                "color: #cccccc; background: transparent; padding-left: 44px;"
            )
            main_layout.addWidget(self.message_label)

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

        # Add subtle shadow effect
        self.setGraphicsEffect(None)  # Clear any existing effect

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
