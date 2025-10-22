@echo off
REM ============================================================================
REM WF EOL Tester - Direct GUI Launcher (No UV)
REM ============================================================================
REM This script directly uses the virtual environment Python
REM Bypasses UV build issues
REM ============================================================================

echo.
echo ========================================
echo  WF EOL Tester - Starting GUI
echo ========================================
echo.

REM Navigate to project root
cd /d "%~dp0"

REM Check virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo [ERROR] Please run: uv sync
    echo.
    pause
    exit /b 1
)

echo [INFO] Using virtual environment: .venv\Scripts\python.exe
echo [INFO] Running: src\main_gui.py
echo.

REM Run GUI directly with virtual environment Python
.venv\Scripts\python.exe src\main_gui.py

echo.
echo [INFO] GUI application closed.
echo.
pause
