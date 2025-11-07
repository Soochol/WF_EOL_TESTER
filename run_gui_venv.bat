@echo off
REM WF EOL Tester GUI Launcher (Using Virtual Environment)
REM This script runs the GUI without requiring UV

echo Starting WF EOL Tester GUI...
.venv\Scripts\python.exe src\main_gui.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start GUI application
    pause
)
