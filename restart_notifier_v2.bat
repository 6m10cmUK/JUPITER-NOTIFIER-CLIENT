@echo off
echo [JUPITER NOTIFIER V2] Restarting...

REM Kill ALL Python processes (both V1 and V2)
echo Terminating all Python processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo Successfully terminated existing Python processes
) else (
    echo No Python processes were running
)

REM Also try pythonw.exe (for GUI apps)
taskkill /F /IM pythonw.exe 2>nul

REM Wait a moment for processes to fully terminate
timeout /t 2 >nul

REM Change to script directory
cd /d "%~dp0"

REM Start notification client V2
echo [JUPITER NOTIFIER V2] Starting improved version...
echo Press Ctrl+C to stop the notification client
echo.
start /B /WAIT python notify_client_v2.py

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

REM Wait before closing
timeout /t 2 >nul