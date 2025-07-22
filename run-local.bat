@echo off
chcp 65001 >nul
echo ===================================
echo JUPITER NOTIFIER CLIENT (LOCAL MODE)
echo ===================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Use local configuration
copy /Y .env.local .env >nul 2>&1

REM Start client
echo Starting client in LOCAL mode...
echo WebSocket Server: ws://localhost:8080
echo.
echo Press Ctrl+C to exit
echo.

python notify_client.py

REM Pause on error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Client terminated abnormally.
    pause
)