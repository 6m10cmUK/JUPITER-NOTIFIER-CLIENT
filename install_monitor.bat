@echo off
chcp 932 > nul
echo === Windows Notification Monitor Setup ===
echo.

echo Installing Python dependencies...
pip install winrt-runtime
pip install websockets
pip install pywin32
pip install comtypes

echo.
echo Installation complete!
echo.
echo Usage:
echo 1. Start Discord bot (WebSocket server)
echo 2. Run notification_monitor.py
echo.
echo Note:
echo - Windows 10/11 version 1809 or later required
echo - Grant notification access when prompted
echo - Settings - Privacy - Notifications
echo.
pause