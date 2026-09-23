# ColorGrabber - set up autostart (via Task Scheduler)
#
# IMPORTANT: run this script in an ADMIN PowerShell window, otherwise the
# "-RunLevel Highest" setting will fail.
#
# What it does:
#   Creates a "ColorGrabber" entry in Task Scheduler that silently (no UAC
#   prompt) starts ColorGrabber.exe with admin rights on every logon. Admin
#   rights are needed for the global keyboard hook.
#
# Usage:
#   1) Build the .exe first (README - "Build a standalone .exe")
#   2) Right-click nothing needed here - just open an admin PowerShell,
#      cd into this folder, then run:
#        powershell -ExecutionPolicy Bypass -File .\setup_autostart.ps1

$ErrorActionPreference = "Stop"

$taskName = "ColorGrabber"
$exePath  = Join-Path $PSScriptRoot "dist\ColorGrabber.exe"

if (-Not (Test-Path $exePath)) {
    Write-Host "ERROR: could not find ColorGrabber.exe at:" -ForegroundColor Red
    Write-Host "  $exePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Build it first (README - 'Build a standalone .exe'):" -ForegroundColor Yellow
    Write-Host "  pyinstaller --noconfirm --onefile --windowed --name ColorGrabber --icon assets\icon.ico main.py" -ForegroundColor Yellow
    exit 1
}

$action    = New-ScheduledTaskAction -Execute $exePath -Argument "--hidden"
$trigger   = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings -Force | Out-Null

Write-Host "Done! ColorGrabber will now start automatically on every logon." -ForegroundColor Green
Write-Host "To remove it, run: .\uninstall_autostart.ps1" -ForegroundColor Gray
