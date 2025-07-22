@echo off
chcp 65001 > nul
title Restart All Notification Systems

echo === Restarting All Notification Systems ===
echo.

echo [1/4] Killing notification clients...
REM Kill notify_client_v2.py
wmic process where "name='python.exe' and commandline like '%%notify_client%%'" delete >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%notify_client%%'" delete >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Jupiter Notification*" >nul 2>&1

echo [2/4] Killing background monitor...
REM Kill background_monitor.py
wmic process where "name='python.exe' and commandline like '%%background_monitor%%'" delete >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%background_monitor%%'" delete >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Background Notification Monitor*" >nul 2>&1

echo [3/4] Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

echo [4/4] Starting all systems...
echo.

REM Start notification client in new window
echo Starting notification client...
start "Jupiter Notification Client" /B python notify_client_v2.py

REM Small delay
timeout /t 2 /nobreak >nul

REM Start background monitor in this window
echo Starting background monitor...
echo.
python background_monitor.py

if errorlevel 1 (
    echo.
    echo Error starting background monitor
    pause
)