# ColorGrabber - create a Start menu shortcut
#
# Does NOT require admin rights - runs fine in a plain PowerShell window.
#
# Usage:
#   1) Build the .exe first (README - "Build a standalone .exe")
#   2) cd into this folder, then run:
#        powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1
#
# Afterwards, typing "Color Grabber" in the Start menu will show it, and
# clicking it opens the window (or just brings it to front if it's already
# running in the background; starts it if nothing is running yet).

$ErrorActionPreference = "Stop"

$exePath = Join-Path $PSScriptRoot "dist\ColorGrabber.exe"
$iconPath = Join-Path $PSScriptRoot "assets\icon.ico"

if (-Not (Test-Path $exePath)) {
    Write-Host "ERROR: could not find ColorGrabber.exe at:" -ForegroundColor Red
    Write-Host "  $exePath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Build it first:" -ForegroundColor Yellow
    Write-Host "  pyinstaller --noconfirm --onefile --windowed --name ColorGrabber --icon assets\icon.ico main.py" -ForegroundColor Yellow
    exit 1
}

$startMenuPrograms = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$shortcutPath = Join-Path $startMenuPrograms "Color Grabber.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $exePath
$Shortcut.WorkingDirectory = Split-Path $exePath -Parent
if (Test-Path $iconPath) {
    $Shortcut.IconLocation = $iconPath
}
$Shortcut.Description = "Color Grabber - grab a color from anywhere (Ctrl+Alt+C)"
$Shortcut.Save()

Write-Host "Done! 'Color Grabber' is now in your Start menu." -ForegroundColor Green
