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
# Third-party imports
import asyncio
import sys
import time
import warnings
from pathlib import Path
from typing import Optional

from loguru import logger

# Suppress NumPy MINGW-W64 warnings on Windows before any NumPy imports
# These warnings are caused by experimental NumPy builds and are non-critical
warnings.filterwarnings("ignore", message="Numpy built with MINGW-W64.*")
warnings.filterwarnings("ignore", message="CRASHES ARE TO BE EXPECTED.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy.*")


# PySide6 diagnostic utility functions
def _run_command(cmd: str) -> tuple[bool, str]:
    """Run command and return success status and output"""
    # Standard library imports
    import subprocess

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=False)
        return result.returncode == 0, result.stdout.strip()
    except Exception:
        return False, ""


def _is_uv_environment() -> bool:
    """Check if running in UV environment"""
    # Standard library imports
    import os

    uv_indicators = [
        os.environ.get("UV_PROJECT_NAME"),
        os.environ.get("VIRTUAL_ENV") and ".venv" in os.environ.get("VIRTUAL_ENV", ""),
        os.path.exists("pyproject.toml") and os.path.exists(".venv"),
    ]
    return any(uv_indicators)


def _check_uv_installation() -> bool:
    """Check if UV is installed and available"""
    success, _ = _run_command("uv --version")
    return success


def _read_pyproject_toml() -> tuple[bool, str]:
    """Read pyproject.toml and check for PySide6 dependency"""
    try:
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            content = f.read()
            return True, content.lower()
    except FileNotFoundError:
        return False, ""


def _print_system_info() -> tuple[bool, bool]:
    """Print system information and return UV environment status"""
    # Standard library imports
    import platform

    print("🔍 Diagnosing PySide6 installation issue...")
    print("📋 System Info:")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print(f"   Python: {platform.python_version()}")

    # Check UV environment
    is_uv_env = _is_uv_environment()
    uv_available = _check_uv_installation()

    if is_uv_env:
        print("   Environment: 🚀 UV Virtual Environment")
        if not uv_available:
            print("   ⚠️  UV command not found!")
    else:
        print("   Environment: 🐍 Standard Python Environment")

    return is_uv_env, uv_available


def _check_windows_diagnostics() -> None:
    """Check Windows-specific diagnostics"""
    # Standard library imports
    import platform

    if platform.system() != "Windows":
        return

    print("\n🪟 Windows-specific diagnostics:")
    print("   Checking Visual C++ Redistributables...")

    vc_paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\*\VC\Redist\MSVC\*\x64\Microsoft.VC143.CRT",
        r"C:\Program Files (x86)\Microsoft Visual Studio\*\VC\Redist\MSVC\*\x64\Microsoft.VC143.CRT",
        r"C:\Windows\System32\msvcp140.dll",
        r"C:\Windows\System32\vcruntime140.dll",
    ]

    found_vc = False
    for path in vc_paths:
        success, _ = _run_command(f'if exist "{path}" echo found')
        if success:
            found_vc = True
            break

    if not found_vc:
        print("   ⚠️  Visual C++ Redistributables not found!")
        print("   💡 Solution: Download and install Microsoft Visual C++ Redistributable")
        print("      📥 Download: https://aka.ms/vs/17/release/vc_redist.x64.exe")
    else:
        print("   ✅ Visual C++ Redistributables found")


def _check_python_packages(is_uv_env: bool, uv_available: bool) -> None:
    """Check Python package installation"""
    print("\n📦 Python package diagnostics:")

    if is_uv_env and uv_available:
        _check_uv_packages()
    else:
        _check_pip_packages()


def _check_uv_packages() -> None:
    """Check UV environment packages"""
    print("   Using UV package manager...")

    # Check UV cache status
    success, _ = _run_command("uv cache info")
    if success:
        print("   📊 UV Cache Status: Available")
    else:
        print("   ⚠️  UV Cache Status: Issues detected")

    # Check PySide6 installation via UV
    success, output = _run_command("uv show pyside6")

    # Check pyproject.toml for PySide6 dependency
    toml_exists, content = _read_pyproject_toml()
    pyside6_in_deps = toml_exists and "pyside6" in content

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
            sync_success, _ = _run_command("uv sync --dry-run")
            if not sync_success:
                print("   📋 UV sync required to install missing dependencies")
        else:
            print("   ❌ PySide6 not found in UV environment or pyproject.toml")
            print("   💡 PySide6 needs to be added to dependencies")


