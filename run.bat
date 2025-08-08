@echo off
REM ========================================================================
REM WF EOL Tester - Windows Launcher
REM ========================================================================
REM This batch file provides easy double-click execution for the EOL Tester
REM on Windows systems with maximized console window. It handles virtual 
REM environment activation and provides proper error handling.
REM ========================================================================

setlocal enabledelayedexpansion

REM Change to the script directory
cd /d "%~dp0"

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

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo [INFO] Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Start maximized console window and run the application
start "WF EOL Tester" /max cmd /k "cd /d %~dp0 && if exist venv\Scripts\activate.bat (echo [INFO] Activating virtual environment... && call venv\Scripts\activate.bat && echo [INFO] Virtual environment activated) else (echo [WARNING] Using system Python...) && echo. && echo ======================================================================== && echo WF EOL Tester - Starting Application && echo ======================================================================== && echo. && python main.py && echo. && echo ======================================================================== && if errorlevel 1 (echo [ERROR] Application exited with error) else (echo [INFO] Application exited normally) && echo ======================================================================== && echo. && echo Press any key to close this window... && pause >nul"

REM Exit the launcher batch file
exit