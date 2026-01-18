# Quick Start Script for NBA Analyzer
# This script sets up and runs the NBA Analyzer application

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NBA 2024-2025 Season Analyzer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/3] Virtual environment found" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[2/3] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install/check dependencies
Write-Host "[3/3] Checking dependencies..." -ForegroundColor Yellow
$requirements = Get-Content requirements.txt
$installed = & python -m pip list --format=freeze

$needsInstall = $false
foreach ($req in $requirements) {
    $package = $req.Split("==")[0]
    if (-not ($installed -match $package)) {
        $needsInstall = $true
        break
    }
}

if ($needsInstall) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    & python -m pip install -r requirements.txt -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "All dependencies are installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Starting NBA Analyzer..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will open in your browser automatically." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Run the Streamlit app using the virtual environment's Python
& .\.venv\Scripts\python.exe -m streamlit run app.py
