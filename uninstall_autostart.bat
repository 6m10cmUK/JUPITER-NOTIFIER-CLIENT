@echo off
echo =====================================
echo JUPITER NOTIFIER 自動起動解除
echo =====================================
echo.

REM スタートアップフォルダのパス
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcutPath=%startupFolder%\JUPITER Notifier.lnk"

REM ショートカットが存在するかチェック
if exist "%shortcutPath%" (
    echo 自動起動設定を解除しています...
    del "%shortcutPath%"
    echo.
    echo =====================================
    echo 解除完了！
    echo =====================================
    echo.
    echo JUPITER Notifierの自動起動が無効になりました。
) else (
    echo.
    echo 自動起動設定が見つかりませんでした。
    echo すでに解除されている可能性があります。
)

echo.
pause