"""
Hardware Widget

Modular hardware management page with device status and controls.
Refactored to use factory pattern and reusable components.
"""

# Standard library imports
from typing import Dict, Optional

# Third-party imports
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.widgets.hardware_status_widget import HardwareStatusWidget

# Local folder imports
# Local hardware control imports
from .hardware import HardwareControlFactory, HardwareControlWidget
from .hardware.styles import HardwareStyles


class HardwareWidget(QWidget):
    """
    Modular hardware widget for device management and control.

    Shows detailed hardware status and provides control options using
    reusable components and factory pattern.
    """

    def __init__(
        self,
        container: ApplicationContainer,
        state_manager: GUIStateManager,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.hardware_controls: Dict[str, HardwareControlWidget] = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self) -> None:
        """Setup the modular hardware UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Hardware Status
        self.hardware_status = HardwareStatusWidget(
            container=self.container,
            state_manager=self.state_manager,
        )
        main_layout.addWidget(self.hardware_status)

        # Hardware Controls
        controls_group = self.create_controls_group()
        main_layout.addWidget(controls_group)

        # Add stretch to push content to top
        main_layout.addStretch()

        # Apply centralized styling
        self.setStyleSheet(HardwareStyles.get_complete_stylesheet())

    def create_controls_group(self) -> QGroupBox:
        """Create modular hardware controls group using factory pattern."""
        group = QGroupBox("Device Controls")
        group.setFont(HardwareStyles.get_group_font())
        grid_layout = QGridLayout(group)
        grid_layout.setSpacing(10)

        # Create all hardware controls using factory
        self.hardware_controls = HardwareControlFactory.create_all_controls(parent=group)

        # Add controls to grid layout in order
        hardware_order = ["loadcell", "mcu", "power_supply", "robot", "digital_io"]
        for row, hardware_type in enumerate(hardware_order):
            if hardware_type in self.hardware_controls:
                control_widget = self.hardware_controls[hardware_type]
                grid_layout.addWidget(control_widget, row, 0, 1, 4)  # Span all columns

        return group

    def setup_connections(self) -> None:
        """Setup button connections for hardware controls."""
        self._setup_loadcell_connections()
        self._setup_mcu_connections()
        self._setup_power_connections()
        self._setup_robot_connections()
        self._setup_io_connections()

    def _setup_loadcell_connections(self) -> None:
        """Setup loadcell control connections."""
        if "loadcell" in self.hardware_controls:
            control = self.hardware_controls["loadcell"]
            control.connect_button("connect", self._on_loadcell_connect)
            control.connect_button("disconnect", self._on_loadcell_disconnect)
            control.connect_button("calibrate", self._on_loadcell_calibrate)

    def _setup_mcu_connections(self) -> None:
        """Setup MCU control connections."""
        if "mcu" in self.hardware_controls:
            control = self.hardware_controls["mcu"]
            control.connect_button("connect", self._on_mcu_connect)
            control.connect_button("disconnect", self._on_mcu_disconnect)
            control.connect_button("reset", self._on_mcu_reset)

    def _setup_power_connections(self) -> None:
        """Setup power supply control connections."""
        if "power_supply" in self.hardware_controls:
            control = self.hardware_controls["power_supply"]
            control.connect_button("connect", self._on_power_connect)
            control.connect_button("disconnect", self._on_power_disconnect)
            control.connect_button("test", self._on_power_test)

    def _setup_robot_connections(self) -> None:
        """Setup robot control connections."""
        if "robot" in self.hardware_controls:
            control = self.hardware_controls["robot"]
            control.connect_button("connect", self._on_robot_connect)
            control.connect_button("disconnect", self._on_robot_disconnect)
            control.connect_button("home", self._on_robot_home)

    def _setup_io_connections(self) -> None:
        """Setup digital I/O control connections."""
        if "digital_io" in self.hardware_controls:
            control = self.hardware_controls["digital_io"]
            control.connect_button("connect", self._on_io_connect)
            control.connect_button("disconnect", self._on_io_disconnect)
            control.connect_button("test", self._on_io_test)

    # Hardware control callbacks
    def _on_loadcell_connect(self) -> None:
        """Handle loadcell connect button."""
        # TODO: Implement loadcell connection logic
        pass

    def _on_loadcell_disconnect(self) -> None:
        """Handle loadcell disconnect button."""
        # TODO: Implement loadcell disconnection logic
        pass

    def _on_loadcell_calibrate(self) -> None:
        """Handle loadcell calibrate button."""
        # TODO: Implement loadcell calibration logic
        pass

    def _on_mcu_connect(self) -> None:
        """Handle MCU connect button."""
        # TODO: Implement MCU connection logic
        pass

    def _on_mcu_disconnect(self) -> None:
        """Handle MCU disconnect button."""
        # TODO: Implement MCU disconnection logic
        pass

    def _on_mcu_reset(self) -> None:
        """Handle MCU reset button."""
        # TODO: Implement MCU reset logic
        pass

    def _on_power_connect(self) -> None:
        """Handle power supply connect button."""
        # TODO: Implement power supply connection logic
        pass

    def _on_power_disconnect(self) -> None:
        """Handle power supply disconnect button."""
        # TODO: Implement power supply disconnection logic
        pass

    def _on_power_test(self) -> None:
        """Handle power supply test button."""
        # TODO: Implement power supply test logic
        pass

    def _on_robot_connect(self) -> None:
        """Handle robot connect button."""
        # TODO: Implement robot connection logic
        pass

    def _on_robot_disconnect(self) -> None:
        """Handle robot disconnect button."""
        # TODO: Implement robot disconnection logic
        pass

    def _on_robot_home(self) -> None:
        """Handle robot home button."""
        # TODO: Implement robot homing logic
        pass

    def _on_io_connect(self) -> None:
        """Handle digital I/O connect button."""
        # TODO: Implement digital I/O connection logic
        pass

    def _on_io_disconnect(self) -> None:
        """Handle digital I/O disconnect button."""
        # TODO: Implement digital I/O disconnection logic
        pass

    def _on_io_test(self) -> None:
        """Handle digital I/O test button."""
        # TODO: Implement digital I/O test logic
        pass

    # Public API for external access to controls
    def get_hardware_control(self, hardware_type: str) -> Optional[HardwareControlWidget]:
        """Get a hardware control widget by type.

        Args:
            hardware_type: Type of hardware control to retrieve

        Returns:
            Hardware control widget or None if not found
        """
        return self.hardware_controls.get(hardware_type)

    def set_hardware_enabled(self, hardware_type: str, enabled: bool) -> None:
        """Enable or disable all buttons for a specific hardware type.

        Args:
            hardware_type: Type of hardware to modify
            enabled: Whether the hardware controls should be enabled
        """
        if hardware_type in self.hardware_controls:
            self.hardware_controls[hardware_type].set_all_buttons_enabled(enabled)
