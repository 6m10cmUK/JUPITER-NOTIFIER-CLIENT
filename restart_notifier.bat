@echo off
echo [JUPITER NOTIFIER] Restarting...

REM Kill existing Python processes
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo Terminated existing processes
) else (
    echo No running processes found
)

REM Wait a moment
timeout /t 2 >nul

REM Change to script directory
cd /d "%~dp0"

REM Start notification client
echo [JUPITER NOTIFIER] Starting...
echo Press Ctrl+C to stop the notification client
echo.
start /B /WAIT python notify_client.py

REM Exit code handling
if %errorlevel%==0 (
    echo.
    echo [JUPITER NOTIFIER] Stopped normally
) else (
    echo.
    echo [JUPITER NOTIFIER] Stopped with error code: %errorlevel%
)