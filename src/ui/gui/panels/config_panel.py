"""
Configuration Panel for WF EOL Tester GUI

Panel for viewing and editing system configuration settings.
"""

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class ConfigurationTab(QWidget):
    """Base class for configuration tab widgets"""

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """Initialize configuration tab"""
        super().__init__(parent)
        self.title = title
        self.is_modified = False

    def load_configuration(self) -> None:
        """Load configuration data into UI"""
        pass

    def save_configuration(self) -> bool:
        """
        Save configuration data from UI

        Returns:
            True if save was successful
        """
        return True

    def reset_configuration(self) -> None:
        """Reset configuration to defaults"""
        pass

    def validate_configuration(self) -> List[str]:
        """
        Validate current configuration

        Returns:
            List of validation error messages
        """
        return []


class HardwareConfigTab(ConfigurationTab):
    """Hardware configuration tab"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize hardware configuration tab"""
        super().__init__("Hardware Configuration", parent)

        # Configuration inputs
        self.robot_port_input: Optional[QLineEdit] = None
        self.robot_baudrate_input: Optional[QSpinBox] = None
        self.mcu_port_input: Optional[QLineEdit] = None
        self.mcu_baudrate_input: Optional[QSpinBox] = None
        self.loadcell_port_input: Optional[QLineEdit] = None
        self.power_ip_input: Optional[QLineEdit] = None
        self.power_port_input: Optional[QSpinBox] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components"""
        main_layout = QVBoxLayout(self)

        # Robot configuration
        robot_group = QGroupBox("Robot Configuration")
        robot_layout = QGridLayout(robot_group)

        robot_layout.addWidget(QLabel("Port:"), 0, 0)
        self.robot_port_input = QLineEdit()
        self.robot_port_input.setPlaceholderText("COM3 or /dev/ttyUSB0")
        robot_layout.addWidget(self.robot_port_input, 0, 1)

        robot_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.robot_baudrate_input = QSpinBox()
        self.robot_baudrate_input.setRange(1200, 921600)
        self.robot_baudrate_input.setValue(115200)
        robot_layout.addWidget(self.robot_baudrate_input, 1, 1)

        # MCU configuration
        mcu_group = QGroupBox("MCU Configuration")
        mcu_layout = QGridLayout(mcu_group)

        mcu_layout.addWidget(QLabel("Port:"), 0, 0)
        self.mcu_port_input = QLineEdit()
        self.mcu_port_input.setPlaceholderText("COM4 or /dev/ttyUSB1")
        mcu_layout.addWidget(self.mcu_port_input, 0, 1)

        mcu_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.mcu_baudrate_input = QSpinBox()
        self.mcu_baudrate_input.setRange(1200, 921600)
        self.mcu_baudrate_input.setValue(115200)
        mcu_layout.addWidget(self.mcu_baudrate_input, 1, 1)

        # Load cell configuration
        loadcell_group = QGroupBox("Load Cell Configuration")
        loadcell_layout = QGridLayout(loadcell_group)

        loadcell_layout.addWidget(QLabel("Port:"), 0, 0)
        self.loadcell_port_input = QLineEdit()
        self.loadcell_port_input.setPlaceholderText("COM5 or /dev/ttyUSB2")
        loadcell_layout.addWidget(self.loadcell_port_input, 0, 1)

        # Power supply configuration
        power_group = QGroupBox("Power Supply Configuration")
        power_layout = QGridLayout(power_group)

        power_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.power_ip_input = QLineEdit()
        self.power_ip_input.setPlaceholderText("192.168.1.100")
        power_layout.addWidget(self.power_ip_input, 0, 1)

        power_layout.addWidget(QLabel("Port:"), 1, 0)
        self.power_port_input = QSpinBox()
        self.power_port_input.setRange(1, 65535)
        self.power_port_input.setValue(5025)
        power_layout.addWidget(self.power_port_input, 1, 1)

        # Add all groups to main layout
        main_layout.addWidget(robot_group)
        main_layout.addWidget(mcu_group)
        main_layout.addWidget(loadcell_group)
        main_layout.addWidget(power_group)
        main_layout.addStretch()


class ApplicationConfigTab(ConfigurationTab):
    """Application configuration tab"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize application configuration tab"""
        super().__init__("Application Configuration", parent)

        # Configuration inputs
        self.log_level_combo: Optional[QComboBox] = None
        self.results_path_input: Optional[QLineEdit] = None
        self.auto_save_checkbox: Optional[QCheckBox] = None
        self.backup_count_spin: Optional[QSpinBox] = None
        self.theme_combo: Optional[QComboBox] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components"""
        main_layout = QVBoxLayout(self)

        # Logging configuration
        logging_group = QGroupBox("Logging Configuration")
        logging_layout = QGridLayout(logging_group)

        logging_layout.addWidget(QLabel("Log Level:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        logging_layout.addWidget(self.log_level_combo, 0, 1)

        # Data storage configuration
        storage_group = QGroupBox("Data Storage Configuration")
        storage_layout = QGridLayout(storage_group)

        storage_layout.addWidget(QLabel("Results Path:"), 0, 0)

        path_layout = QHBoxLayout()
        self.results_path_input = QLineEdit()
        self.results_path_input.setPlaceholderText("./results/")
        path_layout.addWidget(self.results_path_input)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_results_path)
        path_layout.addWidget(browse_button)

        storage_layout.addLayout(path_layout, 0, 1)

        storage_layout.addWidget(QLabel("Auto Save:"), 1, 0)
        self.auto_save_checkbox = QCheckBox("Enable automatic result saving")
        self.auto_save_checkbox.setChecked(True)
        storage_layout.addWidget(self.auto_save_checkbox, 1, 1)

        storage_layout.addWidget(QLabel("Backup Count:"), 2, 0)
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(0, 100)
        self.backup_count_spin.setValue(10)
        storage_layout.addWidget(self.backup_count_spin, 2, 1)

        # UI configuration
        ui_group = QGroupBox("UI Configuration")
        ui_layout = QGridLayout(ui_group)

        ui_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Industrial", "Dark", "Light", "Terminal"])
        self.theme_combo.setCurrentText("Industrial")
        ui_layout.addWidget(self.theme_combo, 0, 1)

        # Add all groups to main layout
        main_layout.addWidget(logging_group)
        main_layout.addWidget(storage_group)
        main_layout.addWidget(ui_group)
        main_layout.addStretch()

    def browse_results_path(self) -> None:
        """Browse for results directory"""
        if self.results_path_input:
            directory = QFileDialog.getExistingDirectory(
                self, "Select Results Directory", self.results_path_input.text() or "./"
            )
            if directory:
                self.results_path_input.setText(directory)


class TestConfigTab(ConfigurationTab):
    """Test configuration tab"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize test configuration tab"""
        super().__init__("Test Configuration", parent)

        # Configuration inputs
        self.test_timeout_spin: Optional[QSpinBox] = None
        self.retry_count_spin: Optional[QSpinBox] = None
        self.force_threshold_spin: Optional[QDoubleSpinBox] = None
        self.position_tolerance_spin: Optional[QDoubleSpinBox] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components"""
        main_layout = QVBoxLayout(self)

        # Test parameters
        test_group = QGroupBox("Test Parameters")
        test_layout = QGridLayout(test_group)

        test_layout.addWidget(QLabel("Test Timeout (s):"), 0, 0)
        self.test_timeout_spin = QSpinBox()
        self.test_timeout_spin.setRange(10, 3600)
        self.test_timeout_spin.setValue(300)
        test_layout.addWidget(self.test_timeout_spin, 0, 1)

        test_layout.addWidget(QLabel("Retry Count:"), 1, 0)
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(0, 10)
        self.retry_count_spin.setValue(3)
        test_layout.addWidget(self.retry_count_spin, 1, 1)

        # Force test parameters
        force_group = QGroupBox("Force Test Parameters")
        force_layout = QGridLayout(force_group)

        force_layout.addWidget(QLabel("Force Threshold (N):"), 0, 0)
        self.force_threshold_spin = QDoubleSpinBox()
        self.force_threshold_spin.setRange(0.1, 1000.0)
        self.force_threshold_spin.setValue(50.0)
        self.force_threshold_spin.setSuffix(" N")
        force_layout.addWidget(self.force_threshold_spin, 0, 1)

        force_layout.addWidget(QLabel("Position Tolerance (mm):"), 1, 0)
        self.position_tolerance_spin = QDoubleSpinBox()
        self.position_tolerance_spin.setRange(0.01, 10.0)
        self.position_tolerance_spin.setValue(0.5)
        self.position_tolerance_spin.setSuffix(" mm")
        force_layout.addWidget(self.position_tolerance_spin, 1, 1)

        # Add groups to main layout
        main_layout.addWidget(test_group)
        main_layout.addWidget(force_group)
        main_layout.addStretch()


class ConfigPanel(QWidget):
    """
    Configuration panel widget

    Provides interface for:
    - Hardware configuration settings
    - Application configuration
    - Test parameter configuration
    - Configuration file management
    """

    # Signals
    status_message = Signal(str)

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize configuration panel

        Args:
            container: Application dependency injection container
            state_manager: GUI state manager
            parent: Parent widget
        """
        super().__init__(parent)

        # Store dependencies
        self.container = container
        self.state_manager = state_manager
        self.configuration_service = container.configuration_service()

        # UI components
        self.tab_widget: Optional[QTabWidget] = None
        self.hardware_tab: Optional[HardwareConfigTab] = None
        self.application_tab: Optional[ApplicationConfigTab] = None
        self.test_tab: Optional[TestConfigTab] = None

        # Control buttons
        self.load_button: Optional[QPushButton] = None
        self.save_button: Optional[QPushButton] = None
        self.reset_button: Optional[QPushButton] = None
        self.validate_button: Optional[QPushButton] = None

        # Status display
        self.status_text: Optional[QTextEdit] = None

        # Setup UI
        self.setup_ui()
        self.setup_layout()
        self.connect_signals()

        # Load initial configuration
        self.load_configuration()

        logger.debug("Configuration panel initialized")

    def setup_ui(self) -> None:
        """Setup UI components"""
        # Set widget properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # === CONFIGURATION TABS ===
        self.tab_widget = QTabWidget()

        # Create configuration tabs
        self.hardware_tab = HardwareConfigTab()
        self.application_tab = ApplicationConfigTab()
        self.test_tab = TestConfigTab()

        # Add tabs to widget
        self.tab_widget.addTab(self.hardware_tab, "Hardware")
        self.tab_widget.addTab(self.application_tab, "Application")
        self.tab_widget.addTab(self.test_tab, "Test Settings")

        # === CONTROL BUTTONS ===
        control_group = QGroupBox("Configuration Management")
        control_layout = QHBoxLayout(control_group)

        self.load_button = QPushButton("Load Configuration")
        self.load_button.setProperty("class", "primary")
        self.load_button.setMinimumHeight(40)
        self.load_button.setAccessibleName("Load Configuration from File")

        self.save_button = QPushButton("Save Configuration")
        self.save_button.setProperty("class", "success")
        self.save_button.setMinimumHeight(40)
        self.save_button.setAccessibleName("Save Configuration to File")

        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setProperty("class", "warning")
        self.reset_button.setMinimumHeight(40)
        self.reset_button.setAccessibleName("Reset Configuration to Defaults")

        self.validate_button = QPushButton("Validate Configuration")
        self.validate_button.setProperty("class", "info")
        self.validate_button.setMinimumHeight(40)
        self.validate_button.setAccessibleName("Validate Current Configuration")

        control_layout.addWidget(self.load_button)
        control_layout.addWidget(self.save_button)
        control_layout.addWidget(self.reset_button)
        control_layout.addWidget(self.validate_button)
        control_layout.addStretch()

        # === STATUS DISPLAY ===
        status_group = QGroupBox("Configuration Status")
        status_layout = QVBoxLayout(status_group)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        self.status_text.setFont(QFont("Consolas", 9))
        self.status_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #34495E;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )

        status_layout.addWidget(self.status_text)

        # Store group references
        self.control_group = control_group
        self.status_group = status_group

    def setup_layout(self) -> None:
        """Setup widget layout"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create main content widget
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Main layout for content
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Add tab widget
        if self.tab_widget:
            main_layout.addWidget(self.tab_widget, 1)  # Give it most space

        # Add control buttons
        main_layout.addWidget(self.control_group)

        # Add status display
        main_layout.addWidget(self.status_group)

        # Set main layout
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

    def connect_signals(self) -> None:
        """Connect signals and slots"""
        # Control button signals
        if self.load_button:
            self.load_button.clicked.connect(self.load_configuration)

        if self.save_button:
            self.save_button.clicked.connect(self.save_configuration)

        if self.reset_button:
            self.reset_button.clicked.connect(self.reset_configuration)

        if self.validate_button:
            self.validate_button.clicked.connect(self.validate_configuration)

        # State manager signals
        if self.state_manager:
            self.state_manager.configuration_changed.connect(self.on_configuration_changed)

    def load_configuration(self) -> None:
        """Load configuration from service"""
        try:
            self.add_status_message("Loading configuration...")

            # This would load actual configuration from service
            # For now, just simulate loading

            # Load default values into tabs
            if self.hardware_tab:
                self.hardware_tab.load_configuration()

            if self.application_tab:
                self.application_tab.load_configuration()

            if self.test_tab:
                self.test_tab.load_configuration()

            self.add_status_message("Configuration loaded successfully")
            self.status_message.emit("Configuration loaded")

            logger.info("Configuration loaded")

        except Exception as e:
            error_msg = f"Failed to load configuration: {e}"
            self.add_status_message(error_msg)
            self.status_message.emit(error_msg)
            logger.error(error_msg)

    def save_configuration(self) -> None:
        """Save configuration to service"""
        try:
            self.add_status_message("Saving configuration...")

            # Validate configuration first
            validation_errors = self.validate_all_tabs()
            if validation_errors:
                error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
                QMessageBox.warning(self, "Validation Error", error_msg)
                self.add_status_message("Save cancelled due to validation errors")
                return

            # Save configuration from all tabs
            if self.hardware_tab:
                self.hardware_tab.save_configuration()

            if self.application_tab:
                self.application_tab.save_configuration()

            if self.test_tab:
                self.test_tab.save_configuration()

            # Notify state manager
            if self.state_manager:
                self.state_manager.load_configuration()

            self.add_status_message("Configuration saved successfully")
            self.status_message.emit("Configuration saved")

            logger.info("Configuration saved")

        except Exception as e:
            error_msg = f"Failed to save configuration: {e}"
            self.add_status_message(error_msg)
            self.status_message.emit(error_msg)
            logger.error(error_msg)

    def reset_configuration(self) -> None:
        """Reset configuration to defaults"""
        try:
            reply = QMessageBox.question(
                self,
                "Reset Configuration",
                "Are you sure you want to reset all configuration to defaults?\n"
                "This will lose any unsaved changes.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            self.add_status_message("Resetting configuration to defaults...")

            # Reset all tabs
            if self.hardware_tab:
                self.hardware_tab.reset_configuration()

            if self.application_tab:
                self.application_tab.reset_configuration()

            if self.test_tab:
                self.test_tab.reset_configuration()

            self.add_status_message("Configuration reset to defaults")
            self.status_message.emit("Configuration reset")

            logger.info("Configuration reset to defaults")

        except Exception as e:
            error_msg = f"Failed to reset configuration: {e}"
            self.add_status_message(error_msg)
            self.status_message.emit(error_msg)
            logger.error(error_msg)

    def validate_configuration(self) -> None:
        """Validate current configuration"""
        try:
            self.add_status_message("Validating configuration...")

            validation_errors = self.validate_all_tabs()

            if validation_errors:
                error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
                self.add_status_message("Validation failed")
                for error in validation_errors:
                    self.add_status_message(f"  - {error}")

                QMessageBox.warning(self, "Validation Failed", error_msg)
            else:
                self.add_status_message("Configuration validation passed")
                QMessageBox.information(self, "Validation Passed", "Configuration is valid")

            logger.info(f"Configuration validation: {len(validation_errors)} errors")

        except Exception as e:
            error_msg = f"Validation failed: {e}"
            self.add_status_message(error_msg)
            self.status_message.emit(error_msg)
            logger.error(error_msg)

    def validate_all_tabs(self) -> List[str]:
        """
        Validate configuration in all tabs

        Returns:
            List of validation error messages
        """
        errors = []

        if self.hardware_tab:
            errors.extend(self.hardware_tab.validate_configuration())

        if self.application_tab:
            errors.extend(self.application_tab.validate_configuration())

        if self.test_tab:
            errors.extend(self.test_tab.validate_configuration())

        return errors

    def on_configuration_changed(self) -> None:
        """Handle configuration change from state manager"""
        self.add_status_message("Configuration updated externally")
        self.load_configuration()

    def add_status_message(self, message: str) -> None:
        """
        Add message to status display

        Args:
            message: Message to add
        """
        if self.status_text:
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"

            self.status_text.append(formatted_message)

            # Auto-scroll to bottom
            cursor = self.status_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.status_text.setTextCursor(cursor)

    def activate_panel(self) -> None:
        """Called when panel becomes active"""
        # Refresh configuration when panel becomes active
        self.load_configuration()
        logger.debug("Configuration panel activated")

    def emergency_stop(self) -> None:
        """Handle emergency stop request"""
        # Configuration panel doesn't need specific emergency stop handling
        self.add_status_message("Emergency stop acknowledged")

    def handle_resize(self) -> None:
        """Handle panel resize"""
        # Could adjust layouts based on panel size
        pass

    def refresh_panel(self) -> None:
        """Refresh panel data"""
        self.load_configuration()
        self.status_message.emit("Configuration panel refreshed")
