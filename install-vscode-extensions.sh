#!/bin/bash
# VSCode Android開発用拡張機能インストールスクリプト

echo "Installing VSCode extensions for Android development..."
echo ""

# 必須拡張機能
echo "Installing required extensions..."
code --install-extension fwcd.kotlin
code --install-extension vscjava.vscode-gradle
code --install-extension vscjava.vscode-java-pack

# 推奨拡張機能
echo ""
echo "Installing recommended extensions..."
code --install-extension redhat.vscode-xml

echo ""
echo "Extensions installed successfully!"
echo "Please restart VSCode if needed."