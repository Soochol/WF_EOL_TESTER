"""
Skeleton Loader Widget

Animated skeleton loading placeholders for lazy-loaded content.
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from typing import List, Tuple


class SkeletonWidget(QWidget):
    """
    Single skeleton loading element with shimmer animation.
    """

    def __init__(self, width: int = 200, height: int = 20, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.shimmer_position = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_shimmer)
        self.animation_timer.start(30)  # 30ms = ~33fps

    def _update_shimmer(self):
        """Update shimmer animation position"""
        self.shimmer_position = (self.shimmer_position + 2) % (self.width() + 100)
        self.update()

    def paintEvent(self, event):
        """Custom paint with shimmer effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_color = QColor(45, 45, 45)  # #2d2d2d
        painter.fillRect(self.rect(), bg_color)

        # Shimmer gradient
        gradient = QLinearGradient(self.shimmer_position - 100, 0,
                                   self.shimmer_position + 100, 0)
        gradient.setColorAt(0.0, QColor(45, 45, 45, 0))
        gradient.setColorAt(0.5, QColor(80, 80, 80, 80))
        gradient.setColorAt(1.0, QColor(45, 45, 45, 0))

        painter.fillRect(self.rect(), gradient)


class SkeletonCard(QWidget):
    """
    Skeleton loading card with multiple elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup skeleton card layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title skeleton (wide)
        title = SkeletonWidget(300, 24)
        layout.addWidget(title)

        # Subtitle skeleton (medium)
        subtitle = SkeletonWidget(220, 18)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Content lines
        for width in [400, 380, 350, 370]:
            line = SkeletonWidget(width, 16)
            layout.addWidget(line)

        layout.addStretch()


class SkeletonDashboard(QWidget):
    """
    Skeleton loading for dashboard page.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet("""
            SkeletonDashboard {
                background-color: #1e1e1e;
            }
        """)

    def setup_ui(self):
        """Setup dashboard skeleton"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header skeleton
        header_layout = QHBoxLayout()
        header_title = SkeletonWidget(250, 32)
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        for _ in range(3):
            card = self._create_info_card_skeleton()
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # Chart area
        chart_skeleton = SkeletonWidget(800, 300)
        layout.addWidget(chart_skeleton)

        layout.addStretch()

    def _create_info_card_skeleton(self) -> QWidget:
        """Create info card skeleton"""
        card = QWidget()
        card.setFixedSize(250, 120)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(16, 16, 16, 16)

        # Card title
        title = SkeletonWidget(150, 18)
        card_layout.addWidget(title)

        # Card value
        value = SkeletonWidget(100, 32)
        card_layout.addWidget(value)

        card_layout.addStretch()

        return card


class SkeletonTable(QWidget):
    """
    Skeleton loading for table/list views.
    """

    def __init__(self, rows: int = 8, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.setup_ui()
        self.setStyleSheet("""
            SkeletonTable {
                background-color: #1e1e1e;
            }
        """)

    def setup_ui(self):
        """Setup table skeleton"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header row (wider elements)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        for width in [150, 200, 180, 120, 100]:
            header_item = SkeletonWidget(width, 20)
            header_layout.addWidget(header_item)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(10)

        # Data rows
        for _ in range(self.rows):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)
            for width in [150, 200, 180, 120, 100]:
                row_item = SkeletonWidget(width, 16)
                row_layout.addWidget(row_item)
            row_layout.addStretch()
            layout.addLayout(row_layout)

        layout.addStretch()


class SkeletonChart(QWidget):
    """
    Skeleton loading for charts/graphs.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet("""
            SkeletonChart {
                background-color: #1e1e1e;
            }
        """)

    def setup_ui(self):
        """Setup chart skeleton"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = SkeletonWidget(200, 24)
        layout.addWidget(title)

        # Chart area
        chart = SkeletonWidget(700, 350)
        layout.addWidget(chart)

        # Legend
        legend_layout = QHBoxLayout()
        for width in [80, 80, 80, 80]:
            legend_item = SkeletonWidget(width, 16)
            legend_layout.addWidget(legend_item)
        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        layout.addStretch()


def create_skeleton_for_page(page_name: str) -> QWidget:
    """
    Factory function to create appropriate skeleton for page.

    Args:
        page_name: Name of the page (dashboard, results, etc.)

    Returns:
        Skeleton widget for the page
    """
    skeletons = {
        "dashboard": SkeletonDashboard,
        "results": SkeletonTable,
        "statistics": SkeletonChart,
        "test_control": SkeletonCard,
        "hardware": SkeletonCard,
        "logs": SkeletonTable,
    }

    skeleton_class = skeletons.get(page_name, SkeletonCard)
    return skeleton_class()