"""
Modern Test Control Widget

Beautiful card-based test control interface with Material Design 3.
"""

import logging
from typing import Optional
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QProgressBar, QFrame, QGroupBox, QApplication
)

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.svg_icon_provider import get_svg_icon_provider
from ui.gui.widgets.log_viewer_widget import LogViewerWidget


class ModernCard(QFrame):
    """Glassmorphism card container"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title: str):
        """Setup card UI"""
        self.setStyleSheet("""
            ModernCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        if title:
            # Card title
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 10px;
            """)
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)


class ModernButton(QPushButton):
    """Material Design 3 button"""

    def __init__(self, text: str, icon_name: str = "", color: str = "primary", parent=None):
        super().__init__(text, parent)
        self.color_type = color
        self.icon_name = icon_name
        self.setup_ui()

    def setup_ui(self):
        """Setup button styling"""
        # Set SVG icon
        if self.icon_name:
            svg_provider = get_svg_icon_provider()
            icon = svg_provider.get_icon(self.icon_name, size=20)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(20, 20))

        # Color schemes
        colors = {
            "primary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #2196F3)",
                "pressed": "#1565C0",
            },
            "success": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00D9A5, stop:1 #00BFA5)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1DE9B6, stop:1 #00D9A5)",
                "pressed": "#00897B",
            },
            "warning": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF9800, stop:1 #F57C00)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFB74D, stop:1 #FF9800)",
                "pressed": "#E65100",
            },
            "danger": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F44336, stop:1 #D32F2F)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF5350, stop:1 #F44336)",
                "pressed": "#B71C1C",
            },
            "secondary": {
                "bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #607D8B, stop:1 #455A64)",
                "hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #78909C, stop:1 #607D8B)",
                "pressed": "#37474F",
            },
        }

        color_scheme = colors.get(self.color_type, colors["primary"])

        self.setStyleSheet(f"""
            QPushButton {{
                background: {color_scheme["bg"]};
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-height: 45px;
            }}
            QPushButton:hover {{
                background: {color_scheme["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {color_scheme["pressed"]};
            }}
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.3);
            }}
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)


