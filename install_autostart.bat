@echo off
echo =====================================
echo JUPITER NOTIFIER 自動起動設定
echo =====================================
echo.

REM 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo エラー: このスクリプトは管理者権限で実行する必要があります。
    echo 右クリックして「管理者として実行」を選択してください。
    pause
    exit /b 1
)

REM スタートアップフォルダのパス
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM ショートカット作成用のVBScriptを生成
echo スタートアップショートカットを作成しています...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut("%startupFolder%\JUPITER Notifier.lnk"^)
echo oLink.TargetPath = "%~dp0start_jupiter_notifier.bat"
echo oLink.WorkingDirectory = "%~dp0"
echo oLink.WindowStyle = 7 'Minimized
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13"
echo oLink.Description = "JUPITER Notifier System - Slack/Discord通知監視"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

REM VBScriptを実行
cscript //NoLogo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo =====================================
echo 設定完了！
echo =====================================
echo.
echo JUPITER Notifierは次回のPC起動時から自動的に開始されます。
echo.
echo 今すぐ起動する場合は start_jupiter_notifier.bat を実行してください。
echo.
pause