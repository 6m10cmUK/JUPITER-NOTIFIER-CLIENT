@echo off
chcp 65001 > nul
title Fix WinRT Installation

echo === Fixing WinRT Installation ===
echo.

echo Uninstalling old versions...
pip uninstall winrt winrt-runtime winrt-Windows.UI.Notifications.Management -y

echo.
echo Installing fresh...
pip install --upgrade pip
pip install winrt-runtime
pip install winrt-Windows.UI.Notifications.Management

echo.
echo Testing import...
python -c "import winrt; print('SUCCESS: winrt imported successfully')"

echo.
pause