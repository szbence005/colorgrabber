# ColorGrabber - remove autostart
# In an admin PowerShell window:
#   powershell -ExecutionPolicy Bypass -File .\uninstall_autostart.ps1

$taskName = "ColorGrabber"

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($null -eq $existing) {
    Write-Host "No '$taskName' entry found in Task Scheduler - nothing to remove." -ForegroundColor Yellow
    exit 0
}

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
Write-Host "Autostart removed." -ForegroundColor Green
