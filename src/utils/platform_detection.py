"""
Platform detection utilities for Windows version-specific dependency management.
"""

# Standard library imports
import platform
import sys
from typing import Any, Dict, Optional, Tuple


class WindowsVersionDetector:
    """Detects Windows version and provides compatibility information."""

    # Windows version mappings (major.minor.build)
    WINDOWS_VERSIONS = {
        "6.1": "Windows 7",
        "6.2": "Windows 8",
        "6.3": "Windows 8.1",
        "10.0.10240": "Windows 10 1507",
        "10.0.10586": "Windows 10 1511",
        "10.0.14393": "Windows 10 1607",
        "10.0.15063": "Windows 10 1703",
        "10.0.16299": "Windows 10 1709",
        "10.0.17134": "Windows 10 1803",
        "10.0.17763": "Windows 10 1809",  # Qt 6 minimum requirement
        "10.0.18362": "Windows 10 1903",
        "10.0.18363": "Windows 10 1909",
        "10.0.19041": "Windows 10 2004",
        "10.0.19042": "Windows 10 20H2",
        "10.0.19043": "Windows 10 21H1",
        "10.0.19044": "Windows 10 21H2",
        "10.0.19045": "Windows 10 22H2",
        "10.0.22000": "Windows 11 21H2",
        "10.0.22621": "Windows 11 22H2",
        "10.0.22631": "Windows 11 23H2",
        "10.0.26100": "Windows 11 24H2",
    }

    # PySide6 compatibility matrix
    PYSIDE6_COMPATIBILITY = {
        "legacy": {
            "windows_versions": ["6.1", "6.2", "6.3"],  # Windows 7, 8, 8.1
            "pyside6_version": ">=6.1.0,<6.2.0",
            "python_version": ">=3.6,<3.9",
            "qt_version": "6.1.x",
            "support_status": "deprecated",
        },
        "legacy_win10": {
            "windows_versions": [
                "10.0.10240",
                "10.0.10586",
                "10.0.14393",
                "10.0.15063",
                "10.0.16299",
                "10.0.17134",
            ],
            "pyside6_version": ">=6.1.0,<6.2.0",
            "python_version": ">=3.6,<3.9",
            "qt_version": "6.1.x",
            "support_status": "limited",
        },
        "modern": {
            "windows_versions": [
                "10.0.17763",
                "10.0.18362",
                "10.0.18363",
                "10.0.19041",
                "10.0.19042",
                "10.0.19043",
                "10.0.19044",
                "10.0.19045",
            ],
            "pyside6_version": ">=6.2.0,<6.8.0",
            "python_version": ">=3.9,<3.14",
            "qt_version": "6.2.x - 6.7.x",
            "support_status": "active",
        },
        "windows11": {
            "windows_versions": ["10.0.22000", "10.0.22621", "10.0.22631", "10.0.26100"],
            "pyside6_version": ">=6.5.0,<6.8.0",
            "python_version": ">=3.9,<3.14",
            "qt_version": "6.5.x - 6.7.x",
            "support_status": "recommended",
        },
    }

    @staticmethod
    def get_windows_version() -> Optional[Tuple[str, str]]:
        """
        Get detailed Windows version information.

        Returns:
            Tuple of (version_key, version_name) or None if not Windows
        """
        if platform.system() != "Windows":
            return None

        version = platform.version()

        # Try to match exact version first
        for version_key, version_name in WindowsVersionDetector.WINDOWS_VERSIONS.items():
            if version.startswith(version_key):
                return (version_key, version_name)

        # Fallback to major.minor matching
        version_parts = version.split(".")
        if len(version_parts) >= 2:
            major_minor = f"{version_parts[0]}.{version_parts[1]}"
            if major_minor in ["6.1", "6.2", "6.3"]:
                return (major_minor, WindowsVersionDetector.WINDOWS_VERSIONS[major_minor])
            elif major_minor == "10.0":
                return ("10.0.unknown", f"Windows 10/11 (Build {version})")

        return (version, f"Unknown Windows version {version}")

    @staticmethod
    def get_pyside6_compatibility() -> Dict[str, Any]:
        """
        Get PySide6 compatibility information for current platform.

        Returns:
            Dictionary with compatibility information
        """
        windows_info = WindowsVersionDetector.get_windows_version()

        if not windows_info:
            return {
                "platform": "non-windows",
                "pyside6_version": ">=6.5.3,<6.8.0",
                "python_version": ">=3.9,<3.14",
                "support_status": "standard",
            }

        version_key, version_name = windows_info

        # Find matching compatibility profile
        for profile_name, profile_info in WindowsVersionDetector.PYSIDE6_COMPATIBILITY.items():
            if any(version_key.startswith(v) for v in profile_info["windows_versions"]):
                return {
                    "platform": "windows",
                    "windows_version": version_name,
                    "windows_version_key": version_key,
                    "profile": profile_name,
                    "pyside6_version": profile_info["pyside6_version"],
                    "python_version": profile_info["python_version"],
                    "qt_version": profile_info["qt_version"],
                    "support_status": profile_info["support_status"],
                }

        # Default to modern profile for unknown versions
        return {
            "platform": "windows",
            "windows_version": version_name,
            "windows_version_key": version_key,
            "profile": "modern",
            "pyside6_version": ">=6.2.0,<6.8.0",
            "python_version": ">=3.9,<3.14",
            "qt_version": "6.2.x - 6.7.x",
            "support_status": "unknown",
        }

    @staticmethod
    def get_recommended_install_command() -> str:
        """
        Get recommended installation command for current platform.

        Returns:
            UV command string for installing appropriate PySide6 version
        """
        compat_info = WindowsVersionDetector.get_pyside6_compatibility()

        if compat_info["platform"] != "windows":
            return "uv sync"

        profile = compat_info["profile"]

        if profile == "legacy":
            return "uv add 'pyside6>=6.1.0,<6.2.0'"
        elif profile == "legacy_win10":
            return "uv add 'pyside6>=6.1.0,<6.2.0'"
        elif profile == "modern":
            return "uv add 'pyside6>=6.2.0,<6.8.0'"
        elif profile == "windows11":
            return "uv add 'pyside6>=6.5.0,<6.8.0'"
        else:
            return "uv sync"

    @staticmethod
    def check_python_compatibility() -> Dict[str, Any]:
        """
        Check if current Python version is compatible with recommended PySide6.

        Returns:
            Dictionary with compatibility check results
        """
        compat_info = WindowsVersionDetector.get_pyside6_compatibility()
        current_python = f"{sys.version_info.major}.{sys.version_info.minor}"

        # Parse version requirements
        python_req: str = compat_info["python_version"]

        # Simple compatibility check (this could be enhanced with packaging library)
        compatible = True
        warning = None

        if "3.6" in python_req and sys.version_info >= (3, 9):
            compatible = False
            warning = (
                f"Python {current_python} too new for legacy PySide6. Consider using Python 3.8."
            )
        elif "3.9" in python_req and sys.version_info < (3, 9):
            compatible = False
            warning = f"Python {current_python} too old for modern PySide6. Consider upgrading to Python 3.9+."
        elif sys.version_info >= (3, 14):
            compatible = False
            warning = f"Python {current_python} not yet supported by PySide6."

        return {
            "current_python": current_python,
            "required_python": python_req,
            "compatible": compatible,
            "warning": warning,
            "compatibility_info": compat_info,
        }


