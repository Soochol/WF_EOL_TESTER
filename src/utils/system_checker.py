#!/usr/bin/env python3
"""
WF EOL Tester - System Requirements Checker

Standalone utility to check system requirements and diagnose common issues
before running the WF EOL Tester GUI application. This tool helps identify
and resolve platform-specific deployment issues.

Usage:
    python src/utils/system_checker.py
    python -m utils.system_checker  # From src/ directory
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SystemChecker:
    """Comprehensive system requirements checker for WF EOL Tester"""

    def __init__(self):
        """Initialize system checker"""
        self.issues_found = []
        self.warnings = []
        self.recommendations = []

    def run_full_check(self) -> bool:
        """Run complete system check and return True if system is ready"""
        print("🔍 WF EOL Tester - System Requirements Check")
        print("=" * 50)

        # Run all checks
        checks = [
            ("System Information", self.check_system_info),
            ("Python Installation", self.check_python),
            ("PySide6 Dependencies", self.check_pyside6),
            ("Required Packages", self.check_packages),
            ("Hardware Access", self.check_hardware_access),
            ("File Permissions", self.check_file_permissions),
        ]

        all_passed = True
        for check_name, check_func in checks:
            print(f"\n📋 {check_name}")
            print("-" * 30)
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Check failed: {e}")
                self.issues_found.append(f"{check_name}: {e}")
                all_passed = False

        # Show summary
        self._show_summary()
        return all_passed

    def check_system_info(self) -> bool:
        """Check basic system information"""
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🏗️  Architecture: {platform.machine()}")
        print(f"🐍 Python: {platform.python_version()}")
        print(f"📁 Working Directory: {Path.cwd()}")

        # Check if we're on a supported platform
        if platform.system() not in ["Windows", "Linux", "Darwin"]:
            self.issues_found.append("Unsupported platform")
            print("⚠️  Warning: Untested platform")
            return False

        return True

    def check_python(self) -> bool:
        """Check Python installation and version"""
        version = sys.version_info

        print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
        print(f"📍 Python Executable: {sys.executable}")
        print(f"🏗️  Python Architecture: {platform.architecture()[0]}")

        # Check minimum version
        if version < (3, 10):
            self.issues_found.append("Python 3.10+ required")
            print("❌ Python 3.10+ required")
            return False

        # Check architecture on Windows
        if platform.system() == "Windows":
            if platform.architecture()[0] != "64bit":
                self.warnings.append("64-bit Python recommended on Windows")
                print("⚠️  64-bit Python recommended on Windows")

        print("✅ Python version OK")
        return True

    def check_pyside6(self) -> bool:
        """Check PySide6 installation and dependencies"""
        try:
            import PySide6
            print(f"✅ PySide6 {PySide6.__version__} installed")

            # Try to get Qt version (optional, may not be available)
            try:
                from PySide6.QtCore import QT_VERSION_STR
                print(f"📦 Qt Version: {QT_VERSION_STR}")
            except ImportError:
                print("📦 Qt Version: (not available)")

            # Try importing core modules
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            from PySide6.QtGui import QIcon
            print("✅ PySide6 core modules import OK")

        except ImportError as e:
            print(f"❌ PySide6 import failed: {e}")
            self.issues_found.append(f"PySide6 import error: {e}")

            # Platform-specific diagnostics
            if platform.system() == "Windows":
                self._check_windows_pyside6_deps()

            return False

        # Windows-specific checks
        if platform.system() == "Windows":
            return self._check_windows_pyside6_deps()

        return True

    def _check_windows_pyside6_deps(self) -> bool:
        """Check Windows-specific PySide6 dependencies"""
        print("\n🪟 Windows PySide6 Dependencies:")

        # Check Visual C++ Redistributables
        vc_files = [
            r"C:\Windows\System32\msvcp140.dll",
            r"C:\Windows\System32\vcruntime140.dll",
            r"C:\Windows\System32\vcruntime140_1.dll"
        ]

        missing_vc = []
        for vc_file in vc_files:
            if os.path.exists(vc_file):
                print(f"✅ {os.path.basename(vc_file)} found")
            else:
                missing_vc.append(vc_file)
                print(f"❌ {os.path.basename(vc_file)} missing")

        if missing_vc:
            self.issues_found.append("Missing Visual C++ Redistributables")
            self.recommendations.append(
                "Install Microsoft Visual C++ Redistributable:\n"
                "   📥 https://aka.ms/vs/17/release/vc_redist.x64.exe"
            )
            return False

        return True

    def check_packages(self) -> bool:
        """Check required Python packages"""
        required_packages = [
            "loguru",
            "dependency-injector",
            "rich",
            "asyncio"
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} available")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} missing")

        if missing_packages:
            self.issues_found.append(f"Missing packages: {', '.join(missing_packages)}")
            self.recommendations.append(f"Install missing packages: pip install {' '.join(missing_packages)}")
            return False

        return True

    def check_hardware_access(self) -> bool:
        """Check hardware access permissions and availability"""
        print("🔌 Hardware Access Check:")

        # Check serial port access (Linux/Windows)
        if platform.system() == "Linux":
            import grp
            try:
                # Check if user is in dialout group
                dialout_gid = grp.getgrnam('dialout').gr_gid
                user_groups = os.getgroups()

                if dialout_gid in user_groups:
                    print("✅ User in 'dialout' group for serial access")
                else:
                    self.warnings.append("User not in 'dialout' group - serial ports may not be accessible")
                    print("⚠️  User not in 'dialout' group")
                    self.recommendations.append("Add user to dialout group: sudo usermod -a -G dialout $USER")
            except KeyError:
                print("⚠️  'dialout' group not found")

        elif platform.system() == "Windows":
            # Windows typically has serial access by default
            print("✅ Windows serial access (assumed available)")

        return True

    def check_file_permissions(self) -> bool:
        """Check file system permissions"""
        project_root = Path.cwd()

        # Check if we can write to logs directory
        logs_dir = project_root / "logs"
        try:
            logs_dir.mkdir(exist_ok=True)
            test_file = logs_dir / "test_permissions.tmp"
            test_file.write_text("test")
            test_file.unlink()
            print("✅ Log directory writable")
        except PermissionError:
            self.issues_found.append("Cannot write to logs directory")
            print("❌ Cannot write to logs directory")
            return False

        # Check configuration directory
        config_dir = project_root / "configuration"
        if config_dir.exists():
            try:
                test_file = config_dir / "test_permissions.tmp"
                test_file.write_text("test")
                test_file.unlink()
                print("✅ Configuration directory writable")
            except PermissionError:
                self.warnings.append("Configuration directory not writable")
                print("⚠️  Configuration directory not writable")

        return True

    def _show_summary(self) -> None:
        """Show check summary with issues and recommendations"""
        print("\n" + "=" * 50)
        print("📊 SYSTEM CHECK SUMMARY")
        print("=" * 50)

        if not self.issues_found and not self.warnings:
            print("🎉 All checks passed! System is ready for WF EOL Tester.")
            print("\n🚀 You can now run the application:")
            print("   python src/main_gui.py")
            return

        if self.issues_found:
            print("\n❌ ISSUES FOUND (must be fixed):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")

        if self.warnings:
            print("\n⚠️  WARNINGS (recommended to fix):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")

        if self.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")

        if self.issues_found:
            print("\n🔧 Please fix the issues above before running the application.")
        else:
            print("\n✅ No critical issues found. You can try running the application:")
            print("   python src/main_gui.py")

    def run_command(self, cmd: str) -> Tuple[bool, str]:
        """Run a system command and return success status and output"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            return False, ""


def main():
    """Main entry point for system checker"""
    print("WF EOL Tester - System Requirements Checker")
    print("Version 1.0.0")
    print()

    checker = SystemChecker()
    system_ready = checker.run_full_check()

    # Exit with appropriate code
    exit_code = 0 if system_ready and not checker.issues_found else 1
    print(f"\n🏁 System check completed (exit code: {exit_code})")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())