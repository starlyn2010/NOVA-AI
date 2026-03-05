$shell = New-Object -ComObject WScript.Shell
$shortcuts = Get-ChildItem "C:\Users\DELL\Desktop\*.lnk"
foreach ($lnk in $shortcuts) {
    $target = $shell.CreateShortcut($lnk.FullName).TargetPath
    Write-Host "$($lnk.Name) -> $target"
}
