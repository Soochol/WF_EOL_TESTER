# WF EOL Tester - Windows Deployment Guide

Complete guide for deploying and troubleshooting the WF EOL Tester GUI application on Windows systems.

## 🎯 Quick Start

### Prerequisites
- Windows 10/11 (64-bit recommended)
- Python 3.10+ (64-bit)
- Visual C++ Redistributable (2019-2022)

### Basic Installation
```bash
# Clone repository
git clone https://github.com/Soochol/WF_EOL_TESTER.git
cd WF_EOL_TESTER

# Install dependencies (recommended: use uv)
pip install uv
uv sync

# Run GUI application
uv run src/main_gui.py
```

### UV Package Manager (Recommended)
This project uses **UV** for fast, reliable dependency management. UV provides better performance and more consistent environments than pip.

**Why UV?**
- 🚀 **10-100x faster** than pip
- 🔒 **Reproducible builds** with lock files
- 🎯 **Better dependency resolution**
- 🛡️ **Isolated environments** prevent conflicts

## 🚨 Common Error: PySide6 DLL Load Failed

### Error Message
```
PySide6 import error: DLL load failed while importing QtCore: 지정된 프로시저를 찾을 수 없습니다.
```

### Root Causes & Solutions

#### 1. **Missing Visual C++ Redistributables** ⭐ Most Common
**Problem**: PySide6 requires Microsoft Visual C++ runtime libraries that may not be installed.

**Solution**:
1. Download Microsoft Visual C++ Redistributable (x64):
   - 🔗 **Download**: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 📋 Alternative: https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

2. Install as Administrator:
   ```cmd
   # Right-click "Run as Administrator"
   vc_redist.x64.exe
   ```

3. Restart your computer after installation

#### 2. **Python Architecture Mismatch**
**Problem**: 32-bit Python with 64-bit system or vice versa.

**Check Python architecture**:
```python
import platform
print(f"Python: {platform.architecture()}")
print(f"System: {platform.machine()}")
```

**Solution**: Install 64-bit Python on 64-bit Windows
- 🔗 Download: https://www.python.org/downloads/windows/
- Select "Windows installer (64-bit)"

#### 3. **UV Environment Issues** ⭐ UV Users
**Problem**: PySide6 installation corruption in UV virtual environment.

**UV-Specific Solutions**:
```bash
# Method 1: Clean reinstall in UV environment
uv remove pyside6
uv cache clean
uv add pyside6

# Method 2: Reset UV environment completely
# (Warning: This removes all packages)
rm -rf .venv
uv sync

# Method 3: Force synchronization
uv sync --reinstall

# Method 4: Use specific PySide6 version
uv add pyside6==6.9.1
```

#### 4. **Corrupted PySide6 Installation (pip)**
**Problem**: Incomplete or damaged PySide6 installation in standard Python environment.

**Solution - Complete Reinstall**:
```bash
# Uninstall completely
pip uninstall PySide6 PySide6-Addons PySide6-Essentials

# Clear pip cache
pip cache purge

# Reinstall with force
pip install PySide6 --force-reinstall --no-cache-dir

# Alternative: Use conda
conda install pyside6 -c conda-forge
```

#### 5. **Conflicting Qt Installations**
**Problem**: Multiple Qt versions (PyQt5, PyQt6, PySide2, PySide6) causing DLL conflicts.

**Check installed Qt packages (UV)**:
```bash
# UV environment
uv show | grep -i qt
uv show | grep -i pyside

# Standard environment
pip list | grep -i qt
pip list | grep -i pyside
```

**UV Solution**:
```bash
# Remove conflicting packages in UV environment
uv remove pyqt5 pyqt6 pyside2 2>/dev/null || true

# Reinstall only PySide6
uv add pyside6
```

**Standard pip Solution**:
```bash
# Remove conflicting packages
pip uninstall PyQt5 PyQt6 PySide2

# Reinstall only PySide6
pip install PySide6
```

#### 5. **Windows Environment Issues**

**Path Issues**:
```cmd
# Check Python and pip paths
where python
where pip

# Ensure they point to the same Python installation
```

**Permission Issues**:
- Run Command Prompt as Administrator
- Install packages with `--user` flag:
  ```bash
  pip install PySide6 --user
  ```

## 🔧 Advanced Troubleshooting

### System Requirements Checker
Use the built-in system checker for comprehensive diagnostics:

```bash
# Run system requirements check
python src/utils/system_checker.py

# From src/ directory
python -m utils.system_checker
```

This tool checks:
- Python version and architecture
- PySide6 installation and dependencies
- Visual C++ redistributables (Windows)
- Required packages
- Hardware access permissions
- File system permissions

### Alternative: Manual Diagnostics Script
If the system checker is not available, save this as `diagnose_pyside6.py`:

