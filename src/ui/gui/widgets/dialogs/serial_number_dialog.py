"""
Serial Number Dialog

Material Design 3 dialog for entering serial numbers.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SerialNumberDialog(QDialog):
    """
    Modern dialog for entering serial numbers with Material Design 3 styling.

    Features:
    - Enter key to submit
    - ESC key to cancel
    - Empty value validation
    - Auto-focus on input field
    - Material Design 3 styling
    """

    def __init__(self, default_value: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.serial_number = ""
        self.default_value = default_value

        self.setup_ui()
        self.setup_connections()

        # Set initial value if provided
        if default_value:
            self.serial_input.setText(default_value)
            self.serial_input.selectAll()

    def setup_ui(self) -> None:
        """Setup dialog UI with Material Design 3 styling"""
        self.setWindowTitle("Serial Number Required")
        self.setModal(True)
        self.setFixedSize(450, 220)

        # Remove window frame, add custom styling
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content widget with dark background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.98),
                    stop:1 rgba(35, 35, 35, 0.98));
                border: 2px solid rgba(33, 150, 243, 0.5);
                border-radius: 16px;
            }
        """)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel("🔢")
        icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        header_layout.addWidget(icon_label)

        title_label = QLabel("Serial Number Required")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        content_layout.addLayout(header_layout)

        # Description
        desc_label = QLabel("Please enter the serial number for this test.")
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #cccccc;
            background: transparent;
            border: none;
            margin-left: 40px;
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        # Serial number input
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter serial number...")
        self.serial_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                padding: 12px 15px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: rgba(33, 150, 243, 0.15);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        content_layout.addWidget(self.serial_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(100, 40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #cccccc;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
                border-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedSize(100, 40)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        content_layout.addLayout(button_layout)

        main_layout.addWidget(content_widget)

        # Auto-focus on input
        self.serial_input.setFocus()

    def setup_connections(self) -> None:
        """Setup signal connections"""
        self.ok_btn.clicked.connect(self._on_ok_clicked)
        self.cancel_btn.clicked.connect(self.reject)
        self.serial_input.returnPressed.connect(self._on_ok_clicked)

    def _on_ok_clicked(self) -> None:
        """Handle OK button click with validation"""
        serial = self.serial_input.text().strip()

        if not serial:
            # Show validation feedback
            self.serial_input.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(244, 67, 54, 0.15);
                    border: 2px solid rgba(244, 67, 54, 0.8);
                    border-radius: 10px;
                    padding: 12px 15px;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 500;
                }
                QLineEdit::placeholder {
                    color: rgba(255, 255, 255, 0.6);
                }
            """)
            self.serial_input.setPlaceholderText("Serial number is required!")
            self.serial_input.setFocus()
            return

        self.serial_number = serial
        self.accept()

    def get_serial_number(self) -> str:
        """Get the entered serial number"""
        return self.serial_number

    def keyPressEvent(self, event):
        """Handle key press events (ESC to cancel)"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
