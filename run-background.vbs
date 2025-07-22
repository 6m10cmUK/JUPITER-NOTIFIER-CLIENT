' JUPITER NOTIFIER CLIENT - Background Runner
' This script runs the notifier client without showing a console window

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get current directory
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Run the batch file hidden
WshShell.Run """" & strPath & "\run.bat""", 0, False