#!/bin/bash
# Android ビルド環境セットアップスクリプト

echo "======================================"
echo "Android Build Environment Setup"
echo "======================================"
echo ""

# 1. Gradle Wrapperの生成
echo "1. Creating Gradle Wrapper..."
gradle wrapper --gradle-version=8.0 --distribution-type=bin

# 2. 実行権限の付与
echo ""
echo "2. Setting executable permissions..."
chmod +x gradlew

# 3. Gradle Wrapperファイルのダウンロード
echo ""
echo "3. Downloading Gradle Wrapper JAR..."
mkdir -p gradle/wrapper
curl -L https://services.gradle.org/distributions/gradle-8.0-bin.zip -o /tmp/gradle-8.0-bin.zip
unzip -j /tmp/gradle-8.0-bin.zip "*/gradle-wrapper.jar" -d gradle/wrapper/
rm /tmp/gradle-8.0-bin.zip

# 4. Android SDKライセンスの承認
echo ""
echo "4. Accepting Android SDK licenses..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses

# 5. 必要なSDKコンポーネントのインストール
echo ""
echo "5. Installing required SDK components..."
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
    "build-tools;34.0.0" \
    "platforms;android-34" \
    "platform-tools" \
    "emulator" \
    "system-images;android-34;google_apis;arm64-v8a"

# 6. プロジェクトの依存関係をダウンロード
echo ""
echo "6. Downloading project dependencies..."
./gradlew dependencies

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "You can now build the project with:"
echo "./gradlew assembleDebug"
echo ""
echo "To check connected devices:"
echo "adb devices"