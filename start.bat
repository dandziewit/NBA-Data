@echo off
REM Quick Start Script for NBA Analyzer (Windows CMD)
REM This script sets up and runs the NBA Analyzer application

echo ============================================
echo   NBA 2025-2026 Season Analyzer
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".\.venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
) else (
    echo [1/3] Virtual environment found
)

REM Activate virtual environment
echo [2/3] Activating virtual environment...
call .\.venv\Scripts\activate.bat

REM Install dependencies
echo [3/3] Checking dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo ============================================
echo   Starting NBA Analyzer...
echo ============================================
echo.
echo The app will open in your browser.
echo Press Ctrl+C to stop the server.
echo.

REM Run the Streamlit app
streamlit run app.py
