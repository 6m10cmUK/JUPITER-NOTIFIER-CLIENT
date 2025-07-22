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
timeout /t 2 /nobreak >nul

REM Change to script directory
cd /d "%~dp0"

REM Start notification client
echo [JUPITER NOTIFIER] Starting...
python notify_client.py

REM Pause if error occurred
if %errorlevel% neq 0 (
    echo.
    echo An error occurred
    pause
)