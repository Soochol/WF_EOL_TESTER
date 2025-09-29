@echo off
REM WF EOL Tester - GUI Only Launcher
REM This script runs the GUI application without showing the command prompt window

REM Check if UV is available
where uv >nul 2>&1
if errorlevel 1 (
    REM Fallback to Python if UV is not available
    where pythonw >nul 2>&1
    if errorlevel 1 (
        REM Use python.exe as last resort
        start "" python src/main_gui.py
    ) else (
        REM Use pythonw.exe to hide console window
        start "" pythonw src/main_gui.py
    )
) else (
    REM Use UV with pythonw to hide console window
    REM Note: UV may still show console briefly, but this is the best we can do
    start "" /min uv run src/main_gui.py
)