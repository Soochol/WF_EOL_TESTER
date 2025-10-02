"""
Zoom Control Widget for Status Bar

Provides UI scaling controls with +/- buttons and keyboard shortcuts.
Changes are persisted to application.yaml.
"""

# Standard library imports
import os
from typing import Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

# Local imports
from loguru import logger


class ZoomControl(QWidget):
    """Zoom control widget for adjusting UI scaling factor"""

    zoom_changed = Signal(float)  # Emits new scaling factor

    def __init__(self, container=None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.container = container
        self.current_scale = self._get_current_scale()
        self.setup_ui()
        self.setup_shortcuts()

    def _get_current_scale(self) -> float:
        """Get current scaling factor from environment or config"""
        try:
            # Try to get from environment variable first
            scale = float(os.environ.get("QT_SCALE_FACTOR", "1.0"))
            return max(0.5, min(2.0, scale))
        except (ValueError, TypeError):
            return 1.0

    def setup_ui(self) -> None:
        """Setup zoom control UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Zoom label
        self.zoom_label = QLabel("🔍")
        self.zoom_label.setToolTip("UI Zoom Level")
        self.zoom_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 13px;
                padding: 2px 4px;
            }
        """)
        layout.addWidget(self.zoom_label)

        # Zoom out button
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out (Ctrl + -)")
        self.zoom_out_btn.setFixedSize(24, 24)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #cccccc;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.2);
                border-color: rgba(33, 150, 243, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(33, 150, 243, 0.3);
            }
            QPushButton:disabled {
                color: #666666;
                background-color: rgba(255, 255, 255, 0.02);
            }
        """)
        layout.addWidget(self.zoom_out_btn)

        # Current zoom percentage
        self.zoom_display = QLabel(f"{int(self.current_scale * 100)}%")
        self.zoom_display.setFixedWidth(50)
        self.zoom_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_display.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                background-color: rgba(33, 150, 243, 0.1);
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.zoom_display)

        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In (Ctrl + +)")
        self.zoom_in_btn.setFixedSize(24, 24)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #cccccc;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.2);
                border-color: rgba(33, 150, 243, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(33, 150, 243, 0.3);
            }
            QPushButton:disabled {
                color: #666666;
                background-color: rgba(255, 255, 255, 0.02);
            }
        """)
        layout.addWidget(self.zoom_in_btn)

        # Update button states
        self.update_button_states()

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for zoom control"""
        # Get main window for shortcuts
        main_window = self.window()
        if not main_window:
            logger.warning("Could not find main window for shortcuts")
            return

        # Ctrl + Plus (zoom in)
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), main_window)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)

        # Ctrl + Minus (zoom out)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), main_window)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)

        # Ctrl + 0 (reset zoom)
        self.zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), main_window)
        self.zoom_reset_shortcut.activated.connect(self.reset_zoom)

        logger.info("Zoom keyboard shortcuts registered: Ctrl+/- and Ctrl+0")

    def zoom_in(self) -> None:
        """Increase zoom by 5% (0.05)"""
        new_scale = min(2.0, self.current_scale + 0.05)
        if new_scale != self.current_scale:
            self.set_zoom(new_scale)

    def zoom_out(self) -> None:
        """Decrease zoom by 5% (0.05)"""
        new_scale = max(0.5, self.current_scale - 0.05)
        if new_scale != self.current_scale:
            self.set_zoom(new_scale)

    def reset_zoom(self) -> None:
        """Reset zoom to 100%"""
        self.set_zoom(1.0)

    def set_zoom(self, scale: float) -> None:
        """Set zoom to specific scale factor"""
        # Clamp between 0.5 and 2.0
        scale = max(0.5, min(2.0, scale))

        if scale == self.current_scale:
            return

        self.current_scale = scale
        self.zoom_display.setText(f"{int(scale * 100)}%")
        self.update_button_states()

        # Save to configuration
        self.save_to_config(scale)

        # Emit signal
        self.zoom_changed.emit(scale)

        logger.info(f"Zoom changed to {int(scale * 100)}%")

    def update_button_states(self) -> None:
        """Update button enabled/disabled states based on current zoom"""
        self.zoom_out_btn.setEnabled(self.current_scale > 0.5)
        self.zoom_in_btn.setEnabled(self.current_scale < 2.0)

    def save_to_config(self, scale: float) -> None:
        """Save scaling factor to application.yaml"""
        try:
            # Import YAML and Path for direct file update
            import yaml
            from pathlib import Path

            # Get application.yaml path
            config_path = Path(__file__).parent.parent.parent.parent.parent.parent / "configuration" / "application.yaml"

            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return

            # Read current config
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # Update scaling_factor
            if 'gui' not in config_data:
                config_data['gui'] = {}

            config_data['gui']['scaling_factor'] = scale

            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Saved scaling_factor={scale} to application.yaml")

        except Exception as e:
            logger.error(f"Failed to save zoom to config: {e}")

    def show_restart_tooltip(self) -> None:
        """Show tooltip indicating restart is required"""
        self.zoom_display.setToolTip(
            "⚠️ Restart required to apply zoom changes.\n"
            f"New zoom: {int(self.current_scale * 100)}%"
        )
