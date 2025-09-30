"""
Log Controls Components

Reusable UI components for log management including filters and action buttons.
"""

# Standard library imports
from typing import Callable, Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class LogLevelFilter(QWidget):
    """
    Log level filter component.
    
    Provides a combo box for selecting log level filters.
    """
    
    level_changed = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the filter UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Log Level:")
        layout.addWidget(label)
        
        # Combo box
        self.combo = QComboBox()
        self.combo.addItems(["All", "INFO", "WARN", "ERROR", "DEBUG"])
        self.combo.setCurrentText("All")
        self.combo.currentTextChanged.connect(self.level_changed.emit)
        layout.addWidget(self.combo)
    
    def get_current_level(self) -> str:
        """Get currently selected log level"""
        return self.combo.currentText()
    
    def set_level(self, level: str) -> None:
        """Set log level selection"""
        if level in ["All", "INFO", "WARN", "ERROR", "DEBUG"]:
            self.combo.setCurrentText(level)


class ActionButton(QPushButton):
    """
    Standardized action button with icon and text.
    """
    
    def __init__(self, icon: str, text: str, parent: Optional[QWidget] = None):
        super().__init__(f"{icon} {text}", parent)
        self.setMinimumSize(100, 35)


class ToggleActionButton(ActionButton):
    """
    Toggle action button that changes appearance when toggled.
    """
    
    def __init__(
        self,
        active_icon: str,
        active_text: str,
        inactive_icon: str,
        inactive_text: str,
        parent: Optional[QWidget] = None
    ):
        super().__init__(active_icon, active_text, parent)
        self.active_icon = active_icon
        self.active_text = active_text
        self.inactive_icon = inactive_icon
        self.inactive_text = inactive_text
        self.is_active = False
        self.setCheckable(True)
        self.clicked.connect(self._toggle_state)
    
    def _toggle_state(self) -> None:
        """Toggle button state and update appearance"""
        self.is_active = not self.is_active
        if self.is_active:
            self.setText(f"{self.inactive_icon} {self.inactive_text}")
        else:
            self.setText(f"{self.active_icon} {self.active_text}")
    
    def set_active(self, active: bool) -> None:
        """Set button active state programmatically"""
        if active != self.is_active:
            self.setChecked(active)
            self._toggle_state()


class LogActionButtons(QWidget):
    """
    Collection of log action buttons (clear, save, pause).
    """
    
    clear_clicked = Signal()
    save_clicked = Signal()
    pause_toggled = Signal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup action buttons"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Clear button
        self.clear_btn = ActionButton("🗑️", "CLEAR")
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        layout.addWidget(self.clear_btn)
        
        # Save button
        self.save_btn = ActionButton("💾", "SAVE")
        self.save_btn.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self.save_btn)
        
        # Pause toggle button
        self.pause_btn = ToggleActionButton("⏸", "PAUSE", "▶", "RESUME")
        self.pause_btn.clicked.connect(lambda: self.pause_toggled.emit(self.pause_btn.is_active))
        layout.addWidget(self.pause_btn)
    
    def set_pause_state(self, paused: bool) -> None:
        """Set pause button state"""
        self.pause_btn.set_active(paused)


class LogControlsFactory:
    """
    Factory for creating log control components.
    """
    
    @staticmethod
    def create_header_group(
        level_change_callback: Callable[[str], None],
        clear_callback: Callable[[], None],
        save_callback: Callable[[], None],
        pause_callback: Callable[[bool], None],
        parent: Optional[QWidget] = None
    ) -> QGroupBox:
        """
        Create complete header group with all log controls.
        
        Args:
            level_change_callback: Callback for log level changes
            clear_callback: Callback for clear action
            save_callback: Callback for save action
            pause_callback: Callback for pause toggle
            parent: Parent widget
            
        Returns:
            Configured QGroupBox with all controls
        """
        group = QGroupBox("System Logs", parent)
        group.setFont(LogControlsFactory._get_group_font())
        
        layout = QHBoxLayout(group)
        layout.setSpacing(10)
        
        # Log level filter
        level_filter = LogLevelFilter()
        level_filter.level_changed.connect(level_change_callback)
        layout.addWidget(level_filter)
        
        # Stretch to separate controls
        layout.addStretch()
        
        # Action buttons
        action_buttons = LogActionButtons()
        action_buttons.clear_clicked.connect(clear_callback)
        action_buttons.save_clicked.connect(save_callback)
        action_buttons.pause_toggled.connect(pause_callback)
        layout.addWidget(action_buttons)
        
        return group
    
    @staticmethod
    def _get_group_font() -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font
