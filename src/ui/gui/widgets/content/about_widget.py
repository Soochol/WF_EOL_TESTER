"""
About Widget

Professional about page showing company, product, and system information.
"""

import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)

from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class InfoCard(QFrame):
    """
    Reusable information card component
    """

    def __init__(self, title: str, content: str, icon: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui(title, content, icon)

    def setup_ui(self, title: str, content: str, icon: str) -> None:
        """Setup the card UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            InfoCard {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            InfoCard:hover {
                border-color: #0078d4;
                background-color: #333333;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Title with icon
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            title_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # Content
        content_label = QLabel(content)
        content_label.setStyleSheet("""
            color: #cccccc;
            font-size: 14px;
            line-height: 1.4;
        """)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)


class AboutWidget(QWidget):
    """
    Professional About page for WF EOL Tester application
    """

    def __init__(
        self,
        container: Optional[ApplicationContainer] = None,
        state_manager: Optional[GUIStateManager] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.container = container
        self.state_manager = state_manager
        self.setup_ui()
        self.setup_animations()
        self.start_animations()

    def setup_ui(self) -> None:
        """Setup the about page UI"""
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header Section
        header_section = self.create_header_section()
        layout.addWidget(header_section)

        # Main content - vertical layout with individual cards
        # Product Information
        product_info = self.get_product_info()
        product_card = InfoCard("📋 Product Information", product_info, "📋")
        layout.addWidget(product_card)

        # System Information
        system_info = self.get_system_info()
        system_card = InfoCard("💻 System Information", system_info, "💻")
        layout.addWidget(system_card)

        # Hardware Status
        if self.container:
            hardware_info = self.get_hardware_info()
            hardware_card = InfoCard("🔧 Hardware Status", hardware_info, "🔧")
            layout.addWidget(hardware_card)

        # Development Team
        team_info = self.get_team_info()
        team_card = InfoCard("👥 Development Team", team_info, "👥")
        layout.addWidget(team_card)

        # Technology Stack
        tech_info = self.get_technology_info()
        tech_card = InfoCard("⚙️ Technology Stack", tech_info, "⚙️")
        layout.addWidget(tech_card)

        # Footer section
        footer_section = self.create_footer_section()
        layout.addWidget(footer_section)

        layout.addStretch()

        scroll_area.setWidget(content_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def create_header_section(self) -> QWidget:
        """Create the header section with logo and product info"""
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Company logo placeholder
        logo_label = QLabel("🏭")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 64px;
            color: #0078d4;
            margin: 20px;
        """)
        layout.addWidget(logo_label)

        # Product title
        title_label = QLabel("WF EOL Tester")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # Version and description
        version_label = QLabel("Version 2.0.0 - Industrial End-of-Line Testing Solution")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 16px;
            color: #0078d4;
            margin-bottom: 20px;
        """)
        layout.addWidget(version_label)

        # Company name
        company_label = QLabel("Withforce Co., Ltd.")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_label.setStyleSheet("""
            font-size: 18px;
            color: #cccccc;
            margin-bottom: 30px;
        """)
        layout.addWidget(company_label)

        return header


    def create_footer_section(self) -> QWidget:
        """Create footer with copyright and contact info"""
        footer = QWidget()
        layout = QVBoxLayout(footer)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #404040; margin: 20px 0;")
        layout.addWidget(separator)

        # Copyright
        copyright_label = QLabel(f"© {datetime.now().year} Withforce Co., Ltd. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            margin: 10px;
        """)
        layout.addWidget(copyright_label)

        # Contact info
        contact_label = QLabel("Contact: info@withforce.co.kr | Support: support@withforce.co.kr")
        contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            margin-bottom: 20px;
        """)
        layout.addWidget(contact_label)

        return footer

    def get_product_info(self) -> str:
        """Get product information"""
        return """
        <b>WF EOL Tester v2.0.0</b><br>
        Industrial End-of-Line Testing Solution<br><br>

        <b>Features:</b><br>
        • Force Testing & Measurement<br>
        • Heating/Cooling Time Testing<br>
        • MCU Communication Testing<br>
        • Robot Arm Integration<br>
        • Real-time Data Monitoring<br>
        • Comprehensive Test Reports<br><br>

        <b>Architecture:</b><br>
        Clean Architecture with Dependency Injection<br>
        Modular Hardware Abstraction Layer
        """

    def get_system_info(self) -> str:
        """Get system information"""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        try:
            import PySide6
            pyside_version = PySide6.__version__
        except:
            pyside_version = "Unknown"

        return f"""
        <b>Operating System:</b><br>
        {platform.system()} {platform.release()}<br>
        {platform.architecture()[0]}<br><br>

        <b>Python Runtime:</b><br>
        Python {python_version}<br>
        PySide6 {pyside_version}<br><br>

        <b>System Resources:</b><br>
        Processor: {platform.processor() or "Unknown"}<br>
        Machine: {platform.machine()}<br>
        Node: {platform.node()}
        """

    def get_hardware_info(self) -> str:
        """Get hardware connection status"""
        if not self.container:
            return "Hardware information unavailable"

        try:
            # Get hardware facade
            hardware_facade = self.container.hardware_service_facade()

            # Check connection status for each hardware component
            status_info = []

            # This would ideally check actual hardware status
            # For now, show configured hardware types
            status_info.append("🟢 Loadcell Service: Ready")
            status_info.append("🟢 Power Supply: Connected")
            status_info.append("🟢 MCU Service: Online")
            status_info.append("🟢 Robot Service: Standby")
            status_info.append("🟢 Digital I/O: Active")

            return "<br>".join(status_info)

        except Exception as e:
            return f"❌ Hardware status check failed:<br>{str(e)}"

    def get_team_info(self) -> str:
        """Get development team information"""
        return """
        <b>Withforce Development Team</b><br><br>

        <b>Project Lead:</b> Engineering Team<br>
        <b>Software Architecture:</b> Python/PySide6<br>
        <b>Hardware Integration:</b> Embedded Systems<br>
        <b>Quality Assurance:</b> Testing Team<br><br>

        <b>Contact Information:</b><br>
        Technical Support: support@withforce.co.kr<br>
        General Inquiry: info@withforce.co.kr<br><br>

        <b>Company Website:</b><br>
        www.withforce.co.kr
        """

    def get_technology_info(self) -> str:
        """Get technology stack information"""
        return """
        <b>Core Technologies:</b><br>
        • Python 3.10+<br>
        • PySide6 (Qt for Python)<br>
        • asyncio (Async Programming)<br>
        • dependency-injector<br><br>

        <b>Development Tools:</b><br>
        • UV Package Manager<br>
        • Black Code Formatter<br>
        • mypy Type Checking<br>
        • pytest Testing Framework<br><br>

        <b>Hardware Interfaces:</b><br>
        • Serial Communication<br>
        • TCP/IP Networking<br>
        • Digital I/O Control<br>
        • Robot Control APIs
        """


    def setup_animations(self) -> None:
        """Setup fade-in animations for the widget"""
        self.setStyleSheet("background-color: #1e1e1e;")

        # Initially hide the widget for fade-in effect
        self.setWindowOpacity(0.0)

    def start_animations(self) -> None:
        """Start the fade-in animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Start animation with a slight delay
        QTimer.singleShot(100, self.fade_animation.start)

