@echo off
title Modern School Bell System Builder

echo ========================================
echo   Modern School Bell System Builder
echo ========================================
echo.

:: Ensure pip and wheel are up to date
echo Updating pip and wheel...
py -m pip install --upgrade pip setuptools wheel packaging >nul 2>&1

:: Install required packages (pygame + pyinstaller)
echo Installing required packages...
py -m pip install --upgrade pygame==2.6.1 pyinstaller==6.15.0 || (
    echo ERROR: Failed to install required packages.
    pause
    exit /b 1
)

:: Clean previous build/dist folders
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SchoolBellSystem.spec del /q SchoolBellSystem.spec

echo.
echo Building DEBUG executable (with console)...
py -m PyInstaller --onefile --name "SchoolBellSystem_DEBUG" ^
    --icon=bell.ico ^
    bell_system.py || (
    echo ERROR: Debug build failed!
    pause
    exit /b 1
)

echo.
echo Building RELEASE executable (windowed, no console)...
py -m PyInstaller --onefile --windowed --name "SchoolBellSystem" ^
    --icon=bell.ico ^
    bell_system.py || (
    echo ERROR: Release build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo.
echo Debug build   : dist\SchoolBellSystem_DEBUG.exe  (console visible)
echo Release build : dist\SchoolBellSystem.exe        (clean windowed)
echo.
echo Distribution Instructions:
echo 1. Use SchoolBellSystem_DEBUG.exe for testing
echo 2. Distribute SchoolBellSystem.exe to school computers
echo ========================================
echo.
pause
