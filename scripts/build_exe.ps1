# Oracle AI Assistant: Executable Build Script
# This script uses PyInstaller to bundle Oracle into a standalone Windows folder.

Write-Host "--- Starting Oracle Executable Build Process ---" -ForegroundColor Cyan

# 1. Install PyInstaller if not present
Write-Host "Checking for PyInstaller..."
pip install pyinstaller

# 2. Find Tcl/Tk paths dynamically and normalize for Windows
$tclPath = python -c "import tkinter, os; print(os.path.normpath(tkinter.Tcl().eval('info library')))"
$tkPath = python -c "import tkinter, os; print(os.path.normpath(tkinter.Tk().eval('info library')))"

Write-Host "--- Path Verification ---"
Write-Host "Tcl Path: $tclPath"
Write-Host "Tk Path: $tkPath"

if (-not (Test-Path $tclPath)) { Write-Error "Tcl path not found!"; exit }
if (-not (Test-Path $tkPath)) { Write-Error "Tk path not found!"; exit }

# 3. Run PyInstaller
# We use --collect-all for customtkinter to ensure all its internal assets are grabbed.
Write-Host "Running PyInstaller... This may take a few minutes."
pyinstaller --noconfirm --onedir --windowed `
    --name "Oracle AI Assistant" `
    --icon "assets/oracle_icon.ico" `
    --add-data "core;core" `
    --add-data "memory;memory" `
    --add-data "safeguards;safeguards" `
    --add-data "ui;ui" `
    --add-data "models;models" `
    --add-data "config;config" `
    --add-data "assets;assets" `
    --add-data "${tclPath};_tcl_data" `
    --add-data "${tkPath};_tk_data" `
    --collect-all "customtkinter" `
    --hidden-import "PIL._tkinter_finder" `
    --hidden-import "PIL.Image" `
    --hidden-import "PIL.ImageTk" `
    --hidden-import "chromadb.telemetry.product.posthog" `
    --hidden-import "posthog" `
    main.py

# Ensure the assets folder is also copied to the root of the dist folder for runtime access
Copy-Item -Path "assets" -Destination "dist/Oracle AI Assistant/assets" -Recurse -Force

Write-Host "--- Build Complete! ---" -ForegroundColor Green
Write-Host "You can find your executable in the 'dist/Oracle AI Assistant' folder." -ForegroundColor Yellow
Write-Host "Note: Run the application once to allow the Web Agent to download its driver." -ForegroundColor Cyan