class StatusPill(QWidget):
    """Animated status indicator"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_text = "Ready"
        self.status_color = "#00D9A5"
        self.setup_ui()

    def setup_ui(self):
        """Setup status pill UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Status dot
        self.dot_label = QLabel("●")
        self.dot_label.setStyleSheet(f"color: {self.status_color}; font-size: 14px;")
        layout.addWidget(self.dot_label)

        # Status text
        self.text_label = QLabel(self.status_text)
        self.text_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
        """)
        layout.addWidget(self.text_label)

        self.update_style()

    def set_status(self, text: str, color: str):
        """Update status"""
        self.status_text = text
        self.status_color = color
        self.text_label.setText(text)
        self.dot_label.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.update_style()

    def update_style(self):
        """Update pill background"""
        self.setStyleSheet(f"""
            StatusPill {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.status_color}20,
                    stop:1 {self.status_color}40);
                border: 1px solid {self.status_color}60;
                border-radius: 20px;
            }}
        """)


class ModernTestControlWidget(QWidget):
    """
    Modern test control widget with Material Design 3.
    """

    # Signals
    test_started = Signal()
    test_stopped = Signal()
    test_paused = Signal()
    robot_home_requested = Signal()
    emergency_stop_requested = Signal()

    # Logger
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager

        self.setup_ui()
        self.setup_connections()

        # Log geometry info immediately and after render
        QTimer.singleShot(100, self._log_geometry_info)  # Faster initial log
        QTimer.singleShot(1000, self._log_geometry_info)  # Second log after full render

    def showEvent(self, event):
        """Override showEvent to log geometry when widget is shown"""
        super().showEvent(event)
        # Log geometry after widget is fully shown
        QTimer.singleShot(200, self._log_geometry_info)

    def setup_ui(self):
        """Setup modern UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark background
        self.setStyleSheet("""
            ModernTestControlWidget {
                background-color: #1e1e1e;
            }
        """)

        # Configuration Card
        config_card = self.create_configuration_card()
        main_layout.addWidget(config_card)

        # Controls Card
        controls_card = self.create_controls_card()
        main_layout.addWidget(controls_card)

        # Status & Progress Card
        status_card = self.create_status_card()
        main_layout.addWidget(status_card)

        # Log Viewer Card
        log_card = self.create_log_card()
        main_layout.addWidget(log_card, stretch=1)

    def create_configuration_card(self) -> ModernCard:
        """Create test configuration card"""
        card = ModernCard("📦 Test Configuration")

        # Serial Number
        serial_layout = QHBoxLayout()
        serial_label = QLabel("Serial Number:")
        serial_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        self.serial_edit = QLineEdit()
        self.serial_edit.setPlaceholderText("Enter serial number...")
        self.serial_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
            }
        """)

        search_btn = QPushButton()
        svg_provider = get_svg_icon_provider()
        search_icon = svg_provider.get_icon("search", size=18, color="#2196F3")
        if not search_icon.isNull():
            search_btn.setIcon(search_icon)
            search_btn.setIconSize(QSize(18, 18))
        search_btn.setFixedSize(40, 40)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(33, 150, 243, 0.2);
                border: 1px solid rgba(33, 150, 243, 0.3);
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.3);
            }
        """)

        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.serial_edit)
        serial_layout.addWidget(search_btn)
        card.add_widget(self.create_layout_widget(serial_layout))

        # Test Type & Parameters
        params_layout = QHBoxLayout()

        # Test Type
        type_label = QLabel("Test Sequence:")
        type_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems([
            "EOL Force Test",
            "Heating Cooling Time Test",
            "Simple MCU Test"
        ])
        self.test_type_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        params_layout.addWidget(type_label)
        params_layout.addWidget(self.test_type_combo)
        params_layout.addStretch()

        card.add_widget(self.create_layout_widget(params_layout))

        return card

    def create_controls_card(self) -> ModernCard:
        """Create test controls card"""
        card = ModernCard("🎮 Test Controls")

        # Main controls row
        main_controls = QHBoxLayout()
        main_controls.setSpacing(12)

        self.start_btn = ModernButton("Start", "play", "success")
        self.pause_btn = ModernButton("Pause", "pause", "warning")
        self.stop_btn = ModernButton("Stop", "stop", "danger")

        main_controls.addWidget(self.start_btn)
        main_controls.addWidget(self.pause_btn)
        main_controls.addWidget(self.stop_btn)

        card.add_widget(self.create_layout_widget(main_controls))

        # Secondary controls row
        secondary_controls = QHBoxLayout()
        secondary_controls.setSpacing(12)

        self.home_btn = ModernButton("Home", "home", "secondary")
        self.emergency_btn = ModernButton("Emergency Stop", "emergency", "danger")

        secondary_controls.addWidget(self.home_btn)
        secondary_controls.addWidget(self.emergency_btn)

        card.add_widget(self.create_layout_widget(secondary_controls))

        return card

    def create_status_card(self) -> ModernCard:
        """Create status and progress card"""
        card = ModernCard("📊 Status & Progress")

        # Status pill
        self.status_pill = StatusPill()
        card.add_widget(self.status_pill)

        # Modern Progress bar with animation support
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(35)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        # Indeterminate animation setup
        self.progress_animation = None
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress_animation)
        self.is_indeterminate = False

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 17px;
                text-align: center;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:0.5 #00D9A5,
                    stop:1 #2196F3);
                border-radius: 17px;
            }
        """)
        card.add_widget(self.progress_bar)

        return card

    def _update_progress_animation(self):
        """Update indeterminate progress animation"""
        if self.is_indeterminate:
            # Pulse animation for indeterminate state
            if not hasattr(self, '_anim_value'):
                self._anim_value = 0

            self._anim_value = (self._anim_value + 1) % 40

            # Show pulsing effect by updating format
            dots_count = (self._anim_value // 10) % 4
            dots = "." * dots_count if dots_count > 0 else ""
            self.progress_bar.setFormat(f"Processing{dots}")

    def start_indeterminate_progress(self):
        """Start indeterminate progress animation"""
        self.is_indeterminate = True
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Processing...")
        self.progress_timer.start(100)  # Update every 100ms

    def stop_indeterminate_progress(self):
        """Stop indeterminate progress animation"""
        self.is_indeterminate = False
        self.progress_timer.stop()
        self.progress_bar.setFormat("%p%")

    def create_log_card(self) -> ModernCard:
        """Create log viewer card"""
        card = ModernCard("📝 Test Logs")

        # Log viewer
        self.log_viewer = LogViewerWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        card.add_widget(self.log_viewer)

        return card

    def create_layout_widget(self, layout):
        """Helper to wrap layout in widget"""
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def setup_connections(self):
        """Setup signal connections"""
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.pause_btn.clicked.connect(self.test_paused.emit)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.home_btn.clicked.connect(self.robot_home_requested.emit)
        self.emergency_btn.clicked.connect(self.emergency_stop_requested.emit)

    def _on_start_clicked(self):
        """Handle start button click"""
        self.start_indeterminate_progress()
        self.test_started.emit()

    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.stop_indeterminate_progress()
        self.test_stopped.emit()

    # API compatibility methods
    def update_status(self, status: str, color: str = "#00D9A5"):
        """Update status display"""
        self.status_pill.set_status(status, color)

    def update_progress(self, value: int):
        """Update progress bar"""
        if value > 0:
            self.stop_indeterminate_progress()
        self.progress_bar.setValue(value)

    def update_test_status(
        self, status: str, icon: str = "status_ready", progress: Optional[int] = None
    ):
        """Update test status display (API compatibility method)"""
        # Map icon to color
        color_map = {
            "status_ready": "#00D9A5",
            "status_running": "#2196F3",
            "status_warning": "#FF9800",
            "status_error": "#F44336",
        }
        color = color_map.get(icon, "#00D9A5")
        self.status_pill.set_status(status, color)

        if progress is not None:
            # Stop indeterminate animation when real progress is available
            if progress > 0:
                self.stop_indeterminate_progress()
            self.progress_bar.setValue(progress)
        else:
            # Start indeterminate animation if no progress provided and running
            if icon == "status_running" and self.progress_bar.value() == 0:
                self.start_indeterminate_progress()

    def update_test_progress(self, progress: int, status_text: Optional[str] = None):
        """Update only the progress bar (API compatibility method)"""
        if progress > 0:
            self.stop_indeterminate_progress()
        self.progress_bar.setValue(progress)
        if status_text:
            self.status_pill.text_label.setText(status_text)

    def disable_start_button(self):
        """Disable START TEST button (API compatibility method)"""
        self.start_btn.setEnabled(False)

    def enable_start_button(self):
        """Enable START TEST button (API compatibility method)"""
        self.start_btn.setEnabled(True)

    def disable_home_button(self):
        """Disable HOME button (API compatibility method)"""
        self.home_btn.setEnabled(False)

    def enable_home_button(self):
        """Enable HOME button (API compatibility method)"""
        self.home_btn.setEnabled(True)

    # Property accessors for backward compatibility
    @property
    def sequence_combo(self):
        """Get sequence combo box (backward compatibility)"""
        return self.test_type_combo

    def _log_geometry_info(self) -> None:
        """Log screen resolution and widget geometry information for debugging"""
        try:
            # Get screen information
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                screen_size = screen.size()
                available_geometry = screen.availableGeometry()

                self.logger.info("=" * 80)
                self.logger.info("MODERN TEST CONTROL - SCREEN & WIDGET GEOMETRY DEBUG")
                self.logger.info("=" * 80)
                self.logger.info(f"Screen Resolution: {screen_size.width()}x{screen_size.height()}")
                self.logger.info(f"Screen Geometry: {screen_geometry}")
                self.logger.info(f"Available Geometry (excluding taskbar): {available_geometry}")

            # Get main window information
            main_window = self.window()
            if main_window:
                self.logger.info(f"\nMain Window Size: {main_window.size().width()}x{main_window.size().height()}")
                self.logger.info(f"Main Window Geometry: {main_window.geometry()}")
                self.logger.info(f"Main Window Position: ({main_window.x()}, {main_window.y()})")

            # Get Modern Test Control Widget information
            self.logger.info(f"\nModern Test Control Widget Size: {self.size().width()}x{self.size().height()}")
            self.logger.info(f"Modern Test Control Widget Geometry: {self.geometry()}")
            self.logger.info(f"Modern Test Control Widget Visible: {self.isVisible()}")

            # Log each card geometry
            self.logger.info("\n" + "-" * 80)
            self.logger.info("CARDS GEOMETRY:")
            self.logger.info("-" * 80)

            # Serial edit (Configuration Card)
            if hasattr(self, 'serial_edit') and self.serial_edit:
                parent = self.serial_edit.parent()
                if parent:
                    config_card = parent.parent() if parent.parent() else parent
                    self.logger.info(f"\n[Configuration Card]")
                    self.logger.info(f"  Card Size: {config_card.size().width()}x{config_card.size().height()}")
                    self.logger.info(f"  Card Geometry: {config_card.geometry()}")
                    self.logger.info(f"  Serial Edit Size: {self.serial_edit.size().width()}x{self.serial_edit.size().height()}")

            # Buttons (Controls Card)
            if hasattr(self, 'start_btn') and self.start_btn:
                parent = self.start_btn.parent()
                if parent:
                    controls_card = parent.parent() if parent.parent() else parent
                    self.logger.info(f"\n[Controls Card]")
                    self.logger.info(f"  Card Size: {controls_card.size().width()}x{controls_card.size().height()}")
                    self.logger.info(f"  Card Geometry: {controls_card.geometry()}")

                    # Log individual button sizes
                    if self.start_btn:
                        self.logger.info(f"  START Button Size: {self.start_btn.size().width()}x{self.start_btn.size().height()}")
                    if self.pause_btn:
                        self.logger.info(f"  PAUSE Button Size: {self.pause_btn.size().width()}x{self.pause_btn.size().height()}")
                    if self.stop_btn:
                        self.logger.info(f"  STOP Button Size: {self.stop_btn.size().width()}x{self.stop_btn.size().height()}")
                    if self.home_btn:
                        self.logger.info(f"  HOME Button Size: {self.home_btn.size().width()}x{self.home_btn.size().height()}")
                    if self.emergency_btn:
                        self.logger.info(f"  EMERGENCY Button Size: {self.emergency_btn.size().width()}x{self.emergency_btn.size().height()}")

            # Status card
            if hasattr(self, 'status_pill') and self.status_pill:
                parent = self.status_pill.parent()
                if parent:
                    self.logger.info(f"\n[Status & Progress Card]")
                    self.logger.info(f"  Card Size: {parent.size().width()}x{parent.size().height()}")
                    self.logger.info(f"  Card Geometry: {parent.geometry()}")
                    if self.progress_bar:
                        self.logger.info(f"  Progress Bar Size: {self.progress_bar.size().width()}x{self.progress_bar.size().height()}")

            # Log viewer card
            if hasattr(self, 'log_viewer') and self.log_viewer:
                parent = self.log_viewer.parent()
                if parent:
                    self.logger.info(f"\n[Test Logs Card]")
                    self.logger.info(f"  Card Size: {parent.size().width()}x{parent.size().height()}")
                    self.logger.info(f"  Card Geometry: {parent.geometry()}")
                    self.logger.info(f"  Log Viewer Size: {self.log_viewer.size().width()}x{self.log_viewer.size().height()}")

            self.logger.info("\n" + "=" * 80)

        except Exception as e:
            self.logger.error(f"Error logging geometry info: {e}", exc_info=True)