# JUPITER NOTIFIER ANDROID

Discord Botからの通知をAndroidデバイスに全画面オーバーレイで表示するアプリ

## 機能

- Discord Botの`/610`コマンドから送信された通知を受信
- 全画面オーバーレイ表示（半透明65%、赤背景 #610610）
- 10秒後に自動的に消える（タップでも閉じる）
- バイブレーションで通知
- バックグラウンドサービスとして動作
- 端末起動時の自動起動

## 必要な権限

- **オーバーレイ表示権限**: 他のアプリの上に表示
- **インターネット権限**: WebSocket通信
- **通知権限**: フォアグラウンドサービス
- **バイブレーション権限**: 通知時の振動
- **自動起動権限**: 端末起動時の自動開始

## セットアップ

### 開発環境

1. Android Studio または VSCode + Android拡張機能
2. Android SDK (API 21以上)
3. Kotlin 1.9.0以上

### ビルド方法

```bash
# Debug APKのビルド
./build-debug.sh

# または手動で
./gradlew assembleDebug
```

### インストール

1. 開発者向けオプションを有効化
2. USBデバッグを有効化
3. PCに接続して以下を実行：

```bash
./gradlew installDebug
```

## 使い方

1. アプリを起動
2. 「オーバーレイ権限を許可」をタップ
3. WebSocket URLを設定（デフォルト: wss://site--jupiter-system--6qtwyp8fx6v7.code.run）
4. 通知サービスをON
5. Discord で `/610` コマンドを実行

## 開発

### プロジェクト構造

```
app/src/main/
├── java/com/jupiter/notifier/
│   ├── MainActivity.kt       # 設定画面
│   ├── WebSocketService.kt   # WebSocket通信サービス
│   ├── OverlayActivity.kt    # オーバーレイ表示
│   └── BootReceiver.kt       # 自動起動レシーバー
└── res/
    ├── layout/               # レイアウトファイル
    └── values/               # リソースファイル
```

### WebSocket通信フォーマット

#### クライアント → サーバー
```json
{
  "type": "register",
  "client_type": "android_notifier",
  "version": "1.0.0"
}
```

#### サーバー → クライアント
```json
{
  "type": "notification",
  "title": "Discord通知",
  "message": "メッセージ内容",
  "sender": "送信者名"
}
```

## トラブルシューティング

### オーバーレイが表示されない

1. オーバーレイ権限が許可されているか確認
2. 通知サービスが実行中か確認
3. WebSocket URLが正しいか確認

### 自動起動しない

一部のデバイスでは追加の設定が必要：
- Xiaomi: セキュリティ → 自動起動を管理
- Huawei: バッテリー → アプリ起動
- OPPO/Vivo: バッテリー → バックグラウンド管理

## ライセンス

MIT License