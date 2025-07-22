@echo off
chcp 65001 >nul
echo ===================================
echo Fix Startup Configuration
echo ===================================
echo.

REM Get current directory
set CURRENT_DIR=%~dp0

REM Startup folder path
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Step 1: Removing old BAT file...
if exist "%STARTUP_DIR%\JupiterNotifierClient.bat" (
    del "%STARTUP_DIR%\JupiterNotifierClient.bat"
    echo - Old BAT file removed
) else (
    echo - No old BAT file found
)

echo.
echo Step 2: Creating new VBS file...
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CURRENT_DIR%"
echo WshShell.Run "run.bat", 0, False
) > "%STARTUP_DIR%\JupiterNotifierClient.vbs"

if exist "%STARTUP_DIR%\JupiterNotifierClient.vbs" (
    echo - New VBS file created successfully
) else (
    echo - [ERROR] Failed to create VBS file
)

echo.
echo ===================================
echo Startup Fix Complete!
echo ===================================
echo.
echo The client will now start in background mode on Windows login.
echo Location: %STARTUP_DIR%\JupiterNotifierClient.vbs
echo.
pause