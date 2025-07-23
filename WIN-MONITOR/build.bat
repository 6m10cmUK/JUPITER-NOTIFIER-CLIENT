@echo off
echo Building Notification Monitor...
echo.

dotnet build -c Release

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable location: bin\Release\net6.0-windows10.0.19041.0\win10-x64\NotificationMonitor.exe
echo.
pause