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
# Ensure dolphin-llama3 is the active model
Start-Process "ollama" -ArgumentList "run dolphin-llama3"

# 2. Check for the Hands (Fooocus)
Write-Host "[2/3] Checking for the Hands (Fooocus)..." -ForegroundColor Yellow
$fooocusPath = Join-Path $PSScriptRoot "..\Fooocus_win64_2-5-0\run.bat"
if (Test-Path $fooocusPath) {
    Write-Host "Starting Fooocus in background..." -ForegroundColor Gray
    Start-Process "cmd.exe" -ArgumentList "/c `"$fooocusPath`"" -WindowStyle Minimized
} else {
    Write-Host "WARNING: Fooocus folder not found at $fooocusPath. Please ensure Fooocus is installed next to the oracle folder." -ForegroundColor Red
}

# 3. Start Oracle
Write-Host "[3/3] Waking up Oracle..." -ForegroundColor Yellow
$oracleScript = Join-Path $PSScriptRoot "scripts\start_oracle.ps1"
if (Test-Path $oracleScript) {
    & $oracleScript
} else {
    Write-Host "ERROR: Oracle startup script not found!" -ForegroundColor Red
}

Write-Host "--- Oracle is now Online ---" -ForegroundColor Green
pause
