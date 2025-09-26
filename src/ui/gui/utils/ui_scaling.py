"""
UI Scaling Setup

Utilities for setting up UI scaling based on platform and user settings.
"""

# Standard library imports
import os
from typing import Any, Dict

# Third-party imports
from loguru import logger

# Local folder imports
from .platform_utils import detect_platform, get_default_scale_factor


def setup_ui_scaling(settings_manager=None) -> float:
    """
    Setup UI scaling based on platform and settings.

    Args:
        settings_manager: Optional settings manager to load configuration from

    Returns:
        Applied scale factor
    """
    try:
        # Get scaling settings from configuration if available
        ui_settings = {}
        if settings_manager is not None:
            try:
                # Try to get UI settings from the settings manager
                if hasattr(settings_manager, 'get_application_config'):
                    app_config = settings_manager.get_application_config()
                    if hasattr(app_config, 'gui') and hasattr(app_config.gui, 'ui'):
                        ui_settings = app_config.gui.ui
                    elif hasattr(app_config, 'ui'):
                        ui_settings = app_config.ui
                elif hasattr(settings_manager, 'settings'):
                    ui_settings = settings_manager.settings.get("ui", {})
                else:
                    # Try direct attribute access
                    ui_settings = getattr(settings_manager, 'ui', {})
            except Exception as e:
                logger.warning(f"Could not load UI settings from settings manager: {e}")
                ui_settings = {}

        # Extract scaling configuration
        auto_platform_scale = ui_settings.get("auto_platform_scale", True)
        custom_scale_factor = ui_settings.get("scale_factor", None)

        # Determine scale factor
        if custom_scale_factor is not None:
            # Use custom scale factor
            scale_factor = float(custom_scale_factor)
            logger.info(f"Using custom scale factor: {scale_factor}")
        elif auto_platform_scale:
            # Auto platform scaling
            platform_type = detect_platform()
            scale_factor = get_default_scale_factor(platform_type)
            logger.info(f"Using auto platform scaling for {platform_type}: {scale_factor}")
        else:
            # Use default scale factor
            scale_factor = 1.0
            logger.info("Using default scale factor: 1.0")

        # Validate scale factor range
        scale_factor = max(0.5, min(3.0, scale_factor))  # Clamp between 0.5x and 3.0x

        # Apply scaling
        _apply_qt_scaling(scale_factor)

        return scale_factor

    except Exception as e:
        logger.error(f"Failed to setup UI scaling: {e}")
        # Fallback to default scaling
        _apply_qt_scaling(1.0)
        return 1.0


def _apply_qt_scaling(scale_factor: float) -> None:
    """
    Apply Qt scaling by setting environment variables

    Args:
        scale_factor: The scale factor to apply
    """
    try:
        # Set Qt scale factor
        os.environ["QT_SCALE_FACTOR"] = str(scale_factor)

        # Optional: Disable auto DPI scaling to use our manual scaling
        # This can help ensure consistent behavior across different displays
        # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"

        logger.debug(f"Applied Qt scaling: QT_SCALE_FACTOR={scale_factor}")

    except Exception as e:
        logger.error(f"Failed to apply Qt scaling: {e}")


def get_current_scale_factor() -> float:
    """
    Get the currently applied scale factor from environment

    Returns:
        Current scale factor, or 1.0 if not set
    """
    try:
        return float(os.environ.get("QT_SCALE_FACTOR", "1.0"))
    except (ValueError, TypeError):
        return 1.0


def reset_ui_scaling() -> None:
    """
    Reset UI scaling to default (1.0)
    """
    _apply_qt_scaling(1.0)


def setup_ui_scaling_from_dict(ui_config: Dict[str, Any]) -> float:
    """
    Setup UI scaling from a dictionary configuration

    Args:
        ui_config: Dictionary containing UI scaling configuration

    Returns:
        Applied scale factor
    """
    # Create a simple mock settings manager
    class MockSettingsManager:
        def __init__(self, config: Dict[str, Any]):
            self.settings = {"ui": config}

    mock_manager = MockSettingsManager(ui_config)
    return setup_ui_scaling(mock_manager)


def get_scaling_info() -> Dict[str, Any]:
    """
    Get comprehensive information about current scaling setup

    Returns:
        Dictionary containing scaling information
    """
    # Local folder imports
    from .platform_utils import get_platform_info

    platform_info = get_platform_info()
    current_scale = get_current_scale_factor()

    return {
        "platform_info": platform_info,
        "current_scale_factor": current_scale,
        "qt_scale_factor_env": os.environ.get("QT_SCALE_FACTOR"),
        "qt_auto_screen_scale_env": os.environ.get("QT_AUTO_SCREEN_SCALE_FACTOR"),
        "recommended_scale": platform_info["default_scale_factor"],
    }
