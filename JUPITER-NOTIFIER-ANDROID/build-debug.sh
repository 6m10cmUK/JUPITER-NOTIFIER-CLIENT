#!/bin/bash
# Android Debug Build Script

echo "======================================"
echo "Building JUPITER NOTIFIER ANDROID"
echo "======================================"
echo ""

# Gradleでビルド
echo "Building debug APK..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "APK location: app/build/outputs/apk/debug/app-debug.apk"
    
    # デバイスが接続されているか確認
    if adb devices | grep -q "device$"; then
        echo ""
        echo "Installing on connected device..."
        ./gradlew installDebug
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "Starting app..."
            adb shell am start -n com.jupiter.notifier/.MainActivity
        fi
    else
        echo ""
        echo "No device connected. Connect a device and run:"
        echo "./gradlew installDebug"
    fi
else
    echo ""
    echo "Build failed!"
    exit 1
fi