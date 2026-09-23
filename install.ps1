# ColorGrabber - one-command setup
#
# Does everything needed to get ColorGrabber running from source:
#   1) Creates a virtual environment (.venv)
#   2) Installs dependencies
#   3) Builds ColorGrabber.exe with PyInstaller
#   4) Creates a Start menu shortcut
#
# Usage (no admin rights needed for this part):
#   powershell -ExecutionPolicy Bypass -File .\install.ps1
#
# If you also want ColorGrabber to start automatically on login, run
# setup_autostart.ps1 afterwards from an ADMIN PowerShell window (see
# README - "Autostart on login").

$ErrorActionPreference = "Stop"

Write-Host "== ColorGrabber setup ==" -ForegroundColor Cyan

# 1) Python check
$python = Get-Command python -ErrorAction SilentlyContinue
if (-Not $python) {
    Write-Host "ERROR: Python was not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://python.org (NOT the Microsoft Store version)." -ForegroundColor Yellow
    exit 1
}

# 2) Virtual environment
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..." -ForegroundColor Cyan
    python -m venv .venv
}
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# 3) Dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip | Out-Null
& $venvPython -m pip install -r requirements.txt

# 4) Build the .exe
Write-Host "Building ColorGrabber.exe..." -ForegroundColor Cyan
& $venvPython -m PyInstaller --noconfirm --onefile --windowed --name ColorGrabber --icon assets\icon.ico main.py

$exePath = Join-Path $PSScriptRoot "dist\ColorGrabber.exe"
if (-Not (Test-Path $exePath)) {
    Write-Host "ERROR: build finished but ColorGrabber.exe was not found." -ForegroundColor Red
    exit 1
}

# 5) Start menu shortcut
Write-Host "Creating Start menu shortcut..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1

Write-Host ""
Write-Host "All done! Search 'Color Grabber' in the Start menu to launch it." -ForegroundColor Green
Write-Host "Shortcuts: Ctrl+Alt+C grab color, Ctrl+Alt+V show window, Ctrl+Alt+Q hide window." -ForegroundColor Gray
Write-Host ""
Write-Host "Note: the 'keyboard' package needs admin rights on Windows for the" -ForegroundColor Gray
Write-Host "global hotkeys to work everywhere - run ColorGrabber.exe as administrator" -ForegroundColor Gray
Write-Host "if a shortcut doesn't seem to trigger in some other elevated app." -ForegroundColor Gray
Write-Host ""
Write-Host "Want ColorGrabber to start automatically on login? Run (as admin):" -ForegroundColor Gray
Write-Host "  powershell -ExecutionPolicy Bypass -File .\setup_autostart.ps1" -ForegroundColor Gray
