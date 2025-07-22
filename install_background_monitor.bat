@echo off
echo === Installing Background Monitor Dependencies ===
echo.

echo Installing core dependencies...
pip install pywin32
pip install psutil  
pip install websockets

echo.
echo Installing optional WinRT support for better notification capture...
pip install winrt-Windows.UI.Notifications.Management 2>nul
if errorlevel 1 (
    echo WinRT installation failed - will use fallback method
) else (
    echo WinRT installed successfully!
)

echo.
echo Installation complete!
pause