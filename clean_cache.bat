@echo off
REM Clean Python cache files on Windows
echo Cleaning Python cache files...

REM Remove __pycache__ directories
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remove .pyc files
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"

echo Cache cleanup complete!
pause