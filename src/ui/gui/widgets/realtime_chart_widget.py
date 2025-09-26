"""
Real-time Chart Widget

Widget for displaying real-time data charts.
"""

# Standard library imports
from collections import deque
import math
from typing import Deque, Optional

# Third-party imports
from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager


class RealtimeChartWidget(QWidget):
    """
    Real-time chart widget for displaying force data.

    Shows a scrolling line chart with force measurements over time.
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
        self.setup_chart_data()
        self.setup_ui()
        self.setup_update_timer()

    def setup_ui(self) -> None:
        """Setup the chart UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create chart group
        self.chart_group = QGroupBox("Real-time Data Chart")
        self.chart_group.setFont(self._get_group_font())
        main_layout.addWidget(self.chart_group)

        # Chart content layout
        content_layout = QVBoxLayout(self.chart_group)
        content_layout.setContentsMargins(15, 20, 15, 15)

        # Chart area (custom paint widget)
        self.chart_area = ChartArea(self.force_data, self.time_data)
        content_layout.addWidget(self.chart_area)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def setup_chart_data(self) -> None:
        """Setup chart data structures"""
        self.max_data_points = 100
        self.force_data: Deque[float] = deque(maxlen=self.max_data_points)
        self.time_data: Deque[float] = deque(maxlen=self.max_data_points)
        self.time_counter = 0.0

        # Initialize with some sample data
        self._generate_sample_data()

    def setup_update_timer(self) -> None:
        """Setup timer for chart updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_chart_data)
        self.update_timer.start(500)  # Update every 500ms

    def _generate_sample_data(self) -> None:
        """Generate sample data for demonstration"""
        for i in range(50):
            time_val = i * 0.5
            # Generate sample force data with some variation
            base_force = 5.0
            variation = 0.5 * math.sin(i * 0.2) + 0.2 * math.cos(i * 0.5)
            force_val = base_force + variation

            self.time_data.append(time_val)
            self.force_data.append(force_val)

        self.time_counter = 25.0

    def _update_chart_data(self) -> None:
        """Update chart with new data point"""
        # Get current force from hardware status
        hardware_status = self.state_manager.get_hardware_status()
        current_force = hardware_status.loadcell_value

        # Add small random variation for demonstration
        # Standard library imports
        import random

        variation = random.uniform(-0.1, 0.1)
        current_force += variation

        # Add new data point
        self.time_data.append(self.time_counter)
        self.force_data.append(current_force)
        self.time_counter += 0.5

        # Update chart area
        self.chart_area.update()

    def _get_group_font(self) -> QFont:
        """Get font for group boxes"""
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def _get_widget_style(self) -> str:
        """Get widget stylesheet"""
        return """
        RealtimeChartWidget {
            background-color: #1e1e1e;
            color: #cccccc;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #404040;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        """


class ChartArea(QWidget):
    """
    Custom widget for drawing the chart.
    """

    def __init__(
        self, force_data: Deque[float], time_data: Deque[float], parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.force_data = force_data
        self.time_data = time_data
        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #404040;")

    def paintEvent(self, event) -> None:
        """Paint the chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        rect = self.rect()
        margin = 40
        chart_rect = QRect(margin, margin, rect.width() - 2 * margin, rect.height() - 2 * margin)

        # Clear background
        painter.fillRect(rect, QColor("#1a1a1a"))

        if not self.force_data or not self.time_data:
            return

        # Draw axes
        self._draw_axes(painter, chart_rect)

        # Draw data
        self._draw_data(painter, chart_rect)

    def _draw_axes(self, painter: QPainter, rect: QRect) -> None:
        """Draw chart axes and labels"""
        pen = QPen(QColor("#666666"), 1)
        painter.setPen(pen)

        # Draw axes
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())  # X-axis
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())  # Y-axis

        # Draw grid lines
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # Horizontal grid lines (force)
        for i in range(1, 6):
            y = rect.bottom() - (i * rect.height() // 6)
            painter.drawLine(rect.left(), y, rect.right(), y)

        # Vertical grid lines (time)
        for i in range(1, 10):
            x = rect.left() + (i * rect.width() // 10)
            painter.drawLine(x, rect.top(), x, rect.bottom())

        # Draw labels
        painter.setPen(QColor("#cccccc"))
        font = QFont()
        font.setPointSize(14)
        painter.setFont(font)

        # Y-axis labels (Force)
        max_force = 6.0
        for i in range(7):
            force_val = i * max_force / 6
            y = rect.bottom() - (i * rect.height() // 6)
            painter.drawText(5, y + 5, f"{force_val:.1f}")

        # X-axis label
        painter.drawText(rect.center().x() - 20, rect.height() + 35, "Time (s)")

        # Y-axis label (rotated)
        painter.save()
        painter.translate(20, rect.center().y())
        painter.rotate(-90)
        painter.drawText(-30, 0, "Force (kgf)")
        painter.restore()

    def _draw_data(self, painter: QPainter, rect: QRect) -> None:
        """Draw the data line"""
        if len(self.force_data) < 2:
            return

        pen = QPen(QColor("#00ff88"), 2)
        painter.setPen(pen)

        # Calculate scales
        force_data_list = list(self.force_data)
        time_data_list = list(self.time_data)

        if not force_data_list or not time_data_list:
            return

        max_force = 6.0
        min_force = 0.0
        force_range = max_force - min_force

        time_range = max(time_data_list) - min(time_data_list) if len(time_data_list) > 1 else 1.0
        min_time = min(time_data_list)

        # Draw the line
        points = []
        for i, (force, time) in enumerate(zip(force_data_list, time_data_list)):
            # Calculate pixel positions
            x = rect.left() + int((time - min_time) / time_range * rect.width())
            y = rect.bottom() - int((force - min_force) / force_range * rect.height())
            points.append((x, y))

        # Draw line segments
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            painter.drawLine(x1, y1, x2, y2)

        # Draw data points
        pen.setWidth(4)
        painter.setPen(pen)
        for x, y in points[-10:]:  # Show last 10 points
            painter.drawPoint(x, y)
