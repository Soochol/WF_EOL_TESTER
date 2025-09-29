@echo off
REM Create Desktop Shortcut for WF EOL Tester GUI

echo ====================================================
echo    Creating Desktop Shortcut for WF EOL Tester
echo ====================================================
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Define shortcut paths
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=WF EOL Tester.lnk"
set "VBS_TARGET=%CURRENT_DIR%\run_gui_silent.vbs"
set "BAT_TARGET=%CURRENT_DIR%\run_gui.bat"
set "ICON_PATH=%CURRENT_DIR%\src\ui\gui\resources\icons"

echo Current project directory: %CURRENT_DIR%
echo Desktop path: %DESKTOP%
echo.

REM Check if VBS file exists (preferred method)
if exist "%VBS_TARGET%" (
    echo Creating shortcut using VBScript launcher (silent mode)...
    set "TARGET_FILE=%VBS_TARGET%"
    set "SHORTCUT_ARGS="
) else if exist "%BAT_TARGET%" (
    echo Creating shortcut using Batch launcher...
    set "TARGET_FILE=%BAT_TARGET%"
    set "SHORTCUT_ARGS="
) else (
    echo No launcher scripts found. Creating shortcut with UV command...
    set "TARGET_FILE=cmd.exe"
    set "SHORTCUT_ARGS=/c cd /d "%CURRENT_DIR%" && uv run src/main_gui.py"
)

REM Create VBScript to generate the shortcut
echo Creating shortcut generation script...
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"

(
echo Set objShell = CreateObject^("WScript.Shell"^)
echo Set objShortcut = objShell.CreateShortcut^("%DESKTOP%\%SHORTCUT_NAME%"^)
echo objShortcut.TargetPath = "%TARGET_FILE%"
if defined SHORTCUT_ARGS echo objShortcut.Arguments = "%SHORTCUT_ARGS%"
echo objShortcut.WorkingDirectory = "%CURRENT_DIR%"
echo objShortcut.Description = "WF EOL Tester - Wafer Fabrication End-of-Line Testing Application"
REM Try to set icon if available
if exist "%ICON_PATH%\app.ico" echo objShortcut.IconLocation = "%ICON_PATH%\app.ico"
echo objShortcut.Save
) > "%VBS_SCRIPT%"

REM Execute the VBScript
cscript //nologo "%VBS_SCRIPT%"

REM Clean up
del "%VBS_SCRIPT%" >nul 2>&1

if exist "%DESKTOP%\%SHORTCUT_NAME%" (
    echo.
    echo SUCCESS: Desktop shortcut created successfully!
    echo Location: %DESKTOP%\%SHORTCUT_NAME%
    echo.
    echo You can now double-click the shortcut to launch WF EOL Tester GUI
    echo without showing the command prompt window.
) else (
    echo.
    echo ERROR: Failed to create desktop shortcut.
    echo Please check permissions or create manually.
)

echo.
echo Additional options:
echo - run_gui_silent.vbs  : Completely silent GUI launcher (recommended)
echo - run_gui.bat         : GUI launcher with minimal console visibility
echo - uv run src/main_gui.py : Standard command-line launch
echo.
pause