@echo off
REM JUPITER-NOTIFIER-CLIENT Startup Installer
REM This script adds/removes the client from Windows startup

setlocal enabledelayedexpansion

echo ========================================
echo JUPITER NOTIFIER - STARTUP INSTALLER
echo ========================================
echo.

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Define startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=JUPITER Notifier.lnk"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\%SHORTCUT_NAME%"

REM Check command line argument
if "%1"=="remove" goto REMOVE
if "%1"=="status" goto STATUS
goto INSTALL

:INSTALL
echo Installing JUPITER Notifier to Windows startup...
echo.

REM Check if run_client.bat exists
if not exist "%CURRENT_DIR%\run_client.bat" (
    echo ERROR: run_client.bat not found in current directory!
    echo Please run this script from the JUPITER-NOTIFIER-CLIENT folder
    pause
    exit /b 1
)

REM Create VBS script to create shortcut
echo Creating startup shortcut...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut("%SHORTCUT_PATH%"^)
echo oLink.TargetPath = "%CURRENT_DIR%\run_client.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.IconLocation = "%CURRENT_DIR%\icon.ico"
echo oLink.Description = "JUPITER Discord Notification Client"
echo oLink.WindowStyle = 7
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

REM Execute VBS script
cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo SUCCESS: JUPITER Notifier has been added to Windows startup!
    echo.
    echo The client will now start automatically when Windows starts.
    echo Shortcut location: %SHORTCUT_PATH%
) else (
    echo.
    echo ERROR: Failed to create startup shortcut
    echo Please try running this script as Administrator
)
goto END

:REMOVE
echo Removing JUPITER Notifier from Windows startup...
echo.

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo SUCCESS: JUPITER Notifier has been removed from Windows startup
) else (
    echo INFO: JUPITER Notifier was not found in Windows startup
)
goto END

:STATUS
echo Checking startup status...
echo.

if exist "%SHORTCUT_PATH%" (
    echo STATUS: JUPITER Notifier is SET TO START with Windows
    echo Shortcut location: %SHORTCUT_PATH%
) else (
    echo STATUS: JUPITER Notifier is NOT set to start with Windows
)
goto END

:END
echo.
echo ========================================
echo Options:
echo   startup_installer.bat         - Add to startup
echo   startup_installer.bat remove  - Remove from startup
echo   startup_installer.bat status  - Check startup status
echo ========================================
echo.
pause