def main():
    """Command-line interface for platform detection."""
    print("=== Windows Platform Detection for PySide6 ===")

    # Basic platform info
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Python: {sys.version}")
    print()

    # Windows version detection
    windows_info = WindowsVersionDetector.get_windows_version()
    if windows_info:
        version_key, version_name = windows_info
        print(f"Windows Version: {version_name} ({version_key})")
    else:
        print("Not a Windows system")
        return

    # PySide6 compatibility
    compat_info = WindowsVersionDetector.get_pyside6_compatibility()
    print(f"\n=== PySide6 Compatibility Profile: {compat_info['profile']} ===")
    print(f"Recommended PySide6: {compat_info['pyside6_version']}")
    print(f"Required Python: {compat_info['python_version']}")
    print(f"Qt Version: {compat_info['qt_version']}")
    print(f"Support Status: {compat_info['support_status']}")

    # Python compatibility check
    python_compat = WindowsVersionDetector.check_python_compatibility()
    print("\n=== Python Compatibility ===")
    print(f"Current Python: {python_compat['current_python']}")
    print(f"Required Python: {python_compat['required_python']}")
    print(f"Compatible: {'YES' if python_compat['compatible'] else 'NO'}")
    if python_compat["warning"]:
        print(f"Warning: {python_compat['warning']}")

    # Installation recommendation
    install_cmd = WindowsVersionDetector.get_recommended_install_command()
    print("\n=== Recommended Installation ===")
    print(f"Command: {install_cmd}")


if __name__ == "__main__":
    main()
