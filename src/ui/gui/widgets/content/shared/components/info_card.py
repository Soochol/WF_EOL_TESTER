"""Reusable information card component.

Provides a standardized card component for displaying information with consistent styling,
icons, and layout across all content widgets.
"""

# Standard library imports
from enum import Enum
from typing import NamedTuple, Optional

# Third-party imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Local folder imports
from ..styles.colors import ThemeType
from ..styles.fonts import Fonts
from ..styles.widgets import WidgetStyles


class InfoCardType(Enum):
    """Information card types."""

    DEFAULT = "default"
    STATUS = "status"
    METRIC = "metric"
    ACTION = "action"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class InfoCardConfig(NamedTuple):
    """Configuration for info card component."""

    title: str
    content: str = ""
    card_type: InfoCardType = InfoCardType.DEFAULT
    icon: Optional[str] = None
    clickable: bool = False
    show_border: bool = True
    compact: bool = False
    theme: ThemeType = ThemeType.DARK


class InfoCard(QFrame):
    """Reusable information card component.

    Features:
    - Consistent styling across all card types
    - Optional icon display
    - Clickable cards with hover effects
    - Compact and full-size variants
    - Theme support
    - Status-specific color coding
    """

    clicked = Signal()

    def __init__(self, config: InfoCardConfig, parent: Optional[QWidget] = None):
        """Initialize info card.

        Args:
            config: Card configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.styles = WidgetStyles(config.theme)

        # Widget references
        self.title_label: Optional[QLabel] = None
        self.content_label: Optional[QLabel] = None
        self.icon_label: Optional[QLabel] = None
        self.action_button: Optional[QPushButton] = None

        self.setup_ui()
        self.apply_styling()

        # Make clickable if configured
        if config.clickable:
            self.setup_click_behavior()

    def setup_ui(self) -> None:
        """Setup the card UI layout."""
        # Main layout
        if self.config.compact:
            compact_layout = QHBoxLayout(self)
            compact_layout.setSpacing(8)
            compact_layout.setContentsMargins(8, 6, 8, 6)
            # Create compact header
            self._create_compact_header(compact_layout)
        else:
            vertical_layout = QVBoxLayout(self)
            vertical_layout.setSpacing(10)
            vertical_layout.setContentsMargins(12, 10, 12, 10)
            # Create header section
            self._create_header_section(vertical_layout)
            # Create content section
            if self.config.content:
                self._create_content_section(vertical_layout)
            # Create action section if card is action type
            if self.config.card_type == InfoCardType.ACTION:
                self._create_action_section(vertical_layout)

    def _create_header_section(self, main_layout: QVBoxLayout) -> None:
        """Create header section with title and optional icon.

        Args:
            main_layout: Main card layout
        """
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Icon (if provided)
        if self.config.icon:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(24, 24)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._update_icon()
            header_layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel(self.config.title)
        self.title_label.setWordWrap(True)
        header_layout.addWidget(self.title_label)

        # Add stretch to push content to left
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

    def _create_compact_header(self, main_layout: QHBoxLayout) -> None:
        """Create compact header for horizontal layout.

        Args:
            main_layout: Main card layout
        """
        # Icon (if provided)
        if self.config.icon:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(16, 16)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._update_icon()
            main_layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel(self.config.title)
        self.title_label.setWordWrap(False)
        main_layout.addWidget(self.title_label)

        # Content (if provided)
        if self.config.content:
            self.content_label = QLabel(self.config.content)
            self.content_label.setWordWrap(False)
            main_layout.addWidget(self.content_label)

        # Add stretch
        main_layout.addStretch()

    def _create_content_section(self, main_layout: QVBoxLayout) -> None:
        """Create content section.

        Args:
            main_layout: Main card layout
        """
        self.content_label = QLabel(self.config.content)
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(self.content_label)

    def _create_action_section(self, main_layout: QVBoxLayout) -> None:
        """Create action section for action cards.

        Args:
            main_layout: Main card layout
        """
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.action_button = QPushButton("Action")
        self.action_button.clicked.connect(self.clicked.emit)
        action_layout.addWidget(self.action_button)

        main_layout.addLayout(action_layout)

    def _update_icon(self) -> None:
        """Update icon display."""
        if not self.icon_label or not self.config.icon:
            return

        # Try to load icon as emoji or text first
        self.icon_label.setText(self.config.icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def apply_styling(self) -> None:
        """Apply card-specific styling."""
        # Base card styling
        card_style = self._get_card_base_style()

        # Type-specific styling
        type_style = self._get_type_specific_style()

        # Combined styling
        self.setStyleSheet(card_style + type_style)

        # Apply font styling to labels
        if self.title_label:
            if self.config.compact:
                font = Fonts.LABEL_BOLD
            else:
                font = Fonts.HEADING_SMALL
            self.title_label.setFont(QFont(font.family, font.size, font.weight))

        if self.content_label:
            font = Fonts.BODY_NORMAL if not self.config.compact else Fonts.BODY_SMALL
            self.content_label.setFont(QFont(font.family, font.size, font.weight))

        if self.icon_label:
            icon_size = 16 if self.config.compact else 20
            self.icon_label.setStyleSheet(f"font-size: {icon_size}px; font-weight: bold;")

    def _get_card_base_style(self) -> str:
        """Get base card styling.

        Returns:
            str: Base CSS styling
        """
        colors = self.styles.colors

        border_style = f"1px solid {colors.border_primary}" if self.config.show_border else "none"

        hover_style = ""
        if self.config.clickable:
            hover_style = f"""
            InfoCard:hover {{
                background-color: {colors.background_elevated};
                border-color: {colors.border_focus};
            }}
            """

        return f"""
        InfoCard {{
            background-color: {colors.background_secondary};
            border: {border_style};
            border-radius: 6px;
        }}
        {hover_style}
        """

    def _get_type_specific_style(self) -> str:
        """Get type-specific styling.

        Returns:
            str: Type-specific CSS styling
        """
        colors = self.styles.colors

        type_styles = {
            InfoCardType.STATUS: f"""
            InfoCard {{
                border-left: 4px solid {colors.info};
            }}
            """,
            InfoCardType.METRIC: f"""
            InfoCard {{
                border-left: 4px solid {colors.accent_primary};
            }}
            """,
            InfoCardType.SUCCESS: f"""
            InfoCard {{
                border-left: 4px solid {colors.success};
                background-color: {colors.background_secondary};
            }}
            """,
            InfoCardType.WARNING: f"""
            InfoCard {{
                border-left: 4px solid {colors.warning};
                background-color: {colors.background_secondary};
            }}
            """,
            InfoCardType.ERROR: f"""
            InfoCard {{
                border-left: 4px solid {colors.error};
                background-color: {colors.background_secondary};
            }}
            """,
            InfoCardType.ACTION: f"""
            InfoCard {{
                border: 2px solid {colors.accent_primary};
            }}
            """,
        }

        return type_styles.get(self.config.card_type, "")

    def setup_click_behavior(self) -> None:
        """Setup click behavior for clickable cards."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click for more information")

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events.

        Args:
            event: Mouse press event
        """
        if self.config.clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def update_content(self, title: Optional[str] = None, content: Optional[str] = None) -> None:
        """Update card content.

        Args:
            title: New title (optional)
            content: New content (optional)
        """
        if title is not None and self.title_label:
            self.title_label.setText(title)

        if content is not None and self.content_label:
            self.content_label.setText(content)

    def update_icon(self, icon: str) -> None:
        """Update card icon.

        Args:
            icon: New icon text or emoji
        """
        self.config = self.config._replace(icon=icon)
        self._update_icon()

    def set_card_type(self, card_type: InfoCardType) -> None:
        """Change card type and update styling.

        Args:
            card_type: New card type
        """
        self.config = self.config._replace(card_type=card_type)
        self.apply_styling()

    def set_clickable(self, clickable: bool) -> None:
        """Enable or disable click behavior.

        Args:
            clickable: Whether the card should be clickable
        """
        self.config = self.config._replace(clickable=clickable)

        if clickable:
            self.setup_click_behavior()
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setToolTip("")

        self.apply_styling()

    def get_config(self) -> InfoCardConfig:
        """Get current card configuration.

        Returns:
            InfoCardConfig: Current configuration
        """
        return self.config


def create_info_card(
    title: str,
    content: str = "",
    card_type: InfoCardType = InfoCardType.DEFAULT,
    icon: Optional[str] = None,
    clickable: bool = False,
    compact: bool = False,
    parent: Optional[QWidget] = None,
) -> InfoCard:
    """Factory function to create info cards easily.

    Args:
        title: Card title
        content: Card content
        card_type: Type of card
        icon: Icon text or emoji
        clickable: Whether card is clickable
        compact: Whether to use compact layout
        parent: Parent widget

    Returns:
        InfoCard: Configured info card
    """
    config = InfoCardConfig(
        title=title,
        content=content,
        card_type=card_type,
        icon=icon,
        clickable=clickable,
        compact=compact,
    )

    return InfoCard(config, parent)


def create_status_card(
    title: str, status: str, icon: str = "ℹ️", parent: Optional[QWidget] = None
) -> InfoCard:
    """Create a status information card.

    Args:
        title: Status title
        status: Status description
        icon: Status icon
        parent: Parent widget

    Returns:
        InfoCard: Status card
    """
    return create_info_card(
        title=title, content=status, card_type=InfoCardType.STATUS, icon=icon, parent=parent
    )


def create_metric_card(
    title: str,
    value: str,
    icon: str = "📊",
    clickable: bool = True,
    parent: Optional[QWidget] = None,
) -> InfoCard:
    """Create a metric information card.

    Args:
        title: Metric title
        value: Metric value
        icon: Metric icon
        clickable: Whether card is clickable
        parent: Parent widget

    Returns:
        InfoCard: Metric card
    """
    return create_info_card(
        title=title,
        content=value,
        card_type=InfoCardType.METRIC,
        icon=icon,
        clickable=clickable,
        parent=parent,
    )
