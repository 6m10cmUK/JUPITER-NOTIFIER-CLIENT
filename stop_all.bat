@echo off
chcp 65001 > nul
title Stop All Notification Systems

echo === Stopping All Notification Systems ===
echo.

echo Stopping notification client...
wmic process where "name='python.exe' and commandline like '%%notify_client%%'" delete >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%notify_client%%'" delete >nul 2>&1

echo Stopping background monitor...
wmic process where "name='python.exe' and commandline like '%%background_monitor%%'" delete >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%background_monitor%%'" delete >nul 2>&1

echo Stopping any remaining Python notification processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Notification*" >nul 2>&1
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq *Notification*" >nul 2>&1

echo.
echo All notification systems stopped.
echo.
pause