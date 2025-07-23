@echo off
echo =====================================
echo JUPITER NOTIFIER SYSTEM 起動中...
echo =====================================
echo.

REM 作業ディレクトリをスクリプトの場所に設定
cd /d "%~dp0"

REM UTF-8コンソール設定
chcp 65001 > nul

REM WIN-MONITOR (通知監視)を起動
echo [1/2] Windows通知監視を起動しています...
start "WIN-MONITOR" /min cmd /c "cd WIN-MONITOR && .\bin\x64\Release\net6.0-windows10.0.19041.0\win10-x64\NotificationMonitor.exe"
timeout /t 2 > nul

REM notify_client.py (通知表示)を起動
echo [2/2] 通知表示クライアントを起動しています...
start "NOTIFY-CLIENT" /min cmd /c "python notify_client.py"

echo.
echo =====================================
echo 起動完了！
echo =====================================
echo.
echo 両方のプログラムがバックグラウンドで実行されています。
echo 終了するには stop_all.bat を実行してください。
echo.
echo このウィンドウは5秒後に自動的に閉じます...
timeout /t 5 > nul