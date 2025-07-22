@echo off
echo ===================================
echo JUPITER NOTIFIER CLIENT 自動起動設定
echo ===================================
echo.

REM 管理者権限の確認
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo このスクリプトは管理者権限で実行する必要があります。
    echo 右クリックして「管理者として実行」を選択してください。
    pause
    exit /b 1
)

REM 現在のディレクトリを取得
set CURRENT_DIR=%~dp0

REM スタートアップフォルダのパス
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM 起動用バッチファイルの作成
echo スタートアップ用バッチファイルを作成しています...
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo start /min run.bat
) > "%STARTUP_DIR%\JupiterNotifierClient.bat"

REM タスクスケジューラーでの設定（オプション）
echo.
echo タスクスケジューラーにも登録しますか？
echo （システム起動時に確実に実行されます）
echo.
choice /C YN /M "登録する場合はY、スキップする場合はN"
if %errorlevel%==1 (
    echo タスクスケジューラーに登録しています...
    schtasks /create /tn "JupiterNotifierClient" /tr "%CURRENT_DIR%run.bat" /sc onlogon /rl highest /f
    if %errorlevel% eq 0 (
        echo タスクスケジューラーへの登録が完了しました。
    ) else (
        echo タスクスケジューラーへの登録に失敗しました。
    )
)

echo.
echo ===================================
echo 自動起動設定が完了しました！
echo ===================================
echo.
echo 設定内容:
echo - スタートアップフォルダ: 登録済み
if exist "%STARTUP_DIR%\JupiterNotifierClient.bat" (
    echo   場所: %STARTUP_DIR%\JupiterNotifierClient.bat
)
echo.
echo 次回のログイン時から自動的に起動します。
echo.
echo 自動起動を無効にする場合:
echo 1. スタートアップフォルダから JupiterNotifierClient.bat を削除
echo 2. タスクスケジューラーから JupiterNotifierClient タスクを削除
echo.
pause