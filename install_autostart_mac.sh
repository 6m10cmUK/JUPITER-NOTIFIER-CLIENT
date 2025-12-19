#!/bin/bash

# JUPITER NOTIFIER CLIENT for macOS - 自動起動設定スクリプト

echo "================================"
echo "JUPITER NOTIFIER 自動起動設定"
echo "================================"
echo ""

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 設定
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.jupiter.notifier.plist"
SOURCE_PLIST="$SCRIPT_DIR/com.jupiter.notifier.plist"
VENV_PATH="$SCRIPT_DIR/venv"
LOGS_DIR="$HOME/Library/Logs"

# 仮想環境の確認
if [ ! -d "$VENV_PATH" ]; then
    echo "仮想環境が見つかりません: $VENV_PATH"
    echo "仮想環境を作成しています..."
    python3 -m venv "$VENV_PATH"
    echo "依存関係をインストールしています..."
    "$VENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements_mac.txt"
fi

# LaunchAgentsディレクトリが存在しない場合は作成
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "LaunchAgentsディレクトリを作成しています..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Logsディレクトリが存在しない場合は作成
if [ ! -d "$LOGS_DIR" ]; then
    echo "Logsディレクトリを作成しています..."
    mkdir -p "$LOGS_DIR"
fi

# 既存のLaunch Agentがある場合は停止
if launchctl list | grep -q "com.jupiter.notifier"; then
    echo "既存のLaunch Agentを停止しています..."
    launchctl unload "$PLIST_FILE" 2>/dev/null
fi

# plistファイルをコピー
echo "Launch Agent設定ファイルをインストールしています..."
if [ -f "$SOURCE_PLIST" ]; then
    cp "$SOURCE_PLIST" "$PLIST_FILE"
else
    echo "エラー: plistファイルが見つかりません: $SOURCE_PLIST"
    exit 1
fi

# Launch Agentを読み込む
echo "Launch Agentを読み込んでいます..."
launchctl load "$PLIST_FILE"

# サービスを起動
echo "サービスを起動しています..."
launchctl start com.jupiter.notifier

# 状態を確認
echo ""
echo "設定が完了しました！"
echo ""
echo "状態を確認:"
launchctl list | grep com.jupiter.notifier

echo ""
echo "詳細情報:"
echo "  仮想環境: $VENV_PATH"
echo "  設定ファイル: $PLIST_FILE"
echo "  作業ディレクトリ: $SCRIPT_DIR"
echo ""
echo "ログファイルの場所:"
echo "  標準出力: ~/Library/Logs/jupiter-notifier.log"
echo "  エラー出力: ~/Library/Logs/jupiter-notifier-error.log"
echo ""
echo "ログを確認するには:"
echo "  tail -f ~/Library/Logs/jupiter-notifier.log"
echo ""
echo "アンインストールする場合は以下を実行:"
echo "  ./uninstall_autostart_mac.sh"