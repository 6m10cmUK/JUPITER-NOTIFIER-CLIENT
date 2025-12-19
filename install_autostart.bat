@echo off
echo =====================================
echo JUPITER NOTIFIER 自動起動設定 (サイレントモード)
echo =====================================
echo.

REM スタートアップフォルダのパス
set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM ショートカット作成用のVBScriptを生成
echo スタートアップショートカットを作成しています...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut("%startupFolder%\JUPITER Notifier.lnk"^)
echo oLink.TargetPath = "wscript.exe"
echo oLink.Arguments = """%~dp0start_jupiter_notifier_silent.vbs"""
echo oLink.WorkingDirectory = "%~dp0"
echo oLink.WindowStyle = 1 'Normal (VBSは元々ウィンドウなし)
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13"
echo oLink.Description = "JUPITER Notifier System - Slack/Discord通知監視 (サイレント起動)"
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
echo (黒いウィンドウは表示されません！)
echo.
echo 今すぐ起動する場合は start_jupiter_notifier_silent.vbs を
echo ダブルクリックしてください。
echo.
pause