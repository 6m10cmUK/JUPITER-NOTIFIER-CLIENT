@echo off
chcp 932 > nul
title Windows Notification Monitor

echo === Windows Notification Monitor ===
echo.
echo Monitoring all Windows notifications including Slack
echo and forwarding to WebSocket server
echo.
echo Prerequisites:
echo - Discord bot running on port 8080
echo - Slack desktop app installed
echo.
echo Starting...
echo.

python notification_monitor.py

if errorlevel 1 (
    echo.
    echo Error occurred
    echo Please install dependencies: install_monitor.bat
    echo.
    pause
)