```python
import sys
import platform
import subprocess
import os

def diagnose_pyside6():
    print("=== PySide6 Installation Diagnostics ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")

    # Check Visual C++ Redistributables
    vc_files = [
        r"C:\Windows\System32\msvcp140.dll",
        r"C:\Windows\System32\vcruntime140.dll",
        r"C:\Windows\System32\vcruntime140_1.dll"
    ]

    print("\n=== Visual C++ Runtime Check ===")
    for file in vc_files:
        exists = os.path.exists(file)
        print(f"{file}: {'✅ Found' if exists else '❌ Missing'}")

    # Check PySide6 installation
    print("\n=== PySide6 Installation Check ===")
    try:
        import PySide6
        print(f"✅ PySide6 imported successfully")
        print(f"   Version: {PySide6.__version__}")

        from PySide6.QtCore import QT_VERSION_STR
        print(f"   Qt Version: {QT_VERSION_STR}")

    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")

    # Check pip packages
    print("\n=== Python Packages ===")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"],
                              capture_output=True, text=True)
        qt_packages = [line for line in result.stdout.split('\n')
                      if any(qt in line.lower() for qt in ['pyside', 'pyqt', 'qt'])]
        for pkg in qt_packages:
            print(f"   {pkg}")
    except Exception as e:
        print(f"❌ Could not check packages: {e}")

if __name__ == "__main__":
    diagnose_pyside6()
```

Run with: `python diagnose_pyside6.py`

### Alternative GUI Libraries

If PySide6 continues to fail, consider alternatives:

#### Option 1: PyQt5 (fallback)
```python
# In main_gui.py, add fallback import
try:
    from PySide6.QtWidgets import QApplication
    GUI_BACKEND = "PySide6"
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
        GUI_BACKEND = "PyQt5"
        print("⚠️ Fallback to PyQt5")
    except ImportError:
        print("❌ No GUI backend available")
        sys.exit(1)
```

#### Option 2: Web-based GUI
Use the CLI version or implement a web interface:
```bash
# Use CLI version instead
python src/main_cli.py
```

## 📦 Standalone Executable (PyInstaller)

Create a standalone executable that includes all dependencies:

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Create Executable
```bash
# Basic executable
pyinstaller --onefile src/main_gui.py

# With icon and additional files
pyinstaller --onefile --windowed \
    --icon=resources/icon.ico \
    --add-data "configuration;configuration" \
    src/main_gui.py
```

### 3. Include VC++ Redistributables
Create a installer package that includes VC++ redistributables:

```bash
# Use tools like NSIS or Inno Setup
# Include vc_redist.x64.exe in installer
```

## 🏗️ Development Environment Setup

### Recommended Development Setup
```bash
# Install Python 3.10+ (64-bit)
# Install Visual Studio Code
# Install Git

# Clone and setup
git clone https://github.com/Soochol/WF_EOL_TESTER.git
cd WF_EOL_TESTER

# Setup virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run tests
pytest
```

### VS Code Extensions
- Python
- Python Debugger
- Qt for Python

## 🆘 Support and Troubleshooting

## 🚀 UV Environment Troubleshooting

### Quick UV Fixes (Try First)
```bash
# 1. Quick PySide6 reinstall
uv remove pyside6 && uv add pyside6

# 2. Clean cache and sync
uv cache clean && uv sync

# 3. Force reinstall everything
uv sync --reinstall

# 4. Nuclear option: Reset environment
rm -rf .venv && uv sync
```

### UV Environment Diagnostics
```bash
# Check UV status
uv --version
uv sync --dry-run

# Check PySide6 in UV
uv show pyside6
uv tree | grep pyside

# Check UV cache
uv cache info
uv cache dir
```

### Common Solutions Summary
1. **Install VC++ Redistributable** (most common fix for Windows)
2. **Use UV environment reset** (`rm -rf .venv && uv sync`)
3. **Clean UV cache** (`uv cache clean`)
4. **Use 64-bit Python** on 64-bit systems
5. **Remove conflicting Qt packages** in UV environment
6. **Run as Administrator** if permission issues

### Getting Help
- Check the diagnostic output from the application
- Run the diagnostic script above
- Create an issue on GitHub with diagnostic information

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10+ (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for application + dependencies
- **Display**: 1280x720 minimum resolution

---

## 📝 Notes for IT Administrators

### Enterprise Deployment
1. Pre-install VC++ Redistributables via Group Policy
2. Use conda environments for consistent package management
3. Deploy as standalone executable to avoid Python conflicts
4. Test on clean Windows VM before deployment

### Security Considerations
- Application requires file system access for logs and configuration
- No network access required for basic operation (offline capable)
- Hardware access required for industrial control interfaces

---

*Last updated: 2025-09-26*
*For technical support: Create issue at https://github.com/Soochol/WF_EOL_TESTER/issues*