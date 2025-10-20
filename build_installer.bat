@echo off
REM ============================================================================
REM WF EOL Tester - Installer Build Script
REM Builds only the installer (requires existing executable build)
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  WF EOL Tester - Installer Build
echo ============================================================================
echo.

REM ============================================================================
REM Step 1: Check if executable exists
REM ============================================================================
echo [1/3] Checking for existing executable...

if not exist "dist\WF_EOL_Tester\WF_EOL_Tester.exe" (
    echo.
    echo ERROR: Executable not found!
    echo Please run build_exe.bat or build_all.bat first to create the executable.
    echo.
    echo Expected location:
    echo   dist\WF_EOL_Tester\WF_EOL_Tester.exe
    echo.
    pause
    exit /b 1
)

echo   - Executable found: OK
echo   Done.
echo.

REM ============================================================================
REM Step 2: Clean previous installer builds
REM ============================================================================
echo [2/3] Preparing installer build...
if exist "build\installer" (
    echo   - Removing old installer directory...
    rmdir /s /q "build\installer"
)
echo   - Creating fresh installer directory...
mkdir "build\installer" 2>nul
echo   Done.
echo.

REM ============================================================================
REM Step 3: Build installer with Inno Setup
REM ============================================================================
echo [3/3] Building installer with Inno Setup...

REM Check if Inno Setup is installed
set "INNO_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_COMPILER%" (
    set "INNO_COMPILER=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%INNO_COMPILER%" (
    echo.
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Installation paths checked:
    echo   - C:\Program Files (x86)\Inno Setup 6\ISCC.exe
    echo   - C:\Program Files\Inno Setup 6\ISCC.exe
    echo.
    pause
    exit /b 1
)

echo   - Inno Setup Compiler found: %INNO_COMPILER%
echo   - Running Inno Setup Compiler...
echo.

"%INNO_COMPILER%" "installer.iss"

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo   Done.
echo.

REM ============================================================================
REM Display build summary
REM ============================================================================
echo ============================================================================
echo  Build Summary
echo ============================================================================
echo.

echo Installer created successfully!
echo.

echo Output File:
echo   build\installer\WF_EOL_Tester_Setup_0.1.0.exe
echo.

REM Check file size
for %%F in ("build\installer\WF_EOL_Tester_Setup_0.1.0.exe") do (
    set "SETUP_SIZE=%%~zF"
    set /a "SETUP_MB=!SETUP_SIZE! / 1048576"
    echo   File Size: !SETUP_MB! MB
)

echo.
echo ============================================================================
echo  Installer build completed!
echo ============================================================================
echo.
