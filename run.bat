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

REM Create temporary batch file for execution
echo @echo off > temp_runner.bat
echo setlocal >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Change to application directory >> temp_runner.bat
echo cd /d "%~dp0" >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Check and activate virtual environment >> temp_runner.bat
echo if exist venv\Scripts\activate.bat ^( >> temp_runner.bat
echo     echo [INFO] Activating virtual environment... >> temp_runner.bat
echo     call venv\Scripts\activate.bat >> temp_runner.bat
echo     echo [INFO] Virtual environment activated >> temp_runner.bat
echo ^) else ^( >> temp_runner.bat
echo     echo [WARNING] Using system Python... >> temp_runner.bat
echo ^) >> temp_runner.bat
echo. >> temp_runner.bat
echo echo. >> temp_runner.bat
echo echo ======================================================================== >> temp_runner.bat
echo echo WF EOL Tester - Starting Application >> temp_runner.bat
echo echo ======================================================================== >> temp_runner.bat
echo echo. >> temp_runner.bat
echo. >> temp_runner.bat
echo REM Run the main application >> temp_runner.bat
echo python main.py >> temp_runner.bat
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