Set wmi = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
Set procs = wmi.ExecQuery("SELECT ProcessId, CommandLine FROM Win32_Process WHERE Name = 'pythonw.exe'")

stopped = False

For Each proc In procs
    If Not IsNull(proc.CommandLine) Then
        If InStr(1, proc.CommandLine, "stockbit_rpc.pyw", vbTextCompare) > 0 Then
            proc.Terminate
            stopped = True
        End If
    End If
Next

If stopped Then
    MsgBox "Stockbit RPC stopped.", vbInformation, "Stockbit RPC"
Else
    MsgBox "Stockbit RPC is not running.", vbExclamation, "Stockbit RPC"
End If
