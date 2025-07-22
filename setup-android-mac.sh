#!/bin/bash
# macOS用 Android開発環境セットアップスクリプト

echo "======================================"
echo "Android Development Setup for macOS"
echo "======================================"
echo ""

# Homebrewの確認
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "1. Installing Java Development Kit..."
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc

echo ""
echo "2. Installing Android Command Line Tools..."
brew install --cask android-commandlinetools

echo ""
echo "3. Setting up environment variables..."
cat >> ~/.zshrc << 'EOF'

# Android SDK
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0
EOF

source ~/.zshrc

echo ""
echo "4. Installing Android SDK components..."
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

echo ""
echo "5. Installing Gradle..."
brew install gradle

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Please restart your terminal or run:"
echo "source ~/.zshrc"
echo ""
echo "Then run ./create-android-project.sh to create the project"