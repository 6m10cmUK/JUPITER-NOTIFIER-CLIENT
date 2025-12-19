#!/bin/bash

# JUPITER NOTIFIER CLIENT for macOS - 自動起動解除スクリプト

echo "================================"
echo "JUPITER NOTIFIER 自動起動解除"
echo "================================"
echo ""

PLIST_FILE="$HOME/Library/LaunchAgents/com.jupiter.notifier.plist"
LOG_FILES=(
    "$HOME/Library/Logs/jupiter-notifier.log"
    "$HOME/Library/Logs/jupiter-notifier-error.log"
)

# サービスの状態を確認
echo "現在のサービス状態:"
if launchctl list | grep -q "com.jupiter.notifier"; then
    launchctl list | grep com.jupiter.notifier
    echo ""
    
    # サービスを停止
    echo "サービスを停止しています..."
    launchctl stop com.jupiter.notifier
    
    # Launch Agentを無効化
    echo "Launch Agentを無効化しています..."
    launchctl unload "$PLIST_FILE" 2>/dev/null
    echo "Launch Agentの無効化が完了しました"
else
    echo "サービスは実行されていません"
fi

echo ""

# plistファイルを削除
if [ -f "$PLIST_FILE" ]; then
    echo "設定ファイルを削除しています..."
    rm "$PLIST_FILE"
    echo "削除完了: $PLIST_FILE"
else
    echo "設定ファイルが見つかりません: $PLIST_FILE"
fi

# ログファイルの処理
echo ""
echo "ログファイルの処理:"
for LOG_FILE in "${LOG_FILES[@]}"; do
    if [ -f "$LOG_FILE" ]; then
        echo "  見つかりました: $LOG_FILE"
    fi
done

echo ""
read -p "ログファイルも削除しますか？ (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for LOG_FILE in "${LOG_FILES[@]}"; do
        if [ -f "$LOG_FILE" ]; then
            rm "$LOG_FILE"
            echo "  削除しました: $LOG_FILE"
        fi
    done
else
    echo "ログファイルは保持されます"
fi

echo ""
echo "自動起動の解除が完了しました！"
echo ""
echo "手動で起動する場合は以下を実行:"
echo "  ./start_jupiter_notifier_mac.sh"