@echo off
chcp 65001 > nul
title Install WinSDK for Notification Monitoring

echo === Installing WinSDK Library ===
echo.
echo This is an alternative to WinRT that may work better.
echo.

echo Uninstalling old packages...
pip uninstall winrt winrt-runtime winrt-Windows.UI.Notifications.Management -y

echo.
echo Installing winsdk...
pip install --upgrade pip
pip install winsdk

echo.
echo Testing winsdk...
python -c "from winsdk.windows.ui.notifications.management import UserNotificationListener; print('SUCCESS: winsdk imported successfully')"

echo.
pause