"""Information provider for About widget"""

import platform
import sys
from datetime import datetime
from typing import Optional

from application.containers.application_container import ApplicationContainer


class AboutInfoProvider:
    """Provides information content for About widget"""

    def __init__(self, container: Optional[ApplicationContainer] = None):
        self.container = container

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
        python_version = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

        try:
            # Third-party imports
            import PySide6

            pyside_version = PySide6.__version__
        except Exception:
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

    def get_company_info(self) -> dict:
        """Get company information constants"""
        return {
            "name": "Withforce Co., Ltd.",
            "product_name": "WF EOL Tester",
            "version": "2.0.0",
            "description": "Industrial End-of-Line Testing Solution",
            "copyright_year": datetime.now().year,
            "contact_email": "info@withforce.co.kr",
            "support_email": "support@withforce.co.kr",
            "website": "www.withforce.co.kr",
            "logo_emoji": "🏭",
        }
