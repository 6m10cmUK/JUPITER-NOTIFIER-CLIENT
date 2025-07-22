@echo off
chcp 65001 >nul
echo ===================================
echo JUPITER NOTIFIER CLIENT Installer
echo ===================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.8 or later.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies with retry
echo Installing dependencies...
echo - websockets
echo - python-dotenv
echo - screeninfo
echo.

pip install -r requirements.txt --upgrade
if %errorlevel% neq 0 (
    echo.
    echo Retrying installation...
    REM Try installing each package individually
    pip install websockets==12.0
    pip install python-dotenv==1.0.0
    pip install screeninfo==0.8.1
    
    REM Check if all packages are installed
    pip show websockets python-dotenv screeninfo >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        echo Please try manual installation:
        echo   pip install websockets python-dotenv screeninfo
        pause
        exit /b 1
    )
)

REM Create .env file
if not exist .env (
    echo Creating configuration file...
    copy .env.example .env
    echo.
    echo [IMPORTANT] .env file created with default settings.
    echo WebSocket URL: wss://site--jupiter-system--6qtwyp8fx6v7.code.run
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import websockets, dotenv, screeninfo; print('All modules installed successfully!')"
if %errorlevel% neq 0 (
    echo [WARNING] Some modules may not be installed correctly.
)

echo.
echo ===================================
echo Installation Complete!
echo ===================================
echo.
echo How to start: Run run.bat
echo Auto-start setup: Run setup-autostart.bat
echo.
pause