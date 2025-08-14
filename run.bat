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

REM Check if uv is available
uv --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv is not installed or not in PATH
    echo.
    echo Please install uv and try again.
    echo You can install uv with: pip install uv
    echo Or visit: https://docs.astral.sh/uv/getting-started/installation/
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

REM Create temporary batch file for execution
echo @echo off > temp_runner.bat
echo setlocal >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Change to application directory >> temp_runner.bat
echo cd /d "%~dp0" >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Initialize uv environment if needed >> temp_runner.bat
echo echo [INFO] Using uv package manager... >> temp_runner.bat
echo uv sync --dev >> temp_runner.bat
echo if errorlevel 1 ^( >> temp_runner.bat
echo     echo [ERROR] Failed to sync dependencies with uv >> temp_runner.bat
echo     pause >> temp_runner.bat
echo     exit /b 1 >> temp_runner.bat
echo ^) >> temp_runner.bat
echo. >> temp_runner.bat
echo echo. >> temp_runner.bat
echo echo ======================================================================== >> temp_runner.bat
echo echo WF EOL Tester - Starting Application >> temp_runner.bat
echo echo ======================================================================== >> temp_runner.bat
echo echo. >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Run the main application >> temp_runner.bat
echo uv run python main.py >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Check exit status >> temp_runner.bat
echo if errorlevel 1 ^( >> temp_runner.bat
echo     echo. >> temp_runner.bat
echo     echo ======================================================================== >> temp_runner.bat
echo     echo [ERROR] Application exited with error >> temp_runner.bat
echo     echo ======================================================================== >> temp_runner.bat
echo ^) else ^( >> temp_runner.bat
echo     echo. >> temp_runner.bat
echo     echo ======================================================================== >> temp_runner.bat
echo     echo [INFO] Application exited normally >> temp_runner.bat
echo     echo ======================================================================== >> temp_runner.bat
echo ^) >> temp_runner.bat
echo. >> temp_runner.bat
echo echo. >> temp_runner.bat
echo echo Press any key to close this window... >> temp_runner.bat
echo pause ^>nul >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Clean up temporary file >> temp_runner.bat
echo del "%~dp0temp_runner.bat" 2^>nul >> temp_runner.bat

REM Execute the temporary batch file in maximized window
start "WF EOL Tester" /max cmd /c temp_runner.bat

REM Exit the launcher batch file
exit