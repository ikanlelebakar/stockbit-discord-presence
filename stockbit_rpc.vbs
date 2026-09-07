Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

base = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = base & "\.venv\Scripts\pythonw.exe"
script = base & "\stockbit_rpc.pyw"

If fso.FileExists(pythonw) Then
    shell.Run """" & pythonw & """ """ & script & """", 0, False
Else
    shell.Run "cmd /c cd /d """ & base & """ && uv venv .venv && uv pip install -r requirements.txt && .venv\Scripts\pythonw.exe stockbit_rpc.pyw", 0, False
End If
