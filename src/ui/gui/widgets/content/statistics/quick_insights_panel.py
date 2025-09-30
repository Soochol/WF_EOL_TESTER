"""Quick Insights Panel

Provides actionable insights and quick actions for efficient statistics usage.
"""

# Standard library imports
from typing import Optional, List, Dict, Any

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)


class InsightCard(QFrame):
    """Individual insight card with icon, message, and action button."""

    action_clicked = Signal(str)  # Emits insight type

    def __init__(
        self,
        icon: str,
        title: str,
        message: str,
        action_text: str,
        insight_type: str,
        severity: str = "info",
        parent: Optional[QWidget] = None,
    ):
        """Initialize insight card.

        Args:
            icon: Emoji icon for the insight
            title: Short title
            message: Detailed message
            action_text: Button text for action
            insight_type: Type identifier for action handling
            severity: Severity level (info, warning, critical, success)
        """
        super().__init__(parent)
        self.insight_type = insight_type
        self.severity = severity
        self.setup_ui(icon, title, message, action_text)

    def setup_ui(self, icon: str, title: str, message: str, action_text: str) -> None:
        """Setup the insight card UI."""
        # Color mapping by severity
        colors = {
            "info": "#2196F3",
            "warning": "#FF9800",
            "critical": "#F44336",
            "success": "#00D9A5",
        }
        accent_color = colors.get(self.severity, "#2196F3")

        # Modern card styling
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 45, 0.95),
                    stop:1 rgba(35, 35, 35, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 4px solid {accent_color};
                border-radius: 12px;
                padding: 15px;
                margin: 5px 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(55, 55, 55, 0.95),
                    stop:1 rgba(45, 45, 45, 0.95));
                border-left: 4px solid {accent_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header: icon + title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {accent_color};")
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #cccccc; font-size: 12px; line-height: 1.4;")
        layout.addWidget(message_label)

        # Action button
        action_btn = QPushButton(action_text)
        action_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({self._hex_to_rgb(accent_color)}, 0.2);
                color: {accent_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 5px;
            }}
            QPushButton:hover {{
                background-color: rgba({self._hex_to_rgb(accent_color)}, 0.3);
            }}
            QPushButton:pressed {{
                background-color: rgba({self._hex_to_rgb(accent_color)}, 0.4);
            }}
        """)
        action_btn.clicked.connect(lambda: self.action_clicked.emit(self.insight_type))
        layout.addWidget(action_btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for rgba()."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"


class QuickInsightsPanel(QWidget):
    """Panel displaying actionable insights and quick actions.

    Provides:
    - Automated insights based on data analysis
    - Quick action buttons for common tasks
    - Anomaly detection alerts
    - Performance recommendations
    """

    insight_action = Signal(str)  # Emits action type for parent handling

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.insights: List[InsightCard] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the quick insights panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_label = QLabel("💡 Quick Insights & Actions")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("""
            color: #ffffff;
            padding: 12px;
            background-color: rgba(33, 150, 243, 0.1);
            border-left: 4px solid #2196F3;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header_label)

        # Insights container (scrollable)
        self.insights_layout = QVBoxLayout()
        self.insights_layout.setSpacing(8)
        main_layout.addLayout(self.insights_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

    def update_insights(self, statistics_data: Dict[str, Any]) -> None:
        """Update insights based on statistics data.

        Args:
            statistics_data: Dictionary containing statistics analysis results
        """
        # Clear existing insights
        self.clear_insights()

        # Generate insights based on data
        insights = self._generate_insights(statistics_data)

        # Add insight cards
        for insight in insights:
            card = InsightCard(
                icon=insight["icon"],
                title=insight["title"],
                message=insight["message"],
                action_text=insight["action"],
                insight_type=insight["type"],
                severity=insight["severity"],
            )
            card.action_clicked.connect(self.insight_action.emit)
            self.insights.append(card)
            self.insights_layout.addWidget(card)

    def _generate_insights(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable insights from statistics data.

        Args:
            data: Statistics data dictionary

        Returns:
            List of insight dictionaries
        """
        insights = []

        # Extract key metrics
        pass_rate = data.get("pass_rate", 0.0)
        total_tests = data.get("total_tests", 0)
        failed_tests = data.get("failed_tests", 0)
        avg_duration = data.get("avg_duration", 0.0)

        # Insight 1: Low pass rate warning
        if pass_rate < 90.0 and total_tests > 10:
            insights.append({
                "icon": "⚠️",
                "title": "Low Pass Rate Detected",
                "message": f"Pass rate is {pass_rate:.1f}% ({failed_tests} failures). "
                           "This may indicate hardware issues or parameter misalignment.",
                "action": "View Failed Tests",
                "type": "view_failures",
                "severity": "critical",
            })

        # Insight 2: High pass rate success
        elif pass_rate >= 95.0 and total_tests > 50:
            insights.append({
                "icon": "✅",
                "title": "Excellent Test Quality",
                "message": f"Pass rate is {pass_rate:.1f}% with {total_tests} tests. "
                           "System performance is stable.",
                "action": "View Report",
                "type": "view_report",
                "severity": "success",
            })

        # Insight 3: Duration analysis
        if avg_duration > 30.0:  # Assuming 30s is threshold
            insights.append({
                "icon": "⏱️",
                "title": "Long Test Duration",
                "message": f"Average test duration is {avg_duration:.1f}s. "
                           "Consider reviewing test parameters for optimization.",
                "action": "View Performance",
                "type": "view_performance",
                "severity": "warning",
            })

        # Insight 4: Sample size recommendation
        if total_tests < 30:
            insights.append({
                "icon": "📊",
                "title": "Limited Sample Size",
                "message": f"Only {total_tests} tests analyzed. "
                           "More data is recommended for reliable statistics.",
                "action": "Run More Tests",
                "type": "run_tests",
                "severity": "info",
            })

        # Insight 5: Export recommendation
        if total_tests >= 100:
            insights.append({
                "icon": "📥",
                "title": "Export Recommended",
                "message": f"{total_tests} tests available. "
                           "Consider exporting data for detailed analysis.",
                "action": "Export Data",
                "type": "export_data",
                "severity": "info",
            })

        # Default insight if no specific insights
        if not insights:
            insights.append({
                "icon": "📈",
                "title": "No Issues Detected",
                "message": "Statistics look normal. Continue monitoring test results.",
                "action": "Refresh Data",
                "type": "refresh",
                "severity": "success",
            })

        return insights

    def clear_insights(self) -> None:
        """Clear all insight cards."""
        for insight in self.insights:
            self.insights_layout.removeWidget(insight)
            insight.deleteLater()
        self.insights.clear()