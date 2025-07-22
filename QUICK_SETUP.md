# クイックセットアップガイド

## 5分で設定完了！

### 1. ダウンロード
```bash
git clone https://github.com/6m10cmUK/JUPITER-NOTIFIER-CLIENT.git
cd JUPITER-NOTIFIER-CLIENT
```

### 2. インストール
```bash
install.bat
```

### 3. 設定ファイルをコピー
```bash
copy .env.windows .env
```

**注意**: `.env.windows`には既にNorthflankの設定が入っているので、そのまま使えます！

### 4. 起動
```bash
run.bat
```

### 5. 動作確認
Discordで以下のコマンドを実行：
```
/610 message: テスト通知
```

Windows PCに全画面で赤い通知が表示されれば成功です！

## 自動起動設定（オプション）
管理者権限でコマンドプロンプトを開いて：
```bash
setup-autostart.bat
```

これでWindows起動時に自動的にクライアントが起動します。

## トラブルシューティング

### 通知が表示されない場合
1. コンソールに「サーバーに接続しました」と表示されているか確認
2. Discordボットがオンラインか確認
3. ファイアウォールでPythonが許可されているか確認

### よくある質問

**Q: Pythonがインストールされているか分からない**
A: コマンドプロンプトで `python --version` を実行してください

**Q: エラーが出て起動できない**
A: `install.bat`を再実行してみてください

**Q: 通知の色や表示時間を変更したい**
A: `/610`コマンドのオプションで変更できます：
```
/610 message: メッセージ title: タイトル duration: 10
```