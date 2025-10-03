"""Modern UI Components for Digital Output Control

Material Design 3 components shared with Robot Control.
Includes ModernCard, ModernButton, and StatusPill.
"""

# Re-export components from robot package for consistency
from ui.gui.widgets.content.robot.modern_components import (
    ModernCard,
    ModernButton,
    StatusPill,
)

__all__ = ["ModernCard", "ModernButton", "StatusPill"]
