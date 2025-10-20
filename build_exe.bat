@echo off
REM ============================================================================
REM WF EOL Tester - Executable Build Script
REM Builds only the executable (faster for testing)
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  WF EOL Tester - Executable Build
echo ============================================================================
echo.

REM Get start time
set START_TIME=%TIME%

REM ============================================================================
REM Step 1: Clean previous builds
REM ============================================================================
echo [1/3] Cleaning previous executable builds...
if exist "build\application" (
    echo   - Removing old application directory...
    rmdir /s /q "build\application"
)
if exist "dist" (
    echo   - Removing old dist directory...
    rmdir /s /q "dist"
)
echo   - Creating fresh application directory...
mkdir "build\application" 2>nul
echo   Done.
echo.

REM ============================================================================
REM Step 2: Build executable with PyInstaller
REM ============================================================================
echo [2/3] Building executable with PyInstaller...
echo   - Running PyInstaller...
echo   - This may take several minutes...
echo.

uv run pyinstaller wf_eol_tester.spec --clean --noconfirm

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
REM Step 3: Display build summary
REM ============================================================================
echo [3/3] Build Summary
echo ============================================================================
echo.

REM Calculate build time
set END_TIME=%TIME%
echo Executable build completed successfully!
echo.
echo Start Time: %START_TIME%
echo End Time:   %END_TIME%
echo.

echo Output Directory:
echo   build\application\WF_EOL_Tester\
echo.

echo Main Executable:
echo   build\application\WF_EOL_Tester\WF_EOL_Tester.exe
echo.

REM Check file size
for %%F in ("build\application\WF_EOL_Tester\WF_EOL_Tester.exe") do (
    set "EXE_SIZE=%%~zF"
    set /a "EXE_MB=!EXE_SIZE! / 1048576"
    echo   File Size: !EXE_MB! MB
)

echo.
echo Configuration Files:
echo   build\application\WF_EOL_Tester\configuration\
echo.

echo Driver Files:
echo   build\application\WF_EOL_Tester\driver\AXL\
echo.

echo ============================================================================
echo  Executable build completed!
echo  You can now test the application or run build_installer.bat
echo ============================================================================
echo.
