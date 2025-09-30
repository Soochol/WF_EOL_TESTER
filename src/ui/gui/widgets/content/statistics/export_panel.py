"""Export Options Panel

Export statistics in various formats (CSV, Excel, PDF, JSON).
"""

# Standard library imports
from pathlib import Path
from typing import Optional

# Third-party imports
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ExportPanel(QWidget):
    """Export options panel for statistics data.

    Features:
    - Export to CSV
    - Export to Excel
    - Export to PDF
    - Export to JSON
    """

    # Signals
    export_requested = Signal(str)  # format: "csv", "excel", "pdf", "json"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the export panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Export Statistics")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Export statistics data in various formats")
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")
        main_layout.addWidget(desc_label)

        # Export options grid
        export_grid = QGridLayout()
        export_grid.setSpacing(15)

        # CSV export
        csv_group = self.create_export_group(
            "CSV Export",
            "📄",
            "Export data as comma-separated values",
            "Export to CSV",
            "csv"
        )
        export_grid.addWidget(csv_group, 0, 0)

        # Excel export
        excel_group = self.create_export_group(
            "Excel Export",
            "📊",
            "Export data as Excel spreadsheet",
            "Export to Excel",
            "excel"
        )
        export_grid.addWidget(excel_group, 0, 1)

        # PDF export
        pdf_group = self.create_export_group(
            "PDF Export",
            "📑",
            "Export formatted statistics report",
            "Export to PDF",
            "pdf"
        )
        export_grid.addWidget(pdf_group, 1, 0)

        # JSON export
        json_group = self.create_export_group(
            "JSON Export",
            "📦",
            "Export raw data in JSON format",
            "Export to JSON",
            "json"
        )
        export_grid.addWidget(json_group, 1, 1)

        main_layout.addLayout(export_grid)
        main_layout.addStretch()

    def create_export_group(
        self,
        title: str,
        icon: str,
        description: str,
        button_text: str,
        format_type: str
    ) -> QGroupBox:
        """Create an export option group.

        Args:
            title: Group title
            icon: Emoji icon
            description: Format description
            button_text: Export button text
            format_type: Export format identifier

        Returns:
            QGroupBox containing the export option
        """
        group = QGroupBox(f"{icon} {title}")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #ffffff;
                border: 2px solid #0078d4;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #cccccc; font-size: 10pt; font-weight: normal;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Export button
        export_btn = QPushButton(button_text)
        export_btn.setMinimumHeight(35)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        export_btn.clicked.connect(lambda: self.export_data(format_type))
        layout.addWidget(export_btn)

        return group

    def export_data(self, format_type: str) -> None:
        """Handle export request.

        Args:
            format_type: Export format ("csv", "excel", "pdf", "json")
        """
        # Define file filters
        filters = {
            "csv": "CSV Files (*.csv)",
            "excel": "Excel Files (*.xlsx)",
            "pdf": "PDF Files (*.pdf)",
            "json": "JSON Files (*.json)",
        }

        # Open file dialog
        file_filter = filters.get(format_type, "All Files (*.*)")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Statistics to {format_type.upper()}",
            str(Path.home() / f"eol_statistics.{format_type}"),
            file_filter
        )

        if file_path:
            # Emit signal with format type
            self.export_requested.emit(format_type)

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Statistics exported to:\n{file_path}"
            )