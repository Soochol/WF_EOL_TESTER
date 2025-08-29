"""
Header Widget for WF EOL Tester GUI

Displays application title, current status, and hardware indicators.
"""

from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QProgressBar, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from loguru import logger

from ui.gui.services.gui_state_manager import GUIStateManager, ConnectionStatus, TestStatus


class StatusIndicator(QFrame):
    """Status indicator widget with color-coded display"""
    
    def __init__(self, label_text: str, parent: Optional[QWidget] = None):
        """
        Initialize status indicator
        
        Args:
            label_text: Label text for the indicator
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.status = ConnectionStatus.DISCONNECTED
        
        # Setup frame properties
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(100, 40)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)
        
        # Create labels
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 8))
        
        self.status_label = QLabel("OFFLINE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        
        # Add to layout
        layout.addWidget(self.label)
        layout.addWidget(self.status_label)
        
        # Set initial style
        self.update_style()
        
    def set_status(self, status: ConnectionStatus) -> None:
        """
        Update indicator status
        
        Args:
            status: New connection status
        """
        if status != self.status:
            self.status = status
            self.update_style()
            
    def update_style(self) -> None:
        """Update indicator style based on status"""
        if self.status == ConnectionStatus.CONNECTED:
            color = "#27AE60"  # Green
            text = "ONLINE"
        elif self.status == ConnectionStatus.CONNECTING:
            color = "#F39C12"  # Orange
            text = "CONNECTING"
        elif self.status == ConnectionStatus.ERROR:
            color = "#E74C3C"  # Red
            text = "ERROR"
        else:  # DISCONNECTED
            color = "#7F8C8D"  # Gray
            text = "OFFLINE"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px solid {color};
                border-radius: 4px;
                color: white;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)
        
        self.status_label.setText(text)


class HeaderWidget(QWidget):
    """
    Header widget for main window
    
    Displays:
    - Application title and version
    - Current test status and progress
    - Hardware status indicators
    - Current time
    """
    
    def __init__(
        self, 
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize header widget
        
        Args:
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.state_manager = state_manager
        
        # Initialize components
        self.title_label: Optional[QLabel] = None
        self.test_status_label: Optional[QLabel] = None
        self.test_progress_bar: Optional[QProgressBar] = None
        self.time_label: Optional[QLabel] = None
        
        # Hardware indicators
        self.robot_indicator: Optional[StatusIndicator] = None
        self.mcu_indicator: Optional[StatusIndicator] = None
        self.loadcell_indicator: Optional[StatusIndicator] = None
        self.power_indicator: Optional[StatusIndicator] = None
        self.dio_indicator: Optional[StatusIndicator] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.setup_timers()
        
        logger.debug("Header widget initialized")
        
    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Title section
        self.title_label = QLabel("WF EOL Tester")
        self.title_label.setProperty("class", "title")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        
        # Test status section
        self.test_status_label = QLabel("Ready")
        self.test_status_label.setProperty("class", "subtitle")
        status_font = QFont("Arial", 12, QFont.Weight.DemiBold)
        self.test_status_label.setFont(status_font)
        
        # Progress bar
        self.test_progress_bar = QProgressBar()
        self.test_progress_bar.setVisible(False)  # Hidden by default
        self.test_progress_bar.setMinimum(0)
        self.test_progress_bar.setMaximum(100)
        self.test_progress_bar.setTextVisible(True)
        
        # Time display
        self.time_label = QLabel()
        time_font = QFont("Arial", 10)
        self.time_label.setFont(time_font)
        self.update_time_display()
        
        # Hardware status indicators
        self.robot_indicator = StatusIndicator("ROBOT")
        self.mcu_indicator = StatusIndicator("MCU")
        self.loadcell_indicator = StatusIndicator("LOADCELL")
        self.power_indicator = StatusIndicator("POWER")
        self.dio_indicator = StatusIndicator("DIO")
        
    def setup_layout(self) -> None:
        """Setup widget layout"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(16)
        
        # Left section - Title and status
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        
        if self.title_label:
            left_layout.addWidget(self.title_label)
            
        # Status row
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)
        
        if self.test_status_label:
            status_layout.addWidget(self.test_status_label)
            
        if self.test_progress_bar:
            self.test_progress_bar.setMaximumWidth(200)
            status_layout.addWidget(self.test_progress_bar)
            
        status_layout.addStretch()
        left_layout.addWidget(status_widget)
        
        # Center section - Hardware indicators
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)
        
        # Add hardware indicators
        for indicator in [
            self.robot_indicator,
            self.mcu_indicator, 
            self.loadcell_indicator,
            self.power_indicator,
            self.dio_indicator
        ]:
            if indicator:
                center_layout.addWidget(indicator)
                
        # Right section - Time
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        if self.time_label:
            right_layout.addWidget(self.time_label)
            
        # Add sections to main layout
        main_layout.addWidget(left_widget, 1)  # Stretch
        main_layout.addWidget(center_widget, 0)  # Fixed
        main_layout.addWidget(right_widget, 0)  # Fixed
        
    def setup_timers(self) -> None:
        """Setup update timers"""
        # Time update timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time_display)
        self.time_timer.start(1000)  # Update every second
        
    def update_test_status(self, status: str) -> None:
        """
        Update test status display
        
        Args:
            status: Test status string
        """
        if not self.test_status_label:
            return
            
        # Update status text
        self.test_status_label.setText(f"Status: {status.title()}")
        
        # Show/hide progress bar based on status
        if self.test_progress_bar:
            show_progress = status in ["preparing", "running"]
            self.test_progress_bar.setVisible(show_progress)
            
            if not show_progress:
                self.test_progress_bar.setValue(0)
                
        # Update status color
        if status == "completed":
            self.test_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")  # Green
        elif status == "failed" or status == "error":
            self.test_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")  # Red
        elif status == "running":
            self.test_status_label.setStyleSheet("color: #3498DB; font-weight: bold;")  # Blue
        elif status == "cancelled":
            self.test_status_label.setStyleSheet("color: #F39C12; font-weight: bold;")  # Orange
        else:  # idle, ready
            self.test_status_label.setStyleSheet("color: #2C3E50; font-weight: bold;")  # Dark
            
    def update_test_progress(self, progress: int, message: str = "") -> None:
        """
        Update test progress display
        
        Args:
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        if not self.test_progress_bar:
            return
            
        self.test_progress_bar.setValue(progress)
        
        if message:
            self.test_progress_bar.setFormat(f"{progress}% - {message}")
        else:
            self.test_progress_bar.setFormat(f"{progress}%")
            
    def update_hardware_status(self, hardware_status) -> None:
        """
        Update hardware status indicators
        
        Args:
            hardware_status: Hardware status object
        """
        # Update individual indicators
        if self.robot_indicator:
            self.robot_indicator.set_status(hardware_status.robot_status)
            
        if self.mcu_indicator:
            self.mcu_indicator.set_status(hardware_status.mcu_status)
            
        if self.loadcell_indicator:
            self.loadcell_indicator.set_status(hardware_status.loadcell_status)
            
        if self.power_indicator:
            self.power_indicator.set_status(hardware_status.power_status)
            
        if self.dio_indicator:
            self.dio_indicator.set_status(hardware_status.digital_io_status)
            
    def update_time_display(self) -> None:
        """Update time display"""
        if self.time_label:
            current_time = datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
            self.time_label.setText(current_time)
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            
    def set_title(self, title: str) -> None:
        """
        Set application title
        
        Args:
            title: New title text
        """
        if self.title_label:
            self.title_label.setText(title)
            
    def show_progress(self, show: bool = True) -> None:
        """
        Show or hide progress bar
        
        Args:
            show: Whether to show progress bar
        """
        if self.test_progress_bar:
            self.test_progress_bar.setVisible(show)
            
    def reset_progress(self) -> None:
        """Reset progress bar to 0%"""
        if self.test_progress_bar:
            self.test_progress_bar.setValue(0)
            self.test_progress_bar.setFormat("0%")
            self.test_progress_bar.setVisible(False)