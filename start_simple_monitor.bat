@echo off
chcp 65001 > nul
title Simple Notification Monitor

echo === Simple Windows Notification Monitor ===
echo.
echo This will monitor Windows notifications and forward them
echo to the WebSocket server (Discord bot).
echo.
echo Starting...
echo.

python simple_notification_monitor.py

if errorlevel 1 (
    echo.
    echo Error occurred. Trying alternative approach...
    echo.
    python notification_monitor.py
    
    if errorlevel 1 (
        echo.
        echo Both monitors failed. Please check:
        echo 1. Python is installed
        echo 2. Dependencies are installed (run install_monitor.bat)
        echo 3. Discord bot is running
        echo.
        pause
    )
)