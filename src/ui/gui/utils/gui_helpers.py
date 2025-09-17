"""
GUI Helper Utilities

Common utility functions and helpers for GUI operations.
"""

# Standard library imports
from typing import Optional, Tuple, Union

# Third-party imports
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


def center_widget_on_screen(widget: QWidget, screen: Optional[QScreen] = None) -> None:
    """
    Center widget on screen

    Args:
        widget: Widget to center
        screen: Target screen (uses primary if None)
    """
    if not screen:
        screen = QApplication.primaryScreen()

    if screen:
        screen_geometry = screen.availableGeometry()
        widget_geometry = widget.geometry()

        x = (screen_geometry.width() - widget_geometry.width()) // 2
        y = (screen_geometry.height() - widget_geometry.height()) // 2

        widget.move(screen_geometry.x() + x, screen_geometry.y() + y)


def show_error_dialog(
    parent: Optional[QWidget], title: str, message: str, detailed_text: Optional[str] = None
) -> None:
    """
    Show error dialog with optional detailed text

    Args:
        parent: Parent widget
        title: Dialog title
        message: Main error message
        detailed_text: Optional detailed error information
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    if detailed_text:
        msg_box.setDetailedText(detailed_text)

    msg_box.exec()


def show_warning_dialog(
    parent: Optional[QWidget], title: str, message: str
) -> QMessageBox.StandardButton:
    """
    Show warning dialog with OK/Cancel buttons

    Args:
        parent: Parent widget
        title: Dialog title
        message: Warning message

    Returns:
        User's button choice
    """
    return QMessageBox.warning(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Cancel,
    )


def show_info_dialog(parent: Optional[QWidget], title: str, message: str) -> None:
    """
    Show information dialog

    Args:
        parent: Parent widget
        title: Dialog title
        message: Information message
    """
    QMessageBox.information(parent, title, message)


def confirm_action(parent: Optional[QWidget], title: str, message: str) -> bool:
    """
    Show confirmation dialog

    Args:
        parent: Parent widget
        title: Dialog title
        message: Confirmation message

    Returns:
        True if user confirmed, False otherwise
    """
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    return reply == QMessageBox.StandardButton.Yes


def set_widget_size_constraints(
    widget: QWidget,
    min_size: Optional[QSize] = None,
    max_size: Optional[QSize] = None,
    fixed_size: Optional[QSize] = None,
) -> None:
    """
    Set size constraints for widget

    Args:
        widget: Widget to constrain
        min_size: Minimum size
        max_size: Maximum size
        fixed_size: Fixed size (overrides min/max)
    """
    if fixed_size:
        widget.setFixedSize(fixed_size)
    else:
        if min_size:
            widget.setMinimumSize(min_size)
        if max_size:
            widget.setMaximumSize(max_size)


def apply_widget_focus_policy(widget: QWidget, focusable: bool = True) -> None:
    """
    Set widget focus policy for accessibility

    Args:
        widget: Widget to configure
        focusable: Whether widget should be focusable
    """
    if focusable:
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    else:
        widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)


def set_widget_tooltip_and_status_tip(
    widget: QWidget, tooltip: str, status_tip: Optional[str] = None
) -> None:
    """
    Set tooltip and status tip for widget

    Args:
        widget: Widget to configure
        tooltip: Tooltip text
        status_tip: Status tip text (uses tooltip if None)
    """
    widget.setToolTip(tooltip)
    widget.setStatusTip(status_tip or tooltip)


def make_widget_accessible(
    widget: QWidget, accessible_name: str, accessible_description: Optional[str] = None
) -> None:
    """
    Configure widget accessibility properties

    Args:
        widget: Widget to configure
        accessible_name: Accessible name
        accessible_description: Accessible description
    """
    widget.setAccessibleName(accessible_name)
    if accessible_description:
        widget.setAccessibleDescription(accessible_description)
