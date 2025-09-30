"""
Platform Detection Utility

Utilities for detecting the current platform and determining appropriate UI scaling factors.
"""

# Standard library imports
import os
import platform
from typing import Literal


PlatformType = Literal["Windows", "Linux", "WSL"]


def detect_platform() -> PlatformType:
    """
    Detect the current platform type

    Returns:
        Platform type: "Windows", "Linux", or "WSL"
    """
    system = platform.system()

    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        # Check if running under WSL
        if is_wsl():
            return "WSL"
        else:
            return "Linux"
    else:
        # Default to Linux for other Unix-like systems
        return "Linux"


def is_wsl() -> bool:
    """
    Check if running under Windows Subsystem for Linux (WSL)

    Returns:
        True if running under WSL, False otherwise
    """
    try:
        # Check for WSL environment variables
        if "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP" in os.environ:
            return True

        # Check /proc/version for Microsoft string (WSL1 and WSL2)
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            if "microsoft" in version_info or "wsl" in version_info:
                return True

        # Check /proc/sys/kernel/osrelease for WSL signature
        with open("/proc/sys/kernel/osrelease", "r") as f:
            kernel_release = f.read().lower()
            if "microsoft" in kernel_release or "wsl" in kernel_release:
                return True

    except (FileNotFoundError, PermissionError, OSError):
        # Files don't exist or can't be read, probably not WSL
        pass

    return False


def get_default_scale_factor(platform_type: PlatformType) -> float:
    """
    Get the default UI scale factor for a given platform

    Args:
        platform_type: The detected platform type

    Returns:
        Default scale factor for the platform
    """
    scale_factors = {
        "WSL": 1.2,  # 30% larger for WSL
        "Windows": 0.8,  # Smaller size for Windows
        "Linux": 1.2,  # Slightly larger for Linux
    }

    return scale_factors.get(platform_type, 1.0)


def get_platform_info() -> dict:
    """
    Get comprehensive platform information

    Returns:
        Dictionary containing platform details
    """
    platform_type = detect_platform()

    return {
        "platform_type": platform_type,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "is_wsl": platform_type == "WSL",
        "default_scale_factor": get_default_scale_factor(platform_type),
    }
