' JUPITER NOTIFIER - サイレント起動スクリプト
' 黒いコンソールウィンドウを表示せずにバックグラウンドで起動します

Option Explicit

Dim objShell, objFSO
Dim strBasePath, strMonitorPath, strPythonPath

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' スクリプトのディレクトリを取得
strBasePath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' WIN-MONITORのパス
strMonitorPath = strBasePath & "\WIN-MONITOR\bin\x64\Release\net6.0-windows10.0.19041.0\win10-x64\NotificationMonitor.exe"

' WIN-MONITORを非表示で起動 (0 = 非表示, False = 完了を待たない)
objShell.Run """" & strMonitorPath & """", 0, False

' 2秒待機
WScript.Sleep 2000

' notify_client.pyをpythonw.exe（非表示）で起動
objShell.CurrentDirectory = strBasePath
objShell.Run "pythonw """ & strBasePath & "\notify_client.py""", 0, False

Set objShell = Nothing
Set objFSO = Nothing

' 完了（このスクリプトはすぐに終了）

