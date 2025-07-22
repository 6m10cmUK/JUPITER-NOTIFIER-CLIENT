@echo off
echo [JUPITER NOTIFIER] Starting...
echo Press Ctrl+C to stop the notification client
echo.

REM Change to script directory
cd /d "%~dp0"

REM Start notification client directly
python notify_client.py

REM Exit code handling
if %errorlevel%==0 (
    echo.
    echo [JUPITER NOTIFIER] Stopped normally
) else if %errorlevel%==-1073741510 (
    echo.
    echo [JUPITER NOTIFIER] Stopped by user (Ctrl+C)
) else (
    echo.
    echo [JUPITER NOTIFIER] Stopped with error code: %errorlevel%
)