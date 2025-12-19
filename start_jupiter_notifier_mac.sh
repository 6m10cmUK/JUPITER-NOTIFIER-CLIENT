#!/bin/bash

# JUPITER NOTIFIER CLIENT for macOS - 起動スクリプト

echo "================================"
echo "JUPITER NOTIFIER CLIENT for macOS"
echo "================================"
echo ""

# Pythonがインストールされているか確認
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python 3がインストールされていません"
    echo "Homebrewを使用してインストールしてください:"
    echo "  brew install python3"
    exit 1
fi

# HomebrewのPythonを優先的に使用
export PATH="/opt/homebrew/opt/python@3.13/bin:$PATH"
PYTHON_PATH="/opt/homebrew/opt/python@3.13/bin/python3"

# 仮想環境が存在しない場合は作成
if [ ! -d "venv" ]; then
    echo "仮想環境を作成しています..."
    $PYTHON_PATH -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係をインストール
echo "依存関係をインストールしています..."
pip install -r requirements_mac.txt

# 環境設定ファイルのチェック
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: .envファイルが見つかりません"
    echo "WS_SERVER_URLを設定する場合は.envファイルを作成してください"
    echo "例:"
    echo "  echo 'WS_SERVER_URL=wss://your-server-url' > .env"
    echo ""
fi

# 準備完了
echo ""
echo "起動中..."

# アプリケーションを起動
echo ""
echo "JUPITER NOTIFIERを起動しています..."
python3 notify_client_mac.py