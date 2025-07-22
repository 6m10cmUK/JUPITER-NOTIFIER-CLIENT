@echo off
echo [JUPITER NOTIFIER V2] Starting improved version...
echo Press Ctrl+C to stop the notification client
echo.

REM Change to script directory
cd /d "%~dp0"

REM Start notification client V2
python notify_client_v2.py

REM Exit code handling
if %errorlevel%==0 (
    echo.
    echo [JUPITER NOTIFIER V2] Stopped normally
) else if %errorlevel%==-1073741510 (
    echo.
    echo [JUPITER NOTIFIER V2] Stopped by user (Ctrl+C)
) else (
    echo.
    echo [JUPITER NOTIFIER V2] Stopped with error code: %errorlevel%
)