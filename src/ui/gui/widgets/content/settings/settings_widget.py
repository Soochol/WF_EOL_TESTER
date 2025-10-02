"""
Main settings widget - simplified entry point.

Provides the main settings interface using the modular architecture
with clean separation of concerns.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from .core import Colors, ConfigFile, ConfigPaths, Styles, UIConstants
from .utils import ConfigFileLoader, ConfigFileSaver, FileOperations, UIHelpers
from .widgets import PropertyEditorWidget, SettingsTreeWidget


class SettingsWidget(QWidget):
    """Main settings widget with modular architecture"""

    settings_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None, container=None, state_manager=None):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.config_files: Dict[str, ConfigFile] = {}
        self.current_config_value = None

        # Initialize UI attributes
        self.search_edit: Optional[QLineEdit] = None
        self.tree_widget: Optional[SettingsTreeWidget] = None
        self.property_editor: Optional[QWidget] = None
        self.welcome_label: Optional[QLabel] = None
        self.property_widget: Optional[PropertyEditorWidget] = None
        self.status_label: Optional[QLabel] = None

        self.setup_ui()
        self.load_configurations()

    def setup_ui(self) -> None:
        """Setup main settings UI"""
        self.setStyleSheet(Styles.MAIN_WIDGET)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        self.setup_header(layout)

        # Main content area
        self.setup_content_area(layout)

        # Footer
        self.setup_footer(layout)

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup header with search and controls"""
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Configuration Settings")
        title_label.setStyleSheet(
            f"""
            font-size: 18px;
            font-weight: bold;
            color: {Colors.TEXT_PRIMARY};
            margin-bottom: 10px;
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search settings...")
        self.search_edit.setMaximumWidth(UIConstants.SEARCH_WIDTH)
        self.search_edit.setStyleSheet(Styles.SEARCH_BOX)
        self.search_edit.textChanged.connect(self.on_search_changed)
        header_layout.addWidget(self.search_edit)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(Styles.BUTTON)
        refresh_btn.clicked.connect(self.load_configurations)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

    def setup_content_area(self, layout: QVBoxLayout) -> None:
        """Setup main content with splitter"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(Styles.SPLITTER)

        # Left panel - settings tree
        self.tree_widget = SettingsTreeWidget()
        self.tree_widget.setting_selected.connect(self.on_setting_selected)
        splitter.addWidget(self.tree_widget)

        # Right panel - property editor
        self.property_editor = QWidget()
        self.property_editor.setStyleSheet(Styles.PROPERTY_PANEL)
        self.setup_property_editor()
        splitter.addWidget(self.property_editor)

        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Tree takes 1/3
        splitter.setStretchFactor(1, 2)  # Editor takes 2/3
        splitter.setSizes([300, 600])

        layout.addWidget(splitter, stretch=1)

    def setup_property_editor(self) -> None:
        """Setup property editor panel"""
        if self.property_editor:
            layout = QVBoxLayout(self.property_editor)
            layout.setContentsMargins(10, 10, 10, 10)

            # Welcome message
            self.welcome_label = QLabel(
                "Select a setting from the tree to edit its value.\\n\\n"
                "Changes are automatically saved when you modify values."
            )
            self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.welcome_label.setStyleSheet(
                f"""
                color: {Colors.TEXT_MUTED};
                font-size: 14px;
                line-height: 1.5;
            """
            )
            layout.addWidget(self.welcome_label)

            self.property_widget = None

    def setup_footer(self, layout: QVBoxLayout) -> None:
        """Setup footer with status information"""
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 11px;
            padding: 5px;
            border-top: 1px solid {Colors.BORDER};
        """
        )
        layout.addWidget(self.status_label, stretch=0)

    def load_configurations(self) -> None:
        """Load all configuration files"""
        from loguru import logger
        from pathlib import Path
        import asyncio

        logger.info("Loading configuration files...")

        try:
            # Get configuration paths
            if self.container:
                config_service = self.container.configuration_service()
                base_paths = {
                    "Application": config_service.application_config_path,
                    "Hardware": config_service.hardware_config_path,
                    "Heating/Cooling": config_service.heating_cooling_config_path,
                    "Profile": config_service.profile_config_path,
                    "DUT Defaults": config_service.dut_defaults_config_path,
                }

                # Get active profile using existing ConfigurationService method
                try:
                    active_profile = asyncio.run(config_service.get_active_profile_name())
                    # Add active test profile to paths
                    test_profile_path = Path(config_service.test_profiles_dir) / f"{active_profile}.yaml"
                    base_paths[f"Test Profile ({active_profile})"] = str(test_profile_path)
                    logger.info(f"Loading active test profile: {active_profile}")
                except Exception as e:
                    logger.warning(f"Failed to get active profile: {e}")
            else:
                # Fallback to default paths if no container available
                base_paths = ConfigPaths.get_default_paths()

            # Ensure missing configuration files are created with defaults
            if self.container:
                try:
                    # Auto-create missing files by loading through ConfigurationService
                    # This will trigger automatic creation if files don't exist
                    asyncio.run(config_service.load_heating_cooling_config())
                    logger.info("Ensured heating/cooling configuration exists")
                except Exception as e:
                    logger.warning(f"Failed to ensure heating/cooling config: {e}")

            # Resolve to absolute paths
            file_paths = FileOperations.resolve_config_paths(base_paths)

            # Check for missing files
            missing_files = FileOperations.get_missing_files(file_paths)

            if missing_files:
                logger.warning(f"Missing configuration files: {missing_files}")
                logger.info("Continuing with available configuration files...")
                # Skip modal dialog to prevent blocking during app startup

            # Load configuration files
            self.config_files = ConfigFileLoader.load_multiple_config_files(file_paths)
            logger.info(f"Loaded {len(self.config_files)} configuration files")

            # Update tree widget
            if self.tree_widget:
                self.tree_widget.load_config_data(self.config_files)

            # Update status
            file_count = len(self.config_files)
            if self.status_label:
                self.status_label.setText(
                    f"Loaded {file_count} configuration files - Changes auto-save"
                )

            logger.info("Configuration loading completed successfully")

        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            UIHelpers.show_error_message(
                self, "Configuration Load Error", f"Failed to load configurations:\\n\\n{str(e)}"
            )

    def on_search_changed(self, text: str) -> None:
        """Handle search text changes"""
        if self.tree_widget:
            self.tree_widget.filter_tree(text)

    def on_setting_selected(self, config_value) -> None:
        """Handle setting selection from tree"""
        self.current_config_value = config_value

        # Clear existing property editor
        if self.property_widget:
            self.property_widget.deleteLater()
            self.property_widget = None

        # Hide welcome message
        if self.welcome_label:
            self.welcome_label.hide()

        # Create new property editor
        self.property_widget = PropertyEditorWidget(config_value)
        self.property_widget.value_changed.connect(self.on_value_changed)

        # Add to layout
        if self.property_editor:
            layout = self.property_editor.layout()
            if layout:
                layout.addWidget(self.property_widget)

    def on_value_changed(self, key: str, new_value) -> None:
        """Handle configuration value changes"""
        from loguru import logger

        try:
            if self.current_config_value:
                # Save the change
                success = ConfigFileSaver.save_config_value(
                    self.current_config_value, self.config_files
                )

                if success:
                    # Update tree display
                    if self.tree_widget:
                        self.tree_widget.update_item_text(key, new_value)

                    # Reload configuration in container to apply changes immediately
                    if self.container and hasattr(self.container, 'reload_configuration'):
                        try:
                            reload_success = self.container.reload_configuration()
                            if reload_success:
                                logger.info(f"✅ Configuration reloaded after changing {key}")
                            else:
                                logger.warning(f"⚠️ Configuration reload failed for {key}")
                        except Exception as e:
                            logger.error(f"Failed to reload configuration: {e}")

                    # Emit change signal
                    self.settings_changed.emit()

                    # Update status
                    if self.status_label:
                        self.status_label.setText(f"Saved & Applied: {key} = {new_value}")
                else:
                    UIHelpers.show_error_message(
                        self, "Save Error", f"Failed to save changes for: {key}"
                    )

        except Exception as e:
            UIHelpers.show_error_message(
                self, "Configuration Error", f"Error updating configuration:\\n\\n{str(e)}"
            )
