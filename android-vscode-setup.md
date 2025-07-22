# VSCode Android Development Setup

## 1. Java Development Kit (JDK) のインストール

### Windows
```powershell
# Chocolateyを使用
choco install openjdk11

# または公式サイトから
# https://adoptium.net/
```

### macOS
```bash
brew install openjdk@11
```

## 2. Android Command Line Tools のインストール

1. [Android Developer](https://developer.android.com/studio#command-tools) から「Command line tools only」をダウンロード
2. 任意の場所に解凍（例: `C:\Android\cmdline-tools` or `~/Android/cmdline-tools`）

## 3. 環境変数の設定

### Windows (PowerShell)
```powershell
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Android", "User")
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Android\cmdline-tools\latest\bin;C:\Android\platform-tools", "User")
```

### macOS/Linux (.bashrc or .zshrc)
```bash
export ANDROID_HOME=$HOME/Android
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
```

## 4. Android SDKのインストール

```bash
# SDK Managerを使用してインストール
sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

## 5. VSCode拡張機能のインストール

VSCodeで以下の拡張機能をインストール:

1. **Android iOS Emulator** (by DiemasMichiels)
2. **Gradle for Java** (by Microsoft)
3. **Kotlin** (by fwcd)
4. **XML** (by Red Hat)

## 6. Gradle Wrapperのセットアップ

プロジェクトルートで:
```bash
gradle wrapper --gradle-version=8.0
```