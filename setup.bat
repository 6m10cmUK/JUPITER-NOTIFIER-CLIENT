@echo off
REM JUPITER-NOTIFIER-CLIENT Complete Setup Script
REM This script performs a complete installation and configuration

echo ========================================
echo JUPITER NOTIFIER CLIENT - SETUP
echo ========================================
echo.
echo Welcome to JUPITER Notifier Client Setup!
echo This wizard will guide you through the installation process.
echo.
pause

REM Step 1: Check Python
echo.
echo [Step 1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download Python for Windows
    echo 3. IMPORTANT: Check "Add Python to PATH" during installation
    echo 4. Run this setup again after installing Python
    pause
    exit /b 1
)
echo Python found:
python --version

REM Step 2: Install dependencies
echo.
echo [Step 2/5] Installing dependencies...
call install_dependencies.bat
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Step 3: Configure settings
echo.
echo [Step 3/5] Configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo.
        echo IMPORTANT: Please edit the .env file with your settings:
        echo - JUPITER_SERVER_URL: Your JUPITER server URL
        echo - DISCORD_USER_ID: Your Discord user ID
        echo - DISCORD_GUILD_ID: Your Discord server ID
        echo.
        echo Opening .env file in notepad...
        start notepad .env
        echo.
        echo Press any key after you have saved your settings...
        pause >nul
    )
)

REM Step 4: Test connection
echo.
echo [Step 4/5] Testing connection...
echo This will verify your configuration is correct.
echo.

REM Create a simple test script
(
echo import os
echo import sys
echo from dotenv import load_dotenv
echo load_dotenv(^)
echo print("Configuration loaded successfully!"^)
echo print(f"Server URL: {os.getenv('JUPITER_SERVER_URL')}"^)
echo print(f"User ID: {os.getenv('DISCORD_USER_ID')}"^)
echo if not os.getenv('JUPITER_SERVER_URL'^) or not os.getenv('DISCORD_USER_ID'^):
echo     print("ERROR: Missing required configuration!"^)
echo     sys.exit(1^)
echo print("Configuration looks good!"^)
) > test_config.py

call venv\Scripts\activate.bat
python test_config.py
if errorlevel 1 (
    del test_config.py
    echo.
    echo ERROR: Configuration test failed
    echo Please check your .env file settings
    pause
    exit /b 1
)
del test_config.py

REM Step 5: Startup option
echo.
echo [Step 5/5] Startup Configuration...
echo.
echo Would you like JUPITER Notifier to start automatically with Windows?
echo.
choice /C YN /M "Add to Windows startup"
if errorlevel 2 (
    echo Skipping startup configuration.
) else (
    call startup_installer.bat
)

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=JUPITER Notifier.lnk"

(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut("%DESKTOP%\%SHORTCUT_NAME%"^)
echo oLink.TargetPath = "%~dp0run_client.bat"
echo oLink.WorkingDirectory = "%~dp0"
echo oLink.IconLocation = "%~dp0icon.ico"
echo oLink.Description = "JUPITER Discord Notification Client"
echo oLink.Save
) > "%TEMP%\create_desktop_shortcut.vbs"

cscript //nologo "%TEMP%\create_desktop_shortcut.vbs"
del "%TEMP%\create_desktop_shortcut.vbs"

REM Final message
echo.
echo ========================================
echo SETUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo JUPITER Notifier Client has been installed.
echo.
echo To start the client:
echo - Use the desktop shortcut
echo - Or run: run_client.bat
echo.
echo For help and documentation, see README.md
echo.
echo Would you like to start JUPITER Notifier now?
choice /C YN /M "Start JUPITER Notifier"
if errorlevel 2 (
    echo.
    echo Setup complete. You can start JUPITER Notifier anytime using the desktop shortcut.
    pause
) else (
    echo.
    echo Starting JUPITER Notifier...
    start "" "%~dp0run_client.bat"
    echo.
    echo JUPITER Notifier is now running!
    echo You can find it in your system tray.
    timeout /t 5
)