def _check_pip_packages() -> None:
    """Check pip environment packages"""
    try:
        success, output = _run_command("pip show pyside6")
        if success:
            print("   ✅ PySide6 package is installed")
            for line in output.split("\n"):
                if line.startswith("Version:"):
                    print(f"      {line}")
        else:
            print("   ❌ PySide6 package not found")
    except ImportError:
        print("   ⚠️  pip not available for diagnostics")


def _print_suggested_solutions(is_uv_env: bool, uv_available: bool) -> None:
    """Print suggested solutions based on environment"""
    # Standard library imports
    import platform

    print("\n🔧 Suggested solutions (try in order):")

    if platform.system() == "Windows":
        print("   1. Install/reinstall Visual C++ Redistributable (Windows only)")
        print("      📥 https://aka.ms/vs/17/release/vc_redist.x64.exe")

    if is_uv_env and uv_available:
        _print_uv_solutions()
    else:
        _print_pip_solutions()

    if platform.system() == "Windows":
        print("   🔍 Additional Windows Checks:")
        print("   • Check for conflicting Qt installations")
        print("   • Run as administrator if permission issues")
        print("   • Ensure 64-bit Python on 64-bit Windows")

    print("\n💬 If issues persist, please check the DEPLOYMENT.md file for detailed instructions.")


def _print_uv_solutions() -> None:
    """Print UV-specific solutions"""
    print("   📦 UV Environment Solutions:")

    # Check if PySide6 is in dependencies
    toml_exists, content = _read_pyproject_toml()
    pyside6_in_deps = toml_exists and "pyside6" in content

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


def _print_pip_solutions() -> None:
    """Print pip-specific solutions"""
    print("   📦 Standard Python Environment Solutions:")
    print("   2. Reinstall PySide6:")
    print("      📝 pip uninstall PySide6")
    print("      📝 pip install PySide6")
    print("   3. Try alternative installation:")
    print("      📝 pip install PySide6 --force-reinstall --no-cache-dir")
    print("   4. Use conda instead:")
    print("      📝 conda install pyside6 -c conda-forge")


def check_pyside6_installation() -> None:
    """Check PySide6 installation and provide detailed diagnostics with UV environment support"""
    is_uv_env, uv_available = _print_system_info()
    _check_windows_diagnostics()
    _check_python_packages(is_uv_env, uv_available)
    _print_suggested_solutions(is_uv_env, uv_available)


# Import version utility (single source of truth from pyproject.toml)
from utils.version import get_project_version

# Try to import PySide6 with diagnostic support
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
# pylint: disable=wrong-import-position  # Must import after PySide6 check
from application.containers.simple_reloadable_container import SimpleReloadableContainer
from ui.gui.main_window import MainWindow
from ui.gui.services.gui_state_manager import GUIStateManager
from ui.gui.utils.styling import ThemeManager
from ui.gui.utils.ui_scaling import setup_ui_scaling
from ui.gui.widgets.splash.modern_splash_screen import ModernSplashScreen, LoadingSteps

# pylint: enable=wrong-import-position


