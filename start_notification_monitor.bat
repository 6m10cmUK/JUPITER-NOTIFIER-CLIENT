@echo off
title Windows Notification Monitor

echo === Windows通知監視システム ===
echo.
echo Slackを含むすべてのWindows通知を監視して
echo WebSocketサーバーに転送します
echo.
echo 前提条件:
echo - Discordボット（ポート8080）が起動していること
echo - Slackデスクトップアプリがインストールされていること
echo.
echo 開始しています...
echo.

python notification_monitor.py

if errorlevel 1 (
    echo.
    echo エラーが発生しました
    echo 依存関係をインストールしてください: install_monitor.bat
    echo.
    pause
)