#!/bin/bash
# Cursor用 Android開発拡張機能インストールスクリプト

echo "Installing Cursor extensions for Android development..."
echo ""

# Cursorのコマンドラインツールを使用
# 必須拡張機能
echo "Installing required extensions..."
cursor --install-extension fwcd.kotlin
cursor --install-extension vscjava.vscode-gradle
cursor --install-extension vscjava.vscode-java-pack

# 推奨拡張機能
echo ""
echo "Installing recommended extensions..."
cursor --install-extension redhat.vscode-xml

echo ""
echo "Extensions installed successfully!"
echo "Please restart Cursor if needed."