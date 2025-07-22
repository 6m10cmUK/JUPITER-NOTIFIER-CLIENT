@echo off
REM JUPITER-NOTIFIER-CLIENT Dependency Installer
REM This script sets up the Python environment and installs required dependencies

echo ========================================
echo JUPITER NOTIFIER CLIENT - INSTALLER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file from example if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo.
        echo Creating .env file from .env.example...
        copy ".env.example" ".env"
        echo Please edit .env file with your configuration
    )
)

echo.
echo ========================================
echo Installation completed successfully!
echo.
echo Next steps:
echo 1. Edit the .env file with your configuration
echo 2. Run 'run_client.bat' to start the client
echo ========================================
echo.
pause