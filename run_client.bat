@echo off
REM JUPITER-NOTIFIER-CLIENT Run Script
REM This script runs the JUPITER notification client

echo ========================================
echo JUPITER NOTIFIER CLIENT
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if client.py exists
if not exist "client.py" (
    echo ERROR: client.py not found!
    echo Please ensure all files are properly extracted
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)

REM Run the client
echo Starting JUPITER Notifier Client...
echo Press Ctrl+C to stop
echo.
python client.py

REM If the script exits, pause to show any error messages
if errorlevel 1 (
    echo.
    echo Client exited with an error
    pause
)