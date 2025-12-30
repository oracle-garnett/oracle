# Oracle Startup Script for PowerShell

Write-Host "Starting Oracle AI Assistant..." -ForegroundColor Cyan

# 1. Check for Python installation
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit
}

# 2. Navigate to the project directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectDir
Set-Location ..

# 3. Install/Update dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# 4. Launch Oracle
Write-Host "Launching Oracle..." -ForegroundColor Green
python main.py

Write-Host "Oracle has shut down." -ForegroundColor Cyan
