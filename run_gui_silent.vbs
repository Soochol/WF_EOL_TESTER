' WF EOL Tester - Silent GUI Launcher
' This VBScript launches the GUI application completely silently (no console window)

Dim objShell, objFSO, currentDir, uvCommand, pythonCommand

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get current directory
currentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to project directory
objShell.CurrentDirectory = currentDir

' Try UV first (preferred method)
On Error Resume Next
uvCommand = "uv run src/main_gui.py"
objShell.Run uvCommand, 0, False  ' 0 = hidden window, False = don't wait

' If UV fails, try with pythonw.exe
If Err.Number <> 0 Then
    Err.Clear
    pythonCommand = "pythonw src/main_gui.py"
    objShell.Run pythonCommand, 0, False
End If

' If pythonw fails, try with python.exe (last resort)
If Err.Number <> 0 Then
    Err.Clear
    pythonCommand = "python src/main_gui.py"
    objShell.Run pythonCommand, 0, False
End If

On Error GoTo 0

Set objShell = Nothing
Set objFSO = Nothing