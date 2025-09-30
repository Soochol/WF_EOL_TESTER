"""
Modern Header Widget

Professional header with glassmorphism, SVG icons, and animations.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider


class StatusPill(QWidget):
    """Animated status indicator pill"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.status = "Ready"
        self.status_color = "#00D9A5"
        self.icon_name = "status_ready"
        self.icon_label: QLabel  # Type hint for icon label
        self.status_label: QLabel  # Type hint for status label
        self.animation: QPropertyAnimation  # Type hint for animation
        self.setup_ui()
        self.start_animation()

    def setup_ui(self) -> None:
        """Setup status pill UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Status icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(12, 12)
        layout.addWidget(self.icon_label)

        # Status text
        self.status_label = QLabel(self.status)
        self.status_label.setStyleSheet(
            """
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
        """
        )
        layout.addWidget(self.status_label)

        self.update_style()

    def update_style(self) -> None:
        """Update pill styling"""
        self.setStyleSheet(
            f"""
            StatusPill {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.status_color}20,
                    stop:1 {self.status_color}40);
                border: 1px solid {self.status_color}60;
                border-radius: 16px;
            }}
        """
        )

        # Update icon with SVG
        svg_provider = get_svg_icon_provider()
        icon = svg_provider.get_icon(self.icon_name, size=12, color=self.status_color)
        if not icon.isNull():
            pixmap = icon.pixmap(QSize(12, 12))
            self.icon_label.setPixmap(pixmap)

    def set_status(self, status: str, color: str, icon_name: str) -> None:
        """Update status"""
        self.status = status
        self.status_color = color
        self.icon_name = icon_name
        self.status_label.setText(status)
        self.update_style()

    def start_animation(self) -> None:
        """Start breathing animation"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(0.8)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()


class NotificationButton(QPushButton):
    """Notification button with badge"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.notification_count = 0
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup notification button"""
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set SVG icon
        svg_provider = get_svg_icon_provider()
        icon = svg_provider.get_icon("bell", size=20, color="#cccccc")
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))

        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(33, 150, 243, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """
        )

    def set_notification_count(self, count: int) -> None:
        """Set notification badge count"""
        self.notification_count = count
        self.update()

    def paintEvent(self, event) -> None:
        """Custom paint to draw badge"""
        super().paintEvent(event)

        if self.notification_count > 0:
            # Third-party imports
            from PySide6.QtGui import QColor, QPainter, QPen

            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Badge background
            badge_size = 16
            badge_x = self.width() - badge_size - 2
            badge_y = 2

            painter.setBrush(QColor("#F44336"))
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)

            # Badge text
            painter.setPen(QColor("#ffffff"))
            font = QFont()
            font.setPointSize(8)
            font.setWeight(QFont.Weight.Bold)
            painter.setFont(font)

            text = str(self.notification_count) if self.notification_count < 10 else "9+"
            painter.drawText(
                badge_x, badge_y, badge_size, badge_size, Qt.AlignmentFlag.AlignCenter, text
            )


class UserProfileButton(QPushButton):
    """User profile button with dropdown"""

    logout_requested = Signal()

    def __init__(self, username: str = "Operator", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.username = username
        self.menu: QMenu  # Type hint for menu attribute
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self) -> None:
        """Setup user button"""
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set SVG icon
        svg_provider = get_svg_icon_provider()
        icon = svg_provider.get_icon("user", size=20, color="#2196F3")
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))

        self.setText(f"  {self.username}")

        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(33, 150, 243, 0.1);
                border: 1px solid rgba(33, 150, 243, 0.3);
                border-radius: 20px;
                padding: 8px 16px;
                color: #2196F3;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.2);
                border-color: rgba(33, 150, 243, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(33, 150, 243, 0.25);
            }
        """
        )

    def setup_menu(self) -> None:
        """Setup dropdown menu"""
        self.menu = QMenu(self)
        self.menu.setStyleSheet(
            """
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #cccccc;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(33, 150, 243, 0.2);
                color: #2196F3;
            }
        """
        )

        # Menu actions
        _ = self.menu.addAction("👤 Profile")  # Reserved for future implementation
        _ = self.menu.addAction("⚙️ Settings")  # Reserved for future implementation
        self.menu.addSeparator()
        logout_action = self.menu.addAction("🚪 Logout")

        logout_action.triggered.connect(self.logout_requested.emit)

        self.clicked.connect(self.show_menu)

    def show_menu(self) -> None:
        """Show dropdown menu"""
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.menu.exec(pos)


class ModernHeaderWidget(QWidget):
    """
    Modern header with glassmorphism and animations
    """

    notifications_requested = Signal()
    emergency_stop_requested = Signal()

    def __init__(
        self,
        container: Optional[ApplicationContainer] = None,
        state_manager: Optional[GUIStateManager] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.test_progress_visible = False
        self.status_pill: StatusPill  # Type hint for status pill
        self.user_button: UserProfileButton  # Type hint for user button
        self.notification_button: NotificationButton  # Type hint for notification button
        self.progress_bar: QProgressBar  # Type hint for progress bar
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup modern header UI"""
        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 8, 20, 8)
        main_layout.setSpacing(4)

        # Top row
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # Left: Branding
        branding_layout = QVBoxLayout()
        branding_layout.setSpacing(2)

        title_label = QLabel("WF EOL Tester")
        title_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: -0.5px;
        """
        )
        branding_layout.addWidget(title_label)

        subtitle_label = QLabel("v2.0.0 • Withforce")
        subtitle_label.setStyleSheet(
            """
            font-size: 11px;
            color: #999999;
        """
        )
        branding_layout.addWidget(subtitle_label)

        top_layout.addLayout(branding_layout)

        # Center: Status Pill
        self.status_pill = StatusPill()
        top_layout.addWidget(self.status_pill, alignment=Qt.AlignmentFlag.AlignCenter)

        top_layout.addStretch()

        # Right: User & Notifications
        self.user_button = UserProfileButton()
        top_layout.addWidget(self.user_button)

        self.notification_button = NotificationButton()
        self.notification_button.clicked.connect(self.notifications_requested.emit)
        top_layout.addWidget(self.notification_button)

        main_layout.addLayout(top_layout)

        # Bottom row: Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:1 #00D9A5);
                border-radius: 2px;
            }
        """
        )
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Apply glassmorphism style
        self.setStyleSheet(
            """
            ModernHeaderWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d2d2d,
                    stop:1 #353535);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """
        )

    def set_system_status(self, status: str, status_type: str = "ready") -> None:
        """Set system status"""
        status_config = {
            "ready": {"color": "#00D9A5", "icon": "status_ready"},
            "testing": {"color": "#2196F3", "icon": "bolt"},
            "warning": {"color": "#FF9800", "icon": "status_warning"},
            "error": {"color": "#F44336", "icon": "status_error"},
            "emergency": {"color": "#D32F2F", "icon": "alert_triangle"},
            "homed": {"color": "#00BCD4", "icon": "status_ready"},
        }

        config = status_config.get(status_type.lower(), status_config["ready"])
        self.status_pill.set_status(status, config["color"], config["icon"])

    def show_test_progress(self, progress: int) -> None:
        """Show test progress bar"""
        if not self.test_progress_visible:
            self.progress_bar.setVisible(True)
            self.test_progress_visible = True
        self.progress_bar.setValue(progress)

    def hide_test_progress(self) -> None:
        """Hide test progress bar"""
        self.progress_bar.setVisible(False)
        self.test_progress_visible = False

    def set_notification_count(self, count: int) -> None:
        """Set notification badge count"""
        self.notification_button.set_notification_count(count)
