"""
Temperature-Force Chart Widget

Widget for displaying temperature vs force XY scatter plot with cycle grouping.
"""

# Standard library imports
from collections import defaultdict
from typing import Dict, List, Optional

# Third-party imports
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

# Local application imports
from application.containers.application_container import ApplicationContainer
from ui.gui.services.gui_state_manager import GUIStateManager, TestResult


class TemperatureForceChartWidget(QWidget):
    """
    Temperature-Force XY chart widget.

    Shows scatter plot with temperature on X-axis and force on Y-axis.
    Points of the same cycle are connected with lines.
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
        self.connect_signals()

    def setup_chart_data(self) -> None:
        """Setup chart data structures"""
        # Data grouped by cycle: {cycle: [(temperature, force), ...]}
        self.cycle_data: Dict[int, List[tuple[float, float]]] = defaultdict(list)

        # Color scheme for different cycles
        self.cycle_colors = [
            QColor("#0078d4"),  # Blue for cycle 1
            QColor("#00b74a"),  # Green for cycle 2
            QColor("#d83b01"),  # Red for cycle 3
            QColor("#8764b8"),  # Purple for cycle 4
            QColor("#ca5010"),  # Orange for cycle 5
            QColor("#038387"),  # Teal for cycle 6
        ]

    def setup_ui(self) -> None:
        """Setup the chart UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Chart area (custom paint widget) - no group box
        self.chart_area = ChartArea(self.cycle_data, self.cycle_colors)
        main_layout.addWidget(self.chart_area)

        # Apply styling
        self.setStyleSheet(self._get_widget_style())

    def connect_signals(self) -> None:
        """Connect to state manager signals"""
        # Connect to test_result_added signal to update chart when test completes
        self.state_manager.test_result_added.connect(self._on_test_result_added)

    def _on_test_result_added(self, result: TestResult) -> None:
        """Handle new test result - extract cycle data and update chart"""
        # Extract temperature-force data from all cycles
        for cycle_data in result.cycles:
            self.add_data_point(
                cycle=cycle_data.cycle,
                temperature=cycle_data.temperature,
                force=cycle_data.force
            )

    def add_data_point(self, cycle: int, temperature: float, force: float) -> None:
        """Add a new data point for the given cycle"""
        self.cycle_data[cycle].append((temperature, force))
        self.chart_area.update()  # Trigger repaint

    def clear_data(self) -> None:
        """Clear all chart data"""
        self.cycle_data.clear()
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
        TemperatureForceChartWidget {
            background-color: transparent;
            color: #cccccc;
        }
        """


class ChartArea(QWidget):
    """
    Custom widget for drawing the temperature-force chart.
    """

    def __init__(
        self,
        cycle_data: Dict[int, List[tuple[float, float]]],
        cycle_colors: List[QColor],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.cycle_data = cycle_data
        self.cycle_colors = cycle_colors
        self.setMinimumHeight(300)
        self.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(45, 45, 45, 0.95),
                stop:1 rgba(35, 35, 35, 0.95));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        """
        )

    def paintEvent(self, event) -> None:
        """Paint the chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        rect = self.rect()
        margin = 60
        chart_rect = QRect(margin, margin, rect.width() - 2 * margin, rect.height() - 2 * margin)

        # Clear background (transparent for glassmorphism)
        painter.fillRect(rect, QColor(0, 0, 0, 0))

        if not self.cycle_data:
            # Draw empty chart with axes
            self._draw_empty_chart(painter, chart_rect)
            return

        # Calculate data ranges
        temp_range, force_range = self._calculate_ranges()

        # Draw axes and grid
        self._draw_axes(painter, chart_rect, temp_range, force_range)

        # Draw data points and lines for each cycle
        self._draw_data(painter, chart_rect, temp_range, force_range)

        # Draw legend
        self._draw_legend(painter, rect)

    def _calculate_ranges(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Calculate temperature and force ranges from data"""
        all_temps = []
        all_forces = []

        for cycle_points in self.cycle_data.values():
            for temp, force in cycle_points:
                all_temps.append(temp)
                all_forces.append(force)

        if not all_temps:
            return (20.0, 30.0), (0.0, 10.0)  # Default ranges

        # Add 10% margin to ranges
        temp_min, temp_max = min(all_temps), max(all_temps)
        force_min, force_max = min(all_forces), max(all_forces)

        temp_margin = (temp_max - temp_min) * 0.1 or 1.0
        force_margin = (force_max - force_min) * 0.1 or 1.0

        temp_range = (temp_min - temp_margin, temp_max + temp_margin)
        force_range = (max(0, force_min - force_margin), force_max + force_margin)

        return temp_range, force_range

    def _draw_empty_chart(self, painter: QPainter, rect: QRect) -> None:
        """Draw empty chart with axes and labels"""
        self._draw_axes(painter, rect, (20.0, 30.0), (0.0, 10.0))

        # Draw "No Data" message
        painter.setPen(QColor("#888888"))
        font = QFont()
        font.setPointSize(16)
        painter.setFont(font)
        painter.drawText(
            rect, Qt.AlignmentFlag.AlignCenter, "No Data Available\nStart a test to see results"
        )

    def _draw_axes(
        self,
        painter: QPainter,
        rect: QRect,
        temp_range: tuple[float, float],
        force_range: tuple[float, float],
    ) -> None:
        """Draw chart axes, grid, and labels"""
        pen = QPen(QColor("#555555"), 2)
        painter.setPen(pen)

        # Draw main axes
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())  # X-axis
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())  # Y-axis

        # Draw grid lines (modern subtle style)
        grid_pen = QPen(QColor("#3a3a3a"), 1)
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)

        # Horizontal grid lines (force)
        for i in range(1, 6):
            y = rect.bottom() - (i * rect.height() // 6)
            painter.drawLine(rect.left(), y, rect.right(), y)

        # Vertical grid lines (temperature)
        for i in range(1, 8):
            x = rect.left() + (i * rect.width() // 8)
            painter.drawLine(x, rect.top(), x, rect.bottom())

        # Draw axis labels (modern style)
        painter.setPen(QColor("#999999"))
        font = QFont()
        font.setPointSize(11)
        painter.setFont(font)

        # Y-axis labels (Force)
        temp_min, temp_max = temp_range
        force_min, force_max = force_range

        for i in range(7):
            force_val = force_min + (force_max - force_min) * i / 6
            y = rect.bottom() - (i * rect.height() // 6)
            painter.drawText(23, y + 5, f"{force_val:.1f}")

        # X-axis labels (Temperature)
        for i in range(9):
            temp_val = temp_min + (temp_max - temp_min) * i / 8
            x = rect.left() + (i * rect.width() // 8)
            painter.drawText(x - 15, rect.height() + 85, f"{temp_val:.1f}")

        # Axis titles (modern bold)
        painter.setPen(QColor("#ffffff"))
        font.setPointSize(13)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        # X-axis title
        painter.drawText(rect.center().x() - 60, rect.height() + 110, "Temperature (°C)")

        # Y-axis title (rotated)
        painter.save()
        painter.translate(15, rect.center().y())
        painter.rotate(-90)
        painter.drawText(-50, 0, "Force (kgf)")
        painter.restore()

    def _draw_data(
        self,
        painter: QPainter,
        rect: QRect,
        temp_range: tuple[float, float],
        force_range: tuple[float, float],
    ) -> None:
        """Draw data points and connecting lines for each cycle"""
        temp_min, temp_max = temp_range
        force_min, force_max = force_range

        temp_span = temp_max - temp_min
        force_span = force_max - force_min

        if temp_span == 0 or force_span == 0:
            return

        for cycle, points in self.cycle_data.items():
            if not points:
                continue

            # Get color for this cycle
            color = self.cycle_colors[(cycle - 1) % len(self.cycle_colors)]

            # Convert data points to pixel coordinates
            pixel_points = []
            for temp, force in points:
                x = rect.left() + int((temp - temp_min) / temp_span * rect.width())
                y = rect.bottom() - int((force - force_min) / force_span * rect.height())
                pixel_points.append((x, y))

            # Draw connecting lines between points of same cycle
            if len(pixel_points) > 1:
                line_pen = QPen(color, 2)
                painter.setPen(line_pen)

                for i in range(len(pixel_points) - 1):
                    x1, y1 = pixel_points[i]
                    x2, y2 = pixel_points[i + 1]
                    painter.drawLine(x1, y1, x2, y2)

            # Draw data points (circles)
            point_pen = QPen(color, 2)
            brush = QBrush(color)
            painter.setPen(point_pen)
            painter.setBrush(brush)

            for x, y in pixel_points:
                painter.drawEllipse(x - 4, y - 4, 8, 8)  # 8x8 pixel circles

    def _draw_legend(self, painter: QPainter, rect: QRect) -> None:
        """Draw legend showing cycle colors"""
        if not self.cycle_data:
            return

        painter.setPen(QColor("#cccccc"))
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)

        # Legend position (top-right corner)
        legend_x = rect.width() - 120
        legend_y = 20

        painter.drawText(legend_x, legend_y, "Cycles:")

        for i, cycle in enumerate(sorted(self.cycle_data.keys())):
            color = self.cycle_colors[(cycle - 1) % len(self.cycle_colors)]
            y = legend_y + 25 + i * 20

            # Draw colored circle
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(legend_x, y - 6, 10, 10)

            # Draw cycle label
            painter.setPen(QColor("#cccccc"))
            painter.drawText(legend_x + 20, y, f"Cycle {cycle}")
