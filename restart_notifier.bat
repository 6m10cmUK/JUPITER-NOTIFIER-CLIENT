@echo off
echo [JUPITER NOTIFIER] 再起動中...

REM 既存のPythonプロセスを終了
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo 既存のプロセスを終了しました
) else (
    echo 起動中のプロセスはありません
)

REM 少し待機
timeout /t 2 /nobreak >nul

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM 通知クライアントを起動
echo [JUPITER NOTIFIER] 起動中...
python notify_client.py

REM エラーが発生した場合は一時停止
if %errorlevel% neq 0 (
    echo.
    echo エラーが発生しました
    pause
)