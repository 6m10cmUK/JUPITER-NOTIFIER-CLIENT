@echo off
chcp 65001 > nul
title Toast Notification Listener

echo === Windows Toast Notification Listener ===
echo.
echo This uses Win32 API to monitor notifications
echo Works without winrt module
echo.
echo Starting...
echo.

python toast_listener.py

if errorlevel 1 (
    echo.
    echo Error occurred
    echo Please run: install_toast_listener.bat
    echo.
    pause
)