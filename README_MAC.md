# JUPITER NOTIFIER CLIENT for macOS

macOS用のJUPITER通知クライアントです。WebSocketでサーバーから通知を受信し、メインディスプレイにオーバーレイ表示します。

## 機能

- WebSocketによるリアルタイム通知受信
- メインディスプレイへの半透明オーバーレイ表示
- 通知のクリックまたは30秒後の自動クローズ
- 他のクライアントへの通知消去の同期
- 自動再接続機能
- システム起動時の自動実行対応

## 必要要件

- macOS 10.15以降
- Python 3.8以降

## インストール

### 1. 依存関係のインストール

```bash
# Homebrewでpython3をインストール（未インストールの場合）
brew install python3

# リポジトリをクローン
git clone [repository-url]
cd JUPITER-NOTIFIER-CLIENT

# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements_mac.txt
```

### 2. 環境設定

`.env`ファイルを作成してWebSocketサーバーのURLを設定：

```bash
echo 'WS_SERVER_URL=wss://your-server-url' > .env
```


## 使用方法

### 手動起動

```bash
# 起動スクリプトを使用
./start_jupiter_notifier_mac.sh

# または直接実行
python3 notify_client_mac.py
```

### 自動起動設定

システム起動時に自動的に実行するように設定：

```bash
# 自動起動を有効にする
./install_autostart_mac.sh

# 自動起動を無効にする
./uninstall_autostart_mac.sh
```

## ログファイル

自動起動時のログは以下の場所に保存されます：

- 標準出力: `~/Library/Logs/jupiter-notifier.log`
- エラー出力: `~/Library/Logs/jupiter-notifier-error.log`

## トラブルシューティング

### 通知が表示されない

1. 通知権限を確認
2. Do Not Disturbモードがオフになっているか確認
3. ログファイルでエラーを確認

### 全画面オーバーレイが表示されない

1. アクセシビリティ権限を確認（システム環境設定 > セキュリティとプライバシー > アクセシビリティ）
2. ターミナルまたはPythonにアクセシビリティ権限を付与

### WebSocket接続エラー

1. インターネット接続を確認
2. `.env`ファイルのWS_SERVER_URLが正しいか確認
3. ファイアウォール設定を確認

## 技術仕様

- **通知ライブラリ**: pync（推奨）またはplyer（代替）
- **GUI**: tkinter（全画面オーバーレイ）
- **WebSocket**: websockets
- **非同期処理**: asyncio
- **自動起動**: launchd (Launch Agent)

## セキュリティ

- WebSocket通信はTLS/SSL (wss://)を使用
- ローカルストレージへの書き込みなし
- 最小限の権限で動作

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。