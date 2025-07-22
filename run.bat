@echo off
chcp 65001 >nul
echo ===================================
echo JUPITER NOTIFIER CLIENT
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

REM Set default WebSocket URL
set WS_SERVER_URL=wss://site--jupiter-system--6qtwyp8fx6v7.code.run

REM Load environment variables from .env if exists
if exist .env (
    echo Loading configuration...
    for /f "usebackq tokens=*" %%a in (".env") do (
        echo %%a | findstr /r "^[^#]" >nul && set "%%a"
    )
)

REM Start client
echo Starting client...
echo WebSocket Server: %WS_SERVER_URL%
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