@echo off
REM ========================================================================
REM WF EOL Tester - Windows Setup Script
REM ========================================================================
REM This batch file sets up the development environment for WF EOL Tester
REM on Windows systems. It creates virtual environment, installs dependencies,
REM and prepares the application for first run.
REM ========================================================================

setlocal enabledelayedexpansion

REM Set console title
title WF EOL Tester - Setup

REM Change to the script directory
cd /d "%~dp0"

echo ========================================================================
echo WF EOL Tester - Windows Setup
echo ========================================================================
echo.
echo This script will set up the WF EOL Tester environment on your Windows system.
echo.

REM Check if Python is available
echo [SETUP] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ before running this setup:
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, make sure to check "Add Python to PATH"
    echo 3. Restart your command prompt and run this script again
    echo.
    pause
    exit /b 1
)

REM Display Python version and check minimum requirement
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [SETUP] Found Python %PYTHON_VERSION%

REM Extract major and minor version numbers
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Check minimum Python version (3.8+)
if %MAJOR% LSS 3 (
    echo [ERROR] Python version too old. Please install Python 3.8 or newer.
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 8 (
    echo [ERROR] Python version too old. Please install Python 3.8 or newer.
    pause
    exit /b 1
)

echo [SETUP] Python version is compatible
echo.

REM Check if pip is available
echo [SETUP] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)
echo [SETUP] pip is available
echo.

REM Create virtual environment
echo [SETUP] Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo [SETUP] Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo [SETUP] Using existing virtual environment
        goto :activate_venv
    )
)

echo [SETUP] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Make sure you have sufficient permissions and disk space
    pause
    exit /b 1
)
echo [SETUP] Virtual environment created successfully

:activate_venv
REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SETUP] Virtual environment activated
echo.

REM Upgrade pip in virtual environment
echo [SETUP] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [SETUP] Installing dependencies...
if exist "pyproject.toml" (
    echo [SETUP] Installing from pyproject.toml...
    python -m pip install -e .
) else if exist "requirements.txt" (
    echo [SETUP] Installing from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo [WARNING] No pyproject.toml or requirements.txt found
    echo [SETUP] Installing basic dependencies...
    python -m pip install loguru pyyaml rich
)

if errorlevel 1 (
    echo [ERROR] Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)
echo [SETUP] Dependencies installed successfully
echo.

REM Verify installation
echo [SETUP] Verifying installation...
python -c "
import sys
print('[SETUP] Python executable:', sys.executable)

# Check key imports
try:
    import loguru
    print('[SETUP] loguru: OK')
except ImportError as e:
    print('[SETUP] loguru: FAILED -', e)

try:
    import yaml
    print('[SETUP] PyYAML: OK')
except ImportError as e:
    print('[SETUP] PyYAML: FAILED -', e)
    
try:
    import rich
    print('[SETUP] rich: OK')
except ImportError as e:
    print('[SETUP] rich: FAILED -', e)

try:
    import asyncio
    print('[SETUP] asyncio: OK')
except ImportError as e:
    print('[SETUP] asyncio: FAILED -', e)
"
echo.

REM Check for configuration files
echo [SETUP] Checking configuration files...
if exist "configuration\hardware_configuration.yaml" (
    echo [SETUP] Hardware configuration found
) else (
    echo [WARNING] Hardware configuration not found at: configuration\hardware_configuration.yaml
)

if exist "configuration\hardware_model.yaml" (
    echo [SETUP] Hardware model found
) else (
    echo [WARNING] Hardware model not found at: configuration\hardware_model.yaml
)
echo.

REM Create logs directory
if not exist "logs" (
    echo [SETUP] Creating logs directory...
    mkdir logs
)

REM Test run (optional)
echo [SETUP] Setup complete!
echo.
set /p TEST_RUN="Do you want to test run the application? (y/N): "
if /i "!TEST_RUN!"=="y" (
    echo [SETUP] Testing application startup...
    echo [SETUP] This will run for 5 seconds then exit...
    echo.
    timeout /t 3 /nobreak >nul
    
    REM Quick test run with timeout
    start /b python -c "
import asyncio
import signal
import sys
sys.path.insert(0, 'src')

async def quick_test():
    try:
        from infrastructure.factory import ServiceFactory
        print('[TEST] Factory import: OK')
        
        # Test mock services
        mock_config = {'model': 'mock'}
        mock_dio = ServiceFactory.create_digital_io_service(mock_config)
        print('[TEST] Mock DIO service: OK')
        
        print('[TEST] Basic functionality test: PASSED')
        return True
    except Exception as e:
        print(f'[TEST] Error: {e}')
        return False

def timeout_handler(signum, frame):
    print('[TEST] Test timeout - this is normal')
    sys.exit(0)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

try:
    result = asyncio.run(quick_test())
    if result:
        print('[TEST] Application test: PASSED')
    else:
        print('[TEST] Application test: FAILED')
except Exception as e:
    print(f'[TEST] Test error: {e}')
"
    timeout /t 2 /nobreak >nul
)

echo.
echo ========================================================================
echo WF EOL Tester Setup Complete!
echo ========================================================================
echo.
echo Next steps:
echo 1. Double-click 'run.bat' to start the application normally
echo 2. Double-click 'run_debug.bat' for debug mode with verbose output
echo 3. Make sure your hardware configuration files are properly set up
echo.
echo Files created:
echo - Virtual environment in 'venv' directory
echo - All Python dependencies installed
echo - Logs directory created
echo.
echo If you encounter any issues:
echo - Check the configuration files in the 'configuration' directory
echo - Run 'run_debug.bat' for detailed error information
echo - Refer to the README.md or WINDOWS_DEPLOYMENT_GUIDE.md
echo.
echo ========================================================================
echo Press any key to exit...
pause >nul