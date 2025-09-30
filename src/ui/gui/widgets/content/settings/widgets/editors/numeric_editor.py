"""
Numeric value editor widget.

Provides spin box controls for integer and float configuration values.
"""

# Standard library imports
from typing import Any, Union

# Third-party imports
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QSpinBox

# Local folder imports
from ...core import Colors
from .base_editor import BaseEditorWidget


class NumericEditorWidget(BaseEditorWidget):
    """Numeric editor for int and float values"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spin_box: Union[QSpinBox, QDoubleSpinBox]

    def setup_ui(self) -> None:
        """Setup numeric editor UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create appropriate spin box based on type
        if self.config_value.data_type == "int":
            self.spin_box = QSpinBox()
            self.spin_box.setRange(-2147483648, 2147483647)
            self.spin_box.setValue(int(self.config_value.value))
        else:  # float
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setRange(-1e308, 1e308)
            self.spin_box.setDecimals(2)  # Changed from 6 to 2 decimal places
            self.spin_box.setValue(float(self.config_value.value))

        # Apply constraints if available
        if self.config_value.min_value is not None:
            if isinstance(self.spin_box, QSpinBox):
                self.spin_box.setMinimum(int(self.config_value.min_value))
            else:
                self.spin_box.setMinimum(self.config_value.min_value)
        if self.config_value.max_value is not None:
            if isinstance(self.spin_box, QSpinBox):
                self.spin_box.setMaximum(int(self.config_value.max_value))
            else:
                self.spin_box.setMaximum(self.config_value.max_value)

        # Modern styling
        self.spin_box.setStyleSheet(
            f"""
            QSpinBox, QDoubleSpinBox {{
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: rgba(255, 255, 255, 0.05);
                color: {Colors.TEXT_PRIMARY};
                min-width: 150px;
                font-weight: 500;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {Colors.PRIMARY_ACCENT};
                background-color: rgba(33, 150, 243, 0.1);
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {Colors.BORDER_HOVER};
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {Colors.BORDER};
                background-color: rgba(255, 255, 255, 0.05);
                border-top-right-radius: 8px;
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                border-left: 1px solid {Colors.BORDER};
                background-color: rgba(255, 255, 255, 0.05);
                border-bottom-right-radius: 8px;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: rgba(33, 150, 243, 0.2);
            }}
        """
        )

        layout.addWidget(self.spin_box)
        layout.addStretch()

    def connect_signals(self) -> None:
        """Connect spin box signals"""
        self.spin_box.valueChanged.connect(self.on_value_changed)

    def get_value(self) -> Any:
        """Get spin box value"""
        return self.spin_box.value()

    def set_value(self, value: Any) -> None:
        """Set spin box value"""
        if isinstance(self.spin_box, QSpinBox):
            self.spin_box.setValue(int(value))
        else:
            self.spin_box.setValue(float(value))
