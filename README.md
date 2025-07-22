# JUPITER NOTIFIER CLIENT

Discord Botからの通知をWindows PCに全画面表示するクライアントアプリケーション

## 機能

- Discord Botの`/610`コマンドから送信された通知を受信
- 全画面での通知表示（暗い赤色の背景）
- 10秒後に自動的に消える
- ESCキーまたはクリックで即座に閉じる
- 自動再接続機能

## 必要な環境

- Windows 10/11
- Python 3.8以降
- Discord Bot側のWebSocketサーバー

## セットアップ

### 1. インストール

1. このリポジトリをクローンまたはダウンロード
```bash
git clone https://github.com/yourusername/JUPITER-NOTIFIER-CLIENT.git
cd JUPITER-NOTIFIER-CLIENT
```

2. インストーラーを実行
```bash
install.bat
```

### 2. 設定

`.env.windows`を`.env`にコピーして使用：

```bash
copy .env.windows .env
```

**Northflankを使用している場合（推奨）**

`.env`ファイルは以下の設定でそのまま使用できます：

```env
# NorthflankでホストされているBotサーバー
WS_SERVER_URL=wss://jupiter-system--jupiter-system--r6m10cms-team.p1.northflank.app
```

**その他の環境の場合**

```env
# ローカルの場合
WS_SERVER_URL=ws://localhost:8080

# LAN内の別PCの場合
WS_SERVER_URL=ws://192.168.1.100:8080
```

### 3. 起動方法

#### 手動起動
```bash
run.bat
```

#### 自動起動設定
管理者権限で実行：
```bash
setup-autostart.bat
```

これにより以下が設定されます：
- Windowsログイン時の自動起動
- タスクスケジューラーへの登録（オプション）

## 使い方

1. クライアントを起動（`run.bat`）
2. Discord Botが起動しているサーバーで`/610`コマンドを実行
3. Windows PCに全画面通知が表示される

### コマンド使用方法

```
/610 message: [メッセージ]
```

- `message`: 表示するメッセージ（必須）
- 表示時間: 10秒固定
- タイトル: "Discord通知"固定

## トラブルシューティング

### 通知が表示されない

1. **クライアントが起動しているか確認**
   - コマンドプロンプトでログを確認
   - 「サーバーに接続しました」と表示されているか

2. **ファイアウォールの設定**
   - Windows Defenderファイアウォールで`python.exe`を許可
   - 使用するポート（デフォルト8080）を開放

3. **WebSocketサーバーのURL**
   - `.env`ファイルのURLが正しいか確認
   - pingでサーバーに到達できるか確認

### 自動起動が機能しない

1. **管理者権限で設定**
   - `setup-autostart.bat`を右クリック→「管理者として実行」

2. **アンチウイルスソフトの確認**
   - スタートアップフォルダへのアクセスがブロックされていないか

3. **手動で確認**
   - `Win + R` → `shell:startup`でスタートアップフォルダを開く
   - `JupiterNotifierClient.bat`が存在するか確認

## ファイル構成

```
JUPITER-NOTIFIER-CLIENT/
├── notify_client.py      # メインのPythonスクリプト
├── requirements.txt      # Python依存関係
├── .env.example         # 設定ファイルのテンプレート
├── .env                 # 実際の設定ファイル（gitignore）
├── install.bat          # インストーラー
├── run.bat              # 起動スクリプト
├── setup-autostart.bat  # 自動起動設定
└── README.md            # このファイル
```

## セキュリティに関する注意

- WebSocketサーバーのURLは信頼できるものを使用してください
- インターネット経由で使用する場合はWSS（WebSocket Secure）を推奨
- 認証機能は現在実装されていません

## ライセンス

MIT License

## 作者

[Your Name]