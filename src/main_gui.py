#!/usr/bin/env python3
"""
WF EOL Tester - GUI Application Entry Point

Complete PySide6 GUI application for the EOL Tester system.
Integrates with existing business logic via ApplicationContainer.
"""

# Standard library imports
# Standard library imports
# Standard library imports
# Standard library imports
from pathlib import Path
import sys
from typing import Optional

# Third-party imports
import asyncio
from loguru import logger


# PySide6 imports with detailed error diagnostics
def check_pyside6_installation():
    """Check PySide6 installation and provide detailed diagnostics with UV environment support"""
    # Standard library imports
    import os
    import platform
    import subprocess

    def run_command(cmd):
        """Run command and return output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=False)
            return result.returncode == 0, result.stdout.strip()
        except Exception:
            return False, ""

    def is_uv_environment():
        """Check if running in UV environment"""
        # Check for UV environment indicators
        uv_indicators = [
            os.environ.get("UV_PROJECT_NAME"),
            os.environ.get("VIRTUAL_ENV") and ".venv" in os.environ.get("VIRTUAL_ENV", ""),
            os.path.exists("pyproject.toml") and os.path.exists(".venv"),
        ]
        return any(uv_indicators)

    def check_uv_installation():
        """Check if UV is installed and available"""
        success, _ = run_command("uv --version")
        return success

    print("🔍 Diagnosing PySide6 installation issue...")
    print("📋 System Info:")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print(f"   Python: {platform.python_version()}")

    # Check UV environment
    is_uv_env = is_uv_environment()
    uv_available = check_uv_installation()

    if is_uv_env:
        print("   Environment: 🚀 UV Virtual Environment")
        if not uv_available:
            print("   ⚠️  UV command not found!")
    else:
        print("   Environment: 🐍 Standard Python Environment")

    if platform.system() == "Windows":
        print("\n🪟 Windows-specific diagnostics:")

        # Check VC++ redistributables
        print("   Checking Visual C++ Redistributables...")
        vc_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022\*\VC\Redist\MSVC\*\x64\Microsoft.VC143.CRT",
            r"C:\Program Files (x86)\Microsoft Visual Studio\*\VC\Redist\MSVC\*\x64\Microsoft.VC143.CRT",
            r"C:\Windows\System32\msvcp140.dll",
            r"C:\Windows\System32\vcruntime140.dll",
        ]

        found_vc = False
        for path in vc_paths:
            success, _ = run_command(f'if exist "{path}" echo found')
            if success:
                found_vc = True
                break

        if not found_vc:
            print("   ⚠️  Visual C++ Redistributables not found!")
            print("   💡 Solution: Download and install Microsoft Visual C++ Redistributable")
            print("      📥 Download: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        else:
            print("   ✅ Visual C++ Redistributables found")

    # Check Python package installation
    print("\n📦 Python package diagnostics:")

    if is_uv_env and uv_available:
        # UV environment diagnostics
        print("   Using UV package manager...")

        # Check UV cache status
        success, _ = run_command("uv cache info")
        if success:
            print("   📊 UV Cache Status: Available")
        else:
            print("   ⚠️  UV Cache Status: Issues detected")

        # Check PySide6 installation via UV
        success, output = run_command("uv show pyside6")

        # Check pyproject.toml for PySide6 dependency
        pyside6_in_deps = False
        try:
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                content = f.read().lower()
                pyside6_in_deps = "pyside6" in content
        except FileNotFoundError:
            pass

        if success:
            print("   ✅ PySide6 package found in UV environment")
            for line in output.split("\n"):
                if line.strip().startswith("version:"):
                    print(f"      Version: {line.split(':', 1)[1].strip()}")
        else:
            if pyside6_in_deps:
                print("   ⚠️  PySide6 defined in pyproject.toml but not installed in UV environment")
                print("   💡 Environment needs synchronization")

                # Check sync status
                sync_success, _ = run_command("uv sync --dry-run")
                if not sync_success:
                    print("   📋 UV sync required to install missing dependencies")
            else:
                print("   ❌ PySide6 not found in UV environment or pyproject.toml")
                print("   💡 PySide6 needs to be added to dependencies")

    else:
        # Standard pip environment diagnostics
        try:
            success, output = run_command("pip show pyside6")
            if success:
                print("   ✅ PySide6 package is installed")
                for line in output.split("\n"):
                    if line.startswith("Version:"):
                        print(f"      {line}")
            else:
                print("   ❌ PySide6 package not found")
        except ImportError:
            print("   ⚠️  pip not available for diagnostics")

    # Suggested solutions
    print("\n🔧 Suggested solutions (try in order):")

    if platform.system() == "Windows":
        print("   1. Install/reinstall Visual C++ Redistributable (Windows only)")
        print("      📥 https://aka.ms/vs/17/release/vc_redist.x64.exe")

    if is_uv_env and uv_available:
        # UV-specific solutions with context-aware recommendations
        print("   📦 UV Environment Solutions:")

        # Check if PySide6 is in dependencies to provide better first step
        pyside6_in_deps = False
        try:
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                content = f.read().lower()
                pyside6_in_deps = "pyside6" in content
        except FileNotFoundError:
            pass

        if pyside6_in_deps:
            # PySide6 is defined but not working - sync first
            print("   🎯 First try (recommended for your situation):")
            print("      📝 uv sync")
            print("   2. If sync fails, clean cache and sync:")
            print("      📝 uv cache clean")
            print("      📝 uv sync")
            print("   3. Force complete reinstall:")
            print("      📝 uv sync --reinstall")
        else:
            # PySide6 not in dependencies - add it first
            print("   🎯 First try (recommended for your situation):")
            print("      📝 uv add pyside6")
            print("   2. If add fails, clean cache first:")
            print("      📝 uv cache clean")
            print("      📝 uv add pyside6")

        print("   4. Reset UV virtual environment (nuclear option):")
        print("      📝 Remove .venv directory")
        print("      📝 uv sync")
        print("   5. Use specific PySide6 version:")
        print("      📝 uv add pyside6==6.9.1")
    else:
        # Standard pip solutions
        print("   📦 Standard Python Environment Solutions:")
        print("   2. Reinstall PySide6:")
        print("      📝 pip uninstall PySide6")
        print("      📝 pip install PySide6")
        print("   3. Try alternative installation:")
        print("      📝 pip install PySide6 --force-reinstall --no-cache-dir")
        print("   4. Use conda instead:")
        print("      📝 conda install pyside6 -c conda-forge")

    if platform.system() == "Windows":
        print("   🔍 Additional Windows Checks:")
        print("   • Check for conflicting Qt installations")
        print("   • Run as administrator if permission issues")
        print("   • Ensure 64-bit Python on 64-bit Windows")

    print("\n💬 If issues persist, please check the DEPLOYMENT.md file for detailed instructions.")


try:
    # Third-party imports - PySide6
    # pylint: disable=no-name-in-module
    # Third-party imports
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    # pylint: enable=no-name-in-module
except ImportError as e:
    print(f"❌ PySide6 import error: {e}")
    check_pyside6_installation()
    sys.exit(1)

# Local application imports
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.main_window import MainWindow
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.styling import ThemeManager
from ui.gui.utils.ui_scaling import setup_ui_scaling


class EOLTesterGUIApplication:
    """
    Main GUI Application class for WF EOL Tester

    Manages application lifecycle, dependency injection, and main window.
    """

    def __init__(self):
        """Initialize GUI application with dependency injection"""
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.container: Optional[SimpleReloadableContainer] = None
        self.state_manager: Optional[GUIStateManager] = None
        self.asyncio_timer: Optional[QTimer] = None

    def setup_ui_scaling(self) -> None:
        """Setup UI scaling before creating QApplication"""
        try:
            # Try to load configuration for UI scaling
            # This must be done before QApplication is created
            settings_manager = None
            try:
                # Create a minimal container to access configuration
                SimpleReloadableContainer.ensure_config_exists()
                temp_container = SimpleReloadableContainer.create()
                settings_manager = temp_container.configuration_service()
            except Exception as e:
                logger.warning(f"Could not load configuration for UI scaling: {e}")
                logger.info("Using default UI scaling settings")

            # Setup UI scaling with or without settings manager
            scale_factor = setup_ui_scaling(settings_manager)
            logger.info(f"UI scaling applied with factor: {scale_factor}")

        except Exception as e:
            logger.error(f"Failed to setup UI scaling: {e}")
            logger.info("Continuing with default scaling")

    def setup_application(self) -> None:
        """Setup QApplication with proper configuration"""
        self.app = QApplication(sys.argv)

        # Application metadata
        self.app.setApplicationName("WF EOL Tester")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("Withforce")
        self.app.setOrganizationDomain("withforce.co.kr")

        # Set application icon if available
        icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        logger.info("GUI Application initialized")

    def setup_container(self) -> None:
        """Initialize dependency injection container"""
        try:
            # Create container with loaded configuration
            # (ensure_config_exists is called internally by create())
            self.container = SimpleReloadableContainer.create()
            logger.info("SimpleReloadableContainer created successfully")

        except Exception as e:
            logger.error(f"Failed to create SimpleReloadableContainer: {e}")
            logger.info("Creating container with fallback configuration")
            # Fallback is handled internally by SimpleReloadableContainer
            self.container = SimpleReloadableContainer.create()

    def setup_state_manager(self) -> None:
        """Initialize GUI state management"""
        logger.info("🔧 GUI State Manager setup started")

        if not self.container:
            logger.error("❌ Container not initialized before state manager setup")
            raise RuntimeError("Container must be initialized before state manager")

        logger.info(f"🔧 Container instance ID: {id(self.container)}")

        try:
            hardware_facade = self.container.hardware_service_facade()
            logger.info(f"🔧 Hardware facade created with ID: {id(hardware_facade)}")
            logger.info(
                f"🔧 Hardware facade GUI State Manager: {getattr(hardware_facade, '_gui_state_manager', 'NOT_SET')}"
            )

            self.state_manager = GUIStateManager(
                hardware_facade=hardware_facade,
                configuration_service=self.container.configuration_service(),
                emergency_stop_service=self.container.emergency_stop_service(),
            )
            logger.info(f"🔧 GUI State Manager created with ID: {id(self.state_manager)}")
        except Exception as e:
            logger.error(f"❌ Failed to create GUI State Manager: {e}")
            raise

        # Register GUI State Manager with the container BEFORE any facade creation
        try:
            logger.info(f"🔧 About to override GUI State Manager in container {id(self.container)}")
            self.container.gui_state_manager.override(self.state_manager)
            logger.info("✅ GUI State Manager registered with dependency injection container")
            logger.info(f"✅ Overridden with state manager ID: {id(self.state_manager)}")
        except Exception as e:
            logger.error(f"❌ Failed to override GUI State Manager: {e}")
            raise

        # Reset the hardware_service_facade Singleton to force recreation with new GUI State Manager
        try:
            logger.info("🔄 About to reset Hardware Service Facade Singleton")
            self.container.hardware_service_facade.reset()
            logger.info(
                "🔄 Hardware Service Facade Singleton reset for new GUI State Manager injection"
            )
        except Exception as e:
            logger.error(f"❌ Failed to reset Hardware Service Facade: {e}")
            raise

        # Also reset any other Singletons that depend on hardware_service_facade
        # Note: EmergencyStopService doesn't need reset as it gets fresh dependencies through facade

        # Note: Direct injection was removed to respect encapsulation
        # The GUI state manager is now properly injected via the container

        # Verify the container registration was successful by creating a new facade
        test_facade = self.container.hardware_service_facade()
        if (
            hasattr(test_facade, "_gui_state_manager")
            and test_facade._gui_state_manager is not None
        ):
            logger.info("✅ GUI State Manager successfully injected through container")
            logger.info(f"🔗 Container GUI State Manager = {id(test_facade._gui_state_manager)}")
            logger.info(f"🔗 Created State Manager = {id(self.state_manager)}")

            # Verify they are the same instance
            if test_facade._gui_state_manager is self.state_manager:
                logger.info("✅ GUI State Manager instances match - injection successful")
            else:
                logger.warning("⚠️ GUI State Manager instances don't match - potential issue")
        else:
            logger.error("❌ Failed to inject GUI State Manager through container")
            raise RuntimeError("Container GUI State Manager injection failed")

    def create_main_window(self) -> None:
        """Create and configure main application window"""
        if not self.container or not self.state_manager:
            raise RuntimeError("Container and state manager must be initialized first")

        self.main_window = MainWindow(container=self.container, state_manager=self.state_manager)

        # Apply industrial theme
        theme_manager = ThemeManager()
        theme_manager.apply_industrial_theme(self.main_window)

        logger.info("Main window created")

    def run(self) -> int:
        """
        Run the GUI application

        Returns:
            Application exit code
        """
        try:
            # Setup UI scaling first (before QApplication)
            self.setup_ui_scaling()

            # Setup application components
            self.setup_application()
            self.setup_container()
            self.setup_state_manager()
            self.create_main_window()

            # Show main window
            if self.main_window:
                self.main_window.show()
                logger.info("Main window displayed")

                # Setup asyncio integration for Qt
                self._setup_asyncio_integration()

                # Run application event loop
                return self.app.exec() if self.app else 1
            else:
                logger.error("Failed to create main window")
                return 1

        except Exception as e:
            logger.error(f"Application startup failed: {e}")
            return 1

    def _setup_asyncio_integration(self) -> None:
        """Setup asyncio integration with Qt event loop"""
        # Create a timer to process asyncio events
        self.asyncio_timer = QTimer()
        self.asyncio_timer.timeout.connect(self._process_asyncio_events)
        self.asyncio_timer.start(10)  # Process every 10ms
        logger.info("Asyncio integration configured")

    def _process_asyncio_events(self) -> None:
        """Process pending asyncio events"""
        try:
            # Try to get running event loop (Python 3.10+ compatible)
            try:
                asyncio.get_running_loop()
                # Loop is already running, process some pending tasks if needed
            except RuntimeError:
                # No running event loop in current thread, this is normal for GUI thread
                pass
        except Exception:
            # Ignore all errors in asyncio processing
            pass


def main() -> int:
    """
    Main entry point for GUI application

    Returns:
        Application exit code
    """
    # Configure logging for GUI application
    logger.remove()  # Remove default logger
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>GUI</cyan> | "
        "<level>{message}</level>",
        colorize=True,
    )

    logger.info("Starting WF EOL Tester GUI Application")

    # Create and run application
    app = EOLTesterGUIApplication()
    exit_code = app.run()

    logger.info(f"GUI Application exited with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