# Application constants
class AppConstants:
    """Constants for the GUI application"""

    # Timing constants (in milliseconds)
    ASYNCIO_TIMER_INTERVAL = 10
    SPLASH_READY_DELAY = 500

    # Timing constants (in seconds)
    PROGRESS_STEP_DELAY = 0.1
    INITIAL_RENDER_DELAY = 0.2

    # UI constants
    DEFAULT_FONT_SIZE = 9
    # Version is read from pyproject.toml (single source of truth)
    APPLICATION_VERSION = get_project_version()

    # Organization info
    ORGANIZATION_NAME = "Withforce"
    ORGANIZATION_DOMAIN = "withforce.co.kr"


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
        self.splash_screen: Optional[ModernSplashScreen] = None

    def setup_ui_scaling(self) -> None:
        """Setup UI scaling before creating QApplication"""
        try:
            # Try to load configuration for UI scaling
            # This must be done before QApplication is created
            container = None
            try:
                # Create a minimal container to access configuration
                SimpleReloadableContainer.ensure_config_exists()
                container = SimpleReloadableContainer.create()
            except Exception as e:
                logger.warning(f"Could not load configuration for UI scaling: {e}")
                logger.info("Using default UI scaling settings")

            # Setup UI scaling with container (not configuration_service)
            scale_factor = setup_ui_scaling(container)
            logger.info(f"UI scaling applied with factor: {scale_factor}")

        except (ImportError, AttributeError, OSError) as e:
            logger.error(f"Failed to setup UI scaling: {e}")
            logger.info("Continuing with default scaling")

    def setup_application(self) -> None:
        """Setup QApplication with proper configuration"""
        self.app = QApplication(sys.argv)

        # Application metadata
        self.app.setApplicationName("WF EOL Tester")
        self.app.setApplicationVersion(AppConstants.APPLICATION_VERSION)
        self.app.setOrganizationName(AppConstants.ORGANIZATION_NAME)
        self.app.setOrganizationDomain(AppConstants.ORGANIZATION_DOMAIN)

        # Set Korean environment safe fonts to prevent DirectWrite errors
        # Third-party imports
        from PySide6.QtGui import QFont

        # Define font fallback chain optimized for Korean Windows environment
        korean_safe_fonts = [
            "Malgun Gothic",  # Windows Korean UI font
            "맑은 고딕",  # Korean name for Malgun Gothic
            "Segoe UI",  # Windows default UI font
            "Microsoft Sans Serif",  # Safer than MS Sans Serif
            "Arial",  # Universal fallback
            "sans-serif",  # System default
        ]

        # Set application default font
        default_font = QFont()
        for font_name in korean_safe_fonts:
            default_font.setFamily(font_name)
            if default_font.exactMatch():
                break

        default_font.setPointSize(AppConstants.DEFAULT_FONT_SIZE)  # Standard Windows UI size
        self.app.setFont(default_font)

        logger.info(f"Application font set to: {default_font.family()}")

        # Set application icon (use same icon as splash screen - SMA Spring SVG)
        icon_path = (
            Path(__file__).parent / "ui" / "gui" / "resources" / "icons" / "sma_spring_100.svg"
        )
        if icon_path.exists():
            # PySide6 supports SVG natively - convert to QPixmap for better compatibility
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtGui import QPixmap, QPainter
            from PySide6.QtCore import Qt

            # Convert SVG to QPixmap (64x64 for taskbar/titlebar)
            svg_renderer = QSvgRenderer(str(icon_path))
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()

            self.app.setWindowIcon(QIcon(pixmap))
            logger.info(f"Application icon set from: {icon_path}")
        else:
            logger.warning(f"Application icon not found: {icon_path}")

        logger.info("GUI Application initialized")

    def create_splash_screen(self) -> None:
        """Create and show splash screen with version from configuration"""
        if not self.app:
            raise RuntimeError("QApplication must be initialized before splash screen")

        # Read application name and version from configuration
        app_name = "WF EOL Tester"  # Default
        version = "1.0.0"  # Default

        try:
            # Try to read from application.yaml directly
            from pathlib import Path
            import yaml

            config_path = Path("configuration/application.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    if config_data and "application" in config_data:
                        app_name = config_data["application"].get("name", app_name)
                        version = config_data["application"].get("version", version)
                        logger.info(f"Loaded splash screen info: {app_name} v{version}")
        except Exception as e:
            logger.warning(f"Failed to load version from config, using defaults: {e}")

        self.splash_screen = ModernSplashScreen(app_name=app_name, version=version)
        self.splash_screen.show_with_animation()

        # Process events to ensure splash screen is visible
        if self.app:
            self.app.processEvents()
        logger.info("Splash screen displayed")

    def update_splash_progress(self, step_index: int) -> None:
        """Update splash screen with loading step"""
        if self.splash_screen and self.app:
            progress, message = LoadingSteps.get_step(step_index)
            self.splash_screen.update_progress(progress, message)
            self.app.processEvents()  # Ensure UI updates are visible

            # Small delay to show progress (except for last step)
            if step_index < LoadingSteps.get_total_steps() - 1:
                time.sleep(AppConstants.PROGRESS_STEP_DELAY)
                self.app.processEvents()

    def setup_container(self) -> None:
        """Initialize dependency injection container"""
        try:
            # Create container with loaded configuration
            # (ensure_config_exists is called internally by create())
            self.container = SimpleReloadableContainer.create()
            logger.info("SimpleReloadableContainer created successfully")

            # Initialize database
            self._initialize_database()

        except (ImportError, AttributeError, FileNotFoundError) as e:
            logger.error(f"Failed to create SimpleReloadableContainer: {e}")
            logger.info("Creating container with fallback configuration")
            # Fallback is handled internally by SimpleReloadableContainer
            self.container = SimpleReloadableContainer.create()

            # Initialize database even with fallback
            self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database manager"""
        try:
            # Log critical path information for debugging production issues
            import sys
            from pathlib import Path
            from domain.value_objects.application_config import (
                PROJECT_ROOT,
                DATABASE_DIR,
                IS_DEVELOPMENT,
                CONFIG_DIR,
                LOGS_DIR,
            )

            logger.info("=" * 70)
            logger.info("PATH DIAGNOSTICS")
            logger.info("=" * 70)
            logger.info(f"IS_DEVELOPMENT: {IS_DEVELOPMENT}")
            logger.info(f"sys.frozen: {getattr(sys, 'frozen', False)}")
            logger.info(f"sys.executable: {sys.executable}")
            logger.info(f"PROJECT_ROOT: {PROJECT_ROOT}")
            logger.info(f"CONFIG_DIR: {CONFIG_DIR}")
            logger.info(f"LOGS_DIR: {LOGS_DIR}")
            logger.info(f"DATABASE_DIR: {DATABASE_DIR}")
            logger.info(f"DATABASE_DIR exists: {DATABASE_DIR.exists()}")
            logger.info(f"APPDATA env var: {Path.home() / 'AppData' / 'Roaming'}")
            logger.info("=" * 70)

            if self.container:
                import asyncio

                db_manager = self.container.database_manager()
                logger.info(f"Database manager path: {db_manager._database_path}")

                # Run async initialization in sync context
                asyncio.get_event_loop().run_until_complete(db_manager.initialize())
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
            logger.info("Application will continue without database logging")

    def _setup_hardware_services_with_progress(self) -> None:
        """Setup hardware services with progress updates for splash screen"""
        logger.info("🔧 Hardware services setup started")

        # Simulate progressive hardware service loading
        hardware_steps = [
            (3, "Loading robot service..."),
            (4, "Loading MCU service..."),
            (5, "Loading power service..."),
            (6, "Loading loadcell service..."),
            (7, "Loading digital I/O service..."),
        ]

        for step_index, step_message in hardware_steps:
            self.update_splash_progress(step_index)
            logger.info(f"🔧 {step_message}")

            # Process events to keep GUI responsive
            if self.app:
                self.app.processEvents()

            # Small delay to simulate hardware loading time and show progress
            # This is where actual hardware initialization happens
            time.sleep(0.2)  # Adjust this value based on actual hardware loading time

        logger.info("✅ Hardware services setup completed")

    def setup_state_manager(self) -> None:
        """Initialize GUI state management"""
        logger.info("🔧 GUI State Manager setup started")

        if not self.container:
            logger.error("❌ Container not initialized before state manager setup")
            raise RuntimeError("Container must be initialized before state manager")

        logger.debug(f"🔧 Container instance ID: {id(self.container)}")

        try:
            hardware_facade = self.container.hardware_service_facade()
            logger.debug(f"🔧 Hardware facade created with ID: {id(hardware_facade)}")
            logger.debug(
                f"🔧 Hardware facade GUI State Manager: {getattr(hardware_facade, '_gui_state_manager', 'NOT_SET')}"
            )

            self.state_manager = GUIStateManager(
                hardware_facade=hardware_facade,
                configuration_service=self.container.configuration_service(),
                emergency_stop_service=self.container.emergency_stop_service(),
            )
            logger.debug(f"🔧 GUI State Manager created with ID: {id(self.state_manager)}")
        except (ImportError, AttributeError, TypeError) as e:
            logger.error(f"❌ Failed to create GUI State Manager: {e}")
            raise RuntimeError(f"GUI State Manager creation failed: {e}") from e

        # Register GUI State Manager with the container BEFORE any facade creation
        try:
            logger.debug(
                f"🔧 About to override GUI State Manager in container {id(self.container)}"
            )
            self.container.gui_state_manager.override(self.state_manager)
            logger.info("✅ GUI State Manager registered with dependency injection container")
            logger.debug(f"✅ Overridden with state manager ID: {id(self.state_manager)}")
        except (AttributeError, TypeError) as e:
            logger.error(f"❌ Failed to override GUI State Manager: {e}")
            raise RuntimeError(f"GUI State Manager registration failed: {e}") from e

        # Reset the hardware_service_facade Singleton to force recreation with new GUI State Manager
        try:
            logger.debug("🔄 About to reset Hardware Service Facade Singleton")
            self.container.hardware_service_facade.reset()
            logger.debug(
                "🔄 Hardware Service Facade Singleton reset for new GUI State Manager injection"
            )
        except (AttributeError, TypeError) as e:
            logger.error(f"❌ Failed to reset Hardware Service Facade: {e}")
            raise RuntimeError(f"Hardware Service Facade reset failed: {e}") from e

        # Verify the container registration was successful by creating a new facade
        test_facade = self.container.hardware_service_facade()
        # pylint: disable=protected-access  # Intentional access for verification
        if (
            hasattr(test_facade, "_gui_state_manager")
            and test_facade._gui_state_manager is not None
        ):
            logger.info("✅ GUI State Manager successfully injected through container")
            logger.debug(f"🔗 Container GUI State Manager = {id(test_facade._gui_state_manager)}")
            logger.debug(f"🔗 Created State Manager = {id(self.state_manager)}")

            # Verify they are the same instance
            if test_facade._gui_state_manager is self.state_manager:
                logger.info("✅ GUI State Manager instances match - injection successful")
            else:
                logger.warning("⚠️ GUI State Manager instances don't match - potential issue")
        else:
            logger.error("❌ Failed to inject GUI State Manager through container")
            raise RuntimeError("Container GUI State Manager injection failed")
        # pylint: enable=protected-access

    def create_main_window_with_progress(self) -> None:
        """Create and configure main application window with progressive tab loading"""
        if not self.container or not self.state_manager:
            raise RuntimeError("Container and state manager must be initialized first")

        # Step 1: Create basic main window structure
        self.update_splash_progress(9)  # Creating main window...
        logger.info("🔧 Creating main window structure...")
        self.main_window = MainWindow(
            container=self.container, state_manager=self.state_manager, lazy_init=True
        )

        # Hide main window until splash is complete
        self.main_window.hide()

        # Process events to keep GUI responsive
        if self.app:
            self.app.processEvents()
        time.sleep(0.1)  # Brief pause for visual feedback

        # Step 2: Initialize header
        self.update_splash_progress(10)  # Applying theme...
        logger.info("🔧 Initializing header...")
        self.main_window.init_header()

        # Process events to keep GUI responsive
        if self.app:
            self.app.processEvents()
        time.sleep(0.1)  # Brief pause for visual feedback

        # Step 3: Initialize sidebar
        self.update_splash_progress(11)  # Initializing widgets...
        logger.info("🔧 Initializing sidebar...")
        self.main_window.init_sidebar()

        # Process events to keep GUI responsive
        if self.app:
            self.app.processEvents()
        time.sleep(0.1)  # Brief pause for visual feedback

        # Step 4: Initialize main tabs progressively
        tabs = [
            ("dashboard", "Loading dashboard..."),
            ("test_control", "Loading test controls..."),
            ("hardware", "Loading hardware controls..."),
            ("results", "Loading results viewer..."),
            ("logs", "Loading logs viewer..."),
            ("settings", "Loading settings..."),
            ("about", "Loading about page..."),
        ]

        current_step = 12
        for tab_name, message in tabs:
            self.update_splash_progress(current_step)
            logger.info(f"🔧 {message}")

            # Initialize the specific tab
            if hasattr(self.main_window, f"init_{tab_name}_tab"):
                getattr(self.main_window, f"init_{tab_name}_tab")()

            # Process events to keep GUI responsive
            if self.app:
                self.app.processEvents()
            time.sleep(0.05)  # Brief pause for visual feedback

            current_step += 1

        # Step 5: Apply theme after all widgets are created
        logger.info("🎨 Applying industrial theme...")
        theme_manager = ThemeManager()
        theme_manager.apply_industrial_theme(self.main_window)

        # Process events to keep GUI responsive
        if self.app:
            self.app.processEvents()
        time.sleep(0.1)  # Brief pause for visual feedback

        # Step 6: Finalize initialization
        logger.info("🔧 Finalizing window initialization...")
        self.main_window.finalize_initialization()

        # Process events to keep GUI responsive
        if self.app:
            self.app.processEvents()
        time.sleep(0.1)  # Brief pause for visual feedback

        logger.info("✅ Main window created and configured with all tabs")

    def create_main_window(self) -> None:
        """Create and configure main application window (legacy method)"""
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
            self.create_splash_screen()
            self.update_splash_progress(0)  # Loading configuration...

            # Small delay to let splash screen render
            time.sleep(AppConstants.INITIAL_RENDER_DELAY)
            if self.app:
                self.app.processEvents()

            self.update_splash_progress(0)  # Loading configuration...

            self.update_splash_progress(1)  # Initializing dependency injection...
            self.setup_container()

            self.update_splash_progress(2)  # Creating hardware factory...
            # Give user visual feedback that hardware factory is being created
            if self.app:
                self.app.processEvents()
            time.sleep(0.1)  # Brief pause for visual feedback

            # Simulate hardware service loading with progress updates
            self._setup_hardware_services_with_progress()

            self.update_splash_progress(8)  # Initializing hardware facade...
            self.setup_state_manager()

            # Create main window with detailed progress updates
            self.create_main_window_with_progress()

            self.update_splash_progress(19)  # Preparing application...
            # Setup asyncio integration for Qt
            self._setup_asyncio_integration()

            # Process events to keep GUI responsive
            if self.app:
                self.app.processEvents()
            time.sleep(0.1)  # Brief pause for visual feedback

            # Show main window and finish splash
            if self.main_window:
                self.update_splash_progress(20)  # Ready!

                # Small delay to show "Ready!" message
                QTimer.singleShot(
                    AppConstants.SPLASH_READY_DELAY, self._finish_splash_and_show_main
                )

                # Run application event loop
                return self.app.exec() if self.app else 1
            else:
                logger.error("Failed to create main window")
                return 1

        except Exception as e:
            logger.error(f"Application startup failed: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
            if self.splash_screen:
                self.splash_screen.close()
            return 1

    def _finish_splash_and_show_main(self) -> None:
        """Finish splash screen and show main window"""
        if self.splash_screen and self.main_window:
            self.splash_screen.finish_with_fade(self.main_window)
            logger.info("Main window displayed")
        elif self.main_window:
            self.main_window.show()
            logger.info("Main window displayed (no splash)")
        else:
            logger.error("Main window not available")

    def _setup_asyncio_integration(self) -> None:
        """Setup asyncio integration with Qt event loop"""
        # Create a timer to process asyncio events
        self.asyncio_timer = QTimer()
        self.asyncio_timer.timeout.connect(self._process_asyncio_events)
        self.asyncio_timer.start(AppConstants.ASYNCIO_TIMER_INTERVAL)  # Process every 10ms
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

    # Get user-writable log directory (important for Program Files installations)
    if sys.platform == "win32":
        import os

        log_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "WF EOL Tester" / "logs"
    else:
        log_dir = Path.home() / ".wf_eol_tester" / "logs"

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gui_application.log"

    # In PyInstaller GUI apps, sys.stderr may be None, so use file logging as fallback
    if sys.stderr is not None:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>GUI</cyan> | "
            "<level>{message}</level>",
            colorize=True,
        )
    else:
        # Fallback to file logging for bundled applications
        logger.add(
            str(log_file),
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | GUI | {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
        )

    logger.info("Starting WF EOL Tester GUI Application")

    # Create and run application
    app = EOLTesterGUIApplication()
    exit_code = app.run()

    logger.info(f"GUI Application exited with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
