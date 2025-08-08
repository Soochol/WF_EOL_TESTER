@echo off
REM ========================================================================
REM WF EOL Tester - Windows Debug Launcher
REM ========================================================================
REM This batch file runs the EOL Tester in debug mode with verbose logging
REM and extended error information for troubleshooting purposes.
REM ========================================================================

setlocal enabledelayedexpansion

REM Set console title
title WF EOL Tester - DEBUG MODE

REM Change to the script directory
cd /d "%~dp0"

echo ========================================================================
echo WF EOL Tester - DEBUG MODE
echo ========================================================================
echo.
echo [DEBUG] This will run the application with verbose logging
echo [DEBUG] All debug information will be displayed
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ and try again.
    echo You can download Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Display detailed system information
echo [DEBUG] System Information:
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [DEBUG] Python Version: !PYTHON_VERSION!
echo [DEBUG] Current Directory: %CD%
echo [DEBUG] Date/Time: %DATE% %TIME%
echo [DEBUG] User: %USERNAME%
echo [DEBUG] Computer: %COMPUTERNAME%
echo.

REM Check virtual environment with debug info
if exist "venv\Scripts\activate.bat" (
    echo [DEBUG] Virtual environment found at: %CD%\venv
    echo [DEBUG] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo [DEBUG] Virtual environment activated successfully
    
    REM Show virtual environment Python version
    echo [DEBUG] Virtual env Python version:
    python --version
) else (
    echo [DEBUG] No virtual environment found
    echo [DEBUG] Searching for venv in current directory...
    dir venv /b 2>nul || echo [DEBUG] No venv directory found
    echo [DEBUG] Using system Python installation
)
echo.

REM Check main.py with detailed info
echo [DEBUG] Checking for main.py...
if not exist "main.py" (
    echo [ERROR] main.py not found!
    echo [DEBUG] Current directory contents:
    dir /b *.py 2>nul || echo [DEBUG] No Python files found
    echo.
    pause
    exit /b 1
) else (
    echo [DEBUG] main.py found
    for %%i in (main.py) do echo [DEBUG] File size: %%~zi bytes, Modified: %%~ti
)
echo.

REM Check for required dependencies
echo [DEBUG] Checking Python environment...
python -c "import sys; print('[DEBUG] Python executable:', sys.executable)"
python -c "import sys; print('[DEBUG] Python path:', sys.path[0])"

REM Show installed packages (if pip is available)
echo [DEBUG] Checking key dependencies...
python -c "
try:
    import loguru
    print('[DEBUG] loguru: OK')
except ImportError:
    print('[DEBUG] loguru: NOT FOUND')

try:
    import asyncio
    print('[DEBUG] asyncio: OK') 
except ImportError:
    print('[DEBUG] asyncio: NOT FOUND')
    
try:
    import yaml
    print('[DEBUG] PyYAML: OK')
except ImportError:
    print('[DEBUG] PyYAML: NOT FOUND')
"
echo.

REM Set debug environment variables
echo [DEBUG] Setting debug environment variables...
set PYTHONPATH=%CD%\src
set DEBUG_MODE=1
set LOGLEVEL=DEBUG

echo [DEBUG] Environment variables set:
echo [DEBUG] PYTHONPATH=%PYTHONPATH%
echo [DEBUG] DEBUG_MODE=%DEBUG_MODE%
echo [DEBUG] LOGLEVEL=%LOGLEVEL%
echo.

echo ========================================================================
echo [DEBUG] Starting WF EOL Tester in DEBUG mode...
echo [DEBUG] Press Ctrl+C to stop the application
echo [DEBUG] All debug output will be shown below
echo ========================================================================
echo.

REM Run with debug output and error capture
python -u main.py 2>&1

REM Capture and display exit information
set EXIT_CODE=%errorlevel%

echo.
echo ========================================================================
echo [DEBUG] Application Debug Summary
echo ========================================================================
echo [DEBUG] Exit Code: %EXIT_CODE%
echo [DEBUG] End Time: %DATE% %TIME%

if %EXIT_CODE% equ 0 (
    echo [DEBUG] Status: NORMAL EXIT
) else (
    echo [DEBUG] Status: ERROR EXIT
    echo [DEBUG] An error occurred during execution
    echo [DEBUG] Check the output above for error details
)

echo ========================================================================
echo [DEBUG] Debug session complete
echo [DEBUG] Press any key to close this window and review the output...
echo ========================================================================
pause >nul