# Oracle AI Assistant: Executable Build Script
# This script uses PyInstaller to bundle Oracle into a standalone Windows folder.

Write-Host "--- Starting Oracle Executable Build Process ---" -ForegroundColor Cyan

# 1. Install PyInstaller if not present
Write-Host "Checking for PyInstaller..."
pip install pyinstaller

# 2. Run PyInstaller
# We use --onedir for better stability with complex imports and assets.
# We use --windowed to hide the console window for the UI.
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
    --hidden-import "customtkinter" `
    --hidden-import "PIL._tkinter_finder" `
    main.py

Write-Host "--- Build Complete! ---" -ForegroundColor Green
Write-Host "You can find your executable in the 'dist/Oracle AI Assistant' folder." -ForegroundColor Yellow
Write-Host "Note: Run the application once to allow the Web Agent to download its driver." -ForegroundColor Cyan
