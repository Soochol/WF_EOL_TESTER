@echo off
REM ============================================================================
REM WF EOL Tester - GUI Launcher
REM ============================================================================
REM This script runs the GUI application (src/main.py)
REM
REM Usage:
REM   run_gui.bat           - Run GUI with console window (for debugging)
REM   run_gui_silent.vbs    - Run GUI without console window (recommended)
REM ============================================================================

echo.
echo ========================================
echo  WF EOL Tester - Starting GUI
echo ========================================
echo.

REM Navigate to project root directory
cd /d "%~dp0"

REM Check if virtual environment exists (priority)
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment Python...
    echo.
    .venv\Scripts\python.exe src\main.py
) else (
    REM Fallback: Check if UV is available
    where uv >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Virtual environment not found, using system Python...
        echo.
        python src\main.py
    ) else (
        echo [INFO] Using UV to run GUI...
        echo.
        uv run src/main.py
    )
)

echo.
echo [INFO] GUI application closed.
echo.
pause