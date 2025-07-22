@echo off
echo [JUPITER NOTIFIER] Installing Android app with 30sec display...

REM Check if ADB is installed
where adb >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: ADB not found. Please install Android SDK Platform Tools.
    echo Download from: https://developer.android.com/studio/releases/platform-tools
    pause
    exit /b 1
)

REM Check if device is connected
adb devices | findstr /r "device$" >nul
if %errorlevel% neq 0 (
    echo ERROR: No Android device connected.
    echo Please connect your device and enable USB debugging.
    pause
    exit /b 1
)

REM Uninstall old version
echo Uninstalling old version...
adb uninstall com.jupiter.notifier 2>nul

REM Install new version
echo Installing new version...
adb install -r jupiter-notifier-30sec.apk
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo The app will now display notifications for 30 seconds.
pause