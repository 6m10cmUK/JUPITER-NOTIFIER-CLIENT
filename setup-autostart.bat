@echo off
chcp 65001 >nul
echo ===================================
echo JUPITER NOTIFIER CLIENT Auto Start Setup
echo ===================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator".
    pause
    exit /b 1
)

REM Get current directory
set CURRENT_DIR=%~dp0

REM Startup folder path
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Create startup VBS file for background execution
echo Creating startup script...
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CURRENT_DIR%"
echo WshShell.Run "run.bat", 0, False
) > "%STARTUP_DIR%\JupiterNotifierClient.vbs"

REM Task Scheduler setup (optional)
echo.
echo Register with Task Scheduler?
echo (Ensures execution at system startup)
echo.
choice /C YN /M "Press Y to register, N to skip"
if %errorlevel%==1 (
    echo Registering with Task Scheduler...
    schtasks /create /tn "JupiterNotifierClient" /tr "%CURRENT_DIR%run.bat" /sc onlogon /rl highest /f
)

echo.
echo ===================================
echo Auto Start Setup Complete!
echo ===================================
echo.
echo Settings:
echo - Startup folder: Registered
if exist "%STARTUP_DIR%\JupiterNotifierClient.vbs" (
    echo   Location: %STARTUP_DIR%\JupiterNotifierClient.vbs
)
echo.
echo The client will start automatically on next login.
echo.
echo To disable auto start:
echo 1. Delete JupiterNotifierClient.vbs from Startup folder
echo 2. Delete JupiterNotifierClient task from Task Scheduler
echo.
pause