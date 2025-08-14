@echo off
REM ========================================================================
REM WF EOL Tester - Windows Setup Script
REM ========================================================================
REM This batch file sets up the development environment for WF EOL Tester
REM on Windows systems. It creates virtual environment, installs dependencies,
REM and prepares the application for first run.
REM ========================================================================

setlocal enabledelayedexpansion

REM Set console title
title WF EOL Tester - Setup

REM Change to the script directory
cd /d "%~dp0"

echo ========================================================================
echo WF EOL Tester - Windows Setup
echo ========================================================================
echo.
echo This script will set up the WF EOL Tester environment on your Windows system.
echo.

REM Check if uv is available
echo [SETUP] Checking uv installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv is not installed or not in PATH
    echo.
    echo Please install uv before running this setup:
    echo 1. Visit: https://docs.astral.sh/uv/getting-started/installation/
    echo 2. Or install with pip: pip install uv
    echo 3. Restart your command prompt and run this script again
    echo.
    pause
    exit /b 1
)

REM Display uv version
for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
echo [SETUP] Found %UV_VERSION%
echo.

REM Initialize uv project
echo [SETUP] Initializing uv environment...
if exist ".venv" (
    echo [WARNING] uv environment already exists
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo [SETUP] Removing existing uv environment...
        rmdir /s /q .venv
    ) else (
        echo [SETUP] Using existing uv environment
        goto :sync_deps
    )
)

:sync_deps
REM Sync dependencies with uv
echo [SETUP] Syncing dependencies with uv...
uv sync --dev
if errorlevel 1 (
    echo [ERROR] Failed to sync dependencies with uv
    echo Make sure pyproject.toml is properly configured
    pause
    exit /b 1
)
echo [SETUP] Dependencies synced successfully
echo.

REM Verify installation
echo [SETUP] Verifying installation...
uv run python -c "
import sys
print('[SETUP] Python executable:', sys.executable)

# Check key imports
try:
    import loguru
    print('[SETUP] loguru: OK')
except ImportError as e:
    print('[SETUP] loguru: FAILED -', e)

try:
    import yaml
    print('[SETUP] PyYAML: OK')
except ImportError as e:
    print('[SETUP] PyYAML: FAILED -', e)
    
try:
    import rich
    print('[SETUP] rich: OK')
except ImportError as e:
    print('[SETUP] rich: FAILED -', e)

try:
    import asyncio
    print('[SETUP] asyncio: OK')
except ImportError as e:
    print('[SETUP] asyncio: FAILED -', e)
"
echo.

REM Check for configuration files
echo [SETUP] Checking configuration files...
if exist "configuration\hardware_configuration.yaml" (
    echo [SETUP] Hardware configuration found
) else (
    echo [WARNING] Hardware configuration not found at: configuration\hardware_configuration.yaml
)

if exist "configuration\hardware_model.yaml" (
    echo [SETUP] Hardware model found
) else (
    echo [WARNING] Hardware model not found at: configuration\hardware_model.yaml
)
echo.

REM Create logs directory
if not exist "logs" (
    echo [SETUP] Creating logs directory...
    mkdir logs
)

REM Test run (optional)
echo [SETUP] Setup complete!
echo.
set /p TEST_RUN="Do you want to test run the application? (y/N): "
if /i "!TEST_RUN!"=="y" (
    echo [SETUP] Testing application startup...
    echo [SETUP] This will run for 5 seconds then exit...
    echo.
    timeout /t 3 /nobreak >nul
    
    REM Quick test run with timeout
    start /b uv run python -c "
import asyncio
import signal
import sys
sys.path.insert(0, 'src')

async def quick_test():
    try:
        from infrastructure.factory import ServiceFactory
        print('[TEST] Factory import: OK')
        
        # Test mock services
        mock_config = {'model': 'mock'}
        mock_dio = ServiceFactory.create_digital_io_service(mock_config)
        print('[TEST] Mock DIO service: OK')
        
        print('[TEST] Basic functionality test: PASSED')
        return True
    except Exception as e:
        print(f'[TEST] Error: {e}')
        return False

def timeout_handler(signum, frame):
    print('[TEST] Test timeout - this is normal')
    sys.exit(0)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

try:
    result = asyncio.run(quick_test())
    if result:
        print('[TEST] Application test: PASSED')
    else:
        print('[TEST] Application test: FAILED')
except Exception as e:
    print(f'[TEST] Test error: {e}')
"
    timeout /t 2 /nobreak >nul
)

echo.
echo ========================================================================
echo WF EOL Tester Setup Complete!
echo ========================================================================
echo.
echo Next steps:
echo 1. Double-click 'run.bat' to start the application normally
echo 2. Double-click 'run_debug.bat' for debug mode with verbose output
echo 3. Make sure your hardware configuration files are properly set up
echo.
echo Files created:
echo - uv environment in '.venv' directory
echo - All Python dependencies installed via uv
echo - Logs directory created
echo.
echo If you encounter any issues:
echo - Check the configuration files in the 'configuration' directory
echo - Run 'run_debug.bat' for detailed error information
echo - Refer to the README.md or WINDOWS_DEPLOYMENT_GUIDE.md
echo.
echo ========================================================================
echo Press any key to exit...
pause >nul