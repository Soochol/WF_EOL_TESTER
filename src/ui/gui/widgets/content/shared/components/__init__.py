"""Shared components package for content widgets.

Provides reusable UI components that can be used across different content widgets:
- Information cards for displaying data
- Standardized control buttons
- Status display components
"""

# Local folder imports
from .info_card import InfoCard, InfoCardConfig


__all__ = [
    "InfoCard",
    "InfoCardConfig",
]
