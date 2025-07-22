#!/bin/bash
# 最小限のAndroid SDK環境をインストール

echo "======================================"
echo "Minimal Android SDK Installation"
echo "======================================"
echo ""

# Android SDK のダウンロード URL
CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-mac-10406996_latest.zip"
SDK_ROOT="$HOME/Library/Android/sdk"

echo "1. Creating SDK directory..."
mkdir -p "$SDK_ROOT"

echo ""
echo "2. Downloading Android command-line tools..."
curl -o /tmp/cmdline-tools.zip "$CMDLINE_TOOLS_URL"

echo ""
echo "3. Extracting tools..."
unzip -q /tmp/cmdline-tools.zip -d /tmp/
mkdir -p "$SDK_ROOT/cmdline-tools"
mv /tmp/cmdline-tools "$SDK_ROOT/cmdline-tools/latest"

echo ""
echo "4. Setting up environment..."
export ANDROID_HOME="$SDK_ROOT"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

echo ""
echo "5. Accepting licenses..."
yes | "$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses

echo ""
echo "6. Installing essential components..."
"$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" \
    "platform-tools" \
    "platforms;android-34" \
    "build-tools;34.0.0"

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Add these to your ~/.zshrc:"
echo 'export ANDROID_HOME="$HOME/Library/Android/sdk"'
echo 'export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"'
echo ""
echo "Then run: source ~/.zshrc"