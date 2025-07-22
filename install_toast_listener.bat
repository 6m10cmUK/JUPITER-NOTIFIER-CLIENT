@echo off
chcp 65001 > nul
echo === Installing Toast Listener Dependencies ===
echo.

echo Installing required packages...
pip install win10toast
pip install psutil
pip install pywin32
pip install websockets

echo.
echo Installation complete!
echo.
echo To run: python toast_listener.py
echo.
pause