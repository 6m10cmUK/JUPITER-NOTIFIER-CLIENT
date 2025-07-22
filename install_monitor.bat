@echo off
echo === Windows通知監視システムのセットアップ ===
echo.

echo Python依存関係をインストールしています...
pip install winrt-runtime
pip install websockets
pip install pywin32
pip install comtypes

echo.
echo インストール完了！
echo.
echo 使用方法:
echo 1. Discordボット（WebSocketサーバー）を起動
echo 2. notification_monitor.py を実行
echo.
echo 注意事項:
echo - Windows 10/11 バージョン1809以降が必要です
echo - 初回実行時に通知へのアクセス許可を求められます
echo - 設定 ^> プライバシー ^> 通知 で許可してください
echo.
pause