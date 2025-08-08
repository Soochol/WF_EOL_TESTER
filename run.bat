@echo off
REM ========================================================================
REM WF EOL Tester - Windows Launcher
REM ========================================================================
REM This batch file provides easy double-click execution for the EOL Tester
REM on Windows systems. It handles virtual environment activation and
REM provides proper error handling.
REM ========================================================================

setlocal enabledelayedexpansion

REM Set console title
title WF EOL Tester

REM Change to the script directory
cd /d "%~dp0"

echo ========================================================================
echo WF EOL Tester - Starting Application
echo ========================================================================
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

REM Display Python version
echo [INFO] Checking Python installation...
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found: !PYTHON_VERSION!
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Found virtual environment, activating...
    call venv\Scripts\activate.bat
    echo [INFO] Virtual environment activated
) else (
    echo [WARNING] Virtual environment not found at 'venv\'
    echo [INFO] Using system Python...
)
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo [INFO] Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Display startup information
echo [INFO] Starting WF EOL Tester...
echo [INFO] Working directory: %CD%
echo [INFO] Press Ctrl+C to stop the application
echo.
echo ========================================================================

REM Run the main Python application
python main.py

REM Capture exit code
set EXIT_CODE=%errorlevel%

echo.
echo ========================================================================
if %EXIT_CODE% equ 0 (
    echo [INFO] Application exited normally
) else (
    echo [ERROR] Application exited with error code: %EXIT_CODE%
)
echo ========================================================================
echo.
echo Press any key to close this window...
pause >nul