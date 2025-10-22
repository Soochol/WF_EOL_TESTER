@echo off
REM ============================================================================
REM WF EOL Tester - Complete Build Script
REM Builds both executable and installer packages
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  WF EOL Tester - Complete Build Process
echo ============================================================================
echo.

REM Get start time
set START_TIME=%TIME%

REM ============================================================================
REM Step 1: Check if PyInstaller is installed
REM ============================================================================
echo [1/5] Checking dependencies...

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo   - PyInstaller not found, installing dependencies...
    echo   - Running uv sync...
    echo.
    echo   NOTE: If this fails with "access denied" error:
    echo   1. Run: uv cache clean
    echo   2. Run: uv sync
    echo   3. Re-run this build script
    echo.
    uv sync
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please run 'uv cache clean' then 'uv sync' manually.
        pause
        exit /b 1
    )
) else (
    echo   - PyInstaller already installed
)
echo   Done.
echo.

REM ============================================================================
REM Step 2: Clean previous builds
REM ============================================================================
echo [2/5] Cleaning previous builds...
if exist "build" (
    echo   - Removing old build directory...
    rmdir /s /q "build"
)
if exist "dist" (
    echo   - Removing old dist directory...
    rmdir /s /q "dist"
)
echo   - Creating fresh build directories...
mkdir "build\application" 2>nul
mkdir "build\installer" 2>nul
echo   Done.
echo.

REM ============================================================================
REM Step 3: Build executable with PyInstaller
REM ============================================================================
echo [3/5] Building executable with PyInstaller...
echo   - Running PyInstaller...
echo   - This may take several minutes...
echo.

REM Use venv Python directly instead of UV to avoid Windows Store Python permission issues
.venv\Scripts\pyinstaller.exe wf_eol_tester.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo   - Moving executable to build/application...
xcopy /E /I /Y "dist\WF_EOL_Tester\*" "build\application\WF_EOL_Tester\"
if errorlevel 1 (
    echo ERROR: Failed to copy executable files!
    pause
    exit /b 1
)
echo   Done.
echo.

REM ============================================================================
REM Step 4: Build installer with Inno Setup
REM ============================================================================
echo [4/5] Building installer with Inno Setup...

REM Check if Inno Setup is installed
set "INNO_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_COMPILER%" (
    set "INNO_COMPILER=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%INNO_COMPILER%" (
    echo.
    echo WARNING: Inno Setup not found!
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo.
    echo Executable build completed successfully.
    echo You can manually run Inno Setup to create the installer.
    pause
    exit /b 0
)

echo   - Running Inno Setup Compiler...
"%INNO_COMPILER%" "installer.iss"

if errorlevel 1 (
    echo.
    echo ERROR: Inno Setup build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo   Done.
echo.

REM ============================================================================
REM Step 5: Display build summary
REM ============================================================================
echo [5/5] Build Summary
echo ============================================================================
echo.

REM Calculate build time
set END_TIME=%TIME%
echo Build completed successfully!
echo.
echo Start Time: %START_TIME%
echo End Time:   %END_TIME%
echo.

echo Output Files:
echo   Executable:  build\application\WF_EOL_Tester\WF_EOL_Tester.exe
echo   Installer:   build\installer\WF_EOL_Tester_Setup_0.1.0.exe
echo.

REM Check file sizes
for %%F in ("build\application\WF_EOL_Tester\WF_EOL_Tester.exe") do (
    set "EXE_SIZE=%%~zF"
    set /a "EXE_MB=!EXE_SIZE! / 1048576"
    echo   Executable Size: !EXE_MB! MB
)

for %%F in ("build\installer\WF_EOL_Tester_Setup_0.1.0.exe") do (
    set "SETUP_SIZE=%%~zF"
    set /a "SETUP_MB=!SETUP_SIZE! / 1048576"
    echo   Installer Size:  !SETUP_MB! MB
)

echo.
echo ============================================================================
echo  All builds completed successfully!
echo ============================================================================
echo.
