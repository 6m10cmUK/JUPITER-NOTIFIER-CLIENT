@echo off
chcp 65001 > nul
title Background Notification Monitor

echo === Background Notification Monitor ===
echo.
echo This will run continuously in the background
echo monitoring all Windows notifications
echo.
echo The console will minimize after 5 seconds
echo Check notification_monitor.log for activity
echo.
echo Starting...
echo.

python background_monitor.py

if errorlevel 1 (
    echo.
    echo Error occurred
    echo Please install dependencies:
    echo pip install pywin32 psutil websockets
    echo.
    pause
)