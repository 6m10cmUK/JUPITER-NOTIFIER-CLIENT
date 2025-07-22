@echo off
echo ===================================
echo JUPITER NOTIFIER CLIENT
echo ===================================
echo.

REM 仮想環境が存在するか確認
if not exist venv (
    echo [エラー] 仮想環境が見つかりません。
    echo 先にinstall.batを実行してください。
    pause
    exit /b 1
)

REM 仮想環境の有効化
call venv\Scripts\activate.bat

REM 環境変数の読み込み
if exist .env (
    echo 設定ファイルを読み込んでいます...
    for /f "delims=" %%x in (.env) do (
        set "%%x"
    )
) else (
    echo [警告] .envファイルが見つかりません。
    echo デフォルト設定を使用します。
)

REM クライアントの起動
echo クライアントを起動しています...
echo WebSocketサーバー: %WS_SERVER_URL%
echo.
echo 終了するには Ctrl+C を押してください
echo.

python notify_client.py

REM エラーが発生した場合は一時停止
if %errorlevel% neq 0 (
    echo.
    echo [エラー] クライアントが異常終了しました。
    pause
)