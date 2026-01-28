# Oracle Master Startup Script
# This script initializes the Brain (Ollama), the Hands (Fooocus), and the Heart (Oracle)

Write-Host "--- Initiating Oracle 'No Limits' Startup ---" -ForegroundColor Cyan

# 1. Check for Ollama and the Uncensored Brain
Write-Host "[1/3] Checking for the Brain (Ollama)..." -ForegroundColor Yellow
$ollamaCheck = Get-Process ollama -ErrorAction SilentlyContinue
if (!$ollamaCheck) {
    Write-Host "Starting Ollama..." -ForegroundColor Gray
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}
# Ensure dolphin-phi is the active model (Switched for better laptop compatibility)
Start-Process "ollama" -ArgumentList "run dolphin-phi"

# 2. Check for the Hands (Fooocus)
Write-Host "[2/3] Checking for the Hands (Fooocus)..." -ForegroundColor Yellow
# Look for Fooocus in common locations
$fooocusPath = Join-Path $PSScriptRoot "..\Fooocus\run.bat"
if (!(Test-Path $fooocusPath)) {
    $fooocusPath = Join-Path $PSScriptRoot "..\Fooocus_win64_2-5-0\run.bat"
}

if (Test-Path $fooocusPath) {
    Write-Host "Starting Fooocus in background..." -ForegroundColor Gray
    Start-Process "cmd.exe" -ArgumentList "/c `"$fooocusPath`"" -WindowStyle Minimized
} else {
    Write-Host "WARNING: Fooocus folder not found. Please ensure Fooocus is installed next to the oracle folder." -ForegroundColor Red
}

# 3. Start Oracle
Write-Host "[3/3] Waking up Oracle..." -ForegroundColor Yellow
Set-Location $PSScriptRoot
python main.py

Write-Host "--- Oracle is now Online ---" -ForegroundColor Green
pause
