# Oracle AI Assistant - Windows Build Script
# This script automates the PyInstaller process with all necessary fixes.

# 1. Ensure we are in the project root
$ProjectRoot = Get-Location
Write-Host "Building Oracle from: $ProjectRoot" -ForegroundColor Cyan

# 2. Dynamically find Tcl/Tk paths to fix the 'Tcl data directory not found' error
$python_path = python -c "import sys; print(sys.prefix)"
$tcl_path = Join-Path $python_path "tcl/tcl8.6"
$tk_path = Join-Path $python_path "tcl/tk8.6"

# Fallback if the versioned folders aren't found
if (-not (Test-Path $tcl_path)) { $tcl_path = Join-Path $python_path "tcl/tcl86" }
if (-not (Test-Path $tk_path)) { $tk_path = Join-Path $python_path "tcl/tk86" }

Write-Host "Found Tcl at: $tcl_path" -ForegroundColor Gray
Write-Host "Found Tk at: $tk_path" -ForegroundColor Gray

# 3. Run PyInstaller
# We use --distpath "release" to bypass any file locks on the old "dist" folder.
pyinstaller --noconfirm --onedir --windowed `
    --name "Oracle AI Assistant" `
    --distpath "release" `
    --icon "assets/oracle_icon.ico" `
    --add-data "$($tcl_path);_tcl_data" `
    --add-data "$($tk_path);_tk_data" `
    --collect-all "customtkinter" `
    --hidden-import "PIL._tkinter_finder" `
    --hidden-import "PIL.Image" `
    --hidden-import "PIL.ImageTk" `
    --hidden-import "chromadb.telemetry.product.posthog" `
    --hidden-import "posthog" `
    --hidden-import "chromadb.api.rust" `
    --hidden-import "chromadb.api.segment" `
    --hidden-import "chromadb.db.impl.sqlite" `
    --hidden-import "chromadb.migrations.embeddings" `
    main.py

# 4. Ensure the assets folder is also copied to the root of the release folder for runtime access
Copy-Item -Path "assets" -Destination "release/Oracle AI Assistant/assets" -Recurse -Force

Write-Host "--- Build Complete! ---" -ForegroundColor Green
Write-Host "You can find your executable in the 'release/Oracle AI Assistant' folder." -ForegroundColor Yellow
Write-Host "Note: Run the application once to allow the Web Agent to download its driver." -ForegroundColor Cyan
