@echo off
echo ===================================
echo JUPITER NOTIFIER CLIENT インストーラー
echo ===================================
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonがインストールされていません。
    echo Python 3.8以降をインストールしてください。
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Pythonが検出されました。
python --version
echo.

REM 仮想環境の作成
echo 仮想環境を作成しています...
python -m venv venv
if %errorlevel% neq 0 (
    echo [エラー] 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

REM 仮想環境の有効化
echo 仮想環境を有効化しています...
call venv\Scripts\activate.bat

REM pipのアップグレード
echo pipをアップグレードしています...
python -m pip install --upgrade pip

REM 依存関係のインストール
echo 依存関係をインストールしています...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [エラー] 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

REM .envファイルの作成
if not exist .env (
    echo 設定ファイルを作成しています...
    copy .env.example .env
    echo.
    echo [重要] .envファイルを編集してWebSocketサーバーのURLを設定してください。
)

echo.
echo ===================================
echo インストールが完了しました！
echo ===================================
echo.
echo 起動方法: run.batを実行してください
echo 自動起動設定: setup-autostart.batを実行してください
echo.
pause