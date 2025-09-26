"""
GUI Resources Package

Resources for icons, styles, and other assets.
"""

# Try to import Qt resources if they exist
try:
    from . import resources_rc  # noqa: F401
    _QT_RESOURCES_LOADED = True
except ImportError:
    _QT_RESOURCES_LOADED = False

# Resource availability status
def resources_available() -> bool:
    """Check if Qt resources are available"""
    return _QT_RESOURCES_LOADED

def build_resources_hint() -> str:
    """Get hint for building resources"""
    return (
        "Qt resources not found. To build resources:\n"
        "1. Add icon files to src/ui/gui/resources/icons/\n"
        "2. Run: python src/ui/gui/resources/build_resources.py\n"
        "3. Or use: pyside6-rcc resources.qrc -o resources_rc.py"
    )