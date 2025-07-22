@echo off
chcp 65001 > nul
title Install WinRT for Notification Monitoring

echo === Installing WinRT Library ===
echo.

echo This will install the Windows Runtime Python binding for better notification support.
echo.

pip install winrt-Windows.UI.Notifications.Management

if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Installation failed!
    echo.
    echo Possible solutions:
    echo 1. Try: pip install winrt
    echo 2. Or: pip install winsdk
    echo 3. Make sure you have Python 3.7 or newer
    echo ============================================
) else (
    echo.
    echo Installation successful!
    echo Please restart the notification monitor.
)

echo.